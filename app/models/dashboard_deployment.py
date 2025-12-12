from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class DeploymentType(str, enum.Enum):
    PROJECT = "project"
    SUBDOMAIN = "subdomain"


class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class DashboardDeployment(Base):
    __tablename__ = "dashboard_deployments"

    id = Column(String(50), primary_key=True, index=True)
    project_id = Column(String(50), ForeignKey("projects.id"))
    subdomain = Column(String(255))
    file_id = Column(String(50), ForeignKey("uploaded_files.id"), nullable=False)
    deployment_type = Column(Enum(DeploymentType), nullable=False)
    deployment_url = Column(String(500))
    deployed_by = Column(String(50), ForeignKey("admins.id"), nullable=False)
    deployment_status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())
    dashboard_instance_id = Column(String(100))

    # Relationships
    project = relationship("Project", back_populates="dashboard_deployments")