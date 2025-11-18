from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    SUPERUSER = "superuser"
    NORMAL = "normal"


class DashboardAccess(str, enum.Enum):
    VIEW_ONLY = "view-only"
    VIEW_AND_EDIT = "view-and-edit"


class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    client_id = Column(String(50), ForeignKey("clients.id"), nullable=False)
    avatar_url = Column(String(500))
    role = Column(Enum(UserRole), default=UserRole.NORMAL)
    dashboard_access = Column(Enum(DashboardAccess), default=DashboardAccess.VIEW_ONLY)
    two_factor_secret = Column(String(32))
    two_factor_enabled = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="users")
    user_projects = relationship("UserProject", back_populates="user")