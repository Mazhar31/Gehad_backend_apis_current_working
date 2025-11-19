from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase_db import firebase_db
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin
from app.services.email_service import send_invoice_email
from typing import Dict, Any
import uuid

router = APIRouter()

@router.post("/", response_model=ResponseModel)
async def create_invoice(
    invoice_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new invoice"""
    invoice_id = f"inv-{uuid.uuid4().hex[:8]}"
    
    # Generate invoice number if not provided
    invoice_number = invoice_data.get('invoice_number')
    if not invoice_number:
        invoice_number = f"INV-{uuid.uuid4().hex[:5].upper()}"
    
    invoice_doc = {
        'invoice_number': invoice_number,
        'client_id': invoice_data.get('client_id'),
        'project_id': invoice_data.get('project_id'),
        'issue_date': invoice_data.get('issue_date'),
        'due_date': invoice_data.get('due_date'),
        'status': invoice_data.get('status', 'Pending'),
        'type': invoice_data.get('type', 'manual'),
        'currency': invoice_data.get('currency', 'USD'),
        'items': invoice_data.get('items', [])
    }
    
    invoice = firebase_db.create('invoices', invoice_doc, invoice_id)
    if not invoice:
        raise HTTPException(status_code=400, detail="Failed to create invoice")
    
    return ResponseModel(
        data=invoice,
        message="Invoice created successfully"
    )

@router.get("/", response_model=ResponseModel)
async def get_invoices(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all invoices"""
    invoices = firebase_db.get_all('invoices')
    return ResponseModel(
        data=invoices,
        message="Invoices retrieved successfully"
    )

@router.get("/{invoice_id}", response_model=ResponseModel)
async def get_invoice(
    invoice_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Get invoice by ID"""
    invoice = firebase_db.get_by_id('invoices', invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return ResponseModel(
        data=invoice,
        message="Invoice retrieved successfully"
    )

@router.put("/{invoice_id}", response_model=ResponseModel)
async def update_invoice(
    invoice_id: str,
    invoice_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_admin)
):
    """Update invoice"""
    update_data = {}
    
    if 'client_id' in invoice_data:
        update_data['client_id'] = invoice_data['client_id']
    if 'project_id' in invoice_data:
        update_data['project_id'] = invoice_data['project_id']
    if 'issue_date' in invoice_data:
        update_data['issue_date'] = invoice_data['issue_date']
    if 'due_date' in invoice_data:
        update_data['due_date'] = invoice_data['due_date']
    if 'status' in invoice_data:
        update_data['status'] = invoice_data['status']
    if 'type' in invoice_data:
        update_data['type'] = invoice_data['type']
    if 'currency' in invoice_data:
        update_data['currency'] = invoice_data['currency']
    if 'items' in invoice_data:
        update_data['items'] = invoice_data['items']
    
    invoice = firebase_db.update('invoices', invoice_id, update_data)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return ResponseModel(
        data=invoice,
        message="Invoice updated successfully"
    )

@router.delete("/{invoice_id}", response_model=ResponseModel)
async def delete_invoice(
    invoice_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete invoice"""
    success = firebase_db.delete('invoices', invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return ResponseModel(message="Invoice deleted successfully")

@router.post("/{invoice_id}/send", response_model=ResponseModel)
async def send_invoice(
    invoice_id: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Send invoice to client"""
    invoice = firebase_db.get_by_id('invoices', invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Get client details
    client = firebase_db.get_by_id('clients', invoice.get('client_id'))
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client_email = client.get('email')
    if not client_email:
        raise HTTPException(status_code=400, detail="Client email not found")
    
    # Send invoice email
    email_sent = await send_invoice_email(
        client_email=client_email,
        client_name=client.get('company', 'Valued Client'),
        invoice_data=invoice
    )
    
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send invoice email")
    
    return ResponseModel(
        message=f"Invoice {invoice.get('invoice_number')} sent successfully to {client_email}"
    )

