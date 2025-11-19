from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase_db import firebase_db
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin
from typing import Dict, Any
import uuid

router = APIRouter()

@router.post("/", response_model=ResponseModel)
async def create_portfolio_case(
    case_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new portfolio case"""
    case_id = f"pc-{uuid.uuid4().hex[:8]}"
    
    case_doc = {
        'category': case_data.get('category'),
        'title': case_data.get('title'),
        'description': case_data.get('description'),
        'image_url': case_data.get('imageUrl'),
        'link': case_data.get('link', '#')
    }
    
    case = firebase_db.create('portfolio_cases', case_doc, case_id)
    if not case:
        raise HTTPException(status_code=400, detail="Failed to create portfolio case")
    
    return ResponseModel(
        data=case,
        message="Portfolio case created successfully"
    )

@router.get("/", response_model=ResponseModel)
async def get_portfolio_cases(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all portfolio cases"""
    cases = firebase_db.get_all('portfolio_cases')
    return ResponseModel(
        data=cases,
        message="Portfolio cases retrieved successfully"
    )

@router.get("/public", response_model=ResponseModel)
async def get_public_portfolio_cases():
    """Get public portfolio cases (no auth required)"""
    cases = firebase_db.get_all('portfolio_cases')
    return ResponseModel(
        data=cases,
        message="Public portfolio cases retrieved successfully"
    )

@router.put("/{case_id}", response_model=ResponseModel)
async def update_portfolio_case(
    case_id: str,
    case_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Update portfolio case"""
    update_data = {}
    
    if 'category' in case_data:
        update_data['category'] = case_data['category']
    if 'title' in case_data:
        update_data['title'] = case_data['title']
    if 'description' in case_data:
        update_data['description'] = case_data['description']
    if 'imageUrl' in case_data:
        update_data['image_url'] = case_data['imageUrl']
    if 'link' in case_data:
        update_data['link'] = case_data['link']
    
    case = firebase_db.update('portfolio_cases', case_id, update_data)
    if not case:
        raise HTTPException(status_code=404, detail="Portfolio case not found")
    
    return ResponseModel(
        data=case,
        message="Portfolio case updated successfully"
    )

@router.delete("/{case_id}", response_model=ResponseModel)
async def delete_portfolio_case(
    case_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete portfolio case"""
    success = firebase_db.delete('portfolio_cases', case_id)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio case not found")
    
    return ResponseModel(message="Portfolio case deleted successfully")