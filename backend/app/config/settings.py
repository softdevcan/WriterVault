"""
Application settings with environment variable loading.
Secure approach using os.getenv() - no hardcoded secrets.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # =============================================================================
        # DATABASE CONFIGURATION
        # =============================================================================
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        self.AUTO_INIT_DB = os.getenv("AUTO_INIT_DB", "false").lower() == "true"
        
        # =============================================================================
        # SERVER CONFIGURATION
        # =============================================================================
        self.HOST = os.getenv("HOST", "127.0.0.1")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.WORKERS = int(os.getenv("WORKERS", "1"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
        
        # =============================================================================
        # APPLICATION SETTINGS
        # =============================================================================
        self.APP_NAME = os.getenv("APP_NAME", "Writers Platform API")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A modern writing platform API")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        
        # =============================================================================
        # SECURITY SETTINGS (NO DEFAULTS!)
        # =============================================================================
        self.SECRET_KEY = os.getenv("SECRET_KEY")  # Must be in .env
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Validate required security settings
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in environment variables")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in environment variables")
        
        # =============================================================================
        # CORS & HOST SECURITY
        # =============================================================================
        self.ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
        self.ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
        self.ALLOWED_METHODS = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS")
        self.HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "31536000"))
        self.CSP_DEVELOPMENT = os.getenv("CSP_DEVELOPMENT", "")
        self.CSP_PRODUCTION = os.getenv("CSP_PRODUCTION", "")
        
        # =============================================================================
        # RATE LIMITING
        # =============================================================================
        self.ROOT_RATE_LIMIT = os.getenv("ROOT_RATE_LIMIT", "100/minute")
        self.HEALTH_RATE_LIMIT = os.getenv("HEALTH_RATE_LIMIT", "60/minute")
        
        # Auth Rate Limits
        self.AUTH_LOGIN_RATE_LIMIT = os.getenv("AUTH_LOGIN_RATE_LIMIT", "5/minute")
        self.AUTH_REGISTER_RATE_LIMIT = os.getenv("AUTH_REGISTER_RATE_LIMIT", "3/minute")
        self.AUTH_LOGOUT_RATE_LIMIT = os.getenv("AUTH_LOGOUT_RATE_LIMIT", "10/minute")
        self.AUTH_ME_RATE_LIMIT = os.getenv("AUTH_ME_RATE_LIMIT", "30/minute")
        self.AUTH_REFRESH_RATE_LIMIT = os.getenv("AUTH_REFRESH_RATE_LIMIT", "10/minute")
        self.AUTH_RESET_REQUEST_RATE_LIMIT = os.getenv("AUTH_RESET_REQUEST_RATE_LIMIT", "3/hour")
        self.AUTH_RESET_CONFIRM_RATE_LIMIT = os.getenv("AUTH_RESET_CONFIRM_RATE_LIMIT", "5/hour")
        self.AUTH_VERIFY_TOKEN_RATE_LIMIT = os.getenv("AUTH_VERIFY_TOKEN_RATE_LIMIT", "10/hour")
        
        # Admin Rate Limits
        self.ADMIN_STATS_RATE_LIMIT = os.getenv("ADMIN_STATS_RATE_LIMIT", "30/minute")
        self.ADMIN_INIT_RATE_LIMIT = os.getenv("ADMIN_INIT_RATE_LIMIT", "5/hour")
        self.ADMIN_RESET_RATE_LIMIT = os.getenv("ADMIN_RESET_RATE_LIMIT", "1/hour")
        self.ADMIN_HEALTH_RATE_LIMIT = os.getenv("ADMIN_HEALTH_RATE_LIMIT", "60/minute")
        
        # =============================================================================
        # ARTICLE SYSTEM RATE LIMITING
        # =============================================================================
        
        # Article API Rate Limits
        self.ARTICLE_CREATE_RATE_LIMIT = os.getenv("ARTICLE_CREATE_RATE_LIMIT", "10/minute")
        self.ARTICLE_UPDATE_RATE_LIMIT = os.getenv("ARTICLE_UPDATE_RATE_LIMIT", "20/minute")
        self.ARTICLE_DELETE_RATE_LIMIT = os.getenv("ARTICLE_DELETE_RATE_LIMIT", "5/minute")
        self.ARTICLE_LIST_RATE_LIMIT = os.getenv("ARTICLE_LIST_RATE_LIMIT", "60/minute")
        self.ARTICLE_DETAIL_RATE_LIMIT = os.getenv("ARTICLE_DETAIL_RATE_LIMIT", "120/minute")
        self.ARTICLE_PUBLISH_RATE_LIMIT = os.getenv("ARTICLE_PUBLISH_RATE_LIMIT", "10/minute")
        
        # Collection API Rate Limits
        self.COLLECTION_CREATE_RATE_LIMIT = os.getenv("COLLECTION_CREATE_RATE_LIMIT", "5/minute")
        self.COLLECTION_UPDATE_RATE_LIMIT = os.getenv("COLLECTION_UPDATE_RATE_LIMIT", "10/minute")
        self.COLLECTION_DELETE_RATE_LIMIT = os.getenv("COLLECTION_DELETE_RATE_LIMIT", "3/minute")
        self.COLLECTION_LIST_RATE_LIMIT = os.getenv("COLLECTION_LIST_RATE_LIMIT", "60/minute")
        self.COLLECTION_DETAIL_RATE_LIMIT = os.getenv("COLLECTION_DETAIL_RATE_LIMIT", "100/minute")
        
        # Category API Rate Limits
        self.CATEGORY_CREATE_RATE_LIMIT = os.getenv("CATEGORY_CREATE_RATE_LIMIT", "10/minute")
        self.CATEGORY_UPDATE_RATE_LIMIT = os.getenv("CATEGORY_UPDATE_RATE_LIMIT", "20/minute")
        self.CATEGORY_DELETE_RATE_LIMIT = os.getenv("CATEGORY_DELETE_RATE_LIMIT", "10/minute")
        self.CATEGORY_LIST_RATE_LIMIT = os.getenv("CATEGORY_LIST_RATE_LIMIT", "100/minute")
        self.CATEGORY_TREE_RATE_LIMIT = os.getenv("CATEGORY_TREE_RATE_LIMIT", "60/minute")
        self.CATEGORY_STATS_RATE_LIMIT = os.getenv("CATEGORY_STATS_RATE_LIMIT", "30/minute")
        self.CATEGORY_MOVE_RATE_LIMIT = os.getenv("CATEGORY_MOVE_RATE_LIMIT", "20/minute")
        self.CATEGORY_BULK_UPDATE_RATE_LIMIT = os.getenv("CATEGORY_BULK_UPDATE_RATE_LIMIT", "5/minute")
        
        # =============================================================================
        # CONTENT SETTINGS
        # =============================================================================
        
        # Article Content Limits
        self.MAX_ARTICLE_TITLE_LENGTH = int(os.getenv("MAX_ARTICLE_TITLE_LENGTH", "200"))
        self.MAX_ARTICLE_CONTENT_LENGTH = int(os.getenv("MAX_ARTICLE_CONTENT_LENGTH", "100000"))
        self.MAX_ARTICLE_SUMMARY_LENGTH = int(os.getenv("MAX_ARTICLE_SUMMARY_LENGTH", "500"))
        self.MAX_ARTICLE_SLUG_LENGTH = int(os.getenv("MAX_ARTICLE_SLUG_LENGTH", "100"))
        
        # Collection Content Limits
        self.MAX_COLLECTION_TITLE_LENGTH = int(os.getenv("MAX_COLLECTION_TITLE_LENGTH", "200"))
        self.MAX_COLLECTION_DESCRIPTION_LENGTH = int(os.getenv("MAX_COLLECTION_DESCRIPTION_LENGTH", "1000"))
        
        # Category Content Limits
        self.MAX_CATEGORY_NAME_LENGTH = int(os.getenv("MAX_CATEGORY_NAME_LENGTH", "100"))
        self.MAX_CATEGORY_DESCRIPTION_LENGTH = int(os.getenv("MAX_CATEGORY_DESCRIPTION_LENGTH", "500"))
        
        # =============================================================================
        # PAGINATION DEFAULTS
        # =============================================================================
        self.DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
        self.MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))
        self.ARTICLES_PER_PAGE = int(os.getenv("ARTICLES_PER_PAGE", "10"))
        self.COLLECTIONS_PER_PAGE = int(os.getenv("COLLECTIONS_PER_PAGE", "12"))
        self.CATEGORIES_PER_PAGE = int(os.getenv("CATEGORIES_PER_PAGE", "50"))
        
        # =============================================================================
        # FILE UPLOAD SETTINGS
        # =============================================================================
        self.UPLOAD_ENABLED = os.getenv("UPLOAD_ENABLED", "false").lower() == "true"
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
        self.ALLOWED_IMAGE_TYPES = os.getenv("ALLOWED_IMAGE_TYPES", "jpg,jpeg,png,gif,webp")
        self.ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "pdf,doc,docx,txt")
        
        # Image Processing
        self.IMAGE_RESIZE_ENABLED = os.getenv("IMAGE_RESIZE_ENABLED", "false").lower() == "true"
        self.MAX_IMAGE_WIDTH = int(os.getenv("MAX_IMAGE_WIDTH", "1920"))
        self.MAX_IMAGE_HEIGHT = int(os.getenv("MAX_IMAGE_HEIGHT", "1080"))
        self.THUMBNAIL_SIZE = int(os.getenv("THUMBNAIL_SIZE", "300"))
        
        # CDN Settings
        self.CDN_ENABLED = os.getenv("CDN_ENABLED", "false").lower() == "true"
        self.CDN_BASE_URL = os.getenv("CDN_BASE_URL", "")
        self.CDN_BUCKET = os.getenv("CDN_BUCKET", "")
        
        # =============================================================================
        # SEARCH & INDEXING
        # =============================================================================
        self.SEARCH_ENABLED = os.getenv("SEARCH_ENABLED", "false").lower() == "true"
        self.ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "")
        self.SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME", "writervault")
        self.ENABLE_FULLTEXT_SEARCH = os.getenv("ENABLE_FULLTEXT_SEARCH", "true").lower() == "true"
        self.MIN_SEARCH_LENGTH = int(os.getenv("MIN_SEARCH_LENGTH", "3"))
        self.MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "50"))
        
        # =============================================================================
        # CONTENT PROCESSING
        # =============================================================================
        self.MARKDOWN_ENABLED = os.getenv("MARKDOWN_ENABLED", "true").lower() == "true"
        self.HTML_SANITIZE = os.getenv("HTML_SANITIZE", "true").lower() == "true"
        self.AUTO_EXCERPT = os.getenv("AUTO_EXCERPT", "true").lower() == "true"
        self.EXCERPT_LENGTH = int(os.getenv("EXCERPT_LENGTH", "150"))
        self.AUTO_META_DESCRIPTION = os.getenv("AUTO_META_DESCRIPTION", "true").lower() == "true"
        self.META_DESCRIPTION_LENGTH = int(os.getenv("META_DESCRIPTION_LENGTH", "160"))
        self.AUTO_SITEMAP = os.getenv("AUTO_SITEMAP", "false").lower() == "true"
        
        # =============================================================================
        # CACHING
        # =============================================================================
        self.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").lower() == "true"
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
        self.ARTICLE_CACHE_TTL = int(os.getenv("ARTICLE_CACHE_TTL", "1800"))
        
        # =============================================================================
        # CONTENT MODERATION
        # =============================================================================
        self.CONTENT_MODERATION = os.getenv("CONTENT_MODERATION", "false").lower() == "true"
        self.AUTO_PUBLISH = os.getenv("AUTO_PUBLISH", "true").lower() == "true"
        self.REQUIRE_APPROVAL = os.getenv("REQUIRE_APPROVAL", "false").lower() == "true"
        self.SPAM_DETECTION = os.getenv("SPAM_DETECTION", "false").lower() == "true"
        
        # =============================================================================
        # ANALYTICS & TRACKING
        # =============================================================================
        self.ANALYTICS_ENABLED = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
        self.TRACK_PAGE_VIEWS = os.getenv("TRACK_PAGE_VIEWS", "true").lower() == "true"
        self.TRACK_USER_ACTIONS = os.getenv("TRACK_USER_ACTIONS", "false").lower() == "true"
        self.GOOGLE_ANALYTICS_ID = os.getenv("GOOGLE_ANALYTICS_ID", "")
        
        # =============================================================================
        # EMAIL SERVICE (NO CREDENTIALS IN CODE!)
        # =============================================================================
        self.EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        self.SMTP_SERVER = os.getenv("SMTP_SERVER", "")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")  # Must be in .env
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Must be in .env
        self.FROM_EMAIL = os.getenv("FROM_EMAIL", "")
        self.FROM_NAME = os.getenv("FROM_NAME", "WriterVault")
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # =============================================================================
        # DEMO USER SETTINGS
        # =============================================================================
        self.DEMO_USERNAME = os.getenv("DEMO_USERNAME", "demo_user")
        self.DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@example.com")
        self.DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "demo123")
        self.DEMO_FULL_NAME = os.getenv("DEMO_FULL_NAME", "Demo User")


# Global settings instance
settings = Settings()