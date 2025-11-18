from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin
from typing import List
import csv
import io

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_user(
    user_data: UserCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new user"""
    # Check if email already exists
    existing_user = UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = UserService.create_user(db, user_data)
    
    # Get project IDs for response
    project_ids = UserService.get_user_project_ids(db, user.id)
    user_response = UserResponse.from_orm(user)
    user_response.project_ids = project_ids
    
    return ResponseModel(
        data=user_response.dict(),
        message="User created successfully"
    )


@router.get("/", response_model=ResponseModel)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: str = Query(None),
    search: str = Query(None),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of users with filtering"""
    users = UserService.get_users(db, skip=skip, limit=limit, client_id=client_id)
    
    # Filter by search term if provided
    if search:
        users = [u for u in users if search.lower() in u.name.lower() or search.lower() in u.email.lower()]
    
    # Get project IDs for each user
    user_responses = []
    for user in users:
        project_ids = UserService.get_user_project_ids(db, user.id)
        user_response = UserResponse.from_orm(user)
        user_response.project_ids = project_ids
        user_responses.append(user_response.dict())
    
    return ResponseModel(
        data=user_responses,
        message="Users retrieved successfully"
    )


@router.get("/{user_id}", response_model=ResponseModel)
async def get_user(
    user_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    project_ids = UserService.get_user_project_ids(db, user.id)
    user_response = UserResponse.from_orm(user)
    user_response.project_ids = project_ids
    
    return ResponseModel(
        data=user_response.dict(),
        message="User retrieved successfully"
    )


@router.put("/{user_id}", response_model=ResponseModel)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update user"""
    user = UserService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    project_ids = UserService.get_user_project_ids(db, user.id)
    user_response = UserResponse.from_orm(user)
    user_response.project_ids = project_ids
    
    return ResponseModel(
        data=user_response.dict(),
        message="User updated successfully"
    )


@router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete user"""
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return ResponseModel(message="User deleted successfully")


@router.get("/export/emails")
async def export_user_emails(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Export user emails as CSV"""
    users = UserService.get_users(db, skip=0, limit=1000)
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['email'])  # Header
    
    for user in users:
        writer.writerow([user.email])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=user_emails.csv"}
    )