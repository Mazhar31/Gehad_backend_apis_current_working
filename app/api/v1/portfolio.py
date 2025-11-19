from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase_db import firebase_db
from app.schemas.portfolio_case import PortfolioCaseCreate, PortfolioCaseUpdate, PortfolioCaseResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from typing import Dict, Any
import uuid

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_portfolio_case(
    case_data: PortfolioCaseCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Create new portfolio case"""
    case_dict = case_data.dict()
    case = firebase_db.create('portfolio_cases', case_dict, f"pc-{uuid.uuid4().hex[:8]}")
    
    if not case:
        raise HTTPException(status_code=500, detail="Failed to create portfolio case")
    
    return ResponseModel(
        data=case,
        message="Portfolio case created successfully"
    )


@router.get("/", response_model=ResponseModel)
async def get_portfolio_cases(
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Get list of portfolio cases"""
    cases = firebase_db.get_all('portfolio_cases')
    return ResponseModel(
        data=cases,
        message="Portfolio cases retrieved successfully"
    )


@router.put("/{case_id}", response_model=ResponseModel)
async def update_portfolio_case(
    case_id: str,
    case_data: PortfolioCaseUpdate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Update portfolio case"""
    update_dict = case_data.dict(exclude_unset=True)
    case = firebase_db.update('portfolio_cases', case_id, update_dict)
    if not case:
        raise HTTPException(status_code=404, detail="Portfolio case not found")
    
    return ResponseModel(
        data=case,
        message="Portfolio case updated successfully"
    )


@router.delete("/{case_id}", response_model=ResponseModel)
async def delete_portfolio_case(
    case_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Delete portfolio case"""
    success = firebase_db.delete('portfolio_cases', case_id)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio case not found")
    
    return ResponseModel(message="Portfolio case deleted successfully")


# Public endpoint for portfolio cases
@router.get("/public", response_model=ResponseModel)
async def get_public_portfolio_cases():
    """Get public portfolio cases (no authentication required)"""
    cases = firebase_db.get_all('portfolio_cases', [('is_public', '==', True)])
    return ResponseModel(
        data=cases,
        message="Public portfolio cases retrieved successfully"
    )