from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.admin_service import AdminService
from app.services.user_service import UserService
from app.schemas.admin import AdminLogin
from app.schemas.user import UserLogin
from app.schemas.auth import Token, TwoFactorVerify, TwoFactorSetup
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin, get_current_user, get_current_admin_or_user
from app.models import Admin, User
from typing import Union

router = APIRouter()


@router.post("/admin/login", response_model=ResponseModel)
async def admin_login(
    login_data: AdminLogin,
    db: Session = Depends(get_db)
):
    admin = AuthService.authenticate_admin(db, login_data.email, login_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # If 2FA is enabled, require token verification
    if admin.two_factor_enabled:
        return ResponseModel(
            data={"requires_2fa": True, "admin_id": admin.id},
            message="2FA verification required"
        )
    
    token = AuthService.create_token(admin.id, "admin")
    return ResponseModel(
        data=token.dict(),
        message="Login successful"
    )


@router.post("/admin/verify-2fa", response_model=ResponseModel)
async def admin_verify_2fa(
    admin_id: str,
    verify_data: TwoFactorVerify,
    db: Session = Depends(get_db)
):
    admin = AdminService.get_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    if not AuthService.verify_2fa(admin, verify_data.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA token"
        )
    
    token = AuthService.create_token(admin.id, "admin")
    return ResponseModel(
        data=token.dict(),
        message="2FA verification successful"
    )


@router.post("/user/login", response_model=ResponseModel)
async def user_login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # If 2FA is enabled, require token verification
    if user.two_factor_enabled:
        return ResponseModel(
            data={"requires_2fa": True, "user_id": user.id},
            message="2FA verification required"
        )
    
    token = AuthService.create_token(user.id, "user")
    return ResponseModel(
        data=token.dict(),
        message="Login successful"
    )


@router.post("/user/verify-2fa", response_model=ResponseModel)
async def user_verify_2fa(
    user_id: str,
    verify_data: TwoFactorVerify,
    db: Session = Depends(get_db)
):
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not AuthService.verify_2fa(user, verify_data.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA token"
        )
    
    token = AuthService.create_token(user.id, "user")
    return ResponseModel(
        data=token.dict(),
        message="2FA verification successful"
    )


@router.post("/admin/setup-2fa", response_model=ResponseModel)
async def admin_setup_2fa(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    setup_data = AdminService.setup_2fa(db, current_admin.id)
    if not setup_data:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return ResponseModel(
        data=setup_data.dict(),
        message="2FA setup initiated. Scan QR code with authenticator app"
    )


@router.post("/admin/enable-2fa", response_model=ResponseModel)
async def admin_enable_2fa(
    verify_data: TwoFactorVerify,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Verify the token before enabling
    if not AuthService.verify_2fa(current_admin, verify_data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA token"
        )
    
    success = AdminService.enable_2fa(db, current_admin.id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to enable 2FA")
    
    return ResponseModel(message="2FA enabled successfully")


@router.post("/admin/disable-2fa", response_model=ResponseModel)
async def admin_disable_2fa(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    success = AdminService.disable_2fa(db, current_admin.id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to disable 2FA")
    
    return ResponseModel(message="2FA disabled successfully")


@router.post("/user/setup-2fa", response_model=ResponseModel)
async def user_setup_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    setup_data = UserService.setup_2fa(db, current_user.id)
    if not setup_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return ResponseModel(
        data=setup_data.dict(),
        message="2FA setup initiated. Scan QR code with authenticator app"
    )


@router.post("/user/enable-2fa", response_model=ResponseModel)
async def user_enable_2fa(
    verify_data: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify the token before enabling
    if not AuthService.verify_2fa(current_user, verify_data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA token"
        )
    
    success = UserService.enable_2fa(db, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to enable 2FA")
    
    return ResponseModel(message="2FA enabled successfully")


@router.post("/user/disable-2fa", response_model=ResponseModel)
async def user_disable_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = UserService.disable_2fa(db, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to disable 2FA")
    
    return ResponseModel(message="2FA disabled successfully")


@router.get("/me", response_model=ResponseModel)
async def get_current_user_info(
    current_user: Union[Admin, User] = Depends(get_current_admin_or_user)
):
    user_data = {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "two_factor_enabled": current_user.two_factor_enabled,
        "user_type": "admin" if isinstance(current_user, Admin) else "user"
    }
    
    if isinstance(current_user, Admin):
        user_data["position"] = current_user.position
    else:
        user_data["position"] = current_user.position
        user_data["client_id"] = current_user.client_id
        user_data["role"] = current_user.role
        user_data["dashboard_access"] = current_user.dashboard_access
    
    return ResponseModel(
        data=user_data,
        message="User information retrieved successfully"
    )