from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(String(50), primary_key=True, index=True)
    company = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    mobile = Column(String(50))
    address = Column(String(500))
    avatar_url = Column(String(500))
    group_id = Column(String(50), ForeignKey("groups.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    group = relationship("Group", back_populates="clients")
    users = relationship("User", back_populates="client")
    projects = relationship("Project", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")