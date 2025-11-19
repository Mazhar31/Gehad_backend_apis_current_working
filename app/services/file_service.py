import os
import uuid
from typing import Optional
from fastapi import UploadFile
from PIL import Image
from io import BytesIO
from app.core.config import settings
from app.models.uploaded_file import UploadType
# Import moved to function level to avoid circular dependency

# Set PIL limits to prevent decompression bomb warnings
Image.MAX_IMAGE_PIXELS = 178956970  # Increase limit but keep reasonable


class FileService:
    @staticmethod
    async def save_file(file: UploadFile, upload_type: str, user_id: str = None) -> dict:
        """Save uploaded file to Firebase Storage and return file info"""
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Determine upload directory based on type with proper structure
        type_dirs = {
            "avatar": "users",
            "logo": "clients", 
            "project": "projects",
            "portfolio": "portfolio",
            "dashboard": "dashboards"
        }
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Optimize image if it's an image file
        if upload_type in ["avatar", "logo", "project", "portfolio"]:
            file_content = FileService._optimize_image_bytes(file_content)
        
        # Upload to Firebase Storage with proper folder structure
        from app.services.firebase_storage_service import firebase_storage_service
        
        # Use entity-specific folder structure
        if user_id:
            file_path = f"{type_dirs[upload_type]}/{user_id}.{file_extension.lstrip('.')}"
        else:
            file_path = f"{type_dirs[upload_type]}/{unique_filename}"
            
        public_url = firebase_storage_service.upload_file(
            file_content, 
            file_path, 
            file.content_type or "application/octet-stream"
        )
        
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "public_url": public_url,
            "file_size": file_size,
            "mime_type": file.content_type,
            "upload_type": upload_type
        }
    
    @staticmethod
    def _optimize_image_bytes(file_content: bytes, max_size: tuple = (800, 800), quality: int = 85) -> bytes:
        """Optimize image size and quality from bytes"""
        try:
            img = Image.open(BytesIO(file_content))
            
            # For avatars, use smaller size
            if max_size == (800, 800):
                max_size = (400, 400)
                quality = 80
            
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Resize if larger than max_size
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes with optimization
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=quality, optimize=True)
            return img_bytes.getvalue()
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return file_content
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file from filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_url(filename: str, upload_type: str) -> str:
        """Generate URL for accessing uploaded file (now returns Firebase Storage URL)"""
        # This method is now less relevant since Firebase Storage provides direct URLs
        # But keeping for backward compatibility
        type_dirs = {
            "avatar": "avatars",
            "logo": "logos",
            "project": "project_images", 
            "portfolio": "portfolio_images",
            "dashboard": "dashboards"
        }
        
        return f"https://firebasestorage.googleapis.com/v0/b/{settings.FIREBASE_STORAGE_BUCKET}/o/{type_dirs[upload_type]}%2F{filename}?alt=media"
    
    @staticmethod
    def validate_file(file: UploadFile, upload_type: str) -> Optional[str]:
        """Validate file type and size"""
        
        # Check file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            return f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
        
        # Define allowed types
        image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        zip_types = ["application/zip", "application/x-zip-compressed"]
        
        allowed_types = {
            "avatar": image_types,
            "logo": image_types,
            "project": image_types,
            "portfolio": image_types,
            "dashboard": zip_types
        }
        
        if file.content_type not in allowed_types[upload_type]:
            return f"Invalid file type. Allowed types: {', '.join(allowed_types[upload_type])}"
        
        return None