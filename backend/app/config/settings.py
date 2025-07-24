"""
Application settings with PostgreSQL configuration.
Modern Pydantic Settings approach for SQLAlchemy 2.0+
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with PostgreSQL support."""
    
    # Database Configuration
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/writervault"
    DATABASE_ECHO: bool = False  # SQLAlchemy echo for development
    AUTO_INIT_DB: bool = False 
    
    # Server Configuration (existing from env.example)
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 1
    LOG_LEVEL: str = "info"
    
    # CORS & Security Configuration
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    HSTS_MAX_AGE: int = 31536000
    
    # Content Security Policy
    CSP_DEVELOPMENT: str = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; connect-src 'self' fastapi.tiangolo.com"
    CSP_PRODUCTION: str = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none'"
    
    # Rate Limiting
    ROOT_RATE_LIMIT: str = "100/minute"
    HEALTH_RATE_LIMIT: str = "60/minute"
    AUTH_LOGIN_RATE_LIMIT: str = "5/minute"
    AUTH_REGISTER_RATE_LIMIT: str = "3/minute"
    AUTH_LOGOUT_RATE_LIMIT: str = "10/minute"
    AUTH_ME_RATE_LIMIT: str = "30/minute"
    AUTH_REFRESH_RATE_LIMIT: str = "10/minute"
    
    # Demo User Settings
    DEMO_USERNAME: str = "demo_user"
    DEMO_EMAIL: str = "demo@example.com"
    DEMO_PASSWORD: str = "demo123"
    DEMO_FULL_NAME: str = "Demo User"
    
    # Existing JWT Settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Settings
    APP_NAME: str = "Writers Platform API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Production-ready API for Writers Platform"
    DEBUG: bool = False
     
    # Rate Limiting
    AUTH_REGISTER_RATE_LIMIT: str = "3/minute"
    AUTH_LOGOUT_RATE_LIMIT: str = "10/minute"
    AUTH_ME_RATE_LIMIT: str = "30/minute"
    AUTH_RESET_REQUEST_RATE_LIMIT: str = "3/hour"
    AUTH_RESET_CONFIRM_RATE_LIMIT: str = "5/hour"
    AUTH_VERIFY_TOKEN_RATE_LIMIT: str = "10/hour"
    
    # Admin Rate Limiting (bunlar eksikti)
    ADMIN_STATS_RATE_LIMIT: str = "30/minute"
    ADMIN_INIT_RATE_LIMIT: str = "5/hour"
    ADMIN_RESET_RATE_LIMIT: str = "1/hour"
    ADMIN_HEALTH_RATE_LIMIT: str = "60/minute"
    
    # Email Service Configuration
    EMAIL_ENABLED: bool = False
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@writervault.com"
    FROM_NAME: str = "WriterVault"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Demo User Settings  
    DEMO_USERNAME: str = "demo_user"
    DEMO_EMAIL: str = "demo@example.com"
    DEMO_PASSWORD: str = "demo123"
    DEMO_FULL_NAME: str = "Demo User"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings() 