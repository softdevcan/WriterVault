"""
Authentication service.
Production-ready business logic for user authentication and registration.
"""
from typing import Optional
import logging

from app.core.security import (
    verify_password, 
    create_access_token, 
    get_password_hash,
    generate_secure_token
)
from app.models.user import User, user_db
from app.schemas.auth import UserRegister, Token

# Configure logging
logger = logging.getLogger(__name__)


class AuthService:
    """Authentication business logic with enhanced security."""
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        
        Args:
            username: The username to authenticate
            password: The plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        try:
            user = user_db.get_user_by_username(username)
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
            logger.error(f"Authentication error for user {username}: {str(e)}")
            return None
    
    def user_exists(self, username: str) -> bool:
        """
        Check if a username already exists.
        
        Args:
            username: The username to check
            
        Returns:
            True if username exists, False otherwise
        """
        try:
            user = user_db.get_user_by_username(username)
            return user is not None
        except Exception as e:
            logger.error(f"Error checking username existence {username}: {str(e)}")
            return False
    
    def email_exists(self, email: str) -> bool:
        """
        Check if an email already exists.
        
        Args:
            email: The email to check
            
        Returns:
            True if email exists, False otherwise
        """
        try:
            user = user_db.get_user_by_email(email)
            return user is not None
        except Exception as e:
            logger.error(f"Error checking email existence {email}: {str(e)}")
            return False
    
    def create_user(self, user_data: UserRegister) -> User:
        """
        Create a new user with validated data.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created User object
            
        Raises:
            ValueError: If user creation fails due to validation
            Exception: For other unexpected errors
        """
        try:
            # Hash the password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user
            new_user = user_db.create_user(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name
            )
            
            logger.info(f"Successfully created user: {user_data.username}")
            return new_user
            
        except ValueError as e:
            logger.warning(f"User creation validation error for {user_data.username}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating user {user_data.username}: {str(e)}")
            raise Exception(f"Failed to create user: {str(e)}")
    
    def create_user_token(self, username: str) -> str:
        """
        Create an access token for a user.
        
        Args:
            username: The username to create token for
            
        Returns:
            JWT access token string
        """
        try:
            access_token = create_access_token(data={"sub": username})
            logger.info(f"Access token created for user: {username}")
            return access_token
        except Exception as e:
            logger.error(f"Token creation error for user {username}: {str(e)}")
            raise Exception(f"Failed to create access token: {str(e)}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: The username to look up
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return user_db.get_user_by_username(username)
        except Exception as e:
            logger.error(f"Error retrieving user {username}: {str(e)}")
            return None
    
    def deactivate_user(self, username: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            username: The username to deactivate
            
        Returns:
            True if deactivation successful, False otherwise
        """
        try:
            user = user_db.get_user_by_username(username)
            if not user:
                logger.warning(f"Attempted to deactivate non-existent user: {username}")
                return False
            
            user.is_active = False
            logger.info(f"User deactivated: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating user {username}: {str(e)}")
            return False
    
    def activate_user(self, username: str) -> bool:
        """
        Activate a user account.
        
        Args:
            username: The username to activate
            
        Returns:
            True if activation successful, False otherwise
        """
        try:
            user = user_db.get_user_by_username(username)
            if not user:
                logger.warning(f"Attempted to activate non-existent user: {username}")
                return False
            
            user.is_active = True
            logger.info(f"User activated: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating user {username}: {str(e)}")
            return False


# Global instance
auth_service = AuthService() 