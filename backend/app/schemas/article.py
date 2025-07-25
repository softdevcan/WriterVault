"""
Article Pydantic schemas for request/response validation.
Modern Pydantic v2 implementation with comprehensive validation.
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, validator, field_validator
from pydantic.types import PositiveInt

from app.models.article import ArticleStatus
from app.models.collection import CollectionType, CollectionStatus


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
            # Remove duplicates and empty strings
            return list(set(filter(None, [tag.strip().lower() for tag in v])))
        return v
    
    @field_validator('scheduled_at')
    @classmethod
    def validate_scheduled_at(cls, v, values):
        if v is not None and 'status' in values.data:
            if values.data['status'] != ArticleStatus.SCHEDULED:
                raise ValueError('scheduled_at can only be set when status is SCHEDULED')
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
    
    @field_validator('scheduled_at')
    @classmethod
    def validate_scheduled_at(cls, v, values):
        if v is not None and values.data.get('status') != ArticleStatus.SCHEDULED:
            raise ValueError('scheduled_at can only be set when status is SCHEDULED')
        return v