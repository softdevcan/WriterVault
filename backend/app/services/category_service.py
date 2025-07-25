"""
Category Service for business logic operations.
Handles category-related business logic and validation.
"""
from typing import Optional, List, Dict, Any
import logging
import re
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.user import User
from app.repositories.category_repository import category_repository
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithChildren,
    CategoryTree, CategoryStats, CategoryListParams, CategoryBulkUpdate,
    CategoryMoveRequest
)
from app.core.exceptions import NotFoundError, ValidationError, PermissionError

logger = logging.getLogger(__name__)


class CategoryService:
    """Service class for category business logic."""
    
    def __init__(self):
        self.repository = category_repository
    
    def create_category(
        self, 
        db: Session, 
        category_data: CategoryCreate,
        current_user: User
    ) -> Category:
        """
        Create a new category.
        
        Args:
            db: Database session
            category_data: Category creation data
            current_user: Current authenticated user
            
        Returns:
            Created category
            
        Raises:
            ValidationError: If validation fails
            PermissionError: If user doesn't have permission
        """
        try:
            # Check if user has permission (admin only for now)
            if not current_user.is_admin:
                raise PermissionError("Admin privileges required to create categories")
            
            # Validate parent category exists if provided
            if category_data.parent_id:
                parent = self.repository.get_by_id(db, category_data.parent_id)
                if not parent:
                    raise ValidationError(f"Parent category with ID {category_data.parent_id} not found")
                
                if not parent.is_active:
                    raise ValidationError("Cannot create category under inactive parent")
            
            # Check if category name already exists
            existing = self.repository.get_by_name(db, category_data.name)
            if existing:
                raise ValidationError(f"Category with name '{category_data.name}' already exists")
            
            # Generate slug
            slug = self._generate_slug(category_data.name)
            existing_slug = self.repository.get_by_slug(db, slug)
            if existing_slug:
                slug = self._generate_unique_slug(db, slug)
            
            # Create category
            category_dict = category_data.model_dump()
            category_dict['slug'] = slug
            
            category = self.repository.create(db, category_dict)
            logger.info(f"✅ Category created: {category.name} (ID: {category.id})")
            
            return category
            
        except (ValidationError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"🚨 Error creating category: {str(e)}")
            raise ValidationError("Failed to create category")
    
    def get_category(self, db: Session, category_id: int) -> Category:
        """Get category by ID."""
        category = self.repository.get_by_id(db, category_id)
        if not category:
            raise NotFoundError(f"Category with ID {category_id} not found")
        return category
    
    def get_category_by_slug(self, db: Session, slug: str) -> Category:
        """Get category by slug."""
        category = self.repository.get_by_slug(db, slug)
        if not category:
            raise NotFoundError(f"Category with slug '{slug}' not found")
        return category
    
    def get_categories(
        self, 
        db: Session, 
        params: CategoryListParams
    ) -> List[Category]:
        """Get categories with filtering and pagination."""
        try:
            if params.search:
                return self.repository.search_categories(
                    db, 
                    params.search,
                    params.is_active,
                    params.skip, 
                    params.limit
                )
            elif params.parent_id is not None:
                return self.repository.get_children(db, params.parent_id, params.is_active)
            elif params.parent_id is None and hasattr(params, 'root_only') and params.root_only:
                return self.repository.get_root_categories(
                    db, 
                    params.is_active, 
                    params.skip, 
                    params.limit
                )
            else:
                return self.repository.get_multi(
                    db, 
                    skip=params.skip, 
                    limit=params.limit,
                    filters={'is_active': params.is_active} if params.is_active is not None else None
                )
        except Exception as e:
            logger.error(f"🚨 Error getting categories: {str(e)}")
            return []
    
    def get_category_tree(self, db: Session, is_active: Optional[bool] = None) -> List[CategoryTree]:
        """Get hierarchical category tree."""
        try:
            categories = self.repository.get_category_tree(db, is_active)
            return self._build_category_tree(categories)
        except Exception as e:
            logger.error(f"🚨 Error getting category tree: {str(e)}")
            return []
    
    def get_category_with_children(self, db: Session, category_id: int) -> CategoryWithChildren:
        """Get category with its children."""
        try:
            category = self.get_category(db, category_id)
            children = self.repository.get_children(db, category_id, is_active=True)
            
            # Get article counts
            category_with_count = self.repository.get_categories_with_article_count(db)
            count_dict = {item['category'].id: item['article_count'] for item in category_with_count}
            
            category_response = CategoryWithChildren.model_validate(category)
            category_response.article_count = count_dict.get(category.id, 0)
            category_response.children = [
                CategoryResponse.model_validate(child) for child in children
            ]
            
            # Calculate total articles including children
            total_articles = category_response.article_count
            for child in children:
                total_articles += count_dict.get(child.id, 0)
            category_response.total_articles_including_children = total_articles
            
            return category_response
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"🚨 Error getting category with children: {str(e)}")
            raise ValidationError("Failed to get category with children")
    
    def update_category(
        self, 
        db: Session, 
        category_id: int, 
        category_data: CategoryUpdate,
        current_user: User
    ) -> Category:
        """Update category."""
        try:
            # Check permissions
            if not current_user.is_admin:
                raise PermissionError("Admin privileges required to update categories")
            
            category = self.get_category(db, category_id)
            
            update_dict = category_data.model_dump(exclude_unset=True)
            
            # Validate parent category if being changed
            if 'parent_id' in update_dict and update_dict['parent_id']:
                if update_dict['parent_id'] == category_id:
                    raise ValidationError("Category cannot be its own parent")
                
                parent = self.repository.get_by_id(db, update_dict['parent_id'])
                if not parent:
                    raise ValidationError(f"Parent category with ID {update_dict['parent_id']} not found")
                
                # Check for circular reference
                if self._would_create_cycle(db, category_id, update_dict['parent_id']):
                    raise ValidationError("Cannot create circular parent-child relationship")
            
            # Check name uniqueness if being changed
            if 'name' in update_dict:
                existing = self.repository.get_by_name(db, update_dict['name'])
                if existing and existing.id != category_id:
                    raise ValidationError(f"Category with name '{update_dict['name']}' already exists")
                
                # Update slug if name changed
                update_dict['slug'] = self._generate_slug(update_dict['name'])
                existing_slug = self.repository.get_by_slug(db, update_dict['slug'])
                if existing_slug and existing_slug.id != category_id:
                    update_dict['slug'] = self._generate_unique_slug(db, update_dict['slug'])
            
            update_dict['updated_at'] = datetime.now(timezone.utc)
            
            updated_category = self.repository.update(db, category, update_dict)
            logger.info(f"✅ Category updated: {updated_category.name} (ID: {category_id})")
            
            return updated_category
            
        except (NotFoundError, ValidationError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"🚨 Error updating category {category_id}: {str(e)}")
            raise ValidationError("Failed to update category")
    
    def delete_category(self, db: Session, category_id: int, current_user: User) -> bool:
        """Delete category."""
        try:
            # Check permissions
            if not current_user.is_admin:
                raise PermissionError("Admin privileges required to delete categories")
            
            category = self.get_category(db, category_id)
            
            # Check if category has children
            children = self.repository.get_children(db, category_id)
            if children:
                raise ValidationError("Cannot delete category with child categories")
            
            # Check if category has articles (optional - you might want to reassign instead)
            category_with_count = self.repository.get_categories_with_article_count(db)
            count_dict = {item['category'].id: item['article_count'] for item in category_with_count}
            
            if count_dict.get(category_id, 0) > 0:
                raise ValidationError("Cannot delete category with articles")
            
            success = self.repository.delete(db, category_id)
            if success:
                logger.info(f"✅ Category deleted: {category.name} (ID: {category_id})")
            
            return success
            
        except (NotFoundError, ValidationError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"🚨 Error deleting category {category_id}: {str(e)}")
            return False
    
    def move_category(
        self, 
        db: Session, 
        category_id: int, 
        move_data: CategoryMoveRequest,
        current_user: User
    ) -> Category:
        """Move category to new parent."""
        try:
            # Check permissions
            if not current_user.is_admin:
                raise PermissionError("Admin privileges required to move categories")
            
            category = self.get_category(db, category_id)
            
            # Validate new parent if provided
            if move_data.new_parent_id:
                if move_data.new_parent_id == category_id:
                    raise ValidationError("Category cannot be its own parent")
                
                parent = self.repository.get_by_id(db, move_data.new_parent_id)
                if not parent:
                    raise ValidationError(f"Parent category with ID {move_data.new_parent_id} not found")
            
            success = self.repository.move_category(db, category_id, move_data.new_parent_id)
            if not success:
                raise ValidationError("Failed to move category")
            
            updated_category = self.get_category(db, category_id)
            logger.info(f"✅ Category moved: {category.name} to parent {move_data.new_parent_id}")
            
            return updated_category
            
        except (NotFoundError, ValidationError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"🚨 Error moving category {category_id}: {str(e)}")
            raise ValidationError("Failed to move category")
    
    def bulk_update_categories(
        self, 
        db: Session, 
        bulk_data: CategoryBulkUpdate,
        current_user: User
    ) -> int:
        """Bulk update categories."""
        try:
            # Check permissions
            if not current_user.is_admin:
                raise PermissionError("Admin privileges required for bulk operations")
            
            updated_count = 0
            
            if bulk_data.is_active is not None:
                updated_count = self.repository.bulk_update_status(
                    db, 
                    bulk_data.category_ids, 
                    bulk_data.is_active
                )
            
            logger.info(f"✅ Bulk updated {updated_count} categories")
            return updated_count
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"🚨 Error in bulk update: {str(e)}")
            return 0
    
    def get_category_statistics(self, db: Session) -> CategoryStats:
        """Get category statistics."""
        try:
            stats_data = self.repository.get_statistics(db)
            return CategoryStats(**stats_data)
        except Exception as e:
            logger.error(f"🚨 Error getting category statistics: {str(e)}")
            return CategoryStats()
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from category name."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _generate_unique_slug(self, db: Session, base_slug: str) -> str:
        """Generate unique slug by appending number if needed."""
        counter = 1
        unique_slug = f"{base_slug}-{counter}"
        
        while self.repository.get_by_slug(db, unique_slug):
            counter += 1
            unique_slug = f"{base_slug}-{counter}"
        
        return unique_slug
    
    def _would_create_cycle(self, db: Session, category_id: int, new_parent_id: int) -> bool:
        """Check if moving category would create circular reference."""
        return self.repository._would_create_cycle(db, category_id, new_parent_id)
    
    def _build_category_tree(self, categories: List[Category], level: int = 0) -> List[CategoryTree]:
        """Build hierarchical category tree structure."""
        tree = []
        
        for category in categories:
            category_tree = CategoryTree.model_validate(category)
            category_tree.level = level
            
            # Build path
            path_parts = [category.name]
            if hasattr(category, '_parent_path'):
                path_parts = category._parent_path + path_parts
            category_tree.path = " > ".join(path_parts)
            
            # Add children if they exist
            if hasattr(category, '_children'):
                for child in category._children:
                    child._parent_path = [category.name]
                category_tree.children = self._build_category_tree(
                    category._children, level + 1
                )
            
            tree.append(category_tree)
        
        return tree


# Create service instance
category_service = CategoryService()