import telebot
import os
import tempfile
import logging
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.utils import extract_archive, get_project_structure, parse_review_tags
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from src.storage import MinioStorage
from datetime import datetime

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


def create_diff_message(diffs: list, page: int, total_pages: int) -> str:
    """Create a formatted diff message for the current page."""
    DIFFS_PER_PAGE = 2  # Show fewer diffs per page since they're larger
    start_idx = (page - 1) * DIFFS_PER_PAGE
    end_idx = start_idx + DIFFS_PER_PAGE
    current_diffs = diffs[start_idx:end_idx]

    message_parts = [f"📝 Review Diffs (Page {page}/{total_pages})\n```diff"]

    for diff in current_diffs:
        message_parts.append(f"\n# {diff['file']} (line {diff['line_number']})")
        message_parts.append(f"# Review: {diff['review']}\n")

        # Split and format the original code block
        original_lines = diff["original"].split("\n")
        for line in original_lines:
            if line.strip():  # Only add non-empty lines
                message_parts.append(f"- {line.rstrip()}")

        message_parts.append(f"+ {diff['replacement']}\n")

    message_parts.append("```")
    return "\n".join(message_parts)


def create_pagination_keyboard(
    current_page: int, total_pages: int, chat_id: str
) -> InlineKeyboardMarkup:
    """Create pagination keyboard."""
    keyboard = InlineKeyboardMarkup()
    buttons = []

    # First page
    if current_page > 1:
        buttons.append(InlineKeyboardButton("⏮️", callback_data=f"page_{chat_id}_1"))

    # Previous page
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton("◀️", callback_data=f"page_{chat_id}_{current_page-1}")
        )

    # Current page indicator
    buttons.append(
        InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop")
    )

    # Next page
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton("▶️", callback_data=f"page_{chat_id}_{current_page+1}")
        )

    # Last page
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton("⏭️", callback_data=f"page_{chat_id}_{total_pages}")
        )

    keyboard.add(*buttons)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def handle_pagination(call):
    """Handle pagination button clicks."""
    try:
        _, chat_id, page = call.data.split("_")
        page = int(page)

        if chat_id not in review_results:
            bot.answer_callback_query(
                call.id, "Review session expired. Please send the archive again."
            )
            return

        diffs = review_results[chat_id]["diffs"]
        total_pages = review_results[chat_id]["total_pages"]

        message = create_diff_message(diffs, page, total_pages)
        keyboard = create_pagination_keyboard(page, total_pages, chat_id)

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
        bot.answer_callback_query(call.id, "An error occurred")


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


def create_diff_message_with_download(diffs: list, page: int, total_pages: int, user_id: int) -> tuple[str, InlineKeyboardMarkup]:
    """Create a formatted diff message with download button"""
    message = create_diff_message(diffs, page, total_pages)

    # Create pagination keyboard with download button
    keyboard = InlineKeyboardMarkup(row_width=5)
    buttons = []

    # Pagination buttons
    if page > 1:
        buttons.extend([
            InlineKeyboardButton("⏮️", callback_data=f"page_{user_id}_1"),
            InlineKeyboardButton("◀️", callback_data=f"page_{user_id}_{page-1}")
        ])

    buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="noop"))

    if page < total_pages:
        buttons.extend([
            InlineKeyboardButton("▶️", callback_data=f"page_{user_id}_{page+1}"),
            InlineKeyboardButton("⏭️", callback_data=f"page_{user_id}_{total_pages}")
        ])

    keyboard.add(*buttons)

    # Add download button in new row
    keyboard.add(InlineKeyboardButton("📥 Download Report", callback_data=f"download_{user_id}_{page}"))

    return message, keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith("download_"))
def handle_download(call):
    """Handle download button clicks"""
    try:
        _, user_id, page = call.data.split("_")
        user_id = int(user_id)
        page = int(page)

        if str(user_id) not in review_results:
            bot.answer_callback_query(
                call.id,
                "Review session expired. Please send the file again."
            )
            return

        diffs = review_results[str(user_id)]["diffs"]
        total_pages = review_results[str(user_id)]["total_pages"]

        # Get diffs for current page
        DIFFS_PER_PAGE = 2
        start_idx = (page - 1) * DIFFS_PER_PAGE
        end_idx = start_idx + DIFFS_PER_PAGE
        current_diffs = diffs[start_idx:end_idx]

        # Generate and upload diff report
        try:
            object_name = storage.generate_diff_report(current_diffs, user_id, page)
            download_url = storage.get_presigned_url('reports', object_name)

            bot.answer_callback_query(call.id)
            bot.send_message(
                call.message.chat.id,
                f"📥 Download your diff report:\n{download_url}",
                disable_web_page_preview=True
            )

        except Exception as e:
            logger.error(f"Error generating diff report: {e}", exc_info=True)
            bot.answer_callback_query(
                call.id,
                "Failed to generate report. Please try again."
            )

    except Exception as e:
        logger.error(f"Error handling download: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "An error occurred")


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
                    'uploads',
                    object_name,
                    metadata={
                        'user_id': str(message.from_user.id),
                        'chat_id': str(message.chat.id),
                        'file_name': file_name,
                        'timestamp': datetime.now().isoformat()
                    }
                )

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

                    if not extract_archive(file_path, extract_dir):
                        bot.edit_message_text(
                            "❌ Failed to extract the archive. Please ensure it is not corrupted.",
                            chat_id=status_message.chat.id,
                            message_id=status_message.message_id,
                        )
                        return

                    # Update status
                    bot.edit_message_text(
                        "🔍 Analyzing files...",
                        chat_id=status_message.chat.id,
                        message_id=status_message.message_id,
                    )

                    # Send project structure for archives
                    structure = get_project_structure(extract_dir)
                    if len(structure) > 4000:
                        structure = structure[:4000] + "\n... (truncated)"

                    bot.send_message(
                        message.chat.id,
                        f"📂 *Project Structure:*\n```\n{structure}\n```",
                        parse_mode="Markdown",
                    )

                    # Parse archive
                    diffs = parse_review_tags(extract_dir)
                else:
                    # Parse single file
                    diffs = parse_review_tags(file_path)

                # Update status
                bot.edit_message_text(
                    "✅ Processing complete!",
                    chat_id=status_message.chat.id,
                    message_id=status_message.message_id,
                )

                if diffs:
                    # Store results for pagination
                    chat_id = str(message.chat.id)
                    DIFFS_PER_PAGE = 2
                    total_pages = (len(diffs) + DIFFS_PER_PAGE - 1) // DIFFS_PER_PAGE

                    review_results[chat_id] = {
                        "diffs": diffs,
                        "total_pages": total_pages,
                    }

                    # Send first page with download button
                    message_text, keyboard = create_diff_message_with_download(
                        diffs, 1, total_pages, message.from_user.id
                    )

                    bot.send_message(
                        message.chat.id,
                        message_text,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
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
