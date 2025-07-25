"""
Article Pydantic schemas for request/response validation.
Central schema facade - imports and re-exports all schemas for API compatibility.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.types import PositiveInt

from app.models.article import ArticleStatus

# ============================================================================
# IMPORT ALL SCHEMAS FROM OTHER MODULES
# ============================================================================

# User schemas
from app.schemas.user import (
    UserResponse, UserProfile, UserCreate, UserUpdate, 
    UserListResponse, UserStats, AuthorProfile, UserPasswordUpdate
)

# Category and Tag schemas  
from app.schemas.category import (
    CategoryResponse, CategoryCreate, CategoryUpdate, CategoryWithChildren,
    CategoryWithParent, CategoryTree, CategoryStats, CategoryListParams,
    TagResponse, TagCreate, TagUpdate, TagStats, TagListParams
)

# Collection schemas - only basic ones (no circular dependency)
from app.schemas.collection import (
    CollectionResponse, CollectionSummary, CollectionCreate, CollectionUpdate, 
    CollectionWithAuthor, CollectionStats, CollectionListParams
)

# ============================================================================
# ARTICLE-SPECIFIC SCHEMAS
# ============================================================================

class ArticleFilter(BaseModel):
    """Schema for filtering articles."""
    status: Optional[ArticleStatus] = None
    category_id: Optional[PositiveInt] = None
    collection_id: Optional[PositiveInt] = None
    author_id: Optional[PositiveInt] = None
    is_featured: Optional[bool] = None
    search: Optional[str] = Field(None, min_length=2, max_length=100)
    tag: Optional[str] = Field(None, min_length=1, max_length=50)
    sort_by: str = Field("created_at", pattern="^(created_at|published_at|updated_at|title|view_count)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class ArticleBase(BaseModel):
    """Base article schema with common fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Article title")
    summary: Optional[str] = Field(None, max_length=500, description="Article summary")
    content: str = Field(..., min_length=1, description="Article content")
    meta_description: Optional[str] = Field(None, max_length=160, description="SEO meta description")
    meta_keywords: Optional[str] = Field(None, max_length=255, description="SEO keywords")
    category_id: Optional[PositiveInt] = Field(None, description="Category ID")
    collection_id: Optional[PositiveInt] = Field(None, description="Collection ID")
    order_in_collection: Optional[PositiveInt] = Field(None, description="Order in collection")
    allow_comments: bool = Field(True, description="Allow comments on article")
    is_featured: bool = Field(False, description="Featured article")


class ArticleCreate(ArticleBase):
    """Schema for creating a new article."""
    status: ArticleStatus = Field(ArticleStatus.DRAFT, description="Article status")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publication time")
    tag_names: Optional[List[str]] = Field(None, description="List of tag names")
    
    @field_validator('tag_names')
    @classmethod
    def validate_tag_names(cls, v):
        if v is not None:
            return list(set(filter(None, [tag.strip().lower() for tag in v])))
        return v


class ArticleUpdate(BaseModel):
    """Schema for updating an existing article."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = Field(None, max_length=255)
    category_id: Optional[PositiveInt] = None
    collection_id: Optional[PositiveInt] = None
    order_in_collection: Optional[PositiveInt] = None
    status: Optional[ArticleStatus] = None
    allow_comments: Optional[bool] = None
    is_featured: Optional[bool] = None
    scheduled_at: Optional[datetime] = None
    tag_names: Optional[List[str]] = None
    
    @field_validator('tag_names')
    @classmethod
    def validate_tag_names(cls, v):
        if v is not None:
            return list(set(filter(None, [tag.strip().lower() for tag in v])))
        return v


class ArticleStatusUpdate(BaseModel):
    """Schema for updating article status only."""
    status: ArticleStatus = Field(..., description="New article status")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled publication time")


class ArticleResponse(BaseModel):
    """Complete article response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    content: str
    meta_description: Optional[str] = None
    reading_time: Optional[int] = None
    status: ArticleStatus
    is_featured: bool
    allow_comments: bool
    order_in_collection: Optional[int] = None
    
    # Statistics
    view_count: int
    like_count: int
    comment_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # Related objects
    author: UserResponse
    category: Optional[CategoryResponse] = None
    collection: Optional[CollectionSummary] = None
    tags: List[TagResponse] = []


class ArticleListResponse(BaseModel):
    """Article list item response (without full content)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    status: ArticleStatus
    is_featured: bool
    reading_time: Optional[int] = None
    order_in_collection: Optional[int] = None
    
    # Statistics
    view_count: int
    like_count: int
    comment_count: int
    
    # Timestamps
    created_at: datetime
    published_at: Optional[datetime] = None
    
    # Related objects
    author: UserResponse
    category: Optional[CategoryResponse] = None
    collection: Optional[CollectionSummary] = None
    tags: List[TagResponse] = []


class ArticleStatsResponse(BaseModel):
    """Article statistics response."""
    total_articles: int
    published_articles: int
    draft_articles: int
    total_views: int
    total_likes: int
    total_comments: int
    featured_articles: int


class PaginatedArticleResponse(BaseModel):
    """Paginated article response."""
    articles: List[ArticleListResponse]
    total: int
    page: int
    size: int
    total_pages: int


# ============================================================================
# LEGACY ALIASES FOR API COMPATIBILITY
# ============================================================================

# Backward compatibility aliases
PaginatedResponse = PaginatedArticleResponse
ArticleStats = ArticleStatsResponse

# ============================================================================
# ALL EXPORTS FOR API FILES
# ============================================================================

__all__ = [
    # Article schemas
    'ArticleCreate', 'ArticleUpdate', 'ArticleResponse', 'ArticleListResponse',
    'ArticleStatusUpdate', 'ArticleFilter', 'ArticleStatsResponse', 'ArticleStats',
    'PaginatedArticleResponse', 'PaginatedResponse',
    
    # User schemas
    'UserResponse', 'UserProfile', 'UserCreate', 'UserUpdate', 
    'UserListResponse', 'UserStats', 'AuthorProfile', 'UserPasswordUpdate',
    
    # Category schemas
    'CategoryResponse', 'CategoryCreate', 'CategoryUpdate', 'CategoryWithChildren',
    'CategoryWithParent', 'CategoryTree', 'CategoryStats', 'CategoryListParams',
    
    # Tag schemas
    'TagResponse', 'TagCreate', 'TagUpdate', 'TagStats', 'TagListParams',
    
    # Collection schemas - basic only (no circular dependency)
    'CollectionResponse', 'CollectionSummary', 'CollectionCreate', 'CollectionUpdate', 
    'CollectionWithAuthor', 'CollectionStats', 'CollectionListParams'
]