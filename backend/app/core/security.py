"""
Core security utilities for authentication.
Production-ready implementation with latest security best practices.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import secrets
import os

from passlib.context import CryptContext
import jwt
from jwt import InvalidTokenError


# Production-ready security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Generate a secure random key for development only
    SECRET_KEY = secrets.token_urlsafe(32)
    print("WARNING: Using auto-generated SECRET_KEY. Set SECRET_KEY environment variable in production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing context with production-ready settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Higher rounds for better security
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Log this in production for security monitoring
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    # Use timezone-aware datetime for better security
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),  # Issued at
        "type": "access"  # Token type for additional security
    })
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return username.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        Optional[str]: Username if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Additional security checks
        if payload.get("type") != "access":
            return None
            
        username: str = payload.get("sub")
        if username is None:
            return None
            
        # Check if token is expired (JWT library handles this, but explicit check for clarity)
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc) > datetime.fromtimestamp(exp, timezone.utc):
            return None
            
        return username
        
    except InvalidTokenError:
        return None
    except Exception:
        # Log this in production for security monitoring
        return None


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token for various uses.
    
    Args:
        length: Length of the token
        
    Returns:
        str: Secure random token
    """
    return secrets.token_urlsafe(length)


def generate_password_reset_token() -> str:
    """
    Generate a secure password reset token.
    
    Returns:
        str: URL-safe password reset token
    """
    return secrets.token_urlsafe(32)


def hash_password_reset_token(token: str) -> str:
    """
    Hash password reset token for secure storage.
    
    Args:
        token: Plain text reset token
        
    Returns:
        str: Hashed token for database storage
    """
    return pwd_context.hash(token)


def verify_password_reset_token(token: str, hashed_token: str) -> bool:
    """
    Verify password reset token against stored hash.
    
    Args:
        token: Plain text reset token
        hashed_token: Stored hashed token
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        return pwd_context.verify(token, hashed_token)
    except Exception:
        return False


def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """
    Check if password meets security requirements.
    
    Args:
        password: The password to check
        
    Returns:
        tuple: (is_strong, list_of_issues)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    if len(password) > 128:
        issues.append("Password must be less than 128 characters")
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one digit")
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("Password must contain at least one special character")
    
    return len(issues) == 0, issues 