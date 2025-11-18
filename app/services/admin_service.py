from sqlalchemy.orm import Session
from app.models import Admin
from app.schemas.admin import AdminCreate, AdminUpdate
from app.core.security import get_password_hash, generate_2fa_secret, generate_2fa_qr_code
from app.schemas.auth import TwoFactorSetup
from typing import Optional, List
import uuid


class AdminService:
    @staticmethod
    def create_admin(db: Session, admin_data: AdminCreate) -> Admin:
        admin_id = f"admin-{uuid.uuid4().hex[:8]}"
        hashed_password = get_password_hash(admin_data.password)
        
        db_admin = Admin(
            id=admin_id,
            name=admin_data.name,
            email=admin_data.email,
            password_hash=hashed_password,
            position=admin_data.position
        )
        
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        return db_admin

    @staticmethod
    def get_admin(db: Session, admin_id: str) -> Optional[Admin]:
        return db.query(Admin).filter(Admin.id == admin_id).first()

    @staticmethod
    def get_admin_by_email(db: Session, email: str) -> Optional[Admin]:
        return db.query(Admin).filter(Admin.email == email).first()

    @staticmethod
    def get_admins(db: Session, skip: int = 0, limit: int = 100) -> List[Admin]:
        return db.query(Admin).offset(skip).limit(limit).all()

    @staticmethod
    def update_admin(db: Session, admin_id: str, admin_data: AdminUpdate) -> Optional[Admin]:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return None
        
        update_data = admin_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(admin, field, value)
        
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def setup_2fa(db: Session, admin_id: str) -> Optional[TwoFactorSetup]:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return None
        
        secret = generate_2fa_secret()
        qr_code = generate_2fa_qr_code(admin.email, secret)
        
        admin.two_factor_secret = secret
        db.commit()
        
        return TwoFactorSetup(secret=secret, qr_code=qr_code)

    @staticmethod
    def enable_2fa(db: Session, admin_id: str) -> bool:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin or not admin.two_factor_secret:
            return False
        
        admin.two_factor_enabled = True
        db.commit()
        return True

    @staticmethod
    def disable_2fa(db: Session, admin_id: str) -> bool:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return False
        
        admin.two_factor_enabled = False
        admin.two_factor_secret = None
        db.commit()
        return True