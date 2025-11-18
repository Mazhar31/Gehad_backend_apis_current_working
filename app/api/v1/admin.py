from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.services.admin_service import AdminService
from app.services.client_service import ClientService
from app.services.project_service import ProjectService
from app.services.invoice_service import InvoiceService
from app.schemas.admin import AdminCreate, AdminUpdate, AdminResponse
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin
from app.models import Admin, Project, Client, Invoice
from typing import List

router = APIRouter()


@router.get("/dashboard/stats", response_model=ResponseModel)
async def get_dashboard_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for admin"""
    
    # Get counts
    total_projects = db.query(Project).count()
    total_clients = db.query(Client).count()
    pending_invoices = db.query(Invoice).filter(Invoice.status == "Pending").count()
    
    # Calculate total revenue from paid invoices
    from app.models import InvoiceItem
    total_revenue = db.query(func.sum(InvoiceItem.price * InvoiceItem.quantity)).join(Invoice).filter(
        Invoice.status == "Paid"
    ).scalar() or 0
    
    stats = {
        "total_projects": total_projects,
        "total_clients": total_clients,
        "pending_invoices": pending_invoices,
        "total_revenue": float(total_revenue)
    }
    
    return ResponseModel(
        data=stats,
        message="Dashboard statistics retrieved successfully"
    )


@router.get("/dashboard/recent-projects", response_model=ResponseModel)
async def get_recent_projects(
    limit: int = Query(5, ge=1, le=20),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get recent projects for dashboard"""
    
    projects = db.query(Project).order_by(Project.created_at.desc()).limit(limit).all()
    
    return ResponseModel(
        data=[{
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "progress": p.progress,
            "client_id": p.client_id,
            "created_at": p.created_at
        } for p in projects],
        message="Recent projects retrieved successfully"
    )


@router.post("/admins", response_model=ResponseModel)
async def create_admin(
    admin_data: AdminCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new admin (super admin only)"""
    
    # Check if email already exists
    existing_admin = AdminService.get_admin_by_email(db, admin_data.email)
    if existing_admin:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    admin = AdminService.create_admin(db, admin_data)
    return ResponseModel(
        data=AdminResponse.from_orm(admin).dict(),
        message="Admin created successfully"
    )


@router.get("/admins", response_model=ResponseModel)
async def get_admins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get list of admins"""
    
    admins = AdminService.get_admins(db, skip=skip, limit=limit)
    return ResponseModel(
        data=[AdminResponse.from_orm(admin).dict() for admin in admins],
        message="Admins retrieved successfully"
    )


@router.get("/admins/{admin_id}", response_model=ResponseModel)
async def get_admin(
    admin_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get admin by ID"""
    
    admin = AdminService.get_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return ResponseModel(
        data=AdminResponse.from_orm(admin).dict(),
        message="Admin retrieved successfully"
    )


@router.put("/admins/{admin_id}", response_model=ResponseModel)
async def update_admin(
    admin_id: str,
    admin_data: AdminUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update admin"""
    
    admin = AdminService.update_admin(db, admin_id, admin_data)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return ResponseModel(
        data=AdminResponse.from_orm(admin).dict(),
        message="Admin updated successfully"
    )


@router.put("/profile", response_model=ResponseModel)
async def update_admin_profile(
    admin_data: AdminUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update current admin's profile"""
    
    admin = AdminService.update_admin(db, current_admin.id, admin_data)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return ResponseModel(
        data=AdminResponse.from_orm(admin).dict(),
        message="Profile updated successfully"
    )