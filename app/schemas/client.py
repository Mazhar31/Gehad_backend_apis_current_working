from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ClientBase(BaseModel):
    company: str
    email: EmailStr
    mobile: Optional[str] = None
    address: Optional[str] = None
    group_id: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    company: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    group_id: Optional[str] = None
    avatar_url: Optional[str] = None


class ClientResponse(ClientBase):
    id: str
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True