from firebase_admin import storage
import uuid
import requests
from io import BytesIO
from PIL import Image
import logging
from app.core.config import settings
from fastapi import UploadFile

logger = logging.getLogger(__name__)

class FirebaseStorageService:
    def __init__(self):
        self._bucket = None
    
    @property
    def bucket(self):
        if self._bucket is None:
            self._bucket = storage.bucket(settings.FIREBASE_STORAGE_BUCKET)
        return self._bucket
    
    def upload_avatar_from_url(self, url: str, user_id: str) -> str:
        """Download image from URL and upload to Firebase Storage"""
        try:
            # Download image
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Process image
            image = Image.open(BytesIO(response.content))
            image = image.convert('RGB')
            image = image.resize((150, 150), Image.Resampling.LANCZOS)
            
            # Save to bytes
            img_bytes = BytesIO()
            image.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            # Upload to Firebase Storage
            blob_name = f"avatars/{user_id}.jpg"
            blob = self.bucket.blob(blob_name)
            blob.upload_from_file(img_bytes, content_type='image/jpeg')
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Failed to upload avatar for {user_id}: {e}")
            # Return a default avatar URL as fallback
            return self.get_default_avatar(user_id)
    
    def upload_file(self, file_content: bytes, file_path: str, content_type: str) -> str:
        """Upload file to Firebase Storage"""
        try:
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(file_content, content_type=content_type)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            raise e
    
    async def upload_avatar(self, file: UploadFile, user_id: str) -> str:
        """Upload user avatar file to Firebase Storage"""
        try:
            # Read file content
            file_content = await file.read()
            
            # Process image
            image = Image.open(BytesIO(file_content))
            image = image.convert('RGB')
            image = image.resize((150, 150), Image.Resampling.LANCZOS)
            
            # Save to bytes
            img_bytes = BytesIO()
            image.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            # Upload to Firebase Storage
            blob_name = f"avatars/{user_id}.jpg"
            blob = self.bucket.blob(blob_name)
            blob.upload_from_file(img_bytes, content_type='image/jpeg')
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Failed to upload avatar for {user_id}: {e}")
            raise e
    
    def get_default_avatar(self, user_id: str) -> str:
        """Generate a default avatar and upload to Firebase Storage"""
        try:
            # Create a simple colored avatar
            from PIL import Image, ImageDraw
            
            # Generate color based on user_id hash
            color_hash = hash(user_id) % 16777215
            color = f"#{color_hash:06x}"
            
            # Create image
            img = Image.new('RGB', (150, 150), color)
            draw = ImageDraw.Draw(img)
            
            # Add initials or simple pattern
            draw.ellipse([25, 25, 125, 125], fill='white', outline=color, width=3)
            
            # Save to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            # Upload to Firebase Storage
            blob_name = f"avatars/default_{user_id}.jpg"
            blob = self.bucket.blob(blob_name)
            blob.upload_from_file(img_bytes, content_type='image/jpeg')
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Failed to create default avatar for {user_id}: {e}")
            return f"https://ui-avatars.com/api/?name={user_id}&size=150&background=random"

firebase_storage_service = FirebaseStorageService()