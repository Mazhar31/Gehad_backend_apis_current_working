from pydantic import BaseModel, EmailStr
from datetime import datetime


class ContactMessageBase(BaseModel):
    name: str
    email: EmailStr
    message: str


class ContactMessageCreate(ContactMessageBase):
    pass


class ContactMessageResponse(ContactMessageBase):
    id: str
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True