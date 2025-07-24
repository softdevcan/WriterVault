"""
FastAPI dependencies for authentication and database.
Clean implementation with PostgreSQL support.
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.core.security import verify_token
from app.models.user import User
from app.services.auth import auth_service


# Database dependency
def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI endpoints.
    Provides SQLAlchemy session with proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token and get username
    username = verify_token(token)
    if username is None:
        raise credentials_exception
    
    # Get user from database
    user = auth_service.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 