"""
Article Repository for database operations.
Implements Repository pattern for clean data access layer.
"""
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError

from app.models.article import Article, ArticleStatus
from app.models.collection import Collection
from app.models.category import Category, Tag, article_tags
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleFilter

# Configure logging
logger = logging.getLogger(__name__)


class ArticleRepository:
    """
    Repository for Article entity database operations.
    Handles all database access logic for Article model.
    """
    
    def get_by_id(self, db: Session, article_id: int, include_relations: bool = True) -> Optional[Article]:
        """
        Get article by ID with optional relations.
        
        Args:
            db: Database session
            article_id: Article ID to search for
            include_relations: Whether to include author, category, tags
            
        Returns:
            Article object if found, None otherwise
        """
        try:
            query = db.query(Article)
            
            if include_relations:
                query = query.options(
                    joinedload(Article.author),
                    joinedload(Article.category),
                    joinedload(Article.collection),
                    joinedload(Article.tags)
                )
            
            return query.filter(Article.id == article_id).first()
        except Exception as e:
            logger.error(f"Database error getting article by ID {article_id}: {str(e)}")
            return None
    
    def get_by_slug(self, db: Session, slug: str, include_relations: bool = True) -> Optional[Article]:
        """
        Get article by slug with optional relations.
        
        Args:
            db: Database session
            slug: Article slug to search for
            include_relations: Whether to include author, category, tags
            
        Returns:
            Article object if found, None otherwise
        """
        try:
            query = db.query(Article)
            
            if include_relations:
                query = query.options(
                    joinedload(Article.author),
                    joinedload(Article.category),
                    joinedload(Article.collection),
                    joinedload(Article.tags)
                )
            
            return query.filter(Article.slug == slug).first()
        except Exception as e:
            logger.error(f"Database error getting article by slug {slug}: {str(e)}")
            return None
    
    def create(self, db: Session, article_data: ArticleCreate, author_id: int, slug: str) -> Optional[Article]:
        """
        Create a new article in database.
        
        Args:
            db: Database session
            article_data: Article creation data
            author_id: ID of the article author
            slug: Generated slug for the article
            
        Returns:
            Created Article object if successful, None otherwise
        """
        try:
            # Create new article instance
            db_article = Article(
                title=article_data.title,
                slug=slug,
                summary=article_data.summary,
                content=article_data.content,
                meta_description=article_data.meta_description,
                meta_keywords=article_data.meta_keywords,
                author_id=author_id,
                category_id=article_data.category_id,
                collection_id=article_data.collection_id,
                order_in_collection=article_data.order_in_collection,
                status=article_data.status,
                allow_comments=article_data.allow_comments,
                is_featured=article_data.is_featured,
                scheduled_at=article_data.scheduled_at,
                reading_time=self._calculate_reading_time(article_data.content)
            )
            
            # Set published_at if status is published
            if article_data.status == ArticleStatus.PUBLISHED:
                db_article.published_at = datetime.now(timezone.utc)
            
            db.add(db_article)
            db.flush()  # Get the article ID without committing
            
            # Handle tags if provided
            if article_data.tag_names:
                self._handle_article_tags(db, db_article, article_data.tag_names)
            
            db.commit()
            db.refresh(db_article)
            
            logger.info(f"Successfully created article: {article_data.title}")
            return db_article
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error creating article {article_data.title}: {str(e)}")
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Database error creating article {article_data.title}: {str(e)}")
            return None
    
    def update(self, db: Session, article: Article, article_data: ArticleUpdate) -> Optional[Article]:
        """
        Update an existing article.
        
        Args:
            db: Database session
            article: Article object to update
            article_data: Update data
            
        Returns:
            Updated Article object if successful, None otherwise
        """
        try:
            update_data = article_data.model_dump(exclude_unset=True)
            
            # Handle status change
            if 'status' in update_data:
                old_status = article.status
                new_status = update_data['status']
                
                # Set published_at when publishing
                if old_status != ArticleStatus.PUBLISHED and new_status == ArticleStatus.PUBLISHED:
                    update_data['published_at'] = datetime.now(timezone.utc)
                # Clear published_at when unpublishing
                elif old_status == ArticleStatus.PUBLISHED and new_status != ArticleStatus.PUBLISHED:
                    update_data['published_at'] = None
            
            # Update slug if title changed
            if 'title' in update_data and update_data['title'] != article.title:
                new_slug = self._generate_unique_slug(db, update_data['title'], article.id)
                update_data['slug'] = new_slug
            
            # Update reading time if content changed
            if 'content' in update_data:
                update_data['reading_time'] = self._calculate_reading_time(update_data['content'])
            
            # Handle tags if provided
            if 'tag_names' in update_data:
                tag_names = update_data.pop('tag_names')
                self._handle_article_tags(db, article, tag_names)
            
            # Apply updates
            for field, value in update_data.items():
                setattr(article, field, value)
            
            db.commit()
            db.refresh(article)
            
            logger.info(f"Successfully updated article: {article.title}")
            return article
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error updating article {article.id}: {str(e)}")
            return None
    
    def delete(self, db: Session, article: Article) -> bool:
        """
        Delete an article from database.
        
        Args:
            db: Database session
            article: Article object to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db.delete(article)
            db.commit()
            
            logger.info(f"Successfully deleted article: {article.title}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error deleting article {article.id}: {str(e)}")
            return False
    
    def get_filtered(
        self, 
        db: Session, 
        filters: ArticleFilter,
        include_relations: bool = True
    ) -> tuple[List[Article], int]:
        """
        Get articles with filtering, sorting, and pagination.
        
        Args:
            db: Database session
            filters: Filter parameters
            include_relations: Whether to include related objects
            
        Returns:
            Tuple of (articles list, total count)
        """
        try:
            query = db.query(Article)
            
            if include_relations:
                query = query.options(
                    joinedload(Article.author),
                    joinedload(Article.category),
                    joinedload(Article.collection),
                    joinedload(Article.tags)
                )
            
            # Apply filters
            if filters.status:
                query = query.filter(Article.status == filters.status)
            
            if filters.category_id:
                query = query.filter(Article.category_id == filters.category_id)
            
            if filters.collection_id:
                query = query.filter(Article.collection_id == filters.collection_id)
            
            if filters.author_id:
                query = query.filter(Article.author_id == filters.author_id)
            
            if filters.is_featured is not None:
                query = query.filter(Article.is_featured == filters.is_featured)
            
            # Search in title and content
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Article.title.ilike(search_term),
                        Article.content.ilike(search_term),
                        Article.summary.ilike(search_term)
                    )
                )
            
            # Filter by tag
            if filters.tag:
                query = query.join(Article.tags).filter(Tag.slug == filters.tag.lower())
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply sorting
            sort_column = getattr(Article, filters.sort_by, Article.created_at)
            if filters.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            articles = query.offset(filters.skip).limit(filters.limit).all()
            
            return articles, total_count
            
        except Exception as e:
            logger.error(f"Database error getting filtered articles: {str(e)}")
            return [], 0
    
    def get_by_author(
        self, 
        db: Session, 
        author_id: int, 
        status: Optional[ArticleStatus] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> tuple[List[Article], int]:
        """
        Get articles by author with optional status filter.
        
        Args:
            db: Database session
            author_id: Author user ID
            status: Optional status filter
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            Tuple of (articles list, total count)
        """
        try:
            query = db.query(Article).filter(Article.author_id == author_id)
            
            if status:
                query = query.filter(Article.status == status)
            
            total_count = query.count()
            articles = query.order_by(desc(Article.created_at)).offset(skip).limit(limit).all()
            
            return articles, total_count
            
        except Exception as e:
            logger.error(f"Database error getting articles by author {author_id}: {str(e)}")
            return [], 0
    
    def get_published(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 20,
        category_id: Optional[int] = None
    ) -> tuple[List[Article], int]:
        """
        Get published articles with optional category filter.
        
        Args:
            db: Database session
            skip: Pagination offset
            limit: Pagination limit
            category_id: Optional category filter
            
        Returns:
            Tuple of (articles list, total count)
        """
        try:
            query = db.query(Article).filter(Article.status == ArticleStatus.PUBLISHED)
            
            if category_id:
                query = query.filter(Article.category_id == category_id)
            
            query = query.options(
                joinedload(Article.author),
                joinedload(Article.category),
                joinedload(Article.tags)
            )
            
            total_count = query.count()
            articles = query.order_by(desc(Article.published_at)).offset(skip).limit(limit).all()
            
            return articles, total_count
            
        except Exception as e:
            logger.error(f"Database error getting published articles: {str(e)}")
            return [], 0
    
    def increment_view_count(self, db: Session, article: Article) -> bool:
        """
        Increment article view count.
        
        Args:
            db: Database session
            article: Article object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            article.view_count += 1
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Database error incrementing view count for article {article.id}: {str(e)}")
            return False
    
    def _generate_unique_slug(self, db: Session, title: str, exclude_id: Optional[int] = None) -> str:
        """Generate a unique slug from title."""
        import re
        from unidecode import unidecode
        
        # Convert to lowercase and remove special characters
        slug = unidecode(title.lower())
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug).strip('-')
        
        # Check for uniqueness
        base_slug = slug
        counter = 1
        
        while True:
            query = db.query(Article).filter(Article.slug == slug)
            if exclude_id:
                query = query.filter(Article.id != exclude_id)
            
            if not query.first():
                break
                
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in minutes."""
        # Average reading speed: 200 words per minute
        word_count = len(content.split())
        reading_time = max(1, round(word_count / 200))
        return reading_time
    
    def _handle_article_tags(self, db: Session, article: Article, tag_names: List[str]) -> None:
        """Handle article tags (create new tags if needed)."""
        if not tag_names:
            # Clear all tags
            article.tags.clear()
            return
        
        # Get or create tags
        tags = []
        for tag_name in tag_names:
            tag_slug = tag_name.lower().replace(' ', '-')
            
            # Try to get existing tag
            tag = db.query(Tag).filter(Tag.slug == tag_slug).first()
            
            if not tag:
                # Create new tag
                tag = Tag(
                    name=tag_name.title(),
                    slug=tag_slug,
                    usage_count=1
                )
                db.add(tag)
                db.flush()
            else:
                # Increment usage count
                tag.usage_count += 1
            
            tags.append(tag)
        
        # Update article tags
        article.tags = tags


# Global article repository instance
article_repository = ArticleRepository()