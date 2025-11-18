from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from app.models.project import ProjectStatus, ProjectType


class ProjectBase(BaseModel):
    name: str
    client_id: str
    plan_id: str
    department_id: str
    status: ProjectStatus = ProjectStatus.IN_PROGRESS
    budget: Optional[Decimal] = None
    progress: int = 0
    start_date: date
    dashboard_url: Optional[str] = None
    currency: str = "USD"
    project_type: ProjectType = ProjectType.DASHBOARD


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[ProjectStatus] = None
    budget: Optional[Decimal] = None
    progress: Optional[int] = None
    dashboard_url: Optional[str] = None
    image_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True