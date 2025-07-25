"""
Production-ready FastAPI application with security enhancements.
"""
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.articles import router as articles_router
from app.api.v1.collections import router as collections_router
from app.api.v1.categories import router as categories_router
from app.core.security import generate_secure_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Application startup/shutdown context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    # Startup
    logger.info("🚀 Starting Writers Platform API...")
    logger.info("📊 Rate limiting enabled")
    logger.info("🔒 Security middleware configured")
    
    yield
    
    # Shutdown
    logger.info("⏹️ Shutting down Writers Platform API...")

# Create FastAPI app with production settings
app = FastAPI(
    title=os.getenv("APP_NAME", "Writers Platform API"),
    description=os.getenv("APP_DESCRIPTION", "Production-ready API for Writers Platform"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    docs_url="/docs" if os.getenv("DEBUG", "false").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "false").lower() == "true" else None,
    lifespan=lifespan
)

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security Middleware - Order matters!

# 1. Trusted Host middleware (first for security)
allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=allowed_hosts
)

# 2. CORS middleware
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
allowed_methods = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=["*"],
)

# Custom middleware for logging and security headers
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers and request logging."""
    start_time = time.time()
    
    # Log incoming request
    logger.info(
        f"📥 {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = os.getenv("X_CONTENT_TYPE_OPTIONS", "nosniff")
    response.headers["X-Frame-Options"] = os.getenv("X_FRAME_OPTIONS", "DENY")
    response.headers["X-XSS-Protection"] = os.getenv("X_XSS_PROTECTION", "1; mode=block")
    response.headers["Strict-Transport-Security"] = f"max-age={os.getenv('HSTS_MAX_AGE', '31536000')}; includeSubDomains"
    response.headers["Referrer-Policy"] = os.getenv("REFERRER_POLICY", "strict-origin-when-cross-origin")
    
    # CSP: Relaxed for development, strict for production
    if os.getenv("DEBUG", "false").lower() == "true":
        # Development: Allow external CDNs for Swagger UI
        csp_dev = os.getenv("CSP_DEVELOPMENT", 
            "default-src 'self'; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data: fastapi.tiangolo.com; font-src 'self' cdn.jsdelivr.net"
        )
        response.headers["Content-Security-Policy"] = csp_dev
    else:
        # Production: Strict CSP
        csp_prod = os.getenv("CSP_PRODUCTION", "default-src 'self'")
        response.headers["Content-Security-Policy"] = csp_prod
    
    # Add request ID for tracking
    request_id = getattr(request.state, 'request_id', generate_secure_token(8))
    response.headers["X-Request-ID"] = request_id
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"📤 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# Include routers with rate limiting
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["authentication"]
)

app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["administration"]
)

# Add this after the existing router includes (around line 95)
app.include_router(
    articles_router,
    prefix="/api/v1/articles",
    tags=["articles"]
)

# Collections router
app.include_router(
    collections_router,
    prefix="/api/v1/collections",
    tags=["collections"],
)

# Categories router  
app.include_router(
    categories_router,
    prefix="/api/v1/categories", 
    tags=["categories"],
)

# Root endpoints
@app.get("/")
@limiter.limit(os.getenv("ROOT_RATE_LIMIT", "10/minute"))
async def root(request: Request):
    """Root endpoint with basic API information."""
    return {
        "message": os.getenv("APP_NAME", "Writers Platform API"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "operational",
        "docs": "/docs" if os.getenv("DEBUG", "false").lower() == "true" else "disabled"
    }

@app.get("/health")
@limiter.limit(os.getenv("HEALTH_RATE_LIMIT", "30/minute")) 
async def health_check(request: Request):
    """Health check endpoint for monitoring systems."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": "operational",
        "version": os.getenv("APP_VERSION", "1.0.0")
    }

@app.get("/api/v1/info")
@limiter.limit(os.getenv("INFO_RATE_LIMIT", "20/minute"))
async def api_info(request: Request):
    """API information endpoint."""
    return {
        "api_name": os.getenv("APP_NAME", "Writers Platform API"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "features": [
            "JWT Authentication",
            "Rate Limiting", 
            "Security Headers",
            "Request Logging",
            "Health Checks"
        ]
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    request_id = getattr(request.state, 'request_id', generate_secure_token(8))
    
    logger.error(
        f"🚨 Unhandled exception - Request ID: {request_id} - "
        f"Path: {request.url.path} - Error: {str(exc)}"
    )
    
    # Don't expose internal errors in production
    if os.getenv("DEBUG", "false").lower() == "true":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "request_id": request_id
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "request_id": request_id
            }
        )

if __name__ == "__main__":
    import uvicorn
    
    # Production-ready uvicorn configuration
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        workers=int(os.getenv("WORKERS", "1")),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    ) 