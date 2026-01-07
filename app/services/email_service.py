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
        
        # Log SMTP configuration on initialization
        logger.info(f"📧 Email Service initialized with SMTP: {self.smtp_host}:{self.smtp_port}, User: {self.smtp_user}")
        logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")

    def send_contact_auto_reply(self, name: str, email: str):
        """Send auto-reply email to user who submitted contact form"""
        logger.info(f"📤 Attempting to send auto-reply email to {email}")
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = email
            msg['Subject'] = "Thank you for contacting OneQlek - We'll be in touch soon!"

            # Email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <p>Hi {name},</p>
                    
                    <p>Thanks for reaching out to OneQlek!</p>
                    
                    <p>We've received your inquiry about our application's features and pricing. Our team is reviewing your message and will get back to you shortly with the details you need.</p>
                    
                    <p>If you have any specific requirements or use cases, feel free to reply to this email and share them with us — it helps us tailor the best option for you.</p>
                    
                    <p>Best regards,<br>
                    Gehad Fouad<br>
                    OneQlek Team<br>
                    help@oneqlek.com</p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))
            logger.info(f"📝 Auto-reply email message created successfully")

            # Send email using SSL for port 465
            if self.smtp_port == 465:
                logger.info(f"🔐 Using SSL connection for port 465")
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                logger.info(f"🔒 Using STARTTLS connection for port {self.smtp_port}")
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            
            logger.info(f"🔑 Attempting SMTP login with user: {self.smtp_user}")
            server.login(self.smtp_user, self.smtp_pass)
            logger.info(f"✅ SMTP login successful")
            
            text = msg.as_string()
            server.sendmail(self.from_email, email, text)
            server.quit()
            logger.info(f"✅ Auto-reply email sent successfully from {self.from_email} to {email}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to send auto-reply email: {str(e)}")
            logger.error(f"🔧 SMTP Config - Host: {self.smtp_host}, Port: {self.smtp_port}, User: {self.smtp_user}")
            return False

    def send_contact_notification(self, name: str, email: str, message: str):
        """Send contact form notification email to admin"""
        logger.info(f"📤 Attempting to send contact notification email from {email} to {self.admin_email}")
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
            logger.info(f"📝 Email message created successfully")

            # Send email using SSL for port 465 or STARTTLS for port 587
            if self.smtp_port == 465:
                logger.info(f"🔐 Using SSL connection for port 465")
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
            else:
                logger.info(f"🔒 Using STARTTLS connection for port {self.smtp_port}")
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                server.starttls()
            
            logger.info(f"🔑 Attempting SMTP login with user: {self.smtp_user}")
            server.login(self.smtp_user, self.smtp_pass)
            logger.info(f"✅ SMTP login successful")
            
            text = msg.as_string()
            server.sendmail(self.from_email, self.admin_email, text)
            server.quit()
            logger.info(f"✅ Contact notification email sent successfully from {self.from_email} to {self.admin_email}")

            # Send auto-reply to the user
            logger.info(f"🔄 Now sending auto-reply to user: {email}")
            auto_reply_success = self.send_contact_auto_reply(name, email)
            if auto_reply_success:
                logger.info(f"✅ Auto-reply sent successfully to {email}")
            else:
                logger.warning(f"⚠️ Auto-reply failed for {email}, but notification was sent to admin")

            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"🚫 SMTP Authentication failed: {str(e)}")
            logger.error(f"🔧 This might be due to IP restrictions from Hostinger")
            logger.error(f"🔧 SMTP Config - Host: {self.smtp_host}, Port: {self.smtp_port}, User: {self.smtp_user}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send contact notification email: {str(e)}")
            logger.error(f"🔧 SMTP Config - Host: {self.smtp_host}, Port: {self.smtp_port}, User: {self.smtp_user}")
            return False

    def send_password_reset_email(self, email: str, reset_url: str):
        """Send password reset email"""
        logger.info(f"📤 Attempting to send password reset email to {email}")
        logger.info(f"🔗 Reset URL: {reset_url}")
        logger.info(f"🔧 SMTP Config - Host: {self.smtp_host}, Port: {self.smtp_port}, User: {self.smtp_user}")
        
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
            logger.info(f"📝 Password reset email message created successfully")

            # Send email using SSL for port 465
            if self.smtp_port == 465:
                logger.info(f"🔐 Using SSL connection for port 465")
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
            else:
                logger.info(f"🔒 Using STARTTLS connection for port {self.smtp_port}")
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                server.starttls()
            
            logger.info(f"🔑 Attempting SMTP login with user: {self.smtp_user}")
            server.login(self.smtp_user, self.smtp_pass)
            logger.info(f"✅ SMTP login successful")
            
            text = msg.as_string()
            server.sendmail(self.from_email, email, text)
            server.quit()
            logger.info(f"✅ Password reset email sent successfully from {self.from_email} to {email}")

            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"🚫 SMTP Authentication failed: {str(e)}")
            logger.error(f"🔧 Check credentials - User: {self.smtp_user}, Host: {self.smtp_host}")
            logger.error(f"📝 This might be due to wrong password or 2FA enabled on email account")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"🚫 SMTP Connection failed: {str(e)}")
            logger.error(f"🔧 Check host and port - Host: {self.smtp_host}, Port: {self.smtp_port}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"🚫 SMTP Recipients refused: {str(e)}")
            logger.error(f"📝 Check recipient email address: {email}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to send password reset email: {str(e)}")
            logger.error(f"🔧 SMTP Config - Host: {self.smtp_host}, Port: {self.smtp_port}, User: {self.smtp_user}")
            return False

    def send_invoice_email(self, client_email: str, client_name: str, invoice_data: dict):
        """Send invoice email to client"""
        logger.info(f"📤 Attempting to send invoice email to {client_email} for invoice {invoice_data.get('invoice_number')}")
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
            logger.info(f"📝 Invoice email message created successfully")

            # Send email using SSL for port 465
            if self.smtp_port == 465:
                logger.info(f"🔐 Using SSL connection for port 465")
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                logger.info(f"🔒 Using STARTTLS connection for port {self.smtp_port}")
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            
            logger.info(f"🔑 Attempting SMTP login with user: {self.smtp_user}")
            server.login(self.smtp_user, self.smtp_pass)
            logger.info(f"✅ SMTP login successful")
            
            text = msg.as_string()
            server.sendmail(self.from_email, client_email, text)
            server.quit()
            logger.info(f"✅ Invoice email sent successfully from {self.from_email} to {client_email}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to send invoice email: {str(e)}")
            logger.error(f"🔧 SMTP Config - Host: {self.smtp_host}, Port: {self.smtp_port}, User: {self.smtp_user}")
            return False

# Create global instance
email_service = EmailService()

# Helper function for easy import
async def send_password_reset_email(email: str, reset_url: str):
    return email_service.send_password_reset_email(email, reset_url)

async def send_invoice_email(client_email: str, client_name: str, invoice_data: dict):
    return email_service.send_invoice_email(client_email, client_name, invoice_data)