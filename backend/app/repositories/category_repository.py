"""
Category Repository for database operations.
Implements Repository pattern for clean data access layer with hierarchical support.
"""
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc

from app.models.category import Category
from app.models.article import Article
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class CategoryRepository(BaseRepository[Category]):
    """Repository for category database operations."""
    
    def __init__(self):
        super().__init__(Category)
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Category]:
        """Get category by slug."""
        try:
            return db.query(Category).filter(Category.slug == slug).first()
        except Exception as e:
            logger.error(f"🚨 Error getting category by slug {slug}: {str(e)}")
            return None
    
    def get_by_name(self, db: Session, name: str) -> Optional[Category]:
        """Get category by name."""
        try:
            return db.query(Category).filter(
                func.lower(Category.name) == name.lower()
            ).first()
        except Exception as e:
            logger.error(f"🚨 Error getting category by name {name}: {str(e)}")
            return None
    
    def get_root_categories(
        self, 
        db: Session, 
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 50
    ) -> List[Category]:
        """Get root categories (categories without parent)."""
        try:
            query = db.query(Category).filter(Category.parent_id.is_(None))
            
            if is_active is not None:
                query = query.filter(Category.is_active == is_active)
            
            return query.order_by(Category.name).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"🚨 Error getting root categories: {str(e)}")
            return []
    
    def get_children(
        self, 
        db: Session, 
        parent_id: int,
        is_active: Optional[bool] = None
    ) -> List[Category]:
        """Get child categories of a parent."""
        try:
            query = db.query(Category).filter(Category.parent_id == parent_id)
            
            if is_active is not None:
                query = query.filter(Category.is_active == is_active)
            
            return query.order_by(Category.name).all()
        except Exception as e:
            logger.error(f"🚨 Error getting children for category {parent_id}: {str(e)}")
            return []
    
    def get_category_tree(self, db: Session, is_active: Optional[bool] = None) -> List[Category]:
        """Get complete category tree with children loaded."""
        try:
            # First get all categories
            query = db.query(Category)
            if is_active is not None:
                query = query.filter(Category.is_active == is_active)
            
            all_categories = query.order_by(Category.name).all()
            
            # Build tree structure
            category_dict = {cat.id: cat for cat in all_categories}
            root_categories = []
            
            for category in all_categories:
                if category.parent_id is None:
                    root_categories.append(category)
                else:
                    parent = category_dict.get(category.parent_id)
                    if parent:
                        if not hasattr(parent, '_children'):
                            parent._children = []
                        parent._children.append(category)
            
            return root_categories
        except Exception as e:
            logger.error(f"🚨 Error getting category tree: {str(e)}")
            return []
    
    def get_category_path(self, db: Session, category_id: int) -> List[Category]:
        """Get the path from root to this category."""
        try:
            path = []
            current_id = category_id
            
            while current_id:
                category = self.get_by_id(db, current_id)
                if not category:
                    break
                path.insert(0, category)
                current_id = category.parent_id
            
            return path
        except Exception as e:
            logger.error(f"🚨 Error getting category path for {category_id}: {str(e)}")
            return []
    
    def search_categories(
        self, 
        db: Session, 
        search_term: str,
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 50
    ) -> List[Category]:
        """Search categories by name and description."""
        try:
            search_filter = or_(
                Category.name.ilike(f"%{search_term}%"),
                Category.description.ilike(f"%{search_term}%")
            )
            
            query = db.query(Category).filter(search_filter)
            
            if is_active is not None:
                query = query.filter(Category.is_active == is_active)
            
            return query.order_by(Category.name).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"🚨 Error searching categories with term '{search_term}': {str(e)}")
            return []
    
    def get_categories_with_article_count(
        self, 
        db: Session,
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get categories with their article counts."""
        try:
            query = db.query(
                Category,
                func.count(Article.id).label('article_count')
            ).outerjoin(Article, and_(
                Article.category_id == Category.id,
                Article.status == 'published'
            )).group_by(Category.id)
            
            if is_active is not None:
                query = query.filter(Category.is_active == is_active)
            
            results = query.order_by(Category.name).offset(skip).limit(limit).all()
            
            return [
                {
                    'category': result[0],
                    'article_count': result[1]
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"🚨 Error getting categories with article count: {str(e)}")
            return []
    
    def get_most_used_categories(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most used categories by article count."""
        try:
            results = db.query(
                Category,
                func.count(Article.id).label('article_count')
            ).join(Article, and_(
                Article.category_id == Category.id,
                Article.status == 'published'
            )).group_by(Category.id).having(
                func.count(Article.id) > 0
            ).order_by(desc('article_count')).limit(limit).all()
            
            return [
                {
                    'category': result[0],
                    'article_count': result[1]
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"🚨 Error getting most used categories: {str(e)}")
            return []
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get category statistics."""
        try:
            total_categories = db.query(func.count(Category.id)).scalar() or 0
            active_categories = db.query(func.count(Category.id)).filter(
                Category.is_active == True
            ).scalar() or 0
            root_categories = db.query(func.count(Category.id)).filter(
                Category.parent_id.is_(None)
            ).scalar() or 0
            
            # Get most used category
            most_used = self.get_most_used_categories(db, limit=1)
            most_used_category = most_used[0]['category'] if most_used else None
            
            # Categories with articles
            categories_with_articles = db.query(func.count(func.distinct(Category.id))).join(
                Article, Article.category_id == Category.id
            ).filter(Article.status == 'published').scalar() or 0
            
            return {
                'total_categories': total_categories,
                'active_categories': active_categories,
                'root_categories': root_categories,
                'most_used_category': most_used_category,
                'categories_with_articles': categories_with_articles,
                'max_depth': self._calculate_max_depth(db)
            }
        except Exception as e:
            logger.error(f"🚨 Error getting category statistics: {str(e)}")
            return {}
    
    def _calculate_max_depth(self, db: Session) -> int:
        """Calculate maximum category tree depth."""
        try:
            max_depth = 0
            root_categories = self.get_root_categories(db)
            
            for root in root_categories:
                depth = self._get_category_depth(db, root.id, 0)
                max_depth = max(max_depth, depth)
            
            return max_depth
        except Exception as e:
            logger.error(f"🚨 Error calculating max depth: {str(e)}")
            return 0
    
    def _get_category_depth(self, db: Session, category_id: int, current_depth: int) -> int:
        """Recursively calculate category depth."""
        children = self.get_children(db, category_id)
        if not children:
            return current_depth
        
        max_child_depth = current_depth
        for child in children:
            child_depth = self._get_category_depth(db, child.id, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def bulk_update_status(self, db: Session, category_ids: List[int], is_active: bool) -> int:
        """Bulk update category active status."""
        try:
            updated_count = db.query(Category).filter(
                Category.id.in_(category_ids)
            ).update(
                {'is_active': is_active, 'updated_at': datetime.now(timezone.utc)},
                synchronize_session=False
            )
            db.commit()
            
            logger.info(f"✅ Bulk updated {updated_count} categories status to {is_active}")
            return updated_count
        except Exception as e:
            logger.error(f"🚨 Error bulk updating categories: {str(e)}")
            db.rollback()
            return 0
    
    def move_category(self, db: Session, category_id: int, new_parent_id: Optional[int]) -> bool:
        """Move category to a new parent."""
        try:
            # Validate that we're not creating a circular reference
            if new_parent_id and self._would_create_cycle(db, category_id, new_parent_id):
                logger.warning(f"🚫 Cannot move category {category_id} to {new_parent_id}: would create cycle")
                return False
            
            category = self.get_by_id(db, category_id)
            if not category:
                return False
            
            category.parent_id = new_parent_id
            category.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            logger.info(f"✅ Moved category {category_id} to parent {new_parent_id}")
            return True
        except Exception as e:
            logger.error(f"🚨 Error moving category {category_id}: {str(e)}")
            db.rollback()
            return False
    
    def _would_create_cycle(self, db: Session, category_id: int, new_parent_id: int) -> bool:
        """Check if moving category would create a circular reference."""
        current_id = new_parent_id
        visited = set()
        
        while current_id and current_id not in visited:
            if current_id == category_id:
                return True
            
            visited.add(current_id)
            category = self.get_by_id(db, current_id)
            current_id = category.parent_id if category else None
        
        return False


# Create instance
category_repository = CategoryRepository()