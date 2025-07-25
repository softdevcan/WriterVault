"""
Article Service for business logic operations.
Handles article-related business logic and validation.
"""
from typing import Optional, List, Tuple
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.article import Article, ArticleStatus
from app.models.user import User
from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleFilter, 
    ArticleResponse, ArticleListResponse, PaginatedResponse
)
from app.repositories.article_repository import article_repository
from app.repositories.user_repository import user_repository
from app.core.exceptions import NotFoundError, PermissionError, ValidationError

# Configure logging
logger = logging.getLogger(__name__)


class ArticleService:
    """
    Service class for article-related business logic.
    Handles validation, permissions, and business rules.
    """
    
    def __init__(self):
        self.article_repo = article_repository
        self.user_repo = user_repository
    
    def create_article(
        self, 
        db: Session, 
        article_data: ArticleCreate, 
        author: User
    ) -> ArticleResponse:
        """
        Create a new article with business logic validation.
        
        Args:
            db: Database session
            article_data: Article creation data
            author: Author user object
            
        Returns:
            Created article response
            
        Raises:
            ValidationError: If data validation fails
            PermissionError: If user lacks permissions
        """
        try:
            # Validate author is active
            if not author.is_active:
                raise PermissionError("Inactive users cannot create articles")
            
            # Validate collection ownership if specified
            if article_data.collection_id:
                self._validate_collection_ownership(db, article_data.collection_id, author.id)
            
            # Generate unique slug
            slug = self._generate_unique_slug(db, article_data.title)
            
            # Create article
            article = self.article_repo.create(db, article_data, author.id, slug)
            
            if not article:
                raise ValidationError("Failed to create article")
            
            logger.info(f"Article created successfully: {article.title} by {author.username}")
            return self._convert_to_response(article)
            
        except (ValidationError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"Error creating article: {str(e)}")
            raise ValidationError("Article creation failed")
    
    def get_article_by_id(
        self, 
        db: Session, 
        article_id: int, 
        current_user: Optional[User] = None
    ) -> ArticleResponse:
        """
        Get article by ID with permission checks.
        
        Args:
            db: Database session
            article_id: Article ID
            current_user: Current authenticated user (optional)
            
        Returns:
            Article response
            
        Raises:
            NotFoundError: If article not found
            PermissionError: If user lacks permissions
        """
        article = self.article_repo.get_by_id(db, article_id)
        
        if not article:
            raise NotFoundError("Article not found")
        
        # Check permissions
        self._check_article_access_permission(article, current_user)
        
        # Increment view count for published articles (excluding author views)
        if (article.status == ArticleStatus.PUBLISHED and 
            current_user and current_user.id != article.author_id):
            self.article_repo.increment_view_count(db, article)
        
        return self._convert_to_response(article)
    
    def get_article_by_slug(
        self, 
        db: Session, 
        slug: str, 
        current_user: Optional[User] = None
    ) -> ArticleResponse:
        """
        Get article by slug with permission checks.
        
        Args:
            db: Database session
            slug: Article slug
            current_user: Current authenticated user (optional)
            
        Returns:
            Article response
            
        Raises:
            NotFoundError: If article not found
            PermissionError: If user lacks permissions
        """
        article = self.article_repo.get_by_slug(db, slug)
        
        if not article:
            raise NotFoundError("Article not found")
        
        # Check permissions
        self._check_article_access_permission(article, current_user)
        
        # Increment view count for published articles (excluding author views)
        if (article.status == ArticleStatus.PUBLISHED and 
            current_user and current_user.id != article.author_id):
            self.article_repo.increment_view_count(db, article)
        
        return self._convert_to_response(article)
    
    def update_article(
        self, 
        db: Session, 
        article_id: int, 
        article_data: ArticleUpdate, 
        current_user: User
    ) -> ArticleResponse:
        """
        Update an existing article with permission checks.
        
        Args:
            db: Database session
            article_id: Article ID to update
            article_data: Update data
            current_user: Current authenticated user
            
        Returns:
            Updated article response
            
        Raises:
            NotFoundError: If article not found
            PermissionError: If user lacks permissions
            ValidationError: If data validation fails
        """
        article = self.article_repo.get_by_id(db, article_id)
        
        if not article:
            raise NotFoundError("Article not found")
        
        # Check permissions
        self._check_article_edit_permission(article, current_user)
        
        # Validate collection ownership if being changed
        if article_data.collection_id and article_data.collection_id != article.collection_id:
            self._validate_collection_ownership(db, article_data.collection_id, current_user.id)
        
        # Update article
        updated_article = self.article_repo.update(db, article, article_data)
        
        if not updated_article:
            raise ValidationError("Failed to update article")
        
        logger.info(f"Article updated successfully: {updated_article.title} by {current_user.username}")
        return self._convert_to_response(updated_article)
    
    def delete_article(
        self, 
        db: Session, 
        article_id: int, 
        current_user: User
    ) -> bool:
        """
        Delete an article with permission checks.
        
        Args:
            db: Database session
            article_id: Article ID to delete
            current_user: Current authenticated user
            
        Returns:
            True if successful
            
        Raises:
            NotFoundError: If article not found
            PermissionError: If user lacks permissions
        """
        article = self.article_repo.get_by_id(db, article_id, include_relations=False)
        
        if not article:
            raise NotFoundError("Article not found")
        
        # Check permissions
        self._check_article_edit_permission(article, current_user)
        
        # Delete article
        success = self.article_repo.delete(db, article)
        
        if success:
            logger.info(f"Article deleted successfully: {article.title} by {current_user.username}")
        
        return success
    
    def get_articles(
        self, 
        db: Session, 
        filters: ArticleFilter,
        current_user: Optional[User] = None
    ) -> PaginatedResponse:
        """
        Get articles with filtering and pagination.
        
        Args:
            db: Database session
            filters: Filter parameters
            current_user: Current authenticated user (optional)
            
        Returns:
            Paginated article response
        """
        # Adjust filters based on user permissions
        if not current_user or not current_user.is_admin:
            # Non-admin users can only see published articles (unless viewing their own)
            if not filters.author_id or (current_user and filters.author_id != current_user.id):
                filters.status = ArticleStatus.PUBLISHED
        
        articles, total_count = self.article_repo.get_filtered(db, filters)
        
        # Convert to list response
        article_list = [self._convert_to_list_response(article) for article in articles]
        
        # Calculate pagination info
        page = (filters.skip // filters.limit) + 1
        pages = (total_count + filters.limit - 1) // filters.limit
        
        return PaginatedResponse(
            items=article_list,
            total=total_count,
            page=page,
            pages=pages,
            per_page=filters.limit,
            has_next=page < pages,
            has_prev=page > 1
        )
    
    def get_user_articles(
        self, 
        db: Session, 
        user_id: int, 
        status: Optional[ArticleStatus] = None,
        skip: int = 0, 
        limit: int = 20,
        current_user: Optional[User] = None
    ) -> PaginatedResponse:
        """
        Get articles by a specific user.
        
        Args:
            db: Database session
            user_id: User ID to get articles for
            status: Optional status filter
            skip: Pagination offset
            limit: Pagination limit
            current_user: Current authenticated user (optional)
            
        Returns:
            Paginated article response
        """
        # Check if viewing own articles or if user has admin permissions
        if current_user and (current_user.id == user_id or current_user.is_admin):
            # Can see all articles
            pass
        else:
            # Only published articles for others
            status = ArticleStatus.PUBLISHED
        
        articles, total_count = self.article_repo.get_by_author(db, user_id, status, skip, limit)
        
        # Convert to list response
        article_list = [self._convert_to_list_response(article) for article in articles]
        
        # Calculate pagination info
        page = (skip // limit) + 1
        pages = (total_count + limit - 1) // limit
        
        return PaginatedResponse(
            items=article_list,
            total=total_count,
            page=page,
            pages=pages,
            per_page=limit,
            has_next=page < pages,
            has_prev=page > 1
        )
    
    def publish_article(
        self, 
        db: Session, 
        article_id: int, 
        current_user: User
    ) -> ArticleResponse:
        """
        Publish a draft article.
        
        Args:
            db: Database session
            article_id: Article ID to publish
            current_user: Current authenticated user
            
        Returns:
            Updated article response
        """
        update_data = ArticleUpdate(
            status=ArticleStatus.PUBLISHED,
            published_at=datetime.now(timezone.utc)
        )
        
        return self.update_article(db, article_id, update_data, current_user)
    
    def unpublish_article(
        self, 
        db: Session, 
        article_id: int, 
        current_user: User
    ) -> ArticleResponse:
        """
        Unpublish a published article (move to draft).
        
        Args:
            db: Database session
            article_id: Article ID to unpublish
            current_user: Current authenticated user
            
        Returns:
            Updated article response
        """
        update_data = ArticleUpdate(status=ArticleStatus.DRAFT)
        
        return self.update_article(db, article_id, update_data, current_user)
    
    def _check_article_access_permission(
        self, 
        article: Article, 
        current_user: Optional[User]
    ) -> None:
        """Check if user can access the article."""
        # Published articles are accessible to everyone
        if article.status == ArticleStatus.PUBLISHED:
            return
        
        # Draft articles are only accessible to author and admins
        if not current_user:
            raise PermissionError("Authentication required")
        
        if article.author_id != current_user.id and not current_user.is_admin:
            raise PermissionError("Insufficient permissions")
    
    def _check_article_edit_permission(
        self, 
        article: Article, 
        current_user: User
    ) -> None:
        """Check if user can edit the article."""
        if article.author_id != current_user.id and not current_user.is_admin:
            raise PermissionError("Insufficient permissions")
    
    def _validate_collection_ownership(
        self, 
        db: Session, 
        collection_id: int, 
        user_id: int
    ) -> None:
        """Validate that user owns the collection."""
        # TODO: Implement when Collection repository is ready
        pass
    
    def _generate_unique_slug(self, db: Session, title: str) -> str:
        """Generate a unique slug from title."""
        return self.article_repo._generate_unique_slug(db, title)
    
    def _convert_to_response(self, article: Article) -> ArticleResponse:
        """Convert Article model to ArticleResponse."""
        return ArticleResponse.model_validate(article)
    
    def _convert_to_list_response(self, article: Article) -> ArticleListResponse:
        """Convert Article model to ArticleListResponse."""
        return ArticleListResponse.model_validate(article)


# Global article service instance
article_service = ArticleService()