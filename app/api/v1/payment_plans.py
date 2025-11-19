from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase_db import firebase_db
from app.schemas.payment_plan import PaymentPlanCreate, PaymentPlanUpdate, PaymentPlanResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from typing import Dict, Any
import uuid

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_payment_plan(
    plan_data: PaymentPlanCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Create new payment plan"""
    plan_dict = plan_data.dict()
    plan_dict['is_active'] = True
    plan = firebase_db.create('payment_plans', plan_dict, f"plan-{uuid.uuid4().hex[:8]}")
    
    if not plan:
        raise HTTPException(status_code=500, detail="Failed to create payment plan")
    
    return ResponseModel(
        data=plan,
        message="Payment plan created successfully"
    )


@router.get("/", response_model=ResponseModel)
async def get_payment_plans(
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Get list of payment plans"""
    plans = firebase_db.get_all('payment_plans', [('is_active', '==', True)])
    return ResponseModel(
        data=plans,
        message="Payment plans retrieved successfully"
    )


@router.put("/{plan_id}", response_model=ResponseModel)
async def update_payment_plan(
    plan_id: str,
    plan_data: PaymentPlanUpdate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Update payment plan"""
    update_dict = plan_data.dict(exclude_unset=True)
    plan = firebase_db.update('payment_plans', plan_id, update_dict)
    if not plan:
        raise HTTPException(status_code=404, detail="Payment plan not found")
    
    return ResponseModel(
        data=plan,
        message="Payment plan updated successfully"
    )


@router.delete("/{plan_id}", response_model=ResponseModel)
async def delete_payment_plan(
    plan_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Delete payment plan (soft delete)"""
    plan = firebase_db.update('payment_plans', plan_id, {'is_active': False})
    if not plan:
        raise HTTPException(status_code=404, detail="Payment plan not found")
    
    return ResponseModel(message="Payment plan deleted successfully")