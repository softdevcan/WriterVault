"""
Collection Repository for database operations.
Implements Repository pattern for clean data access layer.
"""
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc

from app.models.collection import Collection, CollectionType, CollectionStatus
from app.models.article import Article
from app.models.user import User
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class CollectionRepository(BaseRepository[Collection]):
    """Repository for collection database operations."""
    
    def __init__(self):
        super().__init__(Collection)
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Collection]:
        """Get collection by slug."""
        try:
            return db.query(Collection).filter(Collection.slug == slug).first()
        except Exception as e:
            logger.error(f"🚨 Error getting collection by slug {slug}: {str(e)}")
            return None
    
    def get_by_author(
        self, 
        db: Session, 
        author_id: int,
        status: Optional[CollectionStatus] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> List[Collection]:
        """Get collections by author."""
        try:
            query = db.query(Collection).filter(Collection.author_id == author_id)
            
            if status:
                query = query.filter(Collection.status == status)
            
            return query.order_by(desc(Collection.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"🚨 Error getting collections by author {author_id}: {str(e)}")
            return []
    
    def get_published_collections(
        self, 
        db: Session,
        collection_type: Optional[CollectionType] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> List[Collection]:
        """Get published collections."""
        try:
            query = db.query(Collection).filter(Collection.status == CollectionStatus.PUBLISHED)
            
            if collection_type:
                query = query.filter(Collection.type == collection_type)
            
            return query.order_by(desc(Collection.published_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"🚨 Error getting published collections: {str(e)}")
            return []
    
    def get_with_articles(self, db: Session, collection_id: int) -> Optional[Collection]:
        """Get collection with its articles loaded."""
        try:
            return db.query(Collection).options(
                joinedload(Collection.articles).joinedload(Article.author)
            ).filter(Collection.id == collection_id).first()
        except Exception as e:
            logger.error(f"🚨 Error getting collection with articles {collection_id}: {str(e)}")
            return None
    
    def get_with_author(self, db: Session, collection_id: int) -> Optional[Collection]:
        """Get collection with author information."""
        try:
            return db.query(Collection).options(
                joinedload(Collection.author)
            ).filter(Collection.id == collection_id).first()
        except Exception as e:
            logger.error(f"🚨 Error getting collection with author {collection_id}: {str(e)}")
            return None
    
    def search_collections(
        self, 
        db: Session, 
        search_term: str,
        status: Optional[CollectionStatus] = None,
        collection_type: Optional[CollectionType] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> List[Collection]:
        """Search collections by title and description."""
        try:
            search_filter = or_(
                Collection.title.ilike(f"%{search_term}%"),
                Collection.description.ilike(f"%{search_term}%")
            )
            
            query = db.query(Collection).filter(search_filter)
            
            if status:
                query = query.filter(Collection.status == status)
            
            if collection_type:
                query = query.filter(Collection.type == collection_type)
            
            return query.order_by(desc(Collection.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"🚨 Error searching collections with term '{search_term}': {str(e)}")
            return []
    
    def get_collections_with_stats(
        self, 
        db: Session,
        status: Optional[CollectionStatus] = None,
        collection_type: Optional[CollectionType] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get collections with article count and total views."""
        try:
            query = db.query(
                Collection,
                func.count(Article.id).label('article_count'),
                func.coalesce(func.sum(Article.view_count), 0).label('total_views')
            ).outerjoin(Article, and_(
                Article.collection_id == Collection.id,
                Article.status == 'published'
            )).group_by(Collection.id)
            
            if status:
                query = query.filter(Collection.status == status)
            
            if collection_type:
                query = query.filter(Collection.type == collection_type)
            
            results = query.order_by(desc(Collection.created_at)).offset(skip).limit(limit).all()
            
            return [
                {
                    'collection': result[0],
                    'article_count': result[1],
                    'total_views': result[2]
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"🚨 Error getting collections with stats: {str(e)}")
            return []
    
    def get_popular_collections(
        self, 
        db: Session, 
        collection_type: Optional[CollectionType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most popular collections by total views."""
        try:
            query = db.query(
                Collection,
                func.coalesce(func.sum(Article.view_count), 0).label('total_views')
            ).join(Article, and_(
                Article.collection_id == Collection.id,
                Article.status == 'published'
            )).filter(
                Collection.status == CollectionStatus.PUBLISHED
            ).group_by(Collection.id).having(
                func.sum(Article.view_count) > 0
            )
            
            if collection_type:
                query = query.filter(Collection.type == collection_type)
            
            results = query.order_by(desc('total_views')).limit(limit).all()
            
            return [
                {
                    'collection': result[0],
                    'total_views': result[1]
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"🚨 Error getting popular collections: {str(e)}")
            return []
    
    def get_collection_articles_ordered(
        self, 
        db: Session, 
        collection_id: int
    ) -> List[Article]:
        """Get collection articles in order."""
        try:
            return db.query(Article).filter(
                Article.collection_id == collection_id
            ).order_by(Article.order_in_collection, Article.created_at).all()
        except Exception as e:
            logger.error(f"🚨 Error getting ordered articles for collection {collection_id}: {str(e)}")
            return []
    
    def update_article_order(
        self, 
        db: Session, 
        collection_id: int, 
        article_orders: List[Dict[str, int]]
    ) -> bool:
        """Update article order in collection."""
        try:
            for order_data in article_orders:
                article_id = order_data['article_id']
                order = order_data['order']
                
                db.query(Article).filter(
                    and_(
                        Article.id == article_id,
                        Article.collection_id == collection_id
                    )
                ).update(
                    {'order_in_collection': order},
                    synchronize_session=False
                )
            
            db.commit()
            logger.info(f"✅ Updated article order for collection {collection_id}")
            return True
        except Exception as e:
            logger.error(f"🚨 Error updating article order: {str(e)}")
            db.rollback()
            return False
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            total_collections = db.query(func.count(Collection.id)).scalar() or 0
            published_collections = db.query(func.count(Collection.id)).filter(
                Collection.status == CollectionStatus.PUBLISHED
            ).scalar() or 0
            draft_collections = db.query(func.count(Collection.id)).filter(
                Collection.status == CollectionStatus.DRAFT
            ).scalar() or 0
            series_count = db.query(func.count(Collection.id)).filter(
                Collection.type == CollectionType.SERIES
            ).scalar() or 0
            book_count = db.query(func.count(Collection.id)).filter(
                Collection.type == CollectionType.BOOK
            ).scalar() or 0
            
            # Total articles in collections
            total_articles_in_collections = db.query(func.count(Article.id)).filter(
                Article.collection_id.isnot(None)
            ).scalar() or 0
            
            # Average articles per collection
            avg_articles = 0
            if total_collections > 0:
                avg_articles = total_articles_in_collections / total_collections
            
            return {
                'total_collections': total_collections,
                'published_collections': published_collections,
                'draft_collections': draft_collections,
                'series_count': series_count,
                'book_count': book_count,
                'total_articles_in_collections': total_articles_in_collections,
                'avg_articles_per_collection': round(avg_articles, 2)
            }
        except Exception as e:
            logger.error(f"🚨 Error getting collection statistics: {str(e)}")
            return {}
    
    def get_author_collections_count(self, db: Session, author_id: int) -> Dict[str, int]:
        """Get collection counts for an author."""
        try:
            total = db.query(func.count(Collection.id)).filter(
                Collection.author_id == author_id
            ).scalar() or 0
            
            published = db.query(func.count(Collection.id)).filter(
                and_(
                    Collection.author_id == author_id,
                    Collection.status == CollectionStatus.PUBLISHED
                )
            ).scalar() or 0
            
            draft = db.query(func.count(Collection.id)).filter(
                and_(
                    Collection.author_id == author_id,
                    Collection.status == CollectionStatus.DRAFT
                )
            ).scalar() or 0
            
            series = db.query(func.count(Collection.id)).filter(
                and_(
                    Collection.author_id == author_id,
                    Collection.type == CollectionType.SERIES
                )
            ).scalar() or 0
            
            books = db.query(func.count(Collection.id)).filter(
                and_(
                    Collection.author_id == author_id,
                    Collection.type == CollectionType.BOOK
                )
            ).scalar() or 0
            
            return {
                'total_collections': total,
                'published_collections': published,
                'draft_collections': draft,
                'series_count': series,
                'book_count': books
            }
        except Exception as e:
            logger.error(f"🚨 Error getting author collection counts: {str(e)}")
            return {}
    
    def remove_article_from_collection(self, db: Session, article_id: int) -> bool:
        """Remove article from its collection."""
        try:
            updated_rows = db.query(Article).filter(Article.id == article_id).update(
                {
                    'collection_id': None,
                    'order_in_collection': None,
                    'updated_at': datetime.now(timezone.utc)
                },
                synchronize_session=False
            )
            db.commit()
            
            if updated_rows > 0:
                logger.info(f"✅ Removed article {article_id} from collection")
                return True
            return False
        except Exception as e:
            logger.error(f"🚨 Error removing article from collection: {str(e)}")
            db.rollback()
            return False
    
    def add_article_to_collection(
        self, 
        db: Session, 
        article_id: int, 
        collection_id: int,
        order: Optional[int] = None
    ) -> bool:
        """Add article to collection."""
        try:
            # Get next order if not provided
            if order is None:
                max_order = db.query(func.max(Article.order_in_collection)).filter(
                    Article.collection_id == collection_id
                ).scalar() or 0
                order = max_order + 1
            
            updated_rows = db.query(Article).filter(Article.id == article_id).update(
                {
                    'collection_id': collection_id,
                    'order_in_collection': order,
                    'updated_at': datetime.now(timezone.utc)
                },
                synchronize_session=False
            )
            db.commit()
            
            if updated_rows > 0:
                logger.info(f"✅ Added article {article_id} to collection {collection_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"🚨 Error adding article to collection: {str(e)}")
            db.rollback()
            return False


# Create instance
collection_repository = CollectionRepository()