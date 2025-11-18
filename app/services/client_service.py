from sqlalchemy.orm import Session
from app.models import Client
from app.schemas.client import ClientCreate, ClientUpdate
from typing import Optional, List
import uuid


class ClientService:
    @staticmethod
    def create_client(db: Session, client_data: ClientCreate) -> Client:
        client_id = f"c-{uuid.uuid4().hex[:8]}"
        
        db_client = Client(
            id=client_id,
            company=client_data.company,
            email=client_data.email,
            mobile=client_data.mobile,
            address=client_data.address,
            group_id=client_data.group_id,
            avatar_url=f"https://i.pravatar.cc/150?u={client_id}"
        )
        
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client

    @staticmethod
    def get_client(db: Session, client_id: str) -> Optional[Client]:
        return db.query(Client).filter(Client.id == client_id).first()

    @staticmethod
    def get_clients(db: Session, skip: int = 0, limit: int = 100, search: str = None) -> List[Client]:
        query = db.query(Client)
        if search:
            query = query.filter(Client.company.ilike(f"%{search}%"))
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_client(db: Session, client_id: str, client_data: ClientUpdate) -> Optional[Client]:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return None
        
        update_data = client_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def delete_client(db: Session, client_id: str) -> bool:
        from app.models import Project, User, Invoice, UserProject
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return False
        
        # Delete related records in correct order to avoid foreign key constraint violations
        
        # 1. First delete user_projects relationships for users of this client
        user_ids = [u.id for u in db.query(User).filter(User.client_id == client_id).all()]
        for user_id in user_ids:
            db.query(UserProject).filter(UserProject.user_id == user_id).delete()
        
        # 2. Delete user_projects relationships for projects of this client
        project_ids = [p.id for p in db.query(Project).filter(Project.client_id == client_id).all()]
        for project_id in project_ids:
            db.query(UserProject).filter(UserProject.project_id == project_id).delete()
        
        # 3. Delete invoices related to this client
        db.query(Invoice).filter(Invoice.client_id == client_id).delete()
        
        # 4. Delete users related to this client
        db.query(User).filter(User.client_id == client_id).delete()
        
        # 5. Delete projects related to this client
        db.query(Project).filter(Project.client_id == client_id).delete()
        
        # 6. Finally delete the client
        db.delete(client)
        db.commit()
        return True