from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PaymentPlanBase(BaseModel):
    name: str
    price: Decimal
    currency: str = "USD"
    features: List[str]
    is_popular: bool = False


class PaymentPlanCreate(PaymentPlanBase):
    pass


class PaymentPlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    features: Optional[List[str]] = None
    is_popular: Optional[bool] = None
    is_active: Optional[bool] = None


class PaymentPlanResponse(PaymentPlanBase):
    id: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True