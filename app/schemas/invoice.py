from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from app.models.invoice import InvoiceStatus, InvoiceType


class InvoiceItemCreate(BaseModel):
    description: str
    quantity: int = 1
    price: Decimal


class InvoiceItemResponse(InvoiceItemCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    client_id: str
    project_id: Optional[str] = None
    issue_date: date
    due_date: date
    status: InvoiceStatus = InvoiceStatus.PENDING
    currency: str = "USD"


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    items: Optional[List[InvoiceItemCreate]] = None


class InvoiceResponse(InvoiceBase):
    id: str
    invoice_number: str
    type: InvoiceType
    items: List[InvoiceItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True