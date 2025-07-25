"""
Collection API endpoints for article series and books.
Production-ready implementation with security enhancements.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
import os

from app.schemas.article import (
    CollectionCreate, CollectionUpdate, CollectionResponse, 
    CollectionWithArticles, PaginatedResponse
)
from app.services.collection_service import collection_service
from app.api.deps import get_current_active_user, get_current_user_optional, get_db
from app.models.user import User
from app.models.collection import CollectionType, CollectionStatus
from app.core.exceptions import NotFoundError, PermissionError, ValidationError

# Configure logging
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(os.getenv("COLLECTION_CREATE_RATE_LIMIT", "5/minute"))
async def create_collection(
    request: Request,
    collection_data: CollectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new collection (series/book).
    
    Rate limit: 5 collections per minute per IP
    Requires: Valid JWT token, active user
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"📚 Collection creation attempt by user: {current_user.username} from IP: {client_ip}")
    
    try:
        collection = collection_service.create_collection(db, collection_data, current_user)
        
        logger.info(f"✅ Collection created successfully: {collection.title} by {current_user.username}")
        return collection
        
    except ValidationError as e:
        logger.warning(f"🚫 Collection creation validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        logger.warning(f"🚫 Collection creation permission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Collection creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Collection creation failed"
        )


@router.get("/", response_model=List[CollectionResponse])
@limiter.limit(os.getenv("COLLECTION_LIST_RATE_LIMIT", "30/minute"))
async def get_collections(
    request: Request,
    type_filter: Optional[CollectionType] = Query(None, alias="type"),
    status_filter: Optional[CollectionStatus] = Query(None, alias="status"),
    author_id: Optional[int] = Query(None),
    is_featured: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get collections with filtering and pagination.
    
    Rate limit: 30 requests per minute per IP
    Authentication: Optional
    """
    logger.info(f"📚 Collections list request from IP: {request.client.host if request.client else 'unknown'}")
    
    try:
        collections = collection_service.get_collections(
            db, type_filter, status_filter, author_id, is_featured, skip, limit, current_user
        )
        
        logger.info(f"✅ Collections retrieved: {len(collections)} items")
        return collections
        
    except Exception as e:
        logger.error(f"🚨 Collections list error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collections"
        )


@router.get("/{collection_id}", response_model=CollectionWithArticles)
@limiter.limit(os.getenv("COLLECTION_GET_RATE_LIMIT", "60/minute"))
async def get_collection(
    request: Request,
    collection_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get a specific collection with its articles.
    
    Rate limit: 60 requests per minute per IP
    Authentication: Optional (required for draft collections)
    """
    logger.info(f"📖 Collection request: ID {collection_id} from IP: {request.client.host if request.client else 'unknown'}")
    
    try:
        collection = collection_service.get_collection_with_articles(db, collection_id, current_user)
        
        logger.info(f"✅ Collection retrieved: {collection.title}")
        return collection
        
    except NotFoundError as e:
        logger.warning(f"🚫 Collection not found: ID {collection_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Collection access denied: ID {collection_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except Exception as e:
        logger.error(f"🚨 Collection retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collection"
        )


@router.get("/slug/{slug}", response_model=CollectionWithArticles)
@limiter.limit(os.getenv("COLLECTION_GET_RATE_LIMIT", "60/minute"))
async def get_collection_by_slug(
    request: Request,
    slug: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get a specific collection by slug with its articles.
    
    Rate limit: 60 requests per minute per IP
    Authentication: Optional (required for draft collections)
    """
    logger.info(f"📖 Collection request: slug '{slug}' from IP: {request.client.host if request.client else 'unknown'}")
    
    try:
        collection = collection_service.get_collection_by_slug_with_articles(db, slug, current_user)
        
        logger.info(f"✅ Collection retrieved: {collection.title}")
        return collection
        
    except NotFoundError as e:
        logger.warning(f"🚫 Collection not found: slug '{slug}'")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Collection access denied: slug '{slug}'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except Exception as e:
        logger.error(f"🚨 Collection retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve collection"
        )


@router.put("/{collection_id}", response_model=CollectionResponse)
@limiter.limit(os.getenv("COLLECTION_UPDATE_RATE_LIMIT", "10/minute"))
async def update_collection(
    request: Request,
    collection_id: int,
    collection_data: CollectionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing collection.
    
    Rate limit: 10 updates per minute per IP
    Requires: Valid JWT token, collection ownership or admin
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"✏️ Collection update attempt: ID {collection_id} by user: {current_user.username} from IP: {client_ip}")
    
    try:
        collection = collection_service.update_collection(db, collection_id, collection_data, current_user)
        
        logger.info(f"✅ Collection updated successfully: {collection.title} by {current_user.username}")
        return collection
        
    except NotFoundError as e:
        logger.warning(f"🚫 Collection not found for update: ID {collection_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Collection update permission denied: ID {collection_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except ValidationError as e:
        logger.warning(f"🚫 Collection update validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Collection update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Collection update failed"
        )


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(os.getenv("COLLECTION_DELETE_RATE_LIMIT", "5/minute"))
async def delete_collection(
    request: Request,
    collection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a collection.
    
    Rate limit: 5 deletions per minute per IP
    Requires: Valid JWT token, collection ownership or admin
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🗑️ Collection deletion attempt: ID {collection_id} by user: {current_user.username} from IP: {client_ip}")
    
    try:
        success = collection_service.delete_collection(db, collection_id, current_user)
        
        if success:
            logger.info(f"✅ Collection deleted successfully: ID {collection_id} by {current_user.username}")
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete collection"
            )
            
    except NotFoundError as e:
        logger.warning(f"🚫 Collection not found for deletion: ID {collection_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Collection deletion permission denied: ID {collection_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except Exception as e:
        logger.error(f"🚨 Collection deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Collection deletion failed"
        )


@router.get("/user/{user_id}", response_model=List[CollectionResponse])
@limiter.limit(os.getenv("USER_COLLECTIONS_RATE_LIMIT", "30/minute"))
async def get_user_collections(
    request: Request,
    user_id: int,
    status_filter: Optional[CollectionStatus] = Query(None, alias="status"),
    type_filter: Optional[CollectionType] = Query(None, alias="type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get collections by a specific user.
    
    Rate limit: 30 requests per minute per IP
    Authentication: Optional (required to see drafts)
    """
    logger.info(f"👤 User collections request: user ID {user_id} from IP: {request.client.host if request.client else 'unknown'}")
    
    try:
        collections = collection_service.get_user_collections(
            db, user_id, status_filter, type_filter, skip, limit, current_user
        )
        
        logger.info(f"✅ User collections retrieved: {len(collections)} items")
        return collections
        
    except Exception as e:
        logger.error(f"🚨 User collections retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user collections"
        )


@router.post("/{collection_id}/publish", response_model=CollectionResponse)
@limiter.limit(os.getenv("COLLECTION_PUBLISH_RATE_LIMIT", "10/minute"))
async def publish_collection(
    request: Request,
    collection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Publish a draft collection.
    
    Rate limit: 10 publishes per minute per IP
    Requires: Valid JWT token, collection ownership or admin
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"📢 Collection publish attempt: ID {collection_id} by user: {current_user.username} from IP: {client_ip}")
    
    try:
        collection = collection_service.publish_collection(db, collection_id, current_user)
        
        logger.info(f"✅ Collection published successfully: {collection.title}")
        return collection
        
    except NotFoundError as e:
        logger.warning(f"🚫 Collection not found for publish: ID {collection_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Collection publish permission denied: ID {collection_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except Exception as e:
        logger.error(f"🚨 Collection publish error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Collection publish failed"
        )