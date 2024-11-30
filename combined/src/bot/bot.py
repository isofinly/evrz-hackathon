import telebot
import os
import tempfile
import logging
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.utils import extract_archive, get_project_structure, parse_review_tags
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from src.bot.storage import MinioStorage
from datetime import datetime
from src.review.review import ProjectReviewer, FileReviewer
from pathlib import Path

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize bot with state storage
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)

# Initialize MinIO storage
storage = MinioStorage()

# Store review results globally (in-memory storage)
review_results = {}


class ReviewStates(StatesGroup):
    viewing_reviews = State()
    current_page = State()


def create_review_message(reviews: list, page: int, total_pages: int) -> str:
    """Create a formatted review message for the current page."""
    REVIEWS_PER_PAGE = 3
    start_idx = (page - 1) * REVIEWS_PER_PAGE
    end_idx = start_idx + REVIEWS_PER_PAGE
    current_reviews = reviews[start_idx:end_idx]

    message_parts = [f"📝 Code Reviews (Page {page}/{total_pages})\n"]

    for review in current_reviews:
        message_parts.extend(
            [
                f"\n📄 {review['file']} (line {review['line_number']})",
                f"💡 Review: {review['review']}",
                f"\nCurrent code:",
                f"```\n{review['code']}\n```",
            ]
        )

        if review.get("suggested_code"):
            message_parts.append(f"Suggested code:")
            message_parts.append(f"```\n{review['suggested_code']}\n```")

        message_parts.append("─" * 40)

    message_parts.append(
        "\nUse the buttons below to navigate pages or download the complete report."
    )
    return "\n".join(message_parts)


def create_pagination_keyboard(
    current_page: int, total_pages: int, user_id: int
) -> InlineKeyboardMarkup:
    """Create pagination keyboard with download button."""
    keyboard = InlineKeyboardMarkup(row_width=5)
    buttons = []

    # First page
    if current_page > 1:
        buttons.append(InlineKeyboardButton("⏮️", callback_data=f"page_{user_id}_1"))

    # Previous page
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton("◀️", callback_data=f"page_{user_id}_{current_page-1}")
        )

    # Current page indicator
    buttons.append(
        InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop")
    )

    # Next page
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton("▶️", callback_data=f"page_{user_id}_{current_page+1}")
        )

    # Last page
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton("⏭️", callback_data=f"page_{user_id}_{total_pages}")
        )

    # Add navigation buttons row
    keyboard.add(*buttons)

    # Add download button in new row
    keyboard.add(
        InlineKeyboardButton(
            "📥 Download Full Report", callback_data=f"download_{user_id}_all"
        )
    )

    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def handle_pagination(call):
    """Handle pagination button clicks."""
    try:
        _, user_id, page = call.data.split("_")
        page = int(page)
        user_id = int(user_id)

        if str(user_id) not in review_results:
            bot.answer_callback_query(
                call.id, "Review session expired. Please send the archive again."
            )
            return

        reviews = review_results[str(user_id)]["reviews"]
        total_pages = review_results[str(user_id)]["total_pages"]

        message = create_review_message(reviews, page, total_pages)
        keyboard = create_pagination_keyboard(
            page, total_pages, user_id
        )  # Now includes download button

        bot.edit_message_text(
            message,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
        bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Error handling pagination: {e}", exc_info=True)
        bot.answer_callback_query(
            call.id, "❌ Failed to change page. Please try again."
        )


def is_supported_file(file_name: str) -> tuple[bool, str]:
    """Check if the file is supported and return its type."""
    archives = {".zip", ".rar", ".7z"}
    code_files = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".css",
        ".scss",
        ".html",
        ".php",
        ".rb",
        ".go",
        ".rs",
        ".swift",
        ".kt",
        ".cs",
        ".vue",
        ".md",
        ".json",
        ".yml",
        ".yaml",
        ".xml",
    }

    file_name = file_name.lower()
    ext = os.path.splitext(file_name)[1]

    if any(file_name.endswith(archive_ext) for archive_ext in archives):
        return True, "archive"
    elif ext in code_files:
        return True, "code"
    return False, ""


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    """Handle the /start and /help commands."""
    welcome_text = (
        "Hello! I can help you find and process review tags in your code.\n\n"
        "You can send me:\n"
        "1. Archive files (ZIP, RAR, 7z) containing your project\n"
        "2. Individual code files (Python, JavaScript, TypeScript, etc.)\n\n"
        "I'll look for `<REVIEW></REVIEW>` tags and show you what needs to be changed."
    )
    bot.reply_to(message, welcome_text)


@bot.callback_query_handler(func=lambda call: call.data.startswith("download_"))
def handle_download(call):
    """Handle download button clicks."""
    try:
        _, user_id, _ = call.data.split("_")
        user_id = int(user_id)

        if str(user_id) not in review_results:
            bot.answer_callback_query(
                call.id, "Review session expired. Please send the archive again."
            )
            return

        # Get ALL reviews, not just current page
        all_reviews = review_results[str(user_id)]["reviews"]

        # Generate report with all reviews
        object_name = storage.generate_review_report(all_reviews, user_id)

        # Get download URL
        download_url = storage.get_presigned_url("reports", object_name)

        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"📥 [Download Complete Review Report]({download_url})",
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.error(f"Error generating review report: {e}", exc_info=True)
        bot.answer_callback_query(
            call.id, "❌ Failed to generate report. Please try again."
        )


