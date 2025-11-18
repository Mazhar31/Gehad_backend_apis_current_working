from sqlalchemy.orm import Session
from app.models import Admin, User
from app.core.security import verify_password, create_access_token, verify_2fa_token
from app.schemas.auth import Token
from typing import Optional, Union


class AuthService:
    @staticmethod
    def authenticate_admin(db: Session, email: str, password: str) -> Optional[Admin]:
        admin = db.query(Admin).filter(Admin.email == email).first()
        if not admin or not verify_password(password, admin.password_hash):
            return None
        return admin

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email, User.is_active == True).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def verify_2fa(user: Union[Admin, User], token: str) -> bool:
        if not user.two_factor_enabled or not user.two_factor_secret:
            return True  # 2FA not enabled
        return verify_2fa_token(user.two_factor_secret, token)

    @staticmethod
    def create_token(user_id: str, user_type: str) -> Token:
        access_token = create_access_token(subject=f"{user_type}:{user_id}")
        return Token(access_token=access_token, token_type="bearer")