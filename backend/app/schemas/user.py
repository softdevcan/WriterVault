"""
User Pydantic schemas for request/response validation.
Modern Pydantic v2 implementation with comprehensive user management.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr


# ============================================================================
# USER CRUD SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$', description="Username (alphanumeric and underscore only)")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate and clean username."""
        v = v.strip().lower()
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean full name."""
        if v:
            return v.strip()
        return v


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one digit, one letter
        has_digit = any(c.isdigit() for c in v)
        has_letter = any(c.isalpha() for c in v)
        
        if not (has_digit and has_letter):
            raise ValueError('Password must contain at least one letter and one digit')
        
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = Field(None, max_length=255, description="Profile avatar URL")
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean full name."""
        if v:
            return v.strip()
        return v
    
    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean bio."""
        if v:
            return v.strip()
        return v


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_digit = any(c.isdigit() for c in v)
        has_letter = any(c.isalpha() for c in v)
        
        if not (has_digit and has_letter):
            raise ValueError('Password must contain at least one letter and one digit')
        
        return v


class UserAdminUpdate(BaseModel):
    """Schema for admin user updates."""
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_admin: Optional[bool] = None
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class UserResponse(BaseModel):
    """Basic user response schema for article relations."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfile(BaseModel):
    """Complete user profile response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Statistics (can be computed)
    article_count: int = Field(0, description="Number of articles written")
    total_views: int = Field(0, description="Total views across all articles")
    total_likes: int = Field(0, description="Total likes across all articles")


class UserListResponse(BaseModel):
    """User list item response for admin panel."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    
    # Quick stats
    article_count: int = Field(0, description="Number of articles")
    last_login: Optional[datetime] = Field(None, description="Last login time")


class UserStats(BaseModel):
    """User statistics response."""
    total_users: int = 0
    active_users: int = 0
    verified_users: int = 0
    admin_users: int = 0
    users_registered_this_month: int = 0
    most_active_writers: List[UserResponse] = Field(default_factory=list)


# ============================================================================
# QUERY AND FILTER SCHEMAS
# ============================================================================

class UserListParams(BaseModel):
    """Schema for user list query parameters."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of records to return")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_verified: Optional[bool] = Field(None, description="Filter by verified status")
    is_admin: Optional[bool] = Field(None, description="Filter by admin status")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search in username, email, or full name")
    sort_by: str = Field("created_at", pattern="^(username|email|created_at|article_count)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    
    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean search query."""
        if v:
            return v.strip()
        return v


class UserBulkUpdate(BaseModel):
    """Schema for bulk user operations."""
    user_ids: List[int] = Field(..., min_length=1, max_length=50)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


# ============================================================================
# EMAIL AND VERIFICATION SCHEMAS
# ============================================================================

class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""
    email: EmailStr = Field(..., description="Email to verify")


class EmailVerificationConfirm(BaseModel):
    """Schema for email verification confirmation."""
    token: str = Field(..., description="Verification token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="Email for password reset")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_digit = any(c.isdigit() for c in v)
        has_letter = any(c.isalpha() for c in v)
        
        if not (has_digit and has_letter):
            raise ValueError('Password must contain at least one letter and one digit')
        
        return v


# ============================================================================
# AUTHOR SPECIFIC SCHEMAS
# ============================================================================

class AuthorProfile(BaseModel):
    """Author profile with writing statistics."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    
    # Writing statistics
    total_articles: int = 0
    published_articles: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    
    # Recent activity
    last_article_published: Optional[datetime] = None
    avg_articles_per_month: float = 0.0


class AuthorStats(BaseModel):
    """Detailed author statistics."""
    writing_streak_days: int = 0
    most_popular_article_title: Optional[str] = None
    most_popular_article_views: int = 0
    favorite_categories: List[str] = Field(default_factory=list)
    total_words_written: int = 0
    avg_reading_time: float = 0.0