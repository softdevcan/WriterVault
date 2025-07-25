"""
Category SQLAlchemy ORM Model.
Modern SQLAlchemy 2.0+ implementation with hierarchical support.
"""
import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, Integer, Boolean, DateTime, func, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base

# Configure logging
logger = logging.getLogger(__name__)


class Category(Base):
    """
    Modern SQLAlchemy 2.0+ Category ORM Model.
    
    Supports:
    - Hierarchical categories (parent/child)
    - SEO-friendly slugs
    - Category descriptions
    - Article counting
    """
    __tablename__ = "categories"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Category information
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        comment="Category name"
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="URL-friendly slug"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Category description"
    )
    
    # Hierarchical structure
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Parent category ID (for subcategories)"
    )
    
    # Display settings
    color: Mapped[Optional[str]] = mapped_column(
        String(7),  # Hex color code #FFFFFF
        nullable=True,
        comment="Category color (hex code)"
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Category icon name"
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Display order"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether category is active"
    )
    
    # Statistics
    article_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of articles in this category"
    )
    
    # SEO
    meta_description: Mapped[Optional[str]] = mapped_column(
        String(160),
        nullable=True,
        comment="SEO meta description"
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
    # parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id])
    # children: Mapped[List["Category"]] = relationship("Category", back_populates="parent")
    # articles: Mapped[List["Article"]] = relationship(back_populates="category")
    
    # Database indexes for performance
    __table_args__ = (
        Index("idx_category_parent_order", "parent_id", "order_index"),
        Index("idx_category_active_order", "is_active", "order_index"),
    )
    
    def __repr__(self) -> str:
        """String representation of Category."""
        return f"Category(id={self.id}, name='{self.name}', slug='{self.slug}')"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return self.name
    
    @property
    def is_parent(self) -> bool:
        """Check if category is a parent category."""
        return self.parent_id is None
    
    @property
    def is_child(self) -> bool:
        """Check if category is a child category."""
        return self.parent_id is not None


class Tag(Base):
    """
    Tag model for article tagging system.
    Many-to-many relationship with articles.
    """
    __tablename__ = "tags"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Tag information
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Tag name"
    )
    slug: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="URL-friendly slug"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Tag description"
    )
    
    # Statistics
    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times this tag is used"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether tag is active"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Creation timestamp"
    )
    
    # Relationships (will be defined with association table)
    # articles: Mapped[List["Article"]] = relationship(
    #     secondary="article_tags", back_populates="tags"
    # )
    
    def __repr__(self) -> str:
        """String representation of Tag."""
        return f"Tag(id={self.id}, name='{self.name}')"
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return self.name


# Association table for many-to-many relationship between articles and tags
from sqlalchemy import Table, Column, ForeignKey

article_tags = Table(
    'article_tags',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_article_tags_article', 'article_id'),
    Index('idx_article_tags_tag', 'tag_id'),
)