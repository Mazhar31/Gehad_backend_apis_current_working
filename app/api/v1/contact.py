from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase_db import firebase_db
from app.schemas.contact_message import ContactMessageCreate, ContactMessageResponse
from app.schemas.common import ResponseModel
from app.services.email_service import email_service
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def submit_contact_message(
    message_data: ContactMessageCreate
):
    """Submit contact form message (public endpoint)"""
    message_dict = message_data.dict()
    message = firebase_db.create('contact_messages', message_dict, f"msg-{uuid.uuid4().hex[:8]}")
    
    if not message:
        raise HTTPException(status_code=500, detail="Failed to save contact message")
    
    # Send email notification to admin
    try:
        email_service.send_contact_notification(
            name=message_data.name,
            email=message_data.email,
            message=message_data.message
        )
        logger.info(f"Email notification sent for contact message {message['id']}")
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")
        # Continue even if email fails - message is still saved
    
    return ResponseModel(
        data=message,
        message="Contact message submitted successfully"
    )