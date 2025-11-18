from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.invoice_service import InvoiceService
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin, get_current_user
from app.models import Admin, User
from typing import List

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new manual invoice"""
    invoice = InvoiceService.create_invoice(db, invoice_data)
    return ResponseModel(
        data=InvoiceResponse.from_orm(invoice).dict(),
        message="Invoice created successfully"
    )


@router.get("/", response_model=ResponseModel)
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: str = Query(None),
    status: str = Query(None),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of invoices with filtering"""
    invoices = InvoiceService.get_invoices(
        db, skip=skip, limit=limit, client_id=client_id, status=status
    )
    return ResponseModel(
        data=[InvoiceResponse.from_orm(invoice).dict() for invoice in invoices],
        message="Invoices retrieved successfully"
    )


@router.get("/{invoice_id}", response_model=ResponseModel)
async def get_invoice(
    invoice_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get invoice by ID"""
    invoice = InvoiceService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return ResponseModel(
        data=InvoiceResponse.from_orm(invoice).dict(),
        message="Invoice retrieved successfully"
    )


@router.put("/{invoice_id}", response_model=ResponseModel)
async def update_invoice(
    invoice_id: str,
    invoice_data: InvoiceUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update invoice"""
    invoice = InvoiceService.update_invoice(db, invoice_id, invoice_data)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return ResponseModel(
        data=InvoiceResponse.from_orm(invoice).dict(),
        message="Invoice updated successfully"
    )


@router.delete("/{invoice_id}", response_model=ResponseModel)
async def delete_invoice(
    invoice_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete invoice (manual invoices only)"""
    success = InvoiceService.delete_invoice(db, invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found or cannot be deleted")
    
    return ResponseModel(message="Invoice deleted successfully")


@router.post("/{invoice_id}/send", response_model=ResponseModel)
async def send_invoice(
    invoice_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Send invoice to client (simulation)"""
    invoice = InvoiceService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # In a real implementation, this would send an email
    # For now, we'll just simulate it
    return ResponseModel(
        message=f"Invoice {invoice.invoice_number} sent to client successfully"
    )


# User endpoints for invoice access
@router.get("/user/my-invoices", response_model=ResponseModel)
async def get_user_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's client invoices (superuser only)"""
    if current_user.role != "superuser":
        raise HTTPException(status_code=403, detail="Superuser access required")
    
    invoices = InvoiceService.get_invoices(db, client_id=current_user.client_id)
    return ResponseModel(
        data=[InvoiceResponse.from_orm(invoice).dict() for invoice in invoices],
        message="User invoices retrieved successfully"
    )


@router.put("/user/{invoice_id}/pay", response_model=ResponseModel)
async def pay_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark invoice as paid (superuser only)"""
    if current_user.role != "superuser":
        raise HTTPException(status_code=403, detail="Superuser access required")
    
    # Verify invoice belongs to user's client
    invoice = InvoiceService.get_invoice(db, invoice_id)
    if not invoice or invoice.client_id != current_user.client_id:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    from app.schemas.invoice import InvoiceUpdate
    update_data = InvoiceUpdate(status="Paid")
    invoice = InvoiceService.update_invoice(db, invoice_id, update_data)
    
    return ResponseModel(
        data=InvoiceResponse.from_orm(invoice).dict(),
        message="Invoice marked as paid successfully"
    )