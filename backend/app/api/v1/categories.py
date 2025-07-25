"""
Category API endpoints with comprehensive CRUD operations.
Production-ready implementation with security enhancements.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.api.deps import get_db, get_current_admin_user_bearer, get_current_user_optional
from app.models.user import User
from app.services.category_service import category_service
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithChildren,
    CategoryTree, CategoryStats, CategoryListParams, CategoryBulkUpdate,
    CategoryMoveRequest
)
from app.core.exceptions import NotFoundError, ValidationError, PermissionError

# Configure logging
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Router
router = APIRouter()


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Category",
    description="""
    Create a new category.
    
    Rate limit: 10 requests per minute per IP
    Requires: Admin privileges
    """
)
@limiter.limit("10/minute")
async def create_category(
    request: Request,
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_bearer)
):
    """Create a new category."""
    try:
        category = category_service.create_category(db, category_data, current_user)
        logger.info(f"✅ Category created by {current_user.username}: {category.name}")
        return CategoryResponse.model_validate(category)
    
    except ValidationError as e:
        logger.warning(f"🚫 Category creation validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        logger.warning(f"🚫 Category creation permission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Category creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category"
        )


@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="Get Categories",
    description="""
    Get categories with filtering and pagination.
    
    Rate limit: 100 requests per minute per IP
    Public endpoint (no authentication required)
    """
)
@limiter.limit("100/minute")
async def get_categories(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    parent_id: Optional[int] = Query(None, description="Filter by parent category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search term"),
    include_children: bool = Query(False, description="Include children in response"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get categories with filtering and pagination."""
    try:
        # Create list parameters
        params = CategoryListParams(
            skip=skip,
            limit=limit,
            parent_id=parent_id,
            is_active=is_active,
            search=search,
            include_children=include_children
        )
        
        # If user is not admin, only show active categories
        if not current_user or not current_user.is_admin:
            params.is_active = True
        
        categories = category_service.get_categories(db, params)
        
        logger.debug(f"📚 Retrieved {len(categories)} categories")
        return [CategoryResponse.model_validate(cat) for cat in categories]
    
    except ValidationError as e:
        logger.warning(f"🚫 Get categories validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Get categories error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )


@router.get(
    "/tree",
    response_model=List[CategoryTree],
    summary="Get Category Tree",
    description="""
    Get hierarchical category tree.
    
    Rate limit: 60 requests per minute per IP
    Public endpoint (shows only active categories for non-admin users)
    """
)
@limiter.limit("60/minute")
async def get_category_tree(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get hierarchical category tree."""
    try:
        # Show only active categories for non-admin users
        is_active = None if current_user and current_user.is_admin else True
        
        tree = category_service.get_category_tree(db, is_active)
        logger.debug(f"🌳 Retrieved category tree with {len(tree)} root categories")
        return tree
    
    except Exception as e:
        logger.error(f"🚨 Get category tree error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category tree"
        )


@router.get(
    "/stats",
    response_model=CategoryStats,
    summary="Get Category Statistics",
    description="""
    Get category statistics.
    
    Rate limit: 30 requests per minute per IP
    Requires: Admin privileges
    """
)
@limiter.limit("30/minute")
async def get_category_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_bearer)
):
    """Get category statistics."""
    try:
        stats = category_service.get_category_statistics(db)
        logger.debug("📊 Retrieved category statistics")
        return stats
    
    except Exception as e:
        logger.error(f"🚨 Get category statistics error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category statistics"
        )


@router.get(
    "/{category_id}",
    response_model=CategoryWithChildren,
    summary="Get Category",
    description="""
    Get category by ID with children.
    
    Rate limit: 120 requests per minute per IP
    Public endpoint (shows only active for non-admin users)
    """
)
@limiter.limit("120/minute")
async def get_category(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get category by ID with children."""
    try:
        category = category_service.get_category_with_children(db, category_id)
        
        # Check if user can view inactive categories
        if not category.is_active and (not current_user or not current_user.is_admin):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        logger.debug(f"📚 Retrieved category: {category.name}")
        return category
    
    except NotFoundError:
        logger.warning(f"🚫 Category not found: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    except Exception as e:
        logger.error(f"🚨 Get category error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category"
        )


@router.get(
    "/slug/{slug}",
    response_model=CategoryWithChildren,
    summary="Get Category by Slug",
    description="""
    Get category by slug with children.
    
    Rate limit: 120 requests per minute per IP
    Public endpoint (shows only active for non-admin users)
    """
)
@limiter.limit("120/minute")
async def get_category_by_slug(
    request: Request,
    slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get category by slug with children."""
    try:
        category = category_service.get_category_by_slug(db, slug)
        category_with_children = category_service.get_category_with_children(db, category.id)
        
        # Check if user can view inactive categories
        if not category.is_active and (not current_user or not current_user.is_admin):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        logger.debug(f"📚 Retrieved category by slug: {slug}")
        return category_with_children
    
    except NotFoundError:
        logger.warning(f"🚫 Category not found by slug: {slug}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    except Exception as e:
        logger.error(f"🚨 Get category by slug error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve category"
        )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update Category",
    description="""
    Update category by ID.
    
    Rate limit: 20 requests per minute per IP
    Requires: Admin privileges
    """
)
@limiter.limit("20/minute")
async def update_category(
    request: Request,
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_bearer)
):
    """Update category by ID."""
    try:
        category = category_service.update_category(db, category_id, category_data, current_user)
        logger.info(f"✅ Category updated by {current_user.username}: {category.name}")
        return CategoryResponse.model_validate(category)
    
    except NotFoundError:
        logger.warning(f"🚫 Category not found for update: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    except ValidationError as e:
        logger.warning(f"🚫 Category update validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        logger.warning(f"🚫 Category update permission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Category update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category"
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Category",
    description="""
    Delete category by ID.
    
    Rate limit: 10 requests per minute per IP
    Requires: Admin privileges
    """
)
@limiter.limit("10/minute")
async def delete_category(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_bearer)
):
    """Delete category by ID."""
    try:
        success = category_service.delete_category(db, category_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete category"
            )
        
        logger.info(f"✅ Category deleted by {current_user.username}: ID {category_id}")
        return None
    
    except NotFoundError:
        logger.warning(f"🚫 Category not found for deletion: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    except ValidationError as e:
        logger.warning(f"🚫 Category deletion validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        logger.warning(f"🚫 Category deletion permission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Category deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        )


@router.post(
    "/{category_id}/move",
    response_model=CategoryResponse,
    summary="Move Category",
    description="""
    Move category to new parent.
    
    Rate limit: 20 requests per minute per IP
    Requires: Admin privileges
    """
)
@limiter.limit("20/minute")
async def move_category(
    request: Request,
    category_id: int,
    move_data: CategoryMoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_bearer)
):
    """Move category to new parent."""
    try:
        category = category_service.move_category(db, category_id, move_data, current_user)
        logger.info(f"✅ Category moved by {current_user.username}: ID {category_id}")
        return CategoryResponse.model_validate(category)
    
    except NotFoundError:
        logger.warning(f"🚫 Category not found for move: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    except ValidationError as e:
        logger.warning(f"🚫 Category move validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        logger.warning(f"🚫 Category move permission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Category move error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to move category"
        )


@router.post(
    "/bulk-update",
    summary="Bulk Update Categories",
    description="""
    Bulk update categories.
    
    Rate limit: 5 requests per minute per IP
    Requires: Admin privileges
    """
)
@limiter.limit("5/minute")
async def bulk_update_categories(
    request: Request,
    bulk_data: CategoryBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user_bearer)
):
    """Bulk update categories."""
    try:
        updated_count = category_service.bulk_update_categories(db, bulk_data, current_user)
        logger.info(f"✅ Bulk updated {updated_count} categories by {current_user.username}")
        return {"message": f"Successfully updated {updated_count} categories"}
    
    except ValidationError as e:
        logger.warning(f"🚫 Bulk update validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        logger.warning(f"🚫 Bulk update permission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Bulk update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk update categories"
        )