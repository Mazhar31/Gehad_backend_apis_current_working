from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase_db import firebase_db
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin
from app.services.firebase_storage_service import firebase_storage_service
from typing import Dict, Any
import uuid

router = APIRouter()

@router.post("/", response_model=ResponseModel)
async def create_client(
    client_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new client"""
    client_id = f"c-{uuid.uuid4().hex[:8]}"
    
    client_doc = {
        'company': client_data.get('company'),
        'email': client_data.get('email'),
        'mobile': client_data.get('mobile'),
        'address': client_data.get('address'),
        'avatar_url': firebase_storage_service.get_default_avatar(client_id),
        'group_id': client_data.get('groupId')
    }
    
    client = firebase_db.create('clients', client_doc, client_id)
    if not client:
        raise HTTPException(status_code=400, detail="Failed to create client")
    
    return ResponseModel(
        data=client,
        message="Client created successfully"
    )

@router.get("/", response_model=ResponseModel)
async def get_clients(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all clients"""
    clients = firebase_db.get_all('clients')
    return ResponseModel(
        data=clients,
        message="Clients retrieved successfully"
    )

@router.get("/{client_id}", response_model=ResponseModel)
async def get_client(
    client_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Get client by ID"""
    client = firebase_db.get_by_id('clients', client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return ResponseModel(
        data=client,
        message="Client retrieved successfully"
    )

@router.put("/{client_id}", response_model=ResponseModel)
async def update_client(
    client_id: str,
    client_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Update client"""
    update_data = {}
    if 'company' in client_data:
        update_data['company'] = client_data['company']
    if 'email' in client_data:
        update_data['email'] = client_data['email']
    if 'mobile' in client_data:
        update_data['mobile'] = client_data['mobile']
    if 'address' in client_data:
        update_data['address'] = client_data['address']
    if 'avatarUrl' in client_data:
        update_data['avatar_url'] = client_data['avatarUrl']
    if 'groupId' in client_data:
        update_data['group_id'] = client_data['groupId']
    
    client = firebase_db.update('clients', client_id, update_data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return ResponseModel(
        data=client,
        message="Client updated successfully"
    )

@router.delete("/{client_id}", response_model=ResponseModel)
async def delete_client(
    client_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete client"""
    success = firebase_db.delete('clients', client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return ResponseModel(message="Client deleted successfully")