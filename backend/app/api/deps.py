"""
API dependencies for authentication and database access.
Production-ready implementation with comprehensive security.
Combines OAuth2PasswordBearer with HTTPBearer for flexibility.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging

from app.config.database import SessionLocal
from app.core.security import verify_token
from app.repositories.user_repository import user_repository
from app.models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Security schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI endpoints.
    Provides SQLAlchemy session with proper cleanup.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user (required) - OAuth2 style.
    
    Args:
        token: JWT token from OAuth2PasswordBearer
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify JWT token
        user_id = verify_token(token)
        if not user_id:
            logger.warning("🚫 Invalid JWT token")
            raise credentials_exception
        
        # Get user from database
        user = user_repository.get_by_id(db, user_id)
        if not user:
            logger.warning(f"🚫 User not found: ID {user_id}")
            raise credentials_exception
        
        logger.debug(f"✅ User authenticated: {user.username}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 Authentication error: {str(e)}")
        raise credentials_exception


def get_current_user_bearer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user (required) - HTTPBearer style.
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        logger.warning("🚫 Missing authentication credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify JWT token
        user_id = verify_token(credentials.credentials)
        
        if not user_id:
            logger.warning("🚫 Invalid JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = user_repository.get_by_id(db, user_id)
        
        if not user:
            logger.warning(f"🚫 User not found: ID {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"✅ User authenticated: {user.username}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user (optional).
    Used for public endpoints that show different content for authenticated users.
    
    Args:
        credentials: JWT token from Authorization header (optional)
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        # Verify JWT token
        user_id = verify_token(credentials.credentials)
        
        if not user_id:
            return None
        
        # Get user from database
        user = user_repository.get_by_id(db, user_id)
        
        if not user:
            return None
        
        logger.debug(f"✅ Optional user authenticated: {user.username}")
        return user
        
    except Exception as e:
        logger.debug(f"⚠️ Optional authentication failed: {str(e)}")
        return None


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current authenticated and active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        logger.warning(f"🚫 Inactive user access attempt: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    return current_user


def get_current_active_user_bearer(
    current_user: User = Depends(get_current_user_bearer)
) -> User:
    """
    Get current authenticated and active user (HTTPBearer version).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        logger.warning(f"🚫 Inactive user access attempt: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current authenticated admin user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Admin user object
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin:
        logger.warning(f"🚫 Non-admin access attempt: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user


def get_current_admin_user_bearer(
    current_user: User = Depends(get_current_active_user_bearer)
) -> User:
    """
    Get current authenticated admin user (HTTPBearer version).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Admin user object
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin:
        logger.warning(f"🚫 Non-admin access attempt: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current authenticated and verified user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Verified user object
        
    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.is_verified:
        logger.warning(f"🚫 Unverified user access attempt: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return current_user


def get_current_verified_user_bearer(
    current_user: User = Depends(get_current_active_user_bearer)
) -> User:
    """
    Get current authenticated and verified user (HTTPBearer version).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Verified user object
        
    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.is_verified:
        logger.warning(f"🚫 Unverified user access attempt: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return current_user


# Convenience aliases for backward compatibility
get_current_user_required = get_current_user
get_current_user_required_bearer = get_current_user_bearer