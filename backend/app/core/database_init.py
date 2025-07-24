"""
Database Initialization and Seeding.
Creates demo users and initial data for WriterVault API.
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.config.database import SessionLocal, engine
from app.config.settings import Settings
from app.models.user import User
from app.services.auth import auth_service
from app.schemas.auth import UserRegister
from app.core.security import is_password_strong

# Configure logging
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()


class DatabaseInitializer:
    """Database initialization and seeding service."""
    
    def __init__(self):
        """Initialize database initializer."""
        self.demo_users_created = 0
        self.errors: List[str] = []
        
    def initialize_database(self) -> Dict[str, Any]:
        """
        Initialize database with demo data.
        
        Returns:
            Dict with initialization results
        """
        logger.info("🚀 Starting database initialization...")
        
        try:
            # Create database session
            db = SessionLocal()
            
            try:
                # Check database connection
                if not self._test_database_connection(db):
                    return {"success": False, "error": "Database connection failed"}
                
                # Create demo users
                demo_results = self._create_demo_users(db)
                
                # Create additional sample data (future expansion)
                # sample_results = self._create_sample_data(db)
                
                # Summary
                success = len(self.errors) == 0
                
                result = {
                    "success": success,
                    "demo_users_created": self.demo_users_created,
                    "errors": self.errors,
                    "total_errors": len(self.errors)
                }
                
                if success:
                    logger.info("✅ Database initialization completed successfully")
                    logger.info(f"📊 Created {self.demo_users_created} demo users")
                else:
                    logger.error(f"🚨 Database initialization failed with {len(self.errors)} errors")
                    for error in self.errors:
                        logger.error(f"🚨 {error}")
                
                return result
                
            finally:
                db.close()
                
        except Exception as e:
            error_msg = f"Database initialization error: {str(e)}"
            logger.error(f"🚨 {error_msg}")
            return {"success": False, "error": error_msg}
    
    def _test_database_connection(self, db: Session) -> bool:
        """
        Test database connection.
        
        Args:
            db: Database session
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple query to test connection
            db.execute("SELECT 1")
            logger.info("✅ Database connection test successful")
            return True
            
        except Exception as e:
            error_msg = f"Database connection test failed: {str(e)}"
            logger.error(f"🚨 {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def _create_demo_users(self, db: Session) -> Dict[str, Any]:
        """
        Create demo users for testing and development.
        
        Args:
            db: Database session
            
        Returns:
            Dict with creation results
        """
        logger.info("👥 Creating demo users...")
        
        # Demo users configuration
        demo_users = [
            {
                "username": settings.DEMO_USERNAME,
                "email": settings.DEMO_EMAIL,
                "password": settings.DEMO_PASSWORD,
                "full_name": settings.DEMO_FULL_NAME,
                "is_admin": False,
                "is_verified": True
            },
            {
                "username": "admin",
                "email": "admin@writervault.com",
                "password": "admin123!",
                "full_name": "System Administrator",
                "is_admin": True,
                "is_verified": True
            },
            {
                "username": "writer1",
                "email": "writer1@example.com",
                "password": "writer123!",
                "full_name": "John Writer",
                "is_admin": False,
                "is_verified": True
            },
            {
                "username": "writer2",
                "email": "writer2@example.com",
                "password": "writer456!",
                "full_name": "Jane Author",
                "is_admin": False,
                "is_verified": False  # Unverified user for testing
            }
        ]
        
        created_count = 0
        
        for user_data in demo_users:
            try:
                # Check if user already exists
                existing_user = auth_service.get_user_by_username(db, user_data["username"])
                if existing_user:
                    logger.info(f"👤 User {user_data['username']} already exists, skipping...")
                    continue
                
                # Check if email already exists
                existing_email = auth_service.get_user_by_email(db, user_data["email"])
                if existing_email:
                    logger.info(f"📧 Email {user_data['email']} already exists, skipping...")
                    continue
                
                # Validate password strength
                is_strong, issues = is_password_strong(user_data["password"])
                if not is_strong:
                    logger.warning(f"⚠️ Weak password for {user_data['username']}: {', '.join(issues)}")
                
                # Create user registration data
                user_register = UserRegister(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password"],
                    full_name=user_data["full_name"]
                )
                
                # Create user
                created_user = auth_service.create_user(db, user_register)
                
                if created_user:
                    # Set additional properties
                    if user_data.get("is_admin", False):
                        created_user.is_admin = True
                    
                    if user_data.get("is_verified", False):
                        created_user.is_verified = True
                    
                    db.commit()
                    
                    created_count += 1
                    logger.info(f"✅ Created demo user: {user_data['username']} ({user_data['email']})")
                    
                    # Log user role
                    role = "Admin" if created_user.is_admin else "User"
                    status = "Verified" if created_user.is_verified else "Unverified"
                    logger.info(f"   Role: {role}, Status: {status}")
                    
                else:
                    error_msg = f"Failed to create demo user: {user_data['username']}"
                    logger.error(f"🚨 {error_msg}")
                    self.errors.append(error_msg)
                    
            except Exception as e:
                error_msg = f"Error creating demo user {user_data['username']}: {str(e)}"
                logger.error(f"🚨 {error_msg}")
                self.errors.append(error_msg)
                db.rollback()
        
        self.demo_users_created = created_count
        
        if created_count > 0:
            logger.info(f"✅ Successfully created {created_count} demo users")
        else:
            logger.info("ℹ️ No new demo users created (all already exist)")
        
        return {"created": created_count, "errors": len(self.errors)}
    
    def _create_sample_data(self, db: Session) -> Dict[str, Any]:
        """
        Create sample data for testing (future expansion).
        
        Args:
            db: Database session
            
        Returns:
            Dict with creation results
        """
        logger.info("📝 Creating sample data...")
        
        # TODO: Add sample articles, categories, etc. when models are ready
        # For now, just return success
        
        logger.info("✅ Sample data creation completed")
        return {"created": 0, "errors": 0}
    
    def reset_database(self, db: Session) -> bool:
        """
        Reset database (development only).
        
        Args:
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.warning("🗑️ Resetting database (development only)...")
            
            # Delete all users (in future, delete other entities too)
            deleted_count = db.query(User).delete()
            db.commit()
            
            logger.info(f"🗑️ Deleted {deleted_count} users")
            logger.info("✅ Database reset completed")
            
            return True
            
        except Exception as e:
            logger.error(f"🚨 Database reset error: {str(e)}")
            db.rollback()
            return False
    
    def get_user_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get user statistics for monitoring.
        
        Args:
            db: Database session
            
        Returns:
            Dict with user statistics
        """
        try:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            verified_users = db.query(User).filter(User.is_verified == True).count()
            admin_users = db.query(User).filter(User.is_admin == True).count()
            
            stats = {
                "total_users": total_users,
                "active_users": active_users,
                "verified_users": verified_users,
                "admin_users": admin_users,
                "inactive_users": total_users - active_users,
                "unverified_users": total_users - verified_users
            }
            
            logger.info("📊 User Statistics:")
            for key, value in stats.items():
                logger.info(f"   {key.replace('_', ' ').title()}: {value}")
            
            return stats
            
        except Exception as e:
            logger.error(f"🚨 Error getting user statistics: {str(e)}")
            return {}


# Global database initializer instance
db_initializer = DatabaseInitializer() 