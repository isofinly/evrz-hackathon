from minio import Minio
from minio.error import S3Error
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv

load_dotenv()

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


class MinioStorage:
    def __init__(self):
        self.client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
        self._ensure_buckets()

    def _ensure_buckets(self):
        """Ensure required buckets exist"""
        for bucket in ["uploads", "reports"]:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)

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
        """Generate a diff report and upload it to MinIO"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"diff_report_{user_id}_{timestamp}_page{page}.diff"

        with open(f"/tmp/{report_name}", "w") as f:
            for diff in diffs:
                f.write(f"File: {diff['file']} (line {diff['line_number']})\n")
                f.write(f"Review: {diff['review']}\n\n")
                f.write("```diff\n")

                # Write original code with minus signs
                for line in diff["original"].split("\n"):
                    if line.strip():
                        f.write(f"- {line}\n")

                # Write replacement placeholder
                f.write(f"+ {diff['replacement']}\n")
                f.write("```\n\n")

        # Upload to MinIO
        object_name = f"reports/{user_id}/{report_name}"
        self.upload_file(
            f"/tmp/{report_name}",
            "reports",
            object_name,
            metadata={
                "user_id": str(user_id),
                "timestamp": timestamp,
                "page": str(page),
            },
        )

        # Clean up temporary file
        os.remove(f"/tmp/{report_name}")

        return object_name
