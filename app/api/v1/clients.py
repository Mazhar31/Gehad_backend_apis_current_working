from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.client_service import ClientService
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin
from typing import List

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_client(
    client_data: ClientCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new client"""
    client = ClientService.create_client(db, client_data)
    return ResponseModel(
        data=ClientResponse.from_orm(client).dict(),
        message="Client created successfully"
    )


@router.get("/", response_model=ResponseModel)
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str = Query(None),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of clients"""
    clients = ClientService.get_clients(db, skip=skip, limit=limit, search=search)
    return ResponseModel(
        data=[ClientResponse.from_orm(client).dict() for client in clients],
        message="Clients retrieved successfully"
    )


@router.get("/{client_id}", response_model=ResponseModel)
async def get_client(
    client_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get client by ID"""
    client = ClientService.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return ResponseModel(
        data=ClientResponse.from_orm(client).dict(),
        message="Client retrieved successfully"
    )


@router.put("/{client_id}", response_model=ResponseModel)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update client"""
    client = ClientService.update_client(db, client_id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return ResponseModel(
        data=ClientResponse.from_orm(client).dict(),
        message="Client updated successfully"
    )


@router.delete("/{client_id}", response_model=ResponseModel)
async def delete_client(
    client_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete client"""
    success = ClientService.delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return ResponseModel(message="Client deleted successfully")