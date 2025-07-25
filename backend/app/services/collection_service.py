"""
Collection Service for business logic operations.
Handles collection-related business logic and validation.
"""
from typing import Optional, List
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.collection import Collection, CollectionStatus, CollectionType
from app.models.user import User
from app.schemas.article import (
    CollectionCreate, CollectionUpdate, CollectionResponse, 
    CollectionWithArticles
)
from app.repositories.collection_repository import collection_repository
from app.repositories.user_repository import user_repository
from app.core.exceptions import NotFoundError, PermissionError, ValidationError

# Configure logging
logger = logging.getLogger(__name__)


class CollectionService:
    """
    Service class for collection-related business logic.
    Handles validation, permissions, and business rules.
    """
    
    def __init__(self):
        self.collection_repo = collection_repository
        self.user_repo = user_repository
    
    def create_collection(
        self, 
        db: Session, 
        collection_data: CollectionCreate, 
        author: User
    ) -> CollectionResponse:
        """
        Create a new collection with business logic validation.
        
        Args:
            db: Database session
            collection_data: Collection creation data
            author: Author user object
            
        Returns:
            Created collection response
            
        Raises:
            ValidationError: If data validation fails
            PermissionError: If user lacks permissions
        """
        try:
            # Validate author is active
            if not author.is_active:
                raise PermissionError("Inactive users cannot create collections")
            
            # Generate unique slug
            slug = self._generate_unique_slug(db, collection_data.title)
            
            # Create collection
            collection = self.collection_repo.create(db, collection_data, author.id, slug)
            
            if not collection:
                raise ValidationError("Failed to create collection")
            
            logger.info(f"Collection created successfully: {collection.title} by {author.username}")
            return self._convert_to_response(collection)
            
        except (ValidationError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise ValidationError("Collection creation failed")
    
    def get_collection_by_id(
        self, 
        db: Session, 
        collection_id: int, 
        current_user: Optional[User] = None
    ) -> CollectionResponse:
        """
        Get collection by ID with permission checks.
        
        Args:
            db: Database session
            collection_id: Collection ID
            current_user: Current authenticated user (optional)
            
        Returns:
            Collection response
            
        Raises:
            NotFoundError: If collection not found
            PermissionError: If user lacks permissions
        """
        collection = self.collection_repo.get_by_id(db, collection_id)
        
        if not collection:
            raise NotFoundError("Collection not found")
        
        # Check permissions
        self._check_collection_access_permission(collection, current_user)
        
        return self._convert_to_response(collection)
    
    def get_collection_with_articles(
        self, 
        db: Session, 
        collection_id: int, 
        current_user: Optional[User] = None
    ) -> CollectionWithArticles:
        """
        Get collection with articles by ID with permission checks.
        
        Args:
            db: Database session
            collection_id: Collection ID
            current_user: Current authenticated user (optional)
            
        Returns:
            Collection with articles response
            
        Raises:
            NotFoundError: If collection not found
            PermissionError: If user lacks permissions
        """
        collection = self.collection_repo.get_by_id_with_articles(db, collection_id)
        
        if not collection:
            raise NotFoundError("Collection not found")
        
        # Check permissions
        self._check_collection_access_permission(collection, current_user)
        
        return self._convert_to_response_with_articles(collection)
    
    def get_collection_by_slug_with_articles(
        self, 
        db: Session, 
        slug: str, 
        current_user: Optional[User] = None
    ) -> CollectionWithArticles:
        """
        Get collection with articles by slug with permission checks.
        
        Args:
            db: Database session
            slug: Collection slug
            current_user: Current authenticated user (optional)
            
        Returns:
            Collection with articles response
            
        Raises:
            NotFoundError: If collection not found
            PermissionError: If user lacks permissions
        """
        collection = self.collection_repo.get_by_slug_with_articles(db, slug)
        
        if not collection:
            raise NotFoundError("Collection not found")
        
        # Check permissions
        self._check_collection_access_permission(collection, current_user)
        
        return self._convert_to_response_with_articles(collection)
    
    def update_collection(
        self, 
        db: Session, 
        collection_id: int, 
        collection_data: CollectionUpdate, 
        current_user: User
    ) -> CollectionResponse:
        """
        Update an existing collection with permission checks.
        
        Args:
            db: Database session
            collection_id: Collection ID to update
            collection_data: Update data
            current_user: Current authenticated user
            
        Returns:
            Updated collection response
            
        Raises:
            NotFoundError: If collection not found
            PermissionError: If user lacks permissions
            ValidationError: If data validation fails
        """
        collection = self.collection_repo.get_by_id(db, collection_id, include_relations=False)
        
        if not collection:
            raise NotFoundError("Collection not found")
        
        # Check permissions
        self._check_collection_edit_permission(collection, current_user)
        
        # Update collection
        updated_collection = self.collection_repo.update(db, collection, collection_data)
        
        if not updated_collection:
            raise ValidationError("Failed to update collection")
        
        logger.info(f"Collection updated successfully: {updated_collection.title} by {current_user.username}")
        return self._convert_to_response(updated_collection)
    
    def delete_collection(
        self, 
        db: Session, 
        collection_id: int, 
        current_user: User
    ) -> bool:
        """
        Delete a collection with permission checks.
        
        Args:
            db: Database session
            collection_id: Collection ID to delete
            current_user: Current authenticated user
            
        Returns:
            True if successful
            
        Raises:
            NotFoundError: If collection not found
            PermissionError: If user lacks permissions
        """
        collection = self.collection_repo.get_by_id(db, collection_id, include_relations=False)
        
        if not collection:
            raise NotFoundError("Collection not found")
        
        # Check permissions
        self._check_collection_edit_permission(collection, current_user)
        
        # Delete collection
        success = self.collection_repo.delete(db, collection)
        
        if success:
            logger.info(f"Collection deleted successfully: {collection.title} by {current_user.username}")
        
        return success
    
    def get_collections(
        self, 
        db: Session, 
        type_filter: Optional[CollectionType] = None,
        status_filter: Optional[CollectionStatus] = None,
        author_id: Optional[int] = None,
        is_featured: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 20,
        current_user: Optional[User] = None
    ) -> List[CollectionResponse]:
        """
        Get collections with filtering.
        
        Args:
            db: Database session
            type_filter: Collection type filter
            status_filter: Collection status filter
            author_id: Author ID filter
            is_featured: Featured filter
            skip: Pagination offset
            limit: Pagination limit
            current_user: Current authenticated user (optional)
            
        Returns:
            List of collection responses
        """
        # Adjust filters based on user permissions
        if not current_user or not current_user.is_admin:
            # Non-admin users can only see published collections (unless viewing their own)
            if not author_id or (current_user and author_id != current_user.id):
                status_filter = CollectionStatus.PUBLISHED
        
        collections = self.collection_repo.get_filtered(
            db, type_filter, status_filter, author_id, is_featured, skip, limit
        )
        
        return [self._convert_to_response(collection) for collection in collections]
    
    def get_user_collections(
        self, 
        db: Session, 
        user_id: int, 
        status_filter: Optional[CollectionStatus] = None,
        type_filter: Optional[CollectionType] = None,
        skip: int = 0, 
        limit: int = 20,
        current_user: Optional[User] = None
    ) -> List[CollectionResponse]:
        """
        Get collections by a specific user.
        
        Args:
            db: Database session
            user_id: User ID to get collections for
            status_filter: Optional status filter
            type_filter: Optional type filter
            skip: Pagination offset
            limit: Pagination limit
            current_user: Current authenticated user (optional)
            
        Returns:
            List of collection responses
        """
        # Check if viewing own collections or if user has admin permissions
        if current_user and (current_user.id == user_id or current_user.is_admin):
            # Can see all collections
            pass
        else:
            # Only published collections for others
            status_filter = CollectionStatus.PUBLISHED
        
        collections = self.collection_repo.get_by_author(
            db, user_id, status_filter, type_filter, skip, limit
        )
        
        return [self._convert_to_response(collection) for collection in collections]
    
    def publish_collection(
        self, 
        db: Session, 
        collection_id: int, 
        current_user: User
    ) -> CollectionResponse:
        """
        Publish a draft collection.
        
        Args:
            db: Database session
            collection_id: Collection ID to publish
            current_user: Current authenticated user
            
        Returns:
            Updated collection response
        """
        update_data = CollectionUpdate(
            status=CollectionStatus.PUBLISHED,
            published_at=datetime.now(timezone.utc)
        )
        
        return self.update_collection(db, collection_id, update_data, current_user)
    
    def _check_collection_access_permission(
        self, 
        collection: Collection, 
        current_user: Optional[User]
    ) -> None:
        """Check if user can access the collection."""
        # Published collections are accessible to everyone
        if collection.status == CollectionStatus.PUBLISHED:
            return
        
        # Draft collections are only accessible to author and admins
        if not current_user:
            raise PermissionError("Authentication required")
        
        if collection.author_id != current_user.id and not current_user.is_admin:
            raise PermissionError("Insufficient permissions")
    
    def _check_collection_edit_permission(
        self, 
        collection: Collection, 
        current_user: User
    ) -> None:
        """Check if user can edit the collection."""
        if collection.author_id != current_user.id and not current_user.is_admin:
            raise PermissionError("Insufficient permissions")
    
    def _generate_unique_slug(self, db: Session, title: str) -> str:
        """Generate a unique slug from title."""
        return self.collection_repo._generate_unique_slug(db, title)
    
    def _convert_to_response(self, collection: Collection) -> CollectionResponse:
        """Convert Collection model to CollectionResponse."""
        return CollectionResponse.model_validate(collection)
    
    def _convert_to_response_with_articles(self, collection: Collection) -> CollectionWithArticles:
        """Convert Collection model to CollectionWithArticles."""
        return CollectionWithArticles.model_validate(collection)


# Global collection service instance
collection_service = CollectionService()