"""
Category Pydantic schemas for request/response validation.
Modern Pydantic v2 implementation with hierarchical support.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class CategoryBase(BaseModel):
    """Base category schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Category color (hex)")
    icon: Optional[str] = Field(None, max_length=50, description="Category icon name")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean category name."""
        if not v or not v.strip():
            raise ValueError('Category name cannot be empty')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v:
            return v.strip()
        return v


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    parent_id: Optional[int] = Field(None, description="Parent category ID for hierarchical structure")


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean category name."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Category name cannot be empty')
            return v.strip()
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean description."""
        if v:
            return v.strip()
        return v


class CategoryResponse(CategoryBase):
    """Schema for category responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    slug: str
    parent_id: Optional[int] = None
    is_active: bool = True
    article_count: int = Field(0, description="Number of articles in this category")
    created_at: datetime
    updated_at: Optional[datetime] = None


class CategoryWithChildren(CategoryResponse):
    """Schema for category with children categories."""
    children: List['CategoryResponse'] = Field(default_factory=list)
    total_articles_including_children: int = Field(0, description="Total articles including subcategories")


class CategoryWithParent(CategoryResponse):
    """Schema for category with parent information."""
    parent: Optional[CategoryResponse] = None


class CategoryTree(CategoryResponse):
    """Schema for hierarchical category tree."""
    children: List['CategoryTree'] = Field(default_factory=list)
    level: int = Field(0, description="Hierarchy level (0 for root)")
    path: str = Field("", description="Full category path")


class CategoryStats(BaseModel):
    """Schema for category statistics."""
    total_categories: int = 0
    active_categories: int = 0
    root_categories: int = 0  # Categories without parent
    max_depth: int = 0
    most_used_category: Optional[CategoryResponse] = None
    categories_with_articles: int = 0


class CategoryListParams(BaseModel):
    """Schema for category list query parameters."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(50, ge=1, le=100, description="Number of records to return")
    parent_id: Optional[int] = Field(None, description="Filter by parent category")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search in name and description")
    include_children: bool = Field(False, description="Include children in response")
    
    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean search query."""
        if v:
            return v.strip()
        return v


class CategoryBulkUpdate(BaseModel):
    """Schema for bulk category operations."""
    category_ids: List[int] = Field(..., min_length=1, max_length=50)
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None


class CategoryMoveRequest(BaseModel):
    """Schema for moving category to different parent."""
    new_parent_id: Optional[int] = Field(None, description="New parent category ID (null for root)")


# For forward reference resolution
CategoryWithChildren.model_rebuild()
CategoryTree.model_rebuild()