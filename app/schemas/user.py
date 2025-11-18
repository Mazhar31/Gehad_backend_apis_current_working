from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole, DashboardAccess


class UserBase(BaseModel):
    name: str
    email: EmailStr
    position: str
    client_id: str
    role: UserRole = UserRole.NORMAL
    dashboard_access: DashboardAccess = DashboardAccess.VIEW_ONLY


class UserCreate(UserBase):
    password: str
    project_ids: Optional[List[str]] = []


class UserUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    role: Optional[UserRole] = None
    dashboard_access: Optional[DashboardAccess] = None
    avatar_url: Optional[str] = None
    project_ids: Optional[List[str]] = None
    password: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    avatar_url: Optional[str] = None
    two_factor_enabled: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    project_ids: List[str] = []

    class Config:
        from_attributes = True