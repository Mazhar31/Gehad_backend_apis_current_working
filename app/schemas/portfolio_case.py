from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PortfolioCaseBase(BaseModel):
    category: str
    title: str
    description: str
    link: Optional[str] = None
    is_public: bool = True


class PortfolioCaseCreate(PortfolioCaseBase):
    pass


class PortfolioCaseUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    link: Optional[str] = None
    is_public: Optional[bool] = None


class PortfolioCaseResponse(PortfolioCaseBase):
    id: str
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True