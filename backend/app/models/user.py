"""
User SQLAlchemy ORM Model.
Modern SQLAlchemy 2.0+ implementation with PostgreSQL support.
"""
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base

# Configure logging
logger = logging.getLogger(__name__)


class User(Base):
    """
    Modern SQLAlchemy 2.0+ User ORM Model.
    
    Uses Mapped[] type annotations and mapped_column() for type safety
    and modern SQLAlchemy best practices.
    """
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # User credentials and basic info
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="Unique username (3-50 chars, alphanumeric and underscore only)"
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="User email address"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Hashed password (bcrypt)"
    )
    
    # User profile information
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="User's full name"
    )
    
    # User status and permissions
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active"
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user's email is verified"
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user has admin privileges"
    )
    
    # Password reset functionality
    reset_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Password reset token (hashed)"
    )
    reset_token_expires: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Password reset token expiration time"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Account creation timestamp"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        comment="Last update timestamp"
    )
    
    # Future relationships will be added here
    # articles: Mapped[List["Article"]] = relationship(back_populates="author")
    # comments: Mapped[List["Comment"]] = relationship(back_populates="author")
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.full_name or self.username} ({self.email})" 