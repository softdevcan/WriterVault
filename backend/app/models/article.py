"""
Article SQLAlchemy ORM Model.
Modern SQLAlchemy 2.0+ implementation with PostgreSQL support.
Supports standalone articles, series, and book chapters.
"""
import logging
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Text, Integer, Boolean, DateTime, func, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base

# Configure logging
logger = logging.getLogger(__name__)


class ArticleStatus(str, Enum):
    """Article publication status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"


class Article(Base):
    """
    Modern SQLAlchemy 2.0+ Article ORM Model.
    
    Supports:
    - Standalone articles
    - Articles in collections (series/books)
    - Rich content with metadata
    - SEO optimization
    - Publishing workflow
    """
    __tablename__ = "articles"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Content fields
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Article title"
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="URL-friendly slug (auto-generated from title)"
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Article summary/excerpt (max 500 chars)"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Main article content (Markdown or HTML)"
    )
    
    # SEO and metadata
    meta_description: Mapped[Optional[str]] = mapped_column(
        String(160),
        nullable=True,
        comment="SEO meta description (max 160 chars)"
    )
    meta_keywords: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="SEO keywords (comma-separated)"
    )
    reading_time: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Estimated reading time in minutes"
    )
    
    # Relationships
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Author user ID"
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Article category ID"
    )
    collection_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("collections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Collection ID (for series/books)"
    )
    
    # Collection ordering (for series/books)
    order_in_collection: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Order within collection (1, 2, 3...)"
    )
    
    # Publication status and workflow
    status: Mapped[ArticleStatus] = mapped_column(
        String(20),
        default=ArticleStatus.DRAFT,
        nullable=False,
        index=True,
        comment="Publication status"
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether article is featured"
    )
    allow_comments: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether comments are allowed"
    )
    
    # Publishing dates
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Publication timestamp"
    )
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled publication time"
    )
    
    # Statistics (will be updated by triggers or background jobs)
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total view count"
    )
    like_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total like count"
    )
    comment_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total comment count"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Creation timestamp"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        comment="Last update timestamp"
    )
    
    # Relationships (will be defined when other models are created)
    # author: Mapped["User"] = relationship(back_populates="articles")
    # category: Mapped[Optional["Category"]] = relationship(back_populates="articles")
    # collection: Mapped[Optional["Collection"]] = relationship(back_populates="articles")
    # comments: Mapped[List["Comment"]] = relationship(back_populates="article")
    # tags: Mapped[List["Tag"]] = relationship(secondary="article_tags", back_populates="articles")
    
    # Database indexes for performance
    __table_args__ = (
        Index("idx_article_author_status", "author_id", "status"),
        Index("idx_article_published", "published_at", "status"),
        Index("idx_article_collection_order", "collection_id", "order_in_collection"),
    )
    
    def __repr__(self) -> str:
        """String representation of Article."""
        return f"Article(id={self.id}, title='{self.title}', status='{self.status}')"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.title} ({self.status})"
    
    @property
    def is_published(self) -> bool:
        """Check if article is published."""
        return self.status == ArticleStatus.PUBLISHED and self.published_at is not None
    
    @property
    def is_draft(self) -> bool:
        """Check if article is draft."""
        return self.status == ArticleStatus.DRAFT
    
    @property
    def is_in_collection(self) -> bool:
        """Check if article is part of a collection."""
        return self.collection_id is not None