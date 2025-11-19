from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.services.file_service import FileService
from app.utils.dependencies import get_current_admin_or_user
from app.schemas.common import ResponseModel
from typing import Dict, Any

router = APIRouter()

@router.post("/image", response_model=ResponseModel)
async def upload_image(
    file: UploadFile = File(...),
    type: str = Form(...),
    entity_id: str = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_admin_or_user)
):
    """Upload image file to Firebase Storage"""
    
    # Validate file type
    if type not in ['avatar', 'logo', 'project', 'portfolio']:
        raise HTTPException(status_code=400, detail="Invalid upload type")
    
    try:
        # Use entity_id if provided, otherwise use current user id
        user_id = entity_id or current_user.get('id')
        file_info = await FileService.save_file(file, type, user_id)
        return ResponseModel(
            data=file_info,
            message="File uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dashboard", response_model=ResponseModel)
async def upload_dashboard(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_admin_or_user)
):
    """Upload dashboard file to Firebase Storage"""
    
    try:
        file_info = await FileService.save_file(file, 'dashboard', current_user.get('id'))
        return ResponseModel(
            data=file_info,
            message="Dashboard file uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{filename}", response_model=ResponseModel)
async def delete_file(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_admin_or_user)
):
    """Delete file from Firebase Storage"""
    
    # In a real implementation, you'd want to verify the user owns this file
    # For now, we'll allow any authenticated user to delete
    
    success = FileService.delete_file(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found or could not be deleted")
    
    return ResponseModel(message="File deleted successfully")