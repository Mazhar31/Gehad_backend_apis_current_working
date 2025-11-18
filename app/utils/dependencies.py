from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.config import settings
from app.core.database import get_db
from app.models import Admin, User
from app.schemas.auth import TokenData
from typing import Union

security = HTTPBearer()


def get_current_admin_or_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Union[Admin, User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject: str = payload.get("sub")
        if subject is None:
            raise credentials_exception
        
        user_type, user_id = subject.split(":", 1)
        token_data = TokenData(email=user_id, user_type=user_type)
    except (JWTError, ValueError):
        raise credentials_exception
    
    if token_data.user_type == "admin":
        user = db.query(Admin).filter(Admin.id == user_id).first()
    elif token_data.user_type == "user":
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    else:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    return user


def get_current_admin(
    current_user: Union[Admin, User] = Depends(get_current_admin_or_user)
) -> Admin:
    if not isinstance(current_user, Admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_current_user(
    current_user: Union[Admin, User] = Depends(get_current_admin_or_user)
) -> User:
    if not isinstance(current_user, User):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required"
        )
    return current_user