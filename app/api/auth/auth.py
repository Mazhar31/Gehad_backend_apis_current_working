from fastapi import APIRouter, Depends, HTTPException, status
from app.core.firebase_db import firebase_db
from app.schemas.admin import AdminLogin
from app.schemas.user import UserLogin
from app.schemas.common import ResponseModel
from app.utils.dependencies import get_current_admin, get_current_user, get_current_admin_or_user
from app.core.security import verify_password, create_access_token, get_password_hash
from typing import Dict, Any
from datetime import timedelta
from app.core.config import settings
from app.services.email_service import send_password_reset_email
from fastapi import Query
import secrets
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/admin/login", response_model=ResponseModel)
async def admin_login(
    login_data: AdminLogin
):
    admin = firebase_db.get_admin_by_email(login_data.email)
    if not admin or not verify_password(login_data.password, admin.get('password_hash', '')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=f"{admin['id']}:admin", expires_delta=access_token_expires
    )
    
    return ResponseModel(
        data={"access_token": access_token, "token_type": "bearer"},
        message="Login successful"
    )

@router.post("/user/login", response_model=ResponseModel)
async def user_login(
    login_data: UserLogin
):
    user = firebase_db.get_user_by_email(login_data.email)
    if not user or not verify_password(login_data.password, user.get('password_hash', '')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=f"{user['id']}:user", expires_delta=access_token_expires
    )
    
    return ResponseModel(
        data={"access_token": access_token, "token_type": "bearer"},
        message="Login successful"
    )

@router.get("/me", response_model=ResponseModel)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_admin_or_user)
):
    user_data = {
        "id": current_user.get('id'),
        "name": current_user.get('name'),
        "email": current_user.get('email'),
        "avatar_url": current_user.get('avatar_url'),
        "two_factor_enabled": current_user.get('two_factor_enabled', False),
        "user_type": current_user.get('user_type', 'user')
    }
    
    if current_user.get('user_type') == 'admin':
        user_data["position"] = current_user.get('position')
    else:
        user_data["position"] = current_user.get('position')
        user_data["client_id"] = current_user.get('client_id')
        user_data["role"] = current_user.get('role')
        user_data["dashboard_access"] = current_user.get('dashboard_access')
        user_data["project_ids"] = current_user.get('project_ids', [])
    
    return ResponseModel(
        data=user_data,
        message="User information retrieved successfully"
    )

@router.post("/forgot-password", response_model=ResponseModel)
async def forgot_password(email: str = Query(...)):
    """Send password reset email"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔍 Password reset requested for email: {email}")
    
    # Check if user exists (admin or regular user)
    admin = firebase_db.get_admin_by_email(email)
    user = firebase_db.get_user_by_email(email) if not admin else None
    
    if not admin and not user:
        logger.info(f"❌ Email {email} not found in database")
        # Don't reveal if email exists or not for security
        return ResponseModel(
            message="If the email exists, a password reset link has been sent"
        )
    
    logger.info(f"✅ Email {email} found, user type: {'admin' if admin else 'user'}")
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    logger.info(f"🔑 Generated reset token: {reset_token[:10]}...")
    
    # Store reset token in Firebase
    reset_data = {
        "email": email,
        "reset_token": reset_token,
        "user_type": "admin" if admin else "user",
        "user_id": admin['id'] if admin else user['id'],
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }
    
    reset_id = f"reset-{uuid.uuid4().hex[:8]}"
    firebase_db.create('password_resets', reset_data, reset_id)
    logger.info(f"💾 Reset token stored in Firebase with ID: {reset_id}")
    
    # Send email
    reset_url = f"https://oneqlek.com/reset-password?token={reset_token}"
    logger.info(f"📧 Attempting to send email to {email} with reset URL: {reset_url}")
    
    try:
        email_sent = await send_password_reset_email(email, reset_url)
        if email_sent:
            logger.info(f"✅ Password reset email sent successfully to {email}")
        else:
            logger.error(f"❌ Failed to send password reset email to {email}")
            # Still return success message for security
    except Exception as e:
        logger.error(f"💥 Exception while sending email to {email}: {str(e)}")
        # Still return success message for security
    
    return ResponseModel(
        message="If the email exists, a password reset link has been sent"
    )

@router.post("/test-email", response_model=ResponseModel)
async def test_email(email: str = Query(...)):
    """Test email configuration - REMOVE IN PRODUCTION"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🧪 Testing email configuration by sending to: {email}")
    
    try:
        from app.services.email_service import email_service
        
        # Test email service configuration
        logger.info(f"🔧 SMTP Config - Host: {email_service.smtp_host}, Port: {email_service.smtp_port}, User: {email_service.smtp_user}")
        
        # Try to send a test email
        test_url = "https://oneqlek.com/reset-password?token=test123"
        result = await send_password_reset_email(email, test_url)
        
        if result:
            logger.info(f"✅ Test email sent successfully to {email}")
            return ResponseModel(
                message=f"Test email sent successfully to {email}"
            )
        else:
            logger.error(f"❌ Test email failed to send to {email}")
            return ResponseModel(
                message=f"Test email failed to send to {email}"
            )
            
    except Exception as e:
        logger.error(f"💥 Test email exception: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email test failed: {str(e)}"
        )
@router.post("/reset-password", response_model=ResponseModel)
async def reset_password(token: str = Query(...), new_password: str = Query(...)):
    """Reset password using token"""
    from datetime import datetime
    
    # Find reset token
    resets = firebase_db.get_all('password_resets', [('reset_token', '==', token)])
    if not resets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    reset_record = resets[0]
    
    # Check if token is expired
    if datetime.fromisoformat(reset_record['expires_at']) < datetime.utcnow():
        firebase_db.delete('password_resets', reset_record['id'])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update password
    password_hash = get_password_hash(new_password)
    
    if reset_record['user_type'] == 'admin':
        firebase_db.update('admins', reset_record['user_id'], {'password_hash': password_hash})
    else:
        firebase_db.update('users', reset_record['user_id'], {'password_hash': password_hash})
    
    # Delete reset token
    firebase_db.delete('password_resets', reset_record['id'])
    
    return ResponseModel(
        message="Password reset successfully"
    )