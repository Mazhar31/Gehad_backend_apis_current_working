from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.config import settings
from app.core.firebase_db import firebase_db
from typing import Dict, Any

security = HTTPBearer()

def get_current_admin_or_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
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
        
        # Parse user_id:user_type format
        if ":" in subject:
            user_id, user_type = subject.split(":", 1)
        else:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    if user_type == "admin":
        user = firebase_db.get_by_id('admins', user_id)
        if user:
            user['user_type'] = 'admin'
    elif user_type == "user":
        user = firebase_db.get_by_id('users', user_id)
        if user and user.get('is_active', True):
            user['user_type'] = 'user'
        else:
            user = None
    else:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    return user

def get_current_admin(
    current_user: Dict[str, Any] = Depends(get_current_admin_or_user)
) -> Dict[str, Any]:
    if current_user.get('user_type') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_current_user(
    current_user: Dict[str, Any] = Depends(get_current_admin_or_user)
) -> Dict[str, Any]:
    if current_user.get('user_type') != 'user':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required"
        )
    return current_user