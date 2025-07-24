"""
Environment Configuration Validator.
Validates all environment variables for WriterVault API.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class EnvironmentValidator:
    """Validates environment configuration."""
    
    def __init__(self):
        """Initialize validator with configuration rules."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all environment variables.
        
        Returns:
            Dict with validation results
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Core validations
        self._validate_core_settings()
        self._validate_database_config()
        self._validate_security_settings()
        self._validate_rate_limiting()
        self._validate_email_config()
        self._validate_cors_settings()
        
        # Summary
        is_valid = len(self.errors) == 0
        
        result = {
            "valid": is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings)
        }
        
        # Log results
        if is_valid:
            logger.info("✅ Environment configuration validation passed")
            if self.warnings:
                logger.warning(f"⚠️ {len(self.warnings)} warnings found")
                for warning in self.warnings:
                    logger.warning(f"⚠️ {warning}")
        else:
            logger.error(f"🚨 Environment validation failed with {len(self.errors)} errors")
            for error in self.errors:
                logger.error(f"🚨 {error}")
        
        return result
    
    def _validate_core_settings(self):
        """Validate core application settings."""
        # Required settings
        if not os.getenv("SECRET_KEY") or os.getenv("SECRET_KEY") == "your-secret-key-here-change-in-production":
            if os.getenv("ENVIRONMENT") == "production":
                self.errors.append("SECRET_KEY must be set to a secure value in production")
            else:
                self.warnings.append("SECRET_KEY is using default value - change for production")
        
        # App info
        app_name = os.getenv("APP_NAME", "")
        if not app_name:
            self.warnings.append("APP_NAME not set")
        
        # Debug mode check
        debug = os.getenv("DEBUG", "false").lower()
        if debug == "true" and os.getenv("ENVIRONMENT") == "production":
            self.errors.append("DEBUG should be false in production")
    
    def _validate_database_config(self):
        """Validate database configuration."""
        db_url = os.getenv("DATABASE_URL", "")
        
        if not db_url:
            self.errors.append("DATABASE_URL is required")
            return
        
        # Parse database URL
        try:
            parsed = urlparse(db_url)
            
            if not parsed.scheme:
                self.errors.append("DATABASE_URL must include scheme (postgresql+psycopg://)")
            elif not parsed.scheme.startswith("postgresql"):
                self.warnings.append("DATABASE_URL scheme should be postgresql+psycopg for best performance")
            
            if not parsed.hostname:
                self.errors.append("DATABASE_URL must include hostname")
            
            if not parsed.path or parsed.path == "/":
                self.errors.append("DATABASE_URL must include database name")
            
            if not parsed.username:
                self.errors.append("DATABASE_URL must include username")
            
            if not parsed.password:
                self.warnings.append("DATABASE_URL does not include password - ensure it's set correctly")
                
        except Exception as e:
            self.errors.append(f"DATABASE_URL format is invalid: {str(e)}")
        
        # Echo setting
        db_echo = os.getenv("DATABASE_ECHO", "false").lower()
        if db_echo == "true" and os.getenv("ENVIRONMENT") == "production":
            self.warnings.append("DATABASE_ECHO should be false in production for performance")
    
    def _validate_security_settings(self):
        """Validate security settings."""
        # JWT settings
        try:
            token_expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            if token_expire < 5:
                self.warnings.append("ACCESS_TOKEN_EXPIRE_MINUTES is very short (< 5 minutes)")
            elif token_expire > 1440:  # 24 hours
                self.warnings.append("ACCESS_TOKEN_EXPIRE_MINUTES is very long (> 24 hours)")
        except ValueError:
            self.errors.append("ACCESS_TOKEN_EXPIRE_MINUTES must be a valid integer")
        
        # HSTS settings
        try:
            hsts_age = int(os.getenv("HSTS_MAX_AGE", "31536000"))
            if hsts_age < 300 and os.getenv("ENVIRONMENT") == "production":
                self.warnings.append("HSTS_MAX_AGE is very short for production")
        except ValueError:
            self.errors.append("HSTS_MAX_AGE must be a valid integer")
    
    def _validate_rate_limiting(self):
        """Validate rate limiting configuration."""
        rate_limit_vars = [
            "AUTH_LOGIN_RATE_LIMIT",
            "AUTH_REGISTER_RATE_LIMIT",
            "AUTH_RESET_REQUEST_RATE_LIMIT",
            "AUTH_RESET_CONFIRM_RATE_LIMIT",
            "AUTH_VERIFY_TOKEN_RATE_LIMIT"
        ]
        
        for var in rate_limit_vars:
            value = os.getenv(var, "")
            if value:
                # Basic format check (number/timeunit)
                if "/" not in value:
                    self.errors.append(f"{var} must be in format 'number/timeunit' (e.g., '5/minute')")
                else:
                    try:
                        num, unit = value.split("/", 1)
                        int(num)  # Validate number
                        if unit not in ["second", "minute", "hour", "day"]:
                            self.warnings.append(f"{var} uses non-standard time unit: {unit}")
                    except ValueError:
                        self.errors.append(f"{var} has invalid number format: {value}")
    
    def _validate_email_config(self):
        """Validate email service configuration."""
        email_enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        
        if email_enabled:
            required_email_vars = ["SMTP_SERVER", "FROM_EMAIL"]
            for var in required_email_vars:
                if not os.getenv(var):
                    self.errors.append(f"{var} is required when EMAIL_ENABLED=true")
            
            # SMTP port validation
            try:
                smtp_port = int(os.getenv("SMTP_PORT", "587"))
                if smtp_port not in [25, 465, 587, 2525]:
                    self.warnings.append(f"SMTP_PORT {smtp_port} is not a standard SMTP port")
            except ValueError:
                self.errors.append("SMTP_PORT must be a valid integer")
            
            # Email format validation
            from_email = os.getenv("FROM_EMAIL", "")
            if from_email and "@" not in from_email:
                self.errors.append("FROM_EMAIL must be a valid email address")
        
        # Frontend URL validation
        frontend_url = os.getenv("FRONTEND_URL", "")
        if frontend_url:
            try:
                parsed = urlparse(frontend_url)
                if not parsed.scheme or not parsed.hostname:
                    self.errors.append("FRONTEND_URL must be a valid URL with scheme and hostname")
            except Exception:
                self.errors.append("FRONTEND_URL format is invalid")
    
    def _validate_cors_settings(self):
        """Validate CORS configuration."""
        # Allowed origins
        origins = os.getenv("ALLOWED_ORIGINS", "")
        if origins:
            origin_list = [origin.strip() for origin in origins.split(",")]
            for origin in origin_list:
                if origin and not origin.startswith("http"):
                    self.warnings.append(f"ALLOWED_ORIGINS contains non-HTTP origin: {origin}")
        
        # Allowed hosts
        hosts = os.getenv("ALLOWED_HOSTS", "")
        if not hosts:
            self.warnings.append("ALLOWED_HOSTS not set - this may cause issues in production")


# Global validator instance
env_validator = EnvironmentValidator() 