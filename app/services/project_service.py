from sqlalchemy.orm import Session
from app.models import Project, PaymentPlan
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import Optional, List
import uuid


class ProjectService:
    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate) -> Project:
        project_id = f"p-{uuid.uuid4().hex[:8]}"
        
        # Get currency from payment plan
        plan = db.query(PaymentPlan).filter(PaymentPlan.id == project_data.plan_id).first()
        currency = plan.currency if plan else "USD"
        
        db_project = Project(
            id=project_id,
            name=project_data.name,
            client_id=project_data.client_id,
            plan_id=project_data.plan_id,
            department_id=project_data.department_id,
            status=project_data.status,
            budget=project_data.budget,
            progress=project_data.progress,
            start_date=project_data.start_date,
            dashboard_url=project_data.dashboard_url,
            currency=currency,
            project_type=project_data.project_type
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def get_project(db: Session, project_id: str) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def get_projects(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        client_id: str = None,
        search: str = None
    ) -> List[Project]:
        query = db.query(Project)
        if client_id:
            query = query.filter(Project.client_id == client_id)
        if search:
            query = query.filter(Project.name.ilike(f"%{search}%"))
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_project(db: Session, project_id: str, project_data: ProjectUpdate) -> Optional[Project]:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project_id: str) -> bool:
        from app.models import UserProject, Invoice
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        # Delete related records first
        # Delete user-project relationships
        db.query(UserProject).filter(UserProject.project_id == project_id).delete()
        
        # Delete invoices related to this project
        db.query(Invoice).filter(Invoice.project_id == project_id).delete()
        
        # Now delete the project
        db.delete(project)
        db.commit()
        return True

    @staticmethod
    def get_user_projects(db: Session, user_id: str) -> List[Project]:
        from app.models import UserProject
        return db.query(Project).join(UserProject).filter(UserProject.user_id == user_id).all()