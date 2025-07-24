"""
Admin API endpoints for database management.
Requires admin privileges for access.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
import logging
import os

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.core.database_init import db_initializer

# Configure logging
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Verify current user has admin privileges."""
    if not current_user.is_admin:
        logger.warning(f"🚫 Non-admin user {current_user.username} attempted admin access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


@router.get("/stats")
@limiter.limit(os.getenv("ADMIN_STATS_RATE_LIMIT", "30/minute"))
async def get_database_statistics(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Get database statistics.
    
    Rate limit: 30 requests per minute per IP
    Requires: Admin privileges
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"📊 Database statistics requested by admin: {admin_user.username} from IP: {client_ip}")
    
    try:
        # Get user statistics
        stats = db_initializer.get_user_statistics(db)
        
        if stats:
            logger.info(f"✅ Statistics retrieved by admin: {admin_user.username}")
            return {
                "success": True,
                "statistics": stats,
                "message": "Database statistics retrieved successfully"
            }
        else:
            logger.error(f"🚨 Failed to retrieve statistics for admin: {admin_user.username}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve database statistics"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 Statistics error for admin {admin_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database statistics service unavailable"
        )


@router.post("/init-database")
@limiter.limit(os.getenv("ADMIN_INIT_RATE_LIMIT", "5/hour"))
async def initialize_database(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Initialize database with demo users.
    
    Rate limit: 5 requests per hour per IP
    Requires: Admin privileges
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🚀 Database initialization requested by admin: {admin_user.username} from IP: {client_ip}")
    
    try:
        # Run database initialization
        result = db_initializer.initialize_database()
        
        if result.get('success', False):
            logger.info(f"✅ Database initialization successful by admin: {admin_user.username}")
            return {
                "success": True,
                "demo_users_created": result.get('demo_users_created', 0),
                "message": "Database initialization completed successfully",
                "details": {
                    "total_errors": result.get('total_errors', 0),
                    "errors": result.get('errors', [])
                }
            }
        else:
            logger.error(f"🚨 Database initialization failed for admin: {admin_user.username}")
            return {
                "success": False,
                "demo_users_created": 0,
                "message": "Database initialization failed",
                "details": {
                    "total_errors": result.get('total_errors', 0),
                    "errors": result.get('errors', [])
                }
            }
        
    except Exception as e:
        logger.error(f"🚨 Database initialization error for admin {admin_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database initialization service unavailable"
        )


@router.post("/reset-database")
@limiter.limit(os.getenv("ADMIN_RESET_RATE_LIMIT", "1/hour"))
async def reset_database(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Reset database (development only).
    
    Rate limit: 1 request per hour per IP (very restrictive)
    Requires: Admin privileges
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.warning(f"🗑️ Database reset requested by admin: {admin_user.username} from IP: {client_ip}")
    
    # Check environment
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        logger.error(f"🚨 Database reset attempted in production by admin: {admin_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Database reset is not allowed in production"
        )
    
    try:
        # Reset database
        success = db_initializer.reset_database(db)
        
        if success:
            logger.warning(f"🗑️ Database reset successful by admin: {admin_user.username}")
            return {
                "success": True,
                "message": "Database reset completed successfully",
                "warning": "All data has been deleted"
            }
        else:
            logger.error(f"🚨 Database reset failed for admin: {admin_user.username}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database reset failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🚨 Database reset error for admin {admin_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database reset service unavailable"
        )


@router.get("/health-check")
@limiter.limit(os.getenv("ADMIN_HEALTH_RATE_LIMIT", "60/minute"))
async def admin_health_check(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Admin health check with database connection test.
    
    Rate limit: 60 requests per minute per IP
    Requires: Admin privileges
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🔌 Health check requested by admin: {admin_user.username} from IP: {client_ip}")
    
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Get basic statistics
        user_count = db.query(User).count()
        
        logger.info(f"✅ Health check successful for admin: {admin_user.username}")
        
        return {
            "status": "healthy",
            "database": "connected",
            "user_count": user_count,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": "2025-01-17T17:55:00Z"  # This would be dynamic in real implementation
        }
        
    except Exception as e:
        logger.error(f"🚨 Health check failed for admin {admin_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        ) 