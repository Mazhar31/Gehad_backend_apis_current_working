from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase_db import firebase_db
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin
from typing import Dict, Any
import uuid

router = APIRouter()

@router.post("/", response_model=ResponseModel)
async def create_payment_plan(
    plan_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new payment plan"""
    plan_id = f"plan-{uuid.uuid4().hex[:8]}"
    
    plan_doc = {
        'name': plan_data.get('name'),
        'price': plan_data.get('price'),
        'currency': plan_data.get('currency', 'USD'),
        'features': plan_data.get('features', []),
        'is_popular': plan_data.get('is_popular', False)
    }
    
    plan = firebase_db.create('payment_plans', plan_doc, plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="Failed to create payment plan")
    
    return ResponseModel(
        data=plan,
        message="Payment plan created successfully"
    )

@router.get("/", response_model=ResponseModel)
async def get_payment_plans(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all payment plans"""
    plans = firebase_db.get_all('payment_plans')
    return ResponseModel(
        data=plans,
        message="Payment plans retrieved successfully"
    )

@router.put("/{plan_id}", response_model=ResponseModel)
async def update_payment_plan(
    plan_id: str,
    plan_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Update payment plan"""
    update_data = {}
    
    if 'name' in plan_data:
        update_data['name'] = plan_data['name']
    if 'price' in plan_data:
        update_data['price'] = plan_data['price']
    if 'currency' in plan_data:
        update_data['currency'] = plan_data['currency']
    if 'features' in plan_data:
        update_data['features'] = plan_data['features']
    if 'is_popular' in plan_data:
        update_data['is_popular'] = plan_data['is_popular']
    
    plan = firebase_db.update('payment_plans', plan_id, update_data)
    if not plan:
        raise HTTPException(status_code=404, detail="Payment plan not found")
    
    return ResponseModel(
        data=plan,
        message="Payment plan updated successfully"
    )

@router.delete("/{plan_id}", response_model=ResponseModel)
async def delete_payment_plan(
    plan_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete payment plan"""
    success = firebase_db.delete('payment_plans', plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Payment plan not found")
    
    return ResponseModel(message="Payment plan deleted successfully")