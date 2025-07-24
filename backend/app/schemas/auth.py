"""
Authentication schemas.
Clean Pydantic models for auth endpoints.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT Token payload data."""
    username: Optional[str] = None


class UserLogin(BaseModel):
    """User login credentials."""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration data."""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User data in API responses."""
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True


class PasswordResetRequest(BaseModel):
    """Password reset request payload."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation payload."""
    token: str
    new_password: str


class PasswordResetResponse(BaseModel):
    """Password reset response."""
    message: str
    detail: Optional[str] = None 