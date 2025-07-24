"""
Authentication service with PostgreSQL support.
Production-ready business logic for user authentication and registration.
Uses Repository pattern for clean architecture.
"""
from typing import Optional
import logging
from sqlalchemy.orm import Session

from app.core.security import (
    verify_password, 
    create_access_token, 
    generate_secure_token,
    generate_password_reset_token
)
from app.models.user import User
from app.schemas.auth import UserRegister, Token
from app.repositories.user_repository import user_repository

# Configure logging
logger = logging.getLogger(__name__)


class AuthService:
    """Authentication business logic with PostgreSQL support."""
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        
        Args:
            db: Database session
            username: The username to authenticate
            password: The plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            user = user_repository.get_by_username(db, username)
            if not user:
                logger.warning(f"Authentication attempt for non-existent user: {username}")
                return None
            
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Invalid password for user: {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"Inactive user authentication attempt: {username}")
                return None
            
            logger.info(f"Successful authentication for user: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Service error during authentication for {username}: {str(e)}")
            return None
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get user by username from database.
        
        Args:
            db: Database session
            username: Username to search for
            
        Returns:
            User object if found, None otherwise
        """
        return user_repository.get_by_username(db, username)
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email from database.
        
        Args:
            db: Database session
            email: Email to search for
            
        Returns:
            User object if found, None otherwise
        """
        return user_repository.get_by_email(db, email)
    
    def create_user(self, db: Session, user_data: UserRegister) -> Optional[User]:
        """
        Create a new user in database with business logic validation.
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created User object if successful, None otherwise
        """
        try:
            # Business logic: Check if username already exists
            if user_repository.get_by_username(db, user_data.username):
                logger.warning(f"Registration attempt with existing username: {user_data.username}")
                return None
            
            # Business logic: Check if email already exists
            if user_repository.get_by_email(db, user_data.email):
                logger.warning(f"Registration attempt with existing email: {user_data.email}")
                return None
            
            # Delegate user creation to repository
            created_user = user_repository.create(db, user_data)
            
            if created_user:
                logger.info(f"User registration successful: {user_data.username}")
            else:
                logger.error(f"User registration failed: {user_data.username}")
            
            return created_user
            
        except Exception as e:
            logger.error(f"Service error creating user {user_data.username}: {str(e)}")
            return None
    
    def create_access_token_for_user(self, user: User) -> Token:
        """
        Create access token for authenticated user.
        
        Args:
            user: Authenticated user object
            
        Returns:
            Token object with access_token and token_type
        """
        access_token = create_access_token(data={"sub": user.username})
        return Token(access_token=access_token, token_type="bearer")
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID for additional lookups.
        
        Args:
            db: Database session
            user_id: User ID to search for
            
        Returns:
            User object if found, None otherwise
        """
        return user_repository.get_by_id(db, user_id)
    
    def verify_user_email(self, db: Session, username: str) -> bool:
        """
        Mark user email as verified.
        
        Args:
            db: Database session
            username: Username to verify
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = user_repository.get_by_username(db, username)
            if not user:
                logger.warning(f"Email verification attempt for non-existent user: {username}")
                return False
            
            return user_repository.verify_email(db, user)
            
        except Exception as e:
            logger.error(f"Service error verifying email for {username}: {str(e)}")
            return False
    
    def activate_user(self, db: Session, username: str) -> bool:
        """
        Activate user account.
        
        Args:
            db: Database session
            username: Username to activate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = user_repository.get_by_username(db, username)
            if not user:
                logger.warning(f"Activation attempt for non-existent user: {username}")
                return False
            
            return user_repository.activate(db, user)
            
        except Exception as e:
            logger.error(f"Service error activating user {username}: {str(e)}")
            return False
    
    def update_user_password(self, db: Session, username: str, new_password: str) -> bool:
        """
        Update user password with business logic validation.
        
        Args:
            db: Database session
            username: Username of user to update
            new_password: New plain text password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Business logic: Find user first
            user = user_repository.get_by_username(db, username)
            if not user:
                logger.warning(f"Password update attempt for non-existent user: {username}")
                return False
            
            # Delegate password update to repository
            return user_repository.update_password(db, user, new_password)
            
        except Exception as e:
            logger.error(f"Service error updating password for {username}: {str(e)}")
            return False
    
    def deactivate_user(self, db: Session, username: str) -> bool:
        """
        Deactivate user account with business logic validation.
        
        Args:
            db: Database session
            username: Username to deactivate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Business logic: Find user first
            user = user_repository.get_by_username(db, username)
            if not user:
                logger.warning(f"Deactivation attempt for non-existent user: {username}")
                return False
            
            # Delegate deactivation to repository
            return user_repository.deactivate(db, user)
            
        except Exception as e:
            logger.error(f"Service error deactivating user {username}: {str(e)}")
            return False
    
    def request_password_reset(self, db: Session, email: str) -> Optional[str]:
        """
        Request password reset for user by email.
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            Reset token if successful, None otherwise
        """
        try:
            # Find user by email
            user = user_repository.get_by_email(db, email)
            if not user:
                logger.warning(f"Password reset requested for non-existent email: {email}")
                # Don't reveal if email exists for security
                return None
            
            if not user.is_active:
                logger.warning(f"Password reset requested for inactive user: {user.username}")
                return None
            
            # Generate reset token
            reset_token = generate_password_reset_token()
            
            # Store hashed token in database
            if user_repository.set_password_reset_token(db, user, reset_token):
                logger.info(f"Password reset token generated for user: {user.username}")
                return reset_token  # Return plain token for email
            
            return None
            
        except Exception as e:
            logger.error(f"Service error requesting password reset for {email}: {str(e)}")
            return None
    
    def verify_reset_token(self, db: Session, token: str) -> Optional[User]:
        """
        Verify password reset token and return user.
        
        Args:
            db: Database session
            token: Password reset token
            
        Returns:
            User object if token is valid, None otherwise
        """
        try:
            user = user_repository.get_by_reset_token(db, token)
            if user:
                logger.info(f"Valid reset token verified for user: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Service error verifying reset token: {str(e)}")
            return None
    
    def reset_password_with_token(self, db: Session, token: str, new_password: str) -> bool:
        """
        Reset user password using reset token.
        
        Args:
            db: Database session
            token: Password reset token
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify token and get user
            user = user_repository.get_by_reset_token(db, token)
            if not user:
                logger.warning("Password reset attempt with invalid token")
                return False
            
            # Update password
            if user_repository.update_password(db, user, new_password):
                # Clear reset token after successful reset
                user_repository.clear_password_reset_token(db, user)
                logger.info(f"Password reset successful for user: {user.username}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Service error resetting password: {str(e)}")
            return False


# Global auth service instance
auth_service = AuthService() 