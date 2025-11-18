from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.payment_plan import PaymentPlanCreate, PaymentPlanUpdate, PaymentPlanResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin, PaymentPlan
import uuid

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_payment_plan(
    plan_data: PaymentPlanCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new payment plan"""
    plan = PaymentPlan(
        id=f"plan-{uuid.uuid4().hex[:8]}",
        name=plan_data.name,
        price=plan_data.price,
        currency=plan_data.currency,
        features=plan_data.features,
        is_popular=plan_data.is_popular
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    return ResponseModel(
        data=PaymentPlanResponse.from_orm(plan).dict(),
        message="Payment plan created successfully"
    )


@router.get("/", response_model=ResponseModel)
async def get_payment_plans(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of payment plans"""
    plans = db.query(PaymentPlan).filter(PaymentPlan.is_active == True).all()
    return ResponseModel(
        data=[PaymentPlanResponse.from_orm(plan).dict() for plan in plans],
        message="Payment plans retrieved successfully"
    )


@router.put("/{plan_id}", response_model=ResponseModel)
async def update_payment_plan(
    plan_id: str,
    plan_data: PaymentPlanUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update payment plan"""
    plan = db.query(PaymentPlan).filter(PaymentPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Payment plan not found")
    
    update_data = plan_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    db.commit()
    db.refresh(plan)
    
    return ResponseModel(
        data=PaymentPlanResponse.from_orm(plan).dict(),
        message="Payment plan updated successfully"
    )


@router.delete("/{plan_id}", response_model=ResponseModel)
async def delete_payment_plan(
    plan_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete payment plan (soft delete)"""
    plan = db.query(PaymentPlan).filter(PaymentPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Payment plan not found")
    
    plan.is_active = False
    db.commit()
    
    return ResponseModel(message="Payment plan deleted successfully")