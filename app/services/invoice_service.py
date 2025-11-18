from sqlalchemy.orm import Session
from app.models import Invoice, InvoiceItem, Project, PaymentPlan
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.models.invoice import InvoiceStatus, InvoiceType
from typing import Optional, List
from datetime import date, timedelta
import uuid


class InvoiceService:
    @staticmethod
    def create_invoice(db: Session, invoice_data: InvoiceCreate) -> Invoice:
        invoice_id = f"inv-{uuid.uuid4().hex[:8]}"
        invoice_number = f"INV-{str(int(uuid.uuid4().hex[:5], 16))}"
        
        db_invoice = Invoice(
            id=invoice_id,
            invoice_number=invoice_number,
            client_id=invoice_data.client_id,
            project_id=invoice_data.project_id,
            issue_date=invoice_data.issue_date,
            due_date=invoice_data.due_date,
            status=invoice_data.status,
            type=InvoiceType.MANUAL,
            currency=invoice_data.currency
        )
        
        db.add(db_invoice)
        db.flush()
        
        # Add invoice items
        for item_data in invoice_data.items:
            item_id = f"item-{uuid.uuid4().hex[:8]}"
            db_item = InvoiceItem(
                id=item_id,
                invoice_id=invoice_id,
                description=item_data.description,
                quantity=item_data.quantity,
                price=item_data.price
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_invoice)
        return db_invoice

    @staticmethod
    def get_invoice(db: Session, invoice_id: str) -> Optional[Invoice]:
        return db.query(Invoice).filter(Invoice.id == invoice_id).first()

    @staticmethod
    def get_invoices(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        client_id: str = None,
        status: str = None
    ) -> List[Invoice]:
        query = db.query(Invoice)
        if client_id:
            query = query.filter(Invoice.client_id == client_id)
        if status:
            query = query.filter(Invoice.status == status)
        return query.order_by(Invoice.issue_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_invoice(db: Session, invoice_id: str, invoice_data: InvoiceUpdate) -> Optional[Invoice]:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            return None
        
        update_data = invoice_data.dict(exclude_unset=True)
        
        # Handle items update
        if "items" in update_data:
            items_data = update_data.pop("items")
            # Remove existing items
            db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()
            # Add new items
            for item_data in items_data:
                item_id = f"item-{uuid.uuid4().hex[:8]}"
                db_item = InvoiceItem(
                    id=item_id,
                    invoice_id=invoice_id,
                    description=item_data["description"],
                    quantity=item_data["quantity"],
                    price=item_data["price"]
                )
                db.add(db_item)
        
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def delete_invoice(db: Session, invoice_id: str) -> bool:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice or invoice.type == InvoiceType.SUBSCRIPTION:
            return False
        
        db.delete(invoice)
        db.commit()
        return True

    @staticmethod
    def generate_subscription_invoices(db: Session):
        """Generate subscription invoices for completed projects"""
        today = date.today()
        
        # Get completed projects
        completed_projects = db.query(Project).filter(
            Project.status == "Completed",
            Project.plan_id.isnot(None)
        ).all()
        
        for project in completed_projects:
            plan = db.query(PaymentPlan).filter(PaymentPlan.id == project.plan_id).first()
            if not plan:
                continue
            
            # Check if invoice already exists for this period
            existing_invoice = db.query(Invoice).filter(
                Invoice.project_id == project.id,
                Invoice.type == InvoiceType.SUBSCRIPTION,
                Invoice.issue_date >= project.start_date
            ).first()
            
            if existing_invoice:
                continue
            
            # Create subscription invoice
            invoice_id = f"inv-{uuid.uuid4().hex[:8]}"
            invoice_number = f"SUB-{project.id.upper()}-{today.year}{today.month:02d}"
            due_date = today + timedelta(days=15)
            
            db_invoice = Invoice(
                id=invoice_id,
                invoice_number=invoice_number,
                client_id=project.client_id,
                project_id=project.id,
                issue_date=today,
                due_date=due_date,
                status=InvoiceStatus.PENDING,
                type=InvoiceType.SUBSCRIPTION,
                currency=plan.currency
            )
            
            db.add(db_invoice)
            db.flush()
            
            # Add invoice item
            item_id = f"item-{uuid.uuid4().hex[:8]}"
            db_item = InvoiceItem(
                id=item_id,
                invoice_id=invoice_id,
                description=f"{plan.name} Plan (Annual)",
                quantity=1,
                price=plan.price
            )
            db.add(db_item)
        
        db.commit()