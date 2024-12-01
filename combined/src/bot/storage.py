from asyncio.log import logger
from minio import Minio
from minio.error import S3Error
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.units import inch
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename, TextLexer, get_lexer_by_name
import html
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import requests
import tempfile
from pathlib import Path

load_dotenv()

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


class MinioStorage:
    FONT_URLS = {
        "DejaVuSans": "https://github.com/lionel-/fontDejaVu/raw/master/inst/fonts/dejavu-fonts/ttf/DejaVuSans.ttf",
        "DejaVuSans-Bold": "https://github.com/lionel-/fontDejaVu/raw/master/inst/fonts/dejavu-fonts/ttf/DejaVuSans-Bold.ttf",
        "DejaVuSansMono": "https://github.com/lionel-/fontDejaVu/raw/master/inst/fonts/dejavu-fonts/ttf/DejaVuSansMono.ttf",
    }

    def __init__(self):
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
        self._ensure_buckets()
        self.fonts_dir = self._setup_fonts_directory()
        self._register_fonts()

    def _setup_fonts_directory(self) -> Path:
        """Setup fonts directory in user's cache"""
        cache_dir = Path(tempfile.gettempdir()) / "telegram-review-bot" / "fonts"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def _download_font(self, font_name: str, url: str) -> Path:
        """Download a font file if it doesn't exist"""
        font_path = self.fonts_dir / f"{font_name}.ttf"

        if not font_path.exists():
            logger.info(f"Downloading font {font_name}...")
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                with open(font_path, "wb") as f:
                    f.write(response.content)

                logger.info(f"Font {font_name} downloaded successfully")
            except Exception as e:
                logger.error(f"Error downloading font {font_name}: {e}")
                raise

        return font_path

    def _ensure_buckets(self):
        """Ensure required buckets exist"""
        for bucket in ["uploads", "reports"]:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)

    def _register_fonts(self):
        """Register fonts for PDF generation with Unicode support"""
        try:
            # Download and register each font
            for font_name, url in self.FONT_URLS.items():
                font_path = self._download_font(font_name, url)
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))

            # Add font mappings
            addMapping("DejaVuSans", 0, 0, "DejaVuSans")
            addMapping("DejaVuSans", 1, 0, "DejaVuSans-Bold")

            logger.info("Fonts registered successfully")
        except Exception as e:
            logger.error(f"Could not register fonts: {e}")
            raise

    def upload_file(
        self, file_path: str, bucket: str, object_name: str, metadata: dict = None
    ) -> str:
        """Upload a file to MinIO and return its object name"""
        try:
            self.client.fput_object(bucket, object_name, file_path, metadata=metadata)
            return object_name
        except S3Error as e:
            raise Exception(f"Error uploading to MinIO: {e}")

    def get_presigned_url(
        self, bucket: str, object_name: str, expires: int = 3600
    ) -> str:
        """Generate a presigned URL for object download"""
        try:
            return self.client.presigned_get_object(
                bucket, object_name, expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            raise Exception(f"Error generating presigned URL: {e}")

    def _apply_syntax_highlighting(self, code: str, language: str = "text") -> str:
        """Apply syntax highlighting to code"""
        try:
            # First decode any HTML entities in the input
            code = html.unescape(code)

            # Get the appropriate lexer
            lexer = get_lexer_by_name(language, stripall=True)
        except:
            lexer = TextLexer()

        # Use a formatter that outputs plain text with ANSI color codes
        formatter = HtmlFormatter(
            style="monokai", noclasses=True, nowrap=True, linenos=False
        )

        try:
            # Just return the original code without highlighting for now
            # This ensures we get readable code in the PDF
            return code
        except Exception as e:
            logger.error(f"Error in syntax highlighting: {e}")
            return code

    def generate_review_report(self, reviews: list, user_id: int, original_filename: str = None) -> str:
        """Generate a PDF review report with all reviews and upload it to MinIO"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use original filename if provided, otherwise fallback to default name
        base_name = original_filename.rsplit('.', 1)[0] if original_filename else f"review_report_{user_id}"
        report_name = f"{base_name}_review_{timestamp}.pdf"
        pdf_path = f"/tmp/{report_name}"

        # Create PDF document with smaller margins
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Style definitions (keeping the same styles as before)
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontName="DejaVuSans-Bold",
            textColor=colors.HexColor("#2c3e50"),
            fontSize=20,
            spaceAfter=30,
            alignment=1,
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontName="DejaVuSans-Bold",
            fontSize=14,
            textColor=colors.HexColor("#2c3e50"),
            spaceBefore=20,
            spaceAfter=10,
            encoding="utf-8",
        )

        normal_style = ParagraphStyle(
            "CustomNormal",
            parent=styles["Normal"],
            fontName="DejaVuSans",
            fontSize=11,
            leading=14,
            leftIndent=20,
            encoding="utf-8",
        )

        code_style = ParagraphStyle(
            "CodeBlock",
            parent=styles["Code"],
            fontName="DejaVuSansMono",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#2c3e50"),
            backColor=colors.HexColor("#f5f6fa"),
            borderColor=colors.HexColor("#dcdde1"),
            borderWidth=1,
            borderPadding=10,
            spaceBefore=10,
            spaceAfter=20,
            leftIndent=40,
            rightIndent=40,
            encoding="utf-8",
            firstLineIndent=0,
        )

        # Build PDF content
        elements = []

        # Add title with total review count
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        elements.append(
            Paragraph(
                f"Код-ревью (из {len(reviews)} ревью) от {current_time}", title_style
            )
        )
        elements.append(Spacer(1, 0.2 * inch))

        # Group reviews by file for better organization
        reviews_by_file = {}
        for review in reviews:
            file_path = review["file"]
            if file_path not in reviews_by_file:
                reviews_by_file[file_path] = []
            reviews_by_file[file_path].append(review)

        # Process reviews grouped by file
        for file_path, file_reviews in reviews_by_file.items():
            # Add file header
            elements.append(Paragraph(f"Файл: {file_path}", heading_style))
            elements.append(Spacer(1, 0.1 * inch))

            # Sort reviews by line number
            file_reviews.sort(key=lambda x: x["line_number"])

            for review in file_reviews:
                elements.append(
                    Paragraph(f"Строка {review['line_number']}", normal_style)
                )

                # Review comment
                elements.append(Paragraph("• Комментарий:", heading_style))
                escaped_review = html.escape(review["review"])  # Escape HTML tags
                elements.append(Paragraph(escaped_review, normal_style))

                # Current code section
                elements.append(Paragraph("• Текущий код:", heading_style))
                try:
                    current_code = review["code"].strip()
                    current_code = html.unescape(current_code)
                    current_code = current_code.replace("\t", "    ")
                    # Remove line numbers and the separator character
                    lines = current_code.splitlines()
                    cleaned_lines = []
                    for line in lines:
                        # Skip empty lines
                        if not line.strip():
                            cleaned_lines.append("")
                            continue
                        # Remove line numbers and separator (│)
                        parts = line.split("│", 1)
                        if len(parts) > 1:
                            cleaned_lines.append(parts[1].rstrip())
                        else:
                            cleaned_lines.append(line.rstrip())
                    current_code = "\n".join(cleaned_lines)

                    # Remove any leading spaces while preserving relative indentation
                    if cleaned_lines:
                        min_indent = min(
                            len(line) - len(line.lstrip())
                            for line in cleaned_lines
                            if line.strip()
                        )
                        current_code = "\n".join(
                            line[min_indent:] if line.strip() else line
                            for line in cleaned_lines
                        )
                    elements.append(Preformatted(current_code, code_style))
                except Exception as e:
                    logger.error(f"Error processing code block: {e}")
                    elements.append(Preformatted(review["code"], code_style))

                # Suggested code section (if present)
                if review.get("suggested_code"):
                    elements.append(Paragraph("• Предлагаемый код:", heading_style))
                    try:
                        suggested_code = review["suggested_code"].strip()
                        suggested_code = html.unescape(suggested_code)
                        suggested_code = suggested_code.replace("\t", "    ")
                        elements.append(Preformatted(suggested_code, code_style))
                    except Exception as e:
                        logger.error(f"Error processing suggested code block: {e}")
                        elements.append(
                            Preformatted(review["suggested_code"], code_style)
                        )

                # Add separator between reviews
                elements.append(Spacer(1, 0.2 * inch))
                elements.append(
                    Paragraph(
                        "\u2500" * 50,
                        ParagraphStyle(
                            "Separator",
                            alignment=1,
                            textColor=colors.HexColor("#dcdde1"),
                            encoding="utf-8",
                            fontName="DejaVuSans",
                        ),
                    )
                )
                elements.append(Spacer(1, 0.2 * inch))

        # Generate PDF
        try:
            doc.build(elements)
        except Exception as e:
            logger.error(f"Error building PDF: {e}", exc_info=True)
            raise

        # Upload to MinIO
        object_name = f"reports/{user_id}/{report_name}"
        self.upload_file(
            pdf_path,
            "reports",
            object_name,
            metadata={
                "user_id": str(user_id),
                "timestamp": timestamp,
                "content_type": "application/pdf",
            },
        )

        # Clean up temporary file
        os.remove(pdf_path)

        return object_name
