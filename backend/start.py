#!/usr/bin/env python3
"""
Production-ready startup script for Writers Platform API.
Includes environment validation, logging setup, and graceful shutdown.
"""
import os
import sys
import signal
import logging
import uvicorn
from pathlib import Path

# Add the backend directory to the Python path for proper module imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Ensure we can import the app module
try:
    from app.main import app
except ImportError as e:
    print(f"Error importing app module: {e}")
    print("Make sure you're running this script from the backend directory")
    sys.exit(1)


def setup_logging():
    """Configure application logging."""
    log_level = os.getenv("LOG_LEVEL", "info").upper()
    log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log") if os.getenv("ENVIRONMENT") != "production" else logging.NullHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"🔧 Logging configured - Level: {log_level}")
    return logger


def validate_environment():
    """Validate required environment variables using comprehensive validator."""
    logger = logging.getLogger(__name__)
    
    try:
        # Import environment validator
        from app.config.env_validator import env_validator
        
        # Run comprehensive validation
        result = env_validator.validate_all()
        
        # Handle validation results
        if not result["valid"]:
            logger.error(f"🚨 Environment validation failed with {result['total_errors']} errors")
            
            # In production, exit on validation errors
            if os.getenv("ENVIRONMENT") == "production":
                logger.error("🚨 Cannot start in production with configuration errors!")
                sys.exit(1)
            else:
                logger.warning("⚠️ Configuration errors found but continuing in development mode")
        
        # Show summary
        if result["total_warnings"] > 0:
            logger.warning(f"⚠️ Configuration completed with {result['total_warnings']} warnings")
        else:
            logger.info("✅ Environment configuration validation passed")
            
    except ImportError as e:
        # Fallback to basic validation if validator import fails
        logger.warning(f"⚠️ Could not import environment validator: {e}")
        logger.warning("⚠️ Using basic validation...")
        
        # Basic fallback validation
        required_vars = ["SECRET_KEY", "DATABASE_URL"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"🚨 Missing required environment variables: {', '.join(missing_vars)}")
            if os.getenv("ENVIRONMENT") == "production":
                sys.exit(1)
        
        logger.info("✅ Basic environment validation passed")


def setup_signal_handlers():
    """Setup graceful shutdown signal handlers."""
    logger = logging.getLogger(__name__)
    
    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum}. Initiating graceful shutdown...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🔧 Signal handlers configured")


def get_config():
    """Get uvicorn configuration from environment variables."""
    reload_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    config = {
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
        "log_level": os.getenv("LOG_LEVEL", "info").lower(),
        "access_log": True,
        "reload": reload_mode,
    }
    
    # Use import string for reload mode, app object for production
    if reload_mode:
        config["app"] = "app.main:app"  # Import string for reload
    else:
        config["app"] = app  # App object for production
        config["workers"] = int(os.getenv("WORKERS", "1"))
    
    # Production-specific optimizations
    if os.getenv("ENVIRONMENT") == "production":
        config.update({
            "app": "app.main:app",  # Always use import string in production
            "reload": False,
            "debug": False,
            "workers": max(int(os.getenv("WORKERS", "4")), 2),
        })
    
    return config


def initialize_database_if_needed():
    """Initialize database with demo users if needed."""
    logger = logging.getLogger(__name__)
    
    # Check if auto-initialization is enabled
    auto_init = os.getenv("AUTO_INIT_DB", "false").lower() == "true"
    
    if not auto_init:
        logger.info("🔧 Database auto-initialization disabled")
        return
    
    try:
        # Import database initializer
        from app.core.database_init import db_initializer
        
        logger.info("🚀 Auto-initializing database...")
        
        # Run initialization
        result = db_initializer.initialize_database()
        
        if result.get('success', False):
            created_count = result.get('demo_users_created', 0)
            if created_count > 0:
                logger.info(f"✅ Created {created_count} demo users")
            else:
                logger.info("ℹ️ Demo users already exist")
        else:
            logger.error("🚨 Database initialization failed")
            
    except ImportError as e:
        logger.warning(f"⚠️ Could not import database initializer: {e}")
    except Exception as e:
        logger.error(f"🚨 Database initialization error: {str(e)}")


def print_startup_info():
    """Print startup information."""
    logger = logging.getLogger(__name__)
    
    environment = os.getenv("ENVIRONMENT", "development")
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8000")
    workers = os.getenv("WORKERS", "1")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    auto_init = os.getenv("AUTO_INIT_DB", "false").lower() == "true"
    
    logger.info("🚀 Starting Writers Platform API")
    logger.info(f"📍 Environment: {environment}")
    logger.info(f"🌐 Server: http://{host}:{port}")
    logger.info(f"⚙️ Workers: {workers}")
    logger.info(f"🐛 Debug mode: {debug}")
    logger.info(f"🔧 Auto DB Init: {auto_init}")
    
    if debug:
        logger.info(f"📚 API Docs: http://{host}:{port}/docs")
        logger.info(f"📖 ReDoc: http://{host}:{port}/redoc")
    
    logger.info("="*50)


def main():
    """Main startup function."""
    try:
        # Setup logging first
        logger = setup_logging()
        
        # Print startup banner
        print_startup_info()
        
        # Validate environment
        validate_environment()
        
        # Initialize database if needed
        initialize_database_if_needed()
        
        # Setup signal handlers
        setup_signal_handlers()
        
        # Get uvicorn configuration
        config = get_config()
        
        logger.info("🎬 Starting uvicorn server...")
        
        # Start the server
        uvicorn.run(**config)
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"🚨 Failed to start server: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("👋 Writers Platform API shutdown complete")


if __name__ == "__main__":
    main() 