@bot.message_handler(content_types=["document"])
def handle_document(message):
    """Handle incoming documents (both archives and individual files)."""
    try:
        file_name = message.document.file_name
        file_size = message.document.file_size

        # Check file size (Telegram's limit is 50MB)
        if file_size > 50 * 1024 * 1024:  # 50MB in bytes
            bot.reply_to(message, "❌ File is too large. Maximum size is 50MB.")
            return

        is_supported, file_type = is_supported_file(file_name)

        if not is_supported:
            bot.reply_to(
                message,
                "❌ Unsupported file type. Please send a code file or archive (ZIP, RAR, 7z).",
            )
            return

        # Show progress for large files
        status_message = bot.reply_to(message, "📥 Downloading file...")

        try:
            # Download file in chunks for large files
            file_info = bot.get_file(message.document.file_id)

            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = os.path.join(tmpdir, file_name)

                # Download in chunks
                with open(file_path, "wb") as f:
                    file_stream = bot.download_file(file_info.file_path)
                    f.write(file_stream)

                # Upload to MinIO
                object_name = f"uploads/{message.from_user.id}/{file_name}"
                storage.upload_file(
                    file_path,
                    "uploads",
                    object_name,
                    metadata={
                        "user_id": str(message.from_user.id),
                        "chat_id": str(message.chat.id),
                        "file_name": file_name,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                # Create review directories
                review_dir = Path(tmpdir) / "review_output"
                review_dir.mkdir(parents=True, exist_ok=True)

                # Update status
                bot.edit_message_text(
                    "📦 Extracting files..."
                    if file_type == "archive"
                    else "📄 Processing file...",
                    chat_id=status_message.chat.id,
                    message_id=status_message.message_id,
                )

                if file_type == "archive":
                    extract_dir = os.path.join(tmpdir, "extracted")
                    os.makedirs(extract_dir, exist_ok=True)

                    logger.info(f"Attempting to extract {file_name} to {extract_dir}")
                    if not extract_archive(file_path, extract_dir):
                        bot.edit_message_text(
                            "❌ Failed to extract the archive. Please ensure it is not corrupted.",
                            chat_id=status_message.chat.id,
                            message_id=status_message.message_id,
                        )
                        return

                    # Verify the extraction directory has content and find the root project directory
                    extracted_items = list(Path(extract_dir).iterdir())
                    if not extracted_items:
                        bot.edit_message_text(
                            "❌ The archive appears to be empty.",
                            chat_id=status_message.chat.id,
                            message_id=status_message.message_id,
                        )
                        return

                    # If there's a single directory at the root, use that as project root
                    project_root = (
                        extracted_items[0]
                        if len(extracted_items) == 1 and extracted_items[0].is_dir()
                        else Path(extract_dir)
                    )

                    try:
                        project_reviewer = ProjectReviewer(
                            project_path=project_root, result_path=review_dir
                        )
                        project_reviewer.review()
                    except Exception as e:
                        logger.error(f"Project review failed: {str(e)}", exc_info=True)
                        bot.edit_message_text(
                            "❌ Failed to process the archive contents. Please ensure the archive structure is correct.",
                            chat_id=status_message.chat.id,
                            message_id=status_message.message_id,
                        )
                        return
                else:
                    # Use FileReviewer for single files
                    result_file = review_dir / file_name
                    file_reviewer = FileReviewer(
                        file_path=Path(file_path),
                        result_path=result_file
                    )
                    file_reviewer.review()

                # Parse review tags from the output
                reviews = parse_review_tags(review_dir)

                # Update status
                bot.edit_message_text(
                    "✅ Processing complete!",
                    chat_id=status_message.chat.id,
                    message_id=status_message.message_id,
                )

                if reviews:
                    # Store results for pagination
                    chat_id = str(message.chat.id)
                    REVIEWS_PER_PAGE = 3
                    total_pages = (
                        len(reviews) + REVIEWS_PER_PAGE - 1
                    ) // REVIEWS_PER_PAGE

                    review_results[chat_id] = {
                        "reviews": reviews,
                        "total_pages": total_pages,
                    }

                    # Send first page with download button
                    message_text = create_review_message(reviews, 1, total_pages)
                    keyboard = create_pagination_keyboard(
                        1, total_pages, message.from_user.id
                    )

                    bot.send_message(
                        message.chat.id,
                        message_text,
                        reply_markup=keyboard,
                        parse_mode="Markdown",
                    )
                else:
                    bot.send_message(
                        message.chat.id, "✅ No `<REVIEW></REVIEW>` tags found."
                    )

        except Exception as e:
            logger.error(f"Error downloading/processing file: {e}", exc_info=True)
            bot.edit_message_text(
                "❌ Failed to process the file. Please try again.",
                chat_id=status_message.chat.id,
                message_id=status_message.message_id,
            )

    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        bot.reply_to(
            message,
            "❌ An error occurred while processing your file. Please try again.",
        )


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Handle all other messages."""
    bot.reply_to(
        message, "Please send me a code file or archive (ZIP, RAR, 7z) to review."
    )


def run_bot():
    """Entry point for the bot"""
    try:
        logger.info("Starting bot...")
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_bot()
