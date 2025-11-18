from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GroupBase(BaseModel):
    name: str


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = None


class GroupResponse(GroupBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True