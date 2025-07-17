"""
Authentication API endpoints.
Production-ready implementation with security enhancements.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
import os

from app.schemas.auth import Token, UserRegister, UserResponse
from app.services.auth import auth_service
from app.api.deps import get_current_active_user
from app.models.user import User
from app.core.security import is_password_strong

# Configure logging
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit(os.getenv("AUTH_LOGIN_RATE_LIMIT", "5/minute"))  # Rate limit login attempts
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    User login endpoint with rate limiting and security logging.
    
    Rate limit: 5 attempts per minute per IP
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🔐 Login attempt for user: {form_data.username} from IP: {client_ip}")
    
    try:
        user = auth_service.authenticate_user(form_data.username, form_data.password)
        
        if not user:
            logger.warning(f"🚫 Failed login attempt for user: {form_data.username} from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate access token
        access_token = auth_service.create_user_token(user.username)
        
        logger.info(f"✅ Successful login for user: {form_data.username} from IP: {client_ip}")
        
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 Login error for user: {form_data.username} - Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )


@router.post("/register", response_model=UserResponse)
@limiter.limit(os.getenv("AUTH_REGISTER_RATE_LIMIT", "3/minute"))  # Rate limit registration attempts
async def register(request: Request, user_data: UserRegister):
    """
    User registration endpoint with strong password validation.
    
    Rate limit: 3 attempts per minute per IP
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"📝 Registration attempt for user: {user_data.username} from IP: {client_ip}")
    
    try:
        # Validate password strength
        is_strong, password_issues = is_password_strong(user_data.password)
        
        if not is_strong:
            logger.warning(f"🚫 Weak password in registration for user: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "issues": password_issues
                }
            )
        
        # Check if user already exists
        if auth_service.user_exists(user_data.username):
            logger.warning(f"🚫 Duplicate registration attempt for user: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if auth_service.email_exists(user_data.email):
            logger.warning(f"🚫 Duplicate email registration attempt: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = auth_service.create_user(user_data)
        
        logger.info(f"✅ Successful registration for user: {user_data.username} from IP: {client_ip}")
        
        return UserResponse(
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            is_active=new_user.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 Registration error for user: {user_data.username} - Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration service unavailable"
        )


@router.get("/me", response_model=UserResponse)
@limiter.limit(os.getenv("AUTH_PROFILE_RATE_LIMIT", "30/minute"))  # Rate limit profile access
async def get_current_user_profile(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile information.
    
    Rate limit: 30 requests per minute per IP
    Requires: Valid JWT token
    """
    logger.info(f"👤 Profile access for user: {current_user.username}")
    
    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active
    )


@router.post("/logout")
@limiter.limit(os.getenv("AUTH_LOGOUT_RATE_LIMIT", "10/minute"))  # Rate limit logout attempts
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    User logout endpoint.
    
    Rate limit: 10 requests per minute per IP
    Note: With JWT, logout is handled client-side by removing the token.
    This endpoint is for logging purposes and future token blacklisting.
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🚪 Logout for user: {current_user.username} from IP: {client_ip}")
    
    # In a production environment with Redis, you could blacklist the token here
    # For now, we just log the logout event
    
    return {
        "message": "Successfully logged out",
        "detail": "Please remove the token from your client"
    }


@router.get("/validate-token")
@limiter.limit(os.getenv("AUTH_VALIDATE_RATE_LIMIT", "60/minute"))  # Higher limit for token validation
async def validate_token(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate if the provided token is still valid.
    
    Rate limit: 60 requests per minute per IP
    Requires: Valid JWT token
    """
    return {
        "valid": True,
        "username": current_user.username,
        "is_active": current_user.is_active
    } 