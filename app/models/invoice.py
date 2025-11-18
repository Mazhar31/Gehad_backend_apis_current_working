from sqlalchemy import Column, String, DateTime, ForeignKey, Date, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class InvoiceStatus(str, enum.Enum):
    PAID = "Paid"
    PENDING = "Pending"
    OVERDUE = "Overdue"


class InvoiceType(str, enum.Enum):
    MANUAL = "manual"
    SUBSCRIPTION = "subscription"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(50), primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False)
    client_id = Column(String(50), ForeignKey("clients.id"), nullable=False)
    project_id = Column(String(50), ForeignKey("projects.id"))
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING)
    type = Column(Enum(InvoiceType), default=InvoiceType.MANUAL)
    currency = Column(String(3), default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="invoices")
    project = relationship("Project", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")