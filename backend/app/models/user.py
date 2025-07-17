"""
User model and simple in-memory database.
Production-ready implementation for authentication system.
"""
import logging
import os
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.security import get_password_hash

# Configure logging
logger = logging.getLogger(__name__)


class User(BaseModel):
    """
    Enhanced User model with comprehensive validation and security features.
    
    This model represents a user in the system with strong validation rules
    for all fields, including email format validation and username constraints.
    """
    
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$',
        description="Username (3-50 chars, alphanumeric and underscore only)"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    full_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Full name (2-100 characters)"
    )
    hashed_password: str = Field(
        ...,
        description="Hashed password (never store plain text passwords)"
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format and restrictions."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.lower()
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        """Validate full name format."""
        if not v.strip():
            raise ValueError('Full name cannot be empty or just whitespace')
        return v.strip()


class UserDatabase:
    """
    Production-ready in-memory user database with enhanced operations.
    
    Note: In production, this should be replaced with a proper database
    like PostgreSQL, MySQL, or MongoDB with proper persistence.
    """
    
    def __init__(self):
        """Initialize the user database with demo data."""
        self.users: Dict[str, User] = {}
        self.email_index: Dict[str, str] = {}  # email -> username mapping
        self._create_demo_users()
    
    def _create_demo_users(self):
        """Create demo users for development and testing."""
        try:
            # Create demo user with production-ready hashed password
            demo_username = os.getenv("DEMO_USERNAME", "john")
            demo_email = os.getenv("DEMO_EMAIL", "john@demo.com")
            demo_password = os.getenv("DEMO_PASSWORD", "password123")
            demo_full_name = os.getenv("DEMO_FULL_NAME", "John Demo")
            
            demo_user = User(
                username=demo_username,
                email=demo_email,
                hashed_password=get_password_hash(demo_password),
                full_name=demo_full_name
            )
            
            self.users[demo_username] = demo_user
            self.email_index[demo_email] = demo_username
            
            logger.info("Demo users created successfully")
            
        except Exception as e:
            logger.error(f"Error creating demo users: {str(e)}")

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: The username to search for
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return self.users.get(username.lower())
        except Exception as e:
            logger.error(f"Error retrieving user by username '{username}': {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            User object if found, None otherwise
        """
        try:
            username = self.email_index.get(email.lower())
            return self.users.get(username) if username else None
        except Exception as e:
            logger.error(f"Error retrieving user by email '{email}': {str(e)}")
            return None
    
    def create_user(self, user_data: dict) -> Optional[User]:
        """
        Create a new user with comprehensive validation.
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            Created User object if successful, None otherwise
            
        Raises:
            ValueError: If user data is invalid or user already exists
        """
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'full_name', 'hashed_password']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    raise ValueError(f"Missing required field: {field}")
            
            username = user_data['username'].lower()
            email = user_data['email'].lower()
            
            # Check for existing user
            if username in self.users:
                raise ValueError(f"Username '{username}' already exists")
            
            if email in self.email_index:
                raise ValueError(f"Email '{email}' already registered")
            
            # Create user instance with validation
            user = User(**user_data)
            
            # Store user
            self.users[username] = user
            self.email_index[email] = username
            
            logger.info(f"User '{username}' created successfully")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def update_user(self, username: str, update_data: dict) -> Optional[User]:
        """
        Update an existing user's information.
        
        Args:
            username: The username of the user to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated User object if successful, None otherwise
        """
        try:
            user = self.get_user_by_username(username)
            if not user:
                raise ValueError(f"User '{username}' not found")
            
            # Handle email updates (need to update index)
            if 'email' in update_data:
                old_email = user.email.lower()
                new_email = update_data['email'].lower()
                
                if new_email != old_email:
                    if new_email in self.email_index:
                        raise ValueError(f"Email '{new_email}' already registered")
                    
                    # Update email index
                    del self.email_index[old_email]
                    self.email_index[new_email] = username
            
            # Update user fields
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            logger.info(f"User '{username}' updated successfully")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user '{username}': {str(e)}")
            raise
    
    def delete_user(self, username: str) -> bool:
        """
        Delete a user from the database.
        
        Args:
            username: The username of the user to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            user = self.get_user_by_username(username)
            if not user:
                logger.warning(f"Attempted to delete non-existent user: '{username}'")
                return False
            
            # Remove from both indexes
            email = user.email.lower()
            del self.users[username.lower()]
            del self.email_index[email]
            
            logger.info(f"User '{username}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user '{username}': {str(e)}")
            return False
    
    def list_users(self, active_only: bool = True) -> list[User]:
        """
        Get a list of all users.
        
        Args:
            active_only: If True, return only active users
            
        Returns:
            List of User objects
        """
        try:
            users = list(self.users.values())
            if active_only:
                users = [user for user in users if user.is_active]
            
            logger.debug(f"Retrieved {len(users)} users (active_only={active_only})")
            return users
            
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return []
    
    def get_user_count(self, active_only: bool = True) -> int:
        """
        Get the total number of users.
        
        Args:
            active_only: If True, count only active users
            
        Returns:
            Number of users
        """
        try:
            if active_only:
                return sum(1 for user in self.users.values() if user.is_active)
            return len(self.users)
            
        except Exception as e:
            logger.error(f"Error counting users: {str(e)}")
            return 0
    
    def user_exists(self, username: str = None, email: str = None) -> bool:
        """
        Check if a user exists by username or email.
        
        Args:
            username: Username to check
            email: Email to check
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            if username:
                return username.lower() in self.users
            if email:
                return email.lower() in self.email_index
            return False
            
        except Exception as e:
            logger.error(f"Error checking user existence: {str(e)}")
            return False


# Global database instance
user_db = UserDatabase() 