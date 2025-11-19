from fastapi import APIRouter, HTTPException
from app.core.firebase_db import firebase_db
from app.schemas.common import ResponseModel
from app.core.security import get_password_hash
import uuid

router = APIRouter()

@router.post("/create-admin", response_model=ResponseModel)
async def create_initial_admin():
    """Create initial admin account for first-time setup"""
    try:
        # Check if any admin already exists
        existing_admins = firebase_db.get_all('admins', limit=1)
        if existing_admins:
            raise HTTPException(status_code=400, detail="Admin account already exists")
        
        # Create default admin
        admin_data = {
            "name": "Admin",
            "email": "admin@oneqlek.com",
            "password_hash": get_password_hash("admin123"),
            "position": "System Administrator",
            "avatar_url": "https://i.pravatar.cc/150?u=admin",
            "two_factor_enabled": False,
            "is_active": True
        }
        
        admin_id = f"a-{uuid.uuid4().hex[:8]}"
        admin = firebase_db.create('admins', admin_data, admin_id)
        
        if not admin:
            raise HTTPException(status_code=500, detail="Failed to create admin")
        
        return ResponseModel(
            data={
                "email": "admin@oneqlek.com",
                "password": "admin123",
                "admin_id": admin_id
            },
            message="Admin created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/test-firebase", response_model=ResponseModel)
async def test_firebase():
    """Test Firebase connection"""
    try:
        test_data = {"test": "data", "timestamp": "2024-01-01"}
        result = firebase_db.create('test', test_data)
        return ResponseModel(
            data=result,
            message="Firebase connection successful"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase error: {str(e)}")