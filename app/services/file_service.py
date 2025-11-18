import os
import uuid
import shutil
from typing import Optional
from fastapi import UploadFile
from PIL import Image
from app.core.config import settings
from app.models.uploaded_file import UploadType


class FileService:
    @staticmethod
    def save_file(file: UploadFile, upload_type: UploadType, user_id: str = None) -> dict:
        """Save uploaded file and return file info"""
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Determine upload directory based on type
        type_dirs = {
            UploadType.AVATAR: "avatars",
            UploadType.LOGO: "logos", 
            UploadType.PROJECT_IMAGE: "project_images",
            UploadType.PORTFOLIO_IMAGE: "portfolio_images",
            UploadType.DASHBOARD_ZIP: "dashboards"
        }
        
        upload_dir = os.path.join(settings.UPLOAD_DIR, type_dirs[upload_type])
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Optimize image if it's an image file
        if upload_type in [UploadType.AVATAR, UploadType.LOGO, UploadType.PROJECT_IMAGE, UploadType.PORTFOLIO_IMAGE]:
            FileService._optimize_image(file_path)
        
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "mime_type": file.content_type,
            "upload_type": upload_type
        }
    
    @staticmethod
    def _optimize_image(file_path: str, max_size: tuple = (800, 800), quality: int = 85):
        """Optimize image size and quality"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Resize if larger than max_size
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save with optimization
                img.save(file_path, "JPEG", quality=quality, optimize=True)
        except Exception as e:
            print(f"Error optimizing image {file_path}: {e}")
    
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
    def get_file_url(filename: str, upload_type: UploadType) -> str:
        """Generate URL for accessing uploaded file"""
        type_dirs = {
            UploadType.AVATAR: "avatars",
            UploadType.LOGO: "logos",
            UploadType.PROJECT_IMAGE: "project_images", 
            UploadType.PORTFOLIO_IMAGE: "portfolio_images",
            UploadType.DASHBOARD_ZIP: "dashboards"
        }
        
        return f"/static/{type_dirs[upload_type]}/{filename}"
    
    @staticmethod
    def validate_file(file: UploadFile, upload_type: UploadType) -> Optional[str]:
        """Validate file type and size"""
        
        # Check file size
        if file.size > settings.MAX_FILE_SIZE:
            return f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
        
        # Define allowed types
        image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        zip_types = ["application/zip", "application/x-zip-compressed"]
        
        allowed_types = {
            UploadType.AVATAR: image_types,
            UploadType.LOGO: image_types,
            UploadType.PROJECT_IMAGE: image_types,
            UploadType.PORTFOLIO_IMAGE: image_types,
            UploadType.DASHBOARD_ZIP: zip_types
        }
        
        if file.content_type not in allowed_types[upload_type]:
            return f"Invalid file type. Allowed types: {', '.join(allowed_types[upload_type])}"
        
        return None