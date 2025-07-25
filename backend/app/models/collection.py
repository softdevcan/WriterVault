"""
Collection SQLAlchemy ORM Model.
Modern SQLAlchemy 2.0+ implementation for article series and books.
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


class CollectionType(str, Enum):
    """Collection type enum."""
    SERIES = "series"          # Article series (10 part tutorial, etc.)
    BOOK = "book"             # Book with chapters
    ANTHOLOGY = "anthology"    # Collection of related articles
    COURSE = "course"         # Educational course with lessons


class CollectionStatus(str, Enum):
    """Collection publication status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    COMPLETED = "completed"    # All articles/chapters published
    ARCHIVED = "archived"


class Collection(Base):
    """
    Modern SQLAlchemy 2.0+ Collection ORM Model.
    
    Represents:
    - Article series (tutorials, guides)
    - Books with chapters
    - Anthologies
    - Educational courses
    """
    __tablename__ = "collections"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Basic information
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Collection title"
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="URL-friendly slug"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Collection description"
    )
    
    # Collection type and metadata
    type: Mapped[CollectionType] = mapped_column(
        String(20),
        default=CollectionType.SERIES,
        nullable=False,
        index=True,
        comment="Collection type (series, book, anthology, course)"
    )
    cover_image: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="Cover image URL"
    )
    
    # Author and ownership
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Collection author ID"
    )
    
    # Publication status
    status: Mapped[CollectionStatus] = mapped_column(
        String(20),
        default=CollectionStatus.DRAFT,
        nullable=False,
        index=True,
        comment="Collection status"
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether collection is featured"
    )
    
    # Collection settings
    allow_comments: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether comments are allowed on collection"
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether collection is publicly visible"
    )
    
    # Pricing (for future premium content)
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether collection requires payment"
    )
    price: Mapped[Optional[int]] = mapped_column(
        Integer,  # Price in cents/kuruş
        nullable=True,
        comment="Price in cents (for premium collections)"
    )
    
    # Statistics
    article_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of articles in collection"
    )
    published_article_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of published articles"
    )
    total_reading_time: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total estimated reading time in minutes"
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total view count"
    )
    subscriber_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of subscribers (future feature)"
    )
    
    # SEO
    meta_description: Mapped[Optional[str]] = mapped_column(
        String(160),
        nullable=True,
        comment="SEO meta description"
    )
    meta_keywords: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="SEO keywords"
    )
    
    # Publishing dates
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Publication timestamp"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Completion timestamp"
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
    # author: Mapped["User"] = relationship(back_populates="collections")
    # articles: Mapped[List["Article"]] = relationship(
    #     back_populates="collection",
    #     order_by="Article.order_in_collection"
    # )
    
    # Database indexes for performance
    __table_args__ = (
        Index("idx_collection_author_status", "author_id", "status"),
        Index("idx_collection_type_status", "type", "status"),
        Index("idx_collection_published", "published_at", "status"),
    )
    
    def __repr__(self) -> str:
        """String representation of Collection."""
        return f"Collection(id={self.id}, title='{self.title}', type='{self.type}')"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.title} ({self.type})"
    
    @property
    def is_published(self) -> bool:
        """Check if collection is published."""
        return self.status in [CollectionStatus.PUBLISHED, CollectionStatus.COMPLETED]
    
    @property
    def is_completed(self) -> bool:
        """Check if collection is completed."""
        return self.status == CollectionStatus.COMPLETED
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage based on published articles."""
        if self.article_count == 0:
            return 0.0
        return (self.published_article_count / self.article_count) * 100