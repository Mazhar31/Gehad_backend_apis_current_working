from sqlalchemy.orm import Session
from app.models import User, UserProject
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, generate_2fa_secret, generate_2fa_qr_code
from app.schemas.auth import TwoFactorSetup
from typing import Optional, List
import uuid


class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        user_id = f"u-{uuid.uuid4().hex[:8]}"
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            id=user_id,
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            position=user_data.position,
            client_id=user_data.client_id,
            role=user_data.role,
            dashboard_access=user_data.dashboard_access,
            avatar_url=f"https://i.pravatar.cc/150?u={user_id}"
        )
        
        db.add(db_user)
        db.commit()
        
        # Add project assignments
        if user_data.project_ids:
            for project_id in user_data.project_ids:
                user_project = UserProject(user_id=user_id, project_id=project_id)
                db.add(user_project)
        
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, client_id: str = None) -> List[User]:
        query = db.query(User)
        if client_id:
            query = query.filter(User.client_id == client_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        
        # Handle password update
        if "password" in update_data and update_data["password"]:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        # Handle project assignments
        if "project_ids" in update_data:
            project_ids = update_data.pop("project_ids")
            # Remove existing assignments
            db.query(UserProject).filter(UserProject.user_id == user_id).delete()
            # Add new assignments
            for project_id in project_ids:
                user_project = UserProject(user_id=user_id, project_id=project_id)
                db.add(user_project)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Delete user-project relationships first
        db.query(UserProject).filter(UserProject.user_id == user_id).delete()
        
        # Now delete the user
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def get_user_project_ids(db: Session, user_id: str) -> List[str]:
        user_projects = db.query(UserProject).filter(UserProject.user_id == user_id).all()
        return [up.project_id for up in user_projects]

    @staticmethod
    def setup_2fa(db: Session, user_id: str) -> Optional[TwoFactorSetup]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        secret = generate_2fa_secret()
        qr_code = generate_2fa_qr_code(user.email, secret)
        
        user.two_factor_secret = secret
        db.commit()
        
        return TwoFactorSetup(secret=secret, qr_code=qr_code)

    @staticmethod
    def enable_2fa(db: Session, user_id: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.two_factor_secret:
            return False
        
        user.two_factor_enabled = True
        db.commit()
        return True

    @staticmethod
    def disable_2fa(db: Session, user_id: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.two_factor_enabled = False
        user.two_factor_secret = None
        db.commit()
        return True