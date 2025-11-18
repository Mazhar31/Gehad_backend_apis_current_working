from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True