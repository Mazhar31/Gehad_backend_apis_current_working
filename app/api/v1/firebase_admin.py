from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.core.firebase_db import firebase_db
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.services.file_service import FileService
from typing import Optional

router = APIRouter()

@router.put("/profile", response_model=ResponseModel)
async def update_admin_profile(
    name: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    current_admin = Depends(get_current_admin)
):
    """Update current admin's profile"""
    
    update_data = {}
    
    # Update basic fields
    if name:
        update_data["name"] = name
    if position:
        update_data["position"] = position
    
    # Handle avatar upload
    if avatar:
        try:
            # Validate file
            validation_error = FileService.validate_file(avatar, "avatar")
            if validation_error:
                raise HTTPException(status_code=400, detail=validation_error)
            
            # Upload to Firebase Storage with admin folder structure
            from app.services.firebase_storage_service import firebase_storage_service
            import uuid
            
            # Read file content
            file_content = await avatar.read()
            file_extension = avatar.filename.split('.')[-1] if avatar.filename else 'jpg'
            file_path = f"admin/{current_admin['id']}.{file_extension}"
            
            # Upload directly to admin folder
            public_url = firebase_storage_service.upload_file(
                file_content, 
                file_path, 
                avatar.content_type or "image/jpeg"
            )
            update_data["avatar_url"] = public_url
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload avatar: {str(e)}")
    
    # Update admin in Firebase
    if update_data:
        updated_admin = firebase_db.update('admins', current_admin["id"], update_data)
        if not updated_admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        return ResponseModel(
            data=updated_admin,
            message="Profile updated successfully"
        )
    
    return ResponseModel(
        data=current_admin,
        message="No changes made"
    )

@router.get("/profile", response_model=ResponseModel)
async def get_admin_profile(current_admin = Depends(get_current_admin)):
    """Get current admin's profile"""
    
    return ResponseModel(
        data=current_admin,
        message="Profile retrieved successfully"
    )