from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Integer, Date, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"


class ProjectType(str, enum.Enum):
    DASHBOARD = "Dashboard"
    ADDINS = "Add-ins"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    client_id = Column(String(50), ForeignKey("clients.id"), nullable=False)
    plan_id = Column(String(50), ForeignKey("payment_plans.id"), nullable=False)
    department_id = Column(String(50), ForeignKey("departments.id"), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.IN_PROGRESS)
    budget = Column(Numeric(12, 2))
    progress = Column(Integer, default=0)
    start_date = Column(Date, nullable=False)
    dashboard_url = Column(String(500))
    currency = Column(String(3), default="USD")
    image_url = Column(String(500))
    project_type = Column(Enum(ProjectType), default=ProjectType.DASHBOARD)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="projects")
    payment_plan = relationship("PaymentPlan", back_populates="projects")
    department = relationship("Department", back_populates="projects")
    user_projects = relationship("UserProject", back_populates="project")
    invoices = relationship("Invoice", back_populates="project")
    dashboard_deployments = relationship("DashboardDeployment", back_populates="project")