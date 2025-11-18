from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.contact_message import ContactMessageCreate, ContactMessageResponse
from app.schemas.common import ResponseModel
from app.models import ContactMessage
from app.services.email_service import email_service
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def submit_contact_message(
    message_data: ContactMessageCreate,
    db: Session = Depends(get_db)
):
    """Submit contact form message (public endpoint)"""
    message = ContactMessage(
        id=f"msg-{uuid.uuid4().hex[:8]}",
        name=message_data.name,
        email=message_data.email,
        message=message_data.message
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Send email notification to admin
    try:
        email_service.send_contact_notification(
            name=message_data.name,
            email=message_data.email,
            message=message_data.message
        )
        logger.info(f"Email notification sent for contact message {message.id}")
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")
        # Continue even if email fails - message is still saved
    
    return ResponseModel(
        data=ContactMessageResponse.from_orm(message).dict(),
        message="Contact message submitted successfully"
    )