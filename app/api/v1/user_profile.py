from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from app.core.firebase_db import firebase_db
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_user
from app.core.security import get_password_hash, verify_password
from app.services.firebase_storage_service import firebase_storage_service
from typing import Dict, Any

router = APIRouter()

@router.put("/profile", response_model=ResponseModel)
async def update_user_profile(
    profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile"""
    user_id = current_user.get('id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found")
    
    update_data = {}
    if 'name' in profile_data:
        update_data['name'] = profile_data['name']
    if 'avatar_url' in profile_data:
        update_data['avatar_url'] = profile_data['avatar_url']
    
    user = firebase_db.update('users', user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return ResponseModel(
        data=user,
        message="Profile updated successfully"
    )

@router.put("/change-password", response_model=ResponseModel)
async def change_user_password(
    password_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password"""
    user_id = current_user.get('id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found")
    
    current_password = password_data.get('current_password')
    new_password = password_data.get('new_password')
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Current and new passwords are required")
    
    # Verify current password
    user = firebase_db.get_by_id('users', user_id)
    if not user or not verify_password(current_password, user.get('password_hash', '')):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    new_password_hash = get_password_hash(new_password)
    updated_user = firebase_db.update('users', user_id, {'password_hash': new_password_hash})
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return ResponseModel(message="Password changed successfully")

@router.post("/upload-avatar", response_model=ResponseModel)
async def upload_user_avatar(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload user avatar"""
    user_id = current_user.get('id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found")
    
    try:
        # Upload to Firebase Storage
        avatar_url = await firebase_storage_service.upload_avatar(file, user_id)
        
        # Update user record
        user = firebase_db.update('users', user_id, {'avatar_url': avatar_url})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return ResponseModel(
            data={'avatar_url': avatar_url},
            message="Avatar uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload avatar: {str(e)}")