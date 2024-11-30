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
from pygments.lexers import get_lexer_for_filename, TextLexer
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
        'DejaVuSans': 'https://github.com/lionel-/fontDejaVu/raw/master/inst/fonts/dejavu-fonts/ttf/DejaVuSans.ttf',
        'DejaVuSans-Bold': 'https://github.com/lionel-/fontDejaVu/raw/master/inst/fonts/dejavu-fonts/ttf/DejaVuSans-Bold.ttf',
        'DejaVuSansMono': 'https://github.com/lionel-/fontDejaVu/raw/master/inst/fonts/dejavu-fonts/ttf/DejaVuSansMono.ttf'
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
        cache_dir = Path(tempfile.gettempdir()) / 'telegram-review-bot' / 'fonts'
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

                with open(font_path, 'wb') as f:
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
            addMapping('DejaVuSans', 0, 0, 'DejaVuSans')
            addMapping('DejaVuSans', 1, 0, 'DejaVuSans-Bold')

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

    def generate_diff_report(self, diffs: list, user_id: int, page: int) -> str:
        """Generate a PDF diff report and upload it to MinIO"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"diff_report_{user_id}_{timestamp}_page{page}.pdf"
        pdf_path = f"/tmp/{report_name}"

        # Create PDF document with smaller margins
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=36,  # Reduced margins (0.5 inch)
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        # Styles
        styles = getSampleStyleSheet()

        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='DejaVuSans-Bold',
            fontSize=20,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        # Section header style with proper Unicode handling
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName='DejaVuSans-Bold',
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=20,
            spaceAfter=10,
            encoding='utf-8'  # Add explicit encoding
        )

        # File info style
        file_info_style = ParagraphStyle(
            'FileInfo',
            parent=styles['Normal'],
            fontName='DejaVuSans',
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),  # Grey
            leftIndent=20,
            spaceBefore=5,
            spaceAfter=5
        )

        # Normal text style with proper Unicode handling
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName='DejaVuSans',
            fontSize=11,
            leading=14,
            leftIndent=20,
            encoding='utf-8'  # Add explicit encoding
        )

        # Code block style
        code_style = ParagraphStyle(
            'CodeBlock',
            parent=styles['Code'],
            fontName='DejaVuSansMono',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#2c3e50'),
            backColor=colors.HexColor('#f5f6fa'),
            borderColor=colors.HexColor('#dcdde1'),
            borderWidth=1,
            borderPadding=10,
            spaceBefore=10,
            spaceAfter=20,
            leftIndent=40,
            rightIndent=40,
            encoding='utf-8'  # Add explicit encoding
        )

        # Build PDF content
        elements = []

        # Add title
        elements.append(Paragraph(f"Code Review Report", title_style))
        elements.append(Paragraph(f"Page {page}", file_info_style))
        elements.append(Spacer(1, 0.2 * inch))

        for diff in diffs:
            # File information (using simpler Unicode symbols)
            elements.append(Paragraph(
                f"» {html.escape(diff['file'])}",
                heading_style
            ))
            elements.append(Paragraph(
                f"Line: {diff['line_number']}",
                normal_style
            ))

            # Review comment
            elements.append(Paragraph(
                "• Review Comment:",
                heading_style
            ))
            elements.append(Paragraph(
                html.escape(diff['review']),
                normal_style
            ))

            # Original code
            elements.append(Paragraph(
                "• Original Code:",
                heading_style
            ))
            elements.append(
                Preformatted(
                    html.escape(diff["original"]),
                    code_style
                )
            )

            # Suggested replacement
            elements.append(Paragraph(
                "• Suggested Replacement:",
                heading_style
            ))
            elements.append(
                Preformatted(
                    html.escape(diff["replacement"]),
                    code_style
                )
            )

            # Add separator using basic Unicode characters
            elements.append(Spacer(1, 0.3 * inch))
            elements.append(
                Paragraph(
                    "\u2500" * 50,  # Unicode BOX DRAWINGS LIGHT HORIZONTAL
                    ParagraphStyle(
                        'Separator',
                        alignment=1,
                        textColor=colors.HexColor('#dcdde1'),
                        encoding='utf-8',
                        fontName='DejaVuSans'
                    )
                )
            )
            elements.append(Spacer(1, 0.3 * inch))

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
                "page": str(page),
                "content_type": "application/pdf"
            }
        )

        # Clean up temporary file
        os.remove(pdf_path)

        return object_name
