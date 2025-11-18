from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class PortfolioCase(Base):
    __tablename__ = "portfolio_cases"

    id = Column(String(50), primary_key=True, index=True)
    category = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    image_url = Column(String(500))
    link = Column(String(500))
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())