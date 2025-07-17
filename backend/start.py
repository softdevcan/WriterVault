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
    """Validate required environment variables."""
    logger = logging.getLogger(__name__)
    
    required_vars = [
        "SECRET_KEY",
    ]
    
    # Check for required environment variables
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == "generate-with-openssl-rand-hex-32-change-in-production":
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"🚨 Missing required environment variables: {', '.join(missing_vars)}")
        if os.getenv("ENVIRONMENT") == "production":
            logger.error("🚨 Cannot start in production without proper configuration!")
            sys.exit(1)
        else:
            logger.warning("⚠️ Using default values for development. Set proper values for production!")
    
    # Validate numeric environment variables
    numeric_vars = {
        "PORT": (1, 65535),
        "WORKERS": (1, 32),
        "ACCESS_TOKEN_EXPIRE_MINUTES": (1, 1440),
    }
    
    for var, (min_val, max_val) in numeric_vars.items():
        value = os.getenv(var)
        if value:
            try:
                num_value = int(value)
                if not min_val <= num_value <= max_val:
                    logger.warning(f"⚠️ {var}={num_value} is outside recommended range ({min_val}-{max_val})")
            except ValueError:
                logger.error(f"🚨 {var} must be a valid integer, got: {value}")
                sys.exit(1)
    
    logger.info("✅ Environment validation passed")


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
    config = {
        "app": app,  # Use the imported app object directly
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
        "workers": int(os.getenv("WORKERS", "1")),
        "log_level": os.getenv("LOG_LEVEL", "info").lower(),
        "access_log": True,
        "reload": os.getenv("DEBUG", "false").lower() == "true",
    }
    
    # Production-specific optimizations
    if os.getenv("ENVIRONMENT") == "production":
        config.update({
            "reload": False,
            "debug": False,
            "workers": max(int(os.getenv("WORKERS", "4")), 2),
        })
    
    return config


def print_startup_info():
    """Print startup information."""
    logger = logging.getLogger(__name__)
    
    environment = os.getenv("ENVIRONMENT", "development")
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8000")
    workers = os.getenv("WORKERS", "1")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info("🚀 Starting Writers Platform API")
    logger.info(f"📍 Environment: {environment}")
    logger.info(f"🌐 Server: http://{host}:{port}")
    logger.info(f"⚙️ Workers: {workers}")
    logger.info(f"🐛 Debug mode: {debug}")
    
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