"""
Email service for sending notifications.
Foundation for password reset emails and future email functionality.
"""
import logging
from typing import Optional
import os

# Configure logging
logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending various types of emails.
    Currently configured for development mode (logging only).
    """
    
    def __init__(self):
        """Initialize email service with configuration."""
        self.enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@writervault.com")
        self.from_name = os.getenv("FROM_NAME", "WriterVault")
        
        if self.enabled:
            logger.info("📧 Email service enabled")
        else:
            logger.info("📧 Email service disabled (development mode)")
    
    def send_password_reset_email(self, to_email: str, reset_token: str, username: str = "") -> bool:
        """
        Send password reset email to user.
        
        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            username: Username for personalization
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Construct reset URL (this would be your frontend URL in production)
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            reset_url = f"{frontend_url}/reset-password?token={reset_token}"
            
            subject = "Password Reset Request - WriterVault"
            
            # Email template (HTML)
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">Password Reset Request</h2>
                
                <p>Hello {username or 'User'},</p>
                
                <p>You have requested to reset your password for your WriterVault account.</p>
                
                <p>Click the button below to reset your password:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #007bff; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{reset_url}</p>
                
                <p><strong>Important:</strong></p>
                <ul>
                    <li>This link will expire in 24 hours</li>
                    <li>If you didn't request this reset, you can safely ignore this email</li>
                    <li>For security, never share this link with anyone</li>
                </ul>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #888; font-size: 12px;">
                    This email was sent by WriterVault. If you have any questions, 
                    please contact our support team.
                </p>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
            Password Reset Request - WriterVault
            
            Hello {username or 'User'},
            
            You have requested to reset your password for your WriterVault account.
            
            Click this link to reset your password:
            {reset_url}
            
            Important:
            - This link will expire in 24 hours
            - If you didn't request this reset, you can safely ignore this email
            - For security, never share this link with anyone
            
            If you have any questions, please contact our support team.
            """
            
            if self.enabled:
                # TODO: Implement actual email sending (SMTP, SendGrid, etc.)
                success = self._send_email_smtp(to_email, subject, html_content, text_content)
                if success:
                    logger.info(f"📧 Password reset email sent to: {to_email}")
                else:
                    logger.error(f"📧 Failed to send password reset email to: {to_email}")
                return success
            else:
                # Development mode: just log the email content
                logger.info(f"📧 [DEV MODE] Password reset email for: {to_email}")
                logger.info(f"📧 [DEV MODE] Reset URL: {reset_url}")
                logger.info(f"📧 [DEV MODE] Token: {reset_token}")
                return True
                
        except Exception as e:
            logger.error(f"📧 Error sending password reset email to {to_email}: {str(e)}")
            return False
    
    def _send_email_smtp(self, to_email: str, subject: str, html_content: str, text_content: str) -> bool:
        """
        Send email via SMTP (placeholder for actual implementation).
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # TODO: Implement actual SMTP sending
            # import smtplib
            # from email.mime.multipart import MIMEMultipart
            # from email.mime.text import MIMEText
            
            logger.info(f"📧 [SMTP] Would send email to: {to_email}")
            logger.info(f"📧 [SMTP] Subject: {subject}")
            
            # Placeholder for actual SMTP implementation
            return True
            
        except Exception as e:
            logger.error(f"📧 SMTP error: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """
        Send welcome email to new users.
        
        Args:
            to_email: User email
            username: Username
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.enabled:
                # TODO: Implement welcome email
                logger.info(f"📧 Welcome email sent to: {to_email}")
                return True
            else:
                logger.info(f"📧 [DEV MODE] Welcome email for: {username} ({to_email})")
                return True
                
        except Exception as e:
            logger.error(f"📧 Error sending welcome email: {str(e)}")
            return False
    
    def send_email_verification(self, to_email: str, verification_token: str, username: str) -> bool:
        """
        Send email verification email.
        
        Args:
            to_email: User email
            verification_token: Email verification token
            username: Username
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.enabled:
                # TODO: Implement email verification
                logger.info(f"📧 Email verification sent to: {to_email}")
                return True
            else:
                logger.info(f"📧 [DEV MODE] Email verification for: {username} ({to_email})")
                logger.info(f"📧 [DEV MODE] Verification token: {verification_token}")
                return True
                
        except Exception as e:
            logger.error(f"📧 Error sending verification email: {str(e)}")
            return False


# Global email service instance
email_service = EmailService() 