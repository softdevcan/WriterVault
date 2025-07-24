"""
Authentication API endpoints with PostgreSQL support.
Production-ready implementation with security enhancements.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
import logging
import os

from app.schemas.auth import Token, UserRegister, UserResponse, PasswordResetRequest, PasswordResetConfirm, PasswordResetResponse
from app.services.auth import auth_service
from app.services.email import email_service
from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.core.security import is_password_strong

# Configure logging
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit(os.getenv("AUTH_LOGIN_RATE_LIMIT", "5/minute"))  # Rate limit login attempts
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login endpoint with rate limiting and security logging.
    
    Rate limit: 5 attempts per minute per IP
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🔐 Login attempt for user: {form_data.username} from IP: {client_ip}")
    
    try:
        user = auth_service.authenticate_user(db, form_data.username, form_data.password)
        
        if not user:
            logger.warning(f"🚫 Failed login attempt for user: {form_data.username} from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate access token
        token = auth_service.create_access_token_for_user(user)
        
        logger.info(f"✅ Successful login for user: {form_data.username} from IP: {client_ip}")
        
        return token
        
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
async def register(
    request: Request,
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
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
        if auth_service.get_user_by_username(db, user_data.username):
            logger.warning(f"🚫 Duplicate registration attempt for user: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if auth_service.get_user_by_email(db, user_data.email):
            logger.warning(f"🚫 Duplicate email registration attempt: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = auth_service.create_user(db, user_data)
        
        if not new_user:
            logger.error(f"🚨 Failed to create user: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
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


@router.post("/request-password-reset", response_model=PasswordResetResponse)
@limiter.limit(os.getenv("AUTH_RESET_REQUEST_RATE_LIMIT", "3/hour"))  # Strict rate limit
async def request_password_reset(
    request: Request,
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset by email.
    
    Rate limit: 3 requests per hour per IP (strict security)
    Returns success message regardless of whether email exists (security)
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🔑 Password reset requested for email: {reset_request.email} from IP: {client_ip}")
    
    try:
        # Request reset token
        reset_token = auth_service.request_password_reset(db, reset_request.email)
        
        if reset_token:
            logger.info(f"✅ Password reset token generated for email: {reset_request.email}")
            
            # Send password reset email
            email_sent = email_service.send_password_reset_email(
                reset_request.email, 
                reset_token,
                ""  # Username will be fetched by email service if needed
            )
            
            if email_sent:
                logger.info(f"📧 Password reset email sent to: {reset_request.email}")
            else:
                logger.error(f"📧 Failed to send password reset email to: {reset_request.email}")
        else:
            logger.warning(f"🚫 Password reset failed for email: {reset_request.email}")
        
        # Always return success for security (don't reveal if email exists)
        return PasswordResetResponse(
            message="If an account with this email exists, you will receive password reset instructions.",
            detail="Check your email for reset instructions"
        )
        
    except Exception as e:
        logger.error(f"🚨 Password reset request error for {reset_request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset service unavailable"
        )


@router.post("/reset-password", response_model=PasswordResetResponse)
@limiter.limit(os.getenv("AUTH_RESET_CONFIRM_RATE_LIMIT", "5/hour"))  # Rate limit confirmations
async def reset_password(
    request: Request,
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset token.
    
    Rate limit: 5 attempts per hour per IP
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🔑 Password reset attempt with token from IP: {client_ip}")
    
    try:
        # Verify token and reset password
        success = auth_service.reset_password_with_token(
            db, 
            reset_confirm.token, 
            reset_confirm.new_password
        )
        
        if success:
            logger.info(f"✅ Password reset successful from IP: {client_ip}")
            return PasswordResetResponse(
                message="Password reset successful",
                detail="You can now login with your new password"
            )
        else:
            logger.warning(f"🚫 Invalid password reset token from IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset service unavailable"
        )


@router.post("/verify-reset-token")
@limiter.limit(os.getenv("AUTH_VERIFY_TOKEN_RATE_LIMIT", "10/hour"))  # Rate limit verifications
async def verify_reset_token(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify if a password reset token is valid.
    
    Rate limit: 10 attempts per hour per IP
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🔍 Reset token verification from IP: {client_ip}")
    
    try:
        user = auth_service.verify_reset_token(db, token)
        
        if user:
            logger.info(f"✅ Valid reset token verified from IP: {client_ip}")
            return {
                "valid": True,
                "message": "Reset token is valid",
                "username": user.username  # For user confirmation
            }
        else:
            logger.warning(f"🚫 Invalid reset token from IP: {client_ip}")
            return {
                "valid": False,
                "message": "Invalid or expired reset token"
            }
        
    except Exception as e:
        logger.error(f"🚨 Reset token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification service unavailable"
        ) 