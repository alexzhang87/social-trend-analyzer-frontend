from typing import Optional
import smtplib
import secrets
import redis
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        
        # Redis for storing verification codes
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=2,  # Use different DB for email verification
                decode_responses=True
            )
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Email verification will use in-memory storage.")
            self.redis_client = None
            self._memory_store = {}
    
    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    def generate_reset_token(self) -> str:
        """Generate a secure reset token"""
        return secrets.token_urlsafe(32)
    
    def store_verification_code(self, email: str, code: str, expiry_minutes: int = 10) -> bool:
        """Store verification code with expiry"""
        try:
            key = f"email_verification:{email}"
            data = {
                "code": code,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(minutes=expiry_minutes)).isoformat()
            }
            
            if self.redis_client:
                self.redis_client.set(key, str(data), expire=expiry_minutes * 60)
            else:
                self._memory_store[key] = data
            
            return True
        except Exception as e:
            logger.error(f"Failed to store verification code: {e}")
            return False
    
    def store_reset_token(self, email: str, token: str, expiry_minutes: int = 30) -> bool:
        """Store password reset token with expiry"""
        try:
            key = f"password_reset:{email}"
            data = {
                "token": token,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(minutes=expiry_minutes)).isoformat()
            }
            
            if self.redis_client:
                self.redis_client.set(key, str(data), ex=expiry_minutes * 60)
            else:
                self._memory_store[key] = data
            
            return True
        except Exception as e:
            logger.error(f"Failed to store reset token: {e}")
            return False
    
    def verify_code(self, email: str, code: str) -> bool:
        """Verify email verification code"""
        try:
            key = f"email_verification:{email}"
            
            if self.redis_client:
                stored_data = self.redis_client.get(key)
                if not stored_data:
                    return False
                stored_data = eval(stored_data)  # Simple parsing, consider using json
            else:
                stored_data = self._memory_store.get(key)
                if not stored_data:
                    return False
            
            # Check expiry
            expires_at = datetime.fromisoformat(stored_data["expires_at"])
            if datetime.utcnow() > expires_at:
                self._cleanup_expired_code(key)
                return False
            
            # Verify code
            if stored_data["code"] == code:
                self._cleanup_expired_code(key)  # Remove used code
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to verify code: {e}")
            return False
    
    def verify_reset_token(self, email: str, token: str) -> bool:
        """Verify password reset token"""
        try:
            key = f"password_reset:{email}"
            
            if self.redis_client:
                stored_data = self.redis_client.get(key)
                if not stored_data:
                    return False
                stored_data = eval(stored_data)
            else:
                stored_data = self._memory_store.get(key)
                if not stored_data:
                    return False
            
            # Check expiry
            expires_at = datetime.fromisoformat(stored_data["expires_at"])
            if datetime.utcnow() > expires_at:
                self._cleanup_expired_code(key)
                return False
            
            # Verify token
            return stored_data["token"] == token
        except Exception as e:
            logger.error(f"Failed to verify reset token: {e}")
            return False
    
    def _cleanup_expired_code(self, key: str):
        """Remove expired code/token"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self._memory_store.pop(key, None)
        except Exception as e:
            logger.error(f"Failed to cleanup expired code: {e}")
    
    def send_verification_email(self, email: str, code: str) -> bool:
        """Send email verification code"""
        try:
            subject = "Email Verification Code - Social Trend Analyzer"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                        <h2 style="color: #333; text-align: center;">Email Verification</h2>
                        <p style="color: #666; font-size: 16px;">Hello,</p>
                        <p style="color: #666; font-size: 16px;">
                            Thank you for registering with Social Trend Analyzer. 
                            Please use the following verification code to complete your registration:
                        </p>
                        <div style="background-color: #007bff; color: white; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                            <h1 style="margin: 0; font-size: 32px; letter-spacing: 5px;">{code}</h1>
                        </div>
                        <p style="color: #666; font-size: 14px;">
                            This code will expire in 10 minutes. If you didn't request this verification, please ignore this email.
                        </p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #999; font-size: 12px; text-align: center;">
                            Social Trend Analyzer Team<br>
                            This is an automated message, please do not reply.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            return self._send_email(email, subject, html_body)
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            return False
    
    def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """Send password reset email"""
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}&email={email}"
            subject = "Password Reset Request - Social Trend Analyzer"
            
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                        <h2 style="color: #333; text-align: center;">Password Reset Request</h2>
                        <p style="color: #666; font-size: 16px;">Hello,</p>
                        <p style="color: #666; font-size: 16px;">
                            We received a request to reset your password for your Social Trend Analyzer account.
                            Click the button below to reset your password:
                        </p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_url}" 
                               style="background-color: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                                Reset Password
                            </a>
                        </div>
                        <p style="color: #666; font-size: 14px;">
                            If the button doesn't work, copy and paste this link into your browser:
                        </p>
                        <p style="color: #007bff; font-size: 14px; word-break: break-all;">
                            {reset_url}
                        </p>
                        <p style="color: #666; font-size: 14px;">
                            This link will expire in 30 minutes. If you didn't request a password reset, please ignore this email.
                        </p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #999; font-size: 12px; text-align: center;">
                            Social Trend Analyzer Team<br>
                            This is an automated message, please do not reply.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            return self._send_email(email, subject, html_body)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

# Global email service instance
email_service = EmailService()