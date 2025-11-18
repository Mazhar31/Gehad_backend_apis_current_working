from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UploadType(str, enum.Enum):
    AVATAR = "avatar"
    LOGO = "logo"
    PROJECT_IMAGE = "project_image"
    PORTFOLIO_IMAGE = "portfolio_image"
    DASHBOARD_ZIP = "dashboard_zip"


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String(50), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_by_admin = Column(String(50), ForeignKey("admins.id"))
    uploaded_by_user = Column(String(50), ForeignKey("users.id"))
    upload_type = Column(Enum(UploadType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())