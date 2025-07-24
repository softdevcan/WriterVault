"""
User Repository for database operations.
Implements Repository pattern for clean data access layer.
"""
from typing import Optional, List
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.auth import UserRegister
from app.core.security import get_password_hash, hash_password_reset_token, verify_password_reset_token

# Configure logging
logger = logging.getLogger(__name__)


class UserRepository:
    """
    Repository for User entity database operations.
    Handles all database access logic for User model.
    """
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get user by username from database.
        
        Args:
            db: Database session
            username: Username to search for
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Database error getting user by username {username}: {str(e)}")
            return None
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email from database.
        
        Args:
            db: Database session
            email: Email to search for
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Database error getting user by email {email}: {str(e)}")
            return None
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID from database.
        
        Args:
            db: Database session
            user_id: User ID to search for
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Database error getting user by ID {user_id}: {str(e)}")
            return None
    
    def create(self, db: Session, user_data: UserRegister) -> Optional[User]:
        """
        Create a new user in database.
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created User object if successful, None otherwise
        """
        try:
            # Hash password before storing
            hashed_password = get_password_hash(user_data.password)
            
            # Create new user instance
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                is_active=True,
                is_verified=False,  # Email verification required
                is_admin=False
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"Successfully created user: {user_data.username}")
            return db_user
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating user {user_data.username}: {str(e)}")
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Database error creating user {user_data.username}: {str(e)}")
            return None
    
    def update_password(self, db: Session, user: User, new_password: str) -> bool:
        """
        Update user password.
        
        Args:
            db: Database session
            user: User object to update
            new_password: New plain text password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            
            logger.info(f"Password updated for user: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error updating password for {user.username}: {str(e)}")
            return False
    
    def deactivate(self, db: Session, user: User) -> bool:
        """
        Deactivate user account.
        
        Args:
            db: Database session
            user: User object to deactivate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user.is_active = False
            db.commit()
            
            logger.info(f"Deactivated user: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error deactivating user {user.username}: {str(e)}")
            return False
    
    def activate(self, db: Session, user: User) -> bool:
        """
        Activate user account.
        
        Args:
            db: Database session
            user: User object to activate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user.is_active = True
            db.commit()
            
            logger.info(f"Activated user: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error activating user {user.username}: {str(e)}")
            return False
    
    def verify_email(self, db: Session, user: User) -> bool:
        """
        Mark user email as verified.
        
        Args:
            db: Database session
            user: User object to verify
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user.is_verified = True
            db.commit()
            
            logger.info(f"Email verified for user: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error verifying email for {user.username}: {str(e)}")
            return False
    
    def get_all_active(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all active users with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active User objects
        """
        try:
            return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Database error getting active users: {str(e)}")
            return []
    
    def set_password_reset_token(self, db: Session, user: User, token: str, expires_hours: int = 24) -> bool:
        """
        Set password reset token for user.
        
        Args:
            db: Database session
            user: User object to set token for
            token: Plain text reset token
            expires_hours: Hours until token expires (default 24)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Hash the token before storing
            hashed_token = hash_password_reset_token(token)
            
            # Set expiration time
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
            
            user.reset_token = hashed_token
            user.reset_token_expires = expires_at
            db.commit()
            
            logger.info(f"Password reset token set for user: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error setting reset token for {user.username}: {str(e)}")
            return False
    
    def verify_password_reset_token_for_user(self, db: Session, user: User, token: str) -> bool:
        """
        Verify password reset token for user.
        
        Args:
            db: Database session
            user: User object to verify token for
            token: Plain text reset token to verify
            
        Returns:
            True if token is valid and not expired, False otherwise
        """
        try:
            # Check if user has a reset token
            if not user.reset_token or not user.reset_token_expires:
                logger.warning(f"No reset token found for user: {user.username}")
                return False
            
            # Check if token is expired
            if datetime.now(timezone.utc) > user.reset_token_expires:
                logger.warning(f"Expired reset token for user: {user.username}")
                return False
            
            # Verify token hash
            if not verify_password_reset_token(token, user.reset_token):
                logger.warning(f"Invalid reset token for user: {user.username}")
                return False
            
            logger.info(f"Valid reset token verified for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Database error verifying reset token for {user.username}: {str(e)}")
            return False
    
    def clear_password_reset_token(self, db: Session, user: User) -> bool:
        """
        Clear password reset token for user after successful reset.
        
        Args:
            db: Database session
            user: User object to clear token for
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user.reset_token = None
            user.reset_token_expires = None
            db.commit()
            
            logger.info(f"Reset token cleared for user: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error clearing reset token for {user.username}: {str(e)}")
            return False
    
    def get_by_reset_token(self, db: Session, token: str) -> Optional[User]:
        """
        Get user by password reset token.
        
        Args:
            db: Database session
            token: Plain text reset token
            
        Returns:
            User object if found and token is valid, None otherwise
        """
        try:
            # Get all users with non-null reset tokens that haven't expired
            users_with_tokens = db.query(User).filter(
                User.reset_token.isnot(None),
                User.reset_token_expires.isnot(None),
                User.reset_token_expires > datetime.now(timezone.utc)
            ).all()
            
            # Check each user's token
            for user in users_with_tokens:
                if verify_password_reset_token(token, user.reset_token):
                    logger.info(f"User found by reset token: {user.username}")
                    return user
            
            logger.warning("No user found with valid reset token")
            return None
            
        except Exception as e:
            logger.error(f"Database error getting user by reset token: {str(e)}")
            return None
    
    def delete(self, db: Session, user: User) -> bool:
        """
        Delete user from database.
        
        Args:
            db: Database session
            user: User object to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db.delete(user)
            db.commit()
            
            logger.info(f"Deleted user: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error deleting user {user.username}: {str(e)}")
            return False


# Global user repository instance
user_repository = UserRepository() 