import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_pass = settings.SMTP_PASS
        self.admin_email = settings.ADMIN_EMAIL
        self.from_email = settings.FROM_EMAIL

    def send_contact_notification(self, name: str, email: str, message: str):
        """Send contact form notification email to admin"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.admin_email
            msg['Subject'] = f"New Contact Form Submission - OneQlek"

            # Email body
            body = f"""
            <html>
            <body>
                <h2>New Contact Form Submission</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Message:</strong></p>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    {message.replace('\n', '<br>')}
                </div>
                <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            text = msg.as_string()
            server.sendmail(self.from_email, self.admin_email, text)
            server.quit()

            logger.info(f"Contact notification email sent successfully for {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send contact notification email: {str(e)}")
            return False

    def send_password_reset_email(self, email: str, reset_url: str):
        """Send password reset email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = email
            msg['Subject'] = "Password Reset - OneQlek"

            # Email body
            body = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password for your OneQlek account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p>{reset_url}</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                <hr>
                <p><small>OneQlek Team</small></p>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            text = msg.as_string()
            server.sendmail(self.from_email, email, text)
            server.quit()

            logger.info(f"Password reset email sent successfully to {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False

    def send_invoice_email(self, client_email: str, client_name: str, invoice_data: dict):
        """Send invoice email to client"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = client_email
            msg['Subject'] = f"Invoice {invoice_data.get('invoice_number')} - OneQlek"

            # Calculate total
            total = sum(item.get('price', 0) * item.get('quantity', 1) for item in invoice_data.get('items', []))
            currency = invoice_data.get('currency', 'USD')
            
            # Format currency
            currency_symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'AED': 'د.إ'}
            currency_symbol = currency_symbols.get(currency, currency)
            
            # Email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">Invoice from OneQlek</h2>
                    <p>Dear {client_name},</p>
                    <p>Please find your invoice details below:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Invoice Details</h3>
                        <p><strong>Invoice Number:</strong> {invoice_data.get('invoice_number')}</p>
                        <p><strong>Issue Date:</strong> {invoice_data.get('issue_date')}</p>
                        <p><strong>Due Date:</strong> {invoice_data.get('due_date')}</p>
                        <p><strong>Status:</strong> {invoice_data.get('status')}</p>
                        <p><strong>Total Amount:</strong> {currency_symbol}{total:.2f}</p>
                    </div>
                    
                    <p>Please process this invoice by the due date. If you have any questions, please don't hesitate to contact us.</p>
                    
                    <p>Thank you for your business!</p>
                    
                    <hr style="margin: 30px 0;">
                    <p><small>OneQlek Team<br>
                    Email: {self.from_email}</small></p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            text = msg.as_string()
            server.sendmail(self.from_email, client_email, text)
            server.quit()

            logger.info(f"Invoice email sent successfully to {client_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send invoice email: {str(e)}")
            return False

# Create global instance
email_service = EmailService()

# Helper function for easy import
async def send_password_reset_email(email: str, reset_url: str):
    return email_service.send_password_reset_email(email, reset_url)

async def send_invoice_email(client_email: str, client_name: str, invoice_data: dict):
    return email_service.send_invoice_email(client_email, client_name, invoice_data)