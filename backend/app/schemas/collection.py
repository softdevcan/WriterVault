"""
Collection Pydantic schemas for request/response validation.
Modern Pydantic v2 implementation for article series and books.
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.schemas.user import UserResponse


class CollectionType(str, Enum):
    """Collection type enumeration."""
    SERIES = "series"
    BOOK = "book"


class CollectionStatus(str, Enum):
    """Collection status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CollectionBase(BaseModel):
    """Base collection schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Collection title")
    description: Optional[str] = Field(None, max_length=1000, description="Collection description")
    type: CollectionType = Field(..., description="Collection type (series or book)")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean title."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v:
            return v.strip()
        return v


class CollectionCreate(CollectionBase):
    """Schema for creating a new collection."""
    pass


class CollectionUpdate(BaseModel):
    """Schema for updating an existing collection."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    type: Optional[CollectionType] = None
    status: Optional[CollectionStatus] = None
    cover_image: Optional[str] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean title."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Title cannot be empty')
            return v.strip()
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v:
            return v.strip()
        return v


class CollectionResponse(CollectionBase):
    """Schema for collection responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    slug: str
    status: CollectionStatus
    author_id: int
    article_count: int = Field(0, description="Number of articles in collection")
    total_views: int = Field(0, description="Total views across all articles")
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None


class CollectionWithAuthor(CollectionResponse):
    """Schema for collection with author information."""
    author: UserResponse


class CollectionWithArticles(CollectionWithAuthor):
    """Schema for collection with articles included."""
    # Import here to avoid circular imports
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from app.schemas.article import ArticleResponse
    
    articles: List['ArticleResponse'] = Field(default_factory=list)


class CollectionStats(BaseModel):
    """Schema for collection statistics."""
    total_collections: int = 0
    published_collections: int = 0
    draft_collections: int = 0
    series_count: int = 0
    book_count: int = 0
    total_articles_in_collections: int = 0
    avg_articles_per_collection: float = 0.0


class CollectionListParams(BaseModel):
    """Schema for collection list query parameters."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of records to return")
    status: Optional[CollectionStatus] = Field(None, description="Filter by status")
    type: Optional[CollectionType] = Field(None, description="Filter by type")
    author_id: Optional[int] = Field(None, description="Filter by author")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search in title and description")
    
    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean search query."""
        if v:
            return v.strip()
        return v


class CollectionArticleOrder(BaseModel):
    """Schema for updating article order in collection."""
    article_id: int
    order: int = Field(..., ge=1, description="Article order in collection (1-based)")


class CollectionReorderRequest(BaseModel):
    """Schema for reordering articles in a collection."""
    articles: List[CollectionArticleOrder] = Field(..., min_length=1)
    
    @field_validator('articles')
    @classmethod
    def validate_unique_orders(cls, v: List[CollectionArticleOrder]) -> List[CollectionArticleOrder]:
        """Validate that orders are unique."""
        orders = [article.order for article in v]
        article_ids = [article.article_id for article in v]
        
        if len(set(orders)) != len(orders):
            raise ValueError('Article orders must be unique')
        
        if len(set(article_ids)) != len(article_ids):
            raise ValueError('Article IDs must be unique')
        
        return v


# For forward reference resolution
CollectionWithArticles.model_rebuild()