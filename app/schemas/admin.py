from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class AdminBase(BaseModel):
    name: str
    email: EmailStr
    position: Optional[str] = "Admin"


class AdminCreate(AdminBase):
    password: str


class AdminUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    avatar_url: Optional[str] = None


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AdminResponse(AdminBase):
    id: str
    avatar_url: Optional[str] = None
    two_factor_enabled: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True