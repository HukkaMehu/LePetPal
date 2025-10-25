"""
S3/MinIO storage utilities for media management.
"""
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
import logging
from typing import Optional
import io

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing S3/MinIO storage operations."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists, create if it doesn't."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket '{self.bucket_name}'")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
            else:
                logger.error(f"Error checking bucket: {e}")
        except Exception as e:
            # Handle connection errors gracefully (e.g., MinIO not running)
            logger.warning(f"Could not connect to S3/MinIO: {e}. Storage operations will fail until connection is established.")
    
    def upload_file(
        self,
        file_data: bytes,
        object_key: str,
        content_type: str = "image/jpeg"
    ) -> str:
        """
        Upload a file to S3/MinIO.
        
        Args:
            file_data: Binary file data
            object_key: S3 object key (path)
            content_type: MIME type of the file
            
        Returns:
            S3 URI of the uploaded file
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_data,
                ContentType=content_type
            )
            s3_uri = f"s3://{self.bucket_name}/{object_key}"
            logger.info(f"Uploaded file to {s3_uri}")
            return s3_uri
        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def get_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for accessing an S3 object.
        
        Args:
            object_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL or None if error
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    def delete_file(self, object_key: str) -> bool:
        """
        Delete a file from S3/MinIO.
        
        Args:
            object_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            logger.info(f"Deleted file: {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def get_public_url(self, object_key: str) -> str:
        """
        Get the public URL for an S3 object (for MinIO with public access).
        
        Args:
            object_key: S3 object key
            
        Returns:
            Public URL
        """
        return f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{object_key}"


# Singleton instance
storage_service = StorageService()
