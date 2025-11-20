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

@router.get("/invoices", response_model=ResponseModel)
async def get_user_invoices(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user's invoices for their assigned projects only"""
    user_client_id = current_user.get('client_id')
    user_project_ids = current_user.get('project_ids', [])
    
    if not user_client_id or not user_project_ids:
        return ResponseModel(data=[], message="No client or projects associated with user")
    
    # Get invoices for this client that are also for the user's assigned projects
    all_invoices = firebase_db.get_all('invoices', [('client_id', '==', user_client_id)])
    
    # Filter invoices to only include those for user's assigned projects
    user_invoices = []
    for invoice in all_invoices:
        invoice_project_id = invoice.get('project_id')
        if invoice_project_id and invoice_project_id in user_project_ids:
            user_invoices.append(invoice)
    
    # Get client data
    client = firebase_db.get_by_id('clients', user_client_id)
    client_data = None
    if client:
        client_data = {
            'id': client.get('id'),
            'company': client.get('company'),
            'email': client.get('email')
        }
    
    # Add client data to each invoice
    invoices_with_client = []
    for invoice in user_invoices:
        invoice_with_client = {
            **invoice,
            'client': client_data
        }
        invoices_with_client.append(invoice_with_client)
    
    return ResponseModel(
        data=invoices_with_client,
        message="User invoices retrieved successfully"
    )