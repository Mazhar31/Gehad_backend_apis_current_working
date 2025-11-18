from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserProject(Base):
    __tablename__ = "user_projects"

    user_id = Column(String(50), ForeignKey("users.id"), primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.id"), primary_key=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="user_projects")
    project = relationship("Project", back_populates="user_projects")