"""
Article API endpoints with comprehensive CRUD operations.
Production-ready implementation with security enhancements.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os

from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse, ArticleListResponse,
    PaginatedResponse, ArticleFilter, ArticleStatusUpdate
)
from app.services.article_service import article_service
from app.api.deps import get_current_active_user, get_current_user_optional, get_db
from app.models.user import User
from app.models.article import ArticleStatus
from app.core.exceptions import NotFoundError, PermissionError, ValidationError

# Configure logging
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(os.getenv("ARTICLE_CREATE_RATE_LIMIT", "10/minute"))
async def create_article(
    request: Request,
    article_data: ArticleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new article.
    
    Rate limit: 10 articles per minute per IP
    Requires: Valid JWT token, active user
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"📝 Article creation attempt by user: {current_user.username} from IP: {client_ip}")
    
    try:
        article = article_service.create_article(db, article_data, current_user)
        
        logger.info(f"✅ Article created successfully: {article.title} by {current_user.username}")
        return article
        
    except ValidationError as e:
        logger.warning(f"🚫 Article creation validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        logger.warning(f"🚫 Article creation permission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Article creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Article creation failed"
        )


@router.get("/", response_model=PaginatedResponse)
@limiter.limit(os.getenv("ARTICLE_LIST_RATE_LIMIT", "30/minute"))
async def get_articles(
    request: Request,
    status_filter: Optional[ArticleStatus] = Query(None, alias="status"),
    category_id: Optional[int] = Query(None),
    collection_id: Optional[int] = Query(None),
    author_id: Optional[int] = Query(None),
    is_featured: Optional[bool] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get articles with filtering, sorting, and pagination.
    
    Rate limit: 30 requests per minute per IP
    Authentication: Optional
    """
    logger.info(f"📚 Articles list request from IP: {request.client.host if request.client else 'unknown'}")
    
    try:
        filters = ArticleFilter(
            status=status_filter,
            category_id=category_id,
            collection_id=collection_id,
            author_id=author_id,
            is_featured=is_featured,
            tag=tag,
            search=search,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        articles = article_service.get_articles(db, filters, current_user)
        
        logger.info(f"✅ Articles retrieved: {len(articles.items)} items, {articles.total} total")
        return articles
        
    except ValidationError as e:
        logger.warning(f"🚫 Articles list validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Articles list error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve articles"
        )


@router.get("/{article_id}", response_model=ArticleResponse)
@limiter.limit(os.getenv("ARTICLE_GET_RATE_LIMIT", "60/minute"))
async def get_article(
    request: Request,
    article_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get a specific article by ID.
    
    Rate limit: 60 requests per minute per IP
    Authentication: Optional (required for draft articles)
    """
    logger.info(f"📖 Article request: ID {article_id} from IP: {request.client.host if request.client else 'unknown'}")
    
    try:
        article = article_service.get_article_by_id(db, article_id, current_user)
        
        logger.info(f"✅ Article retrieved: {article.title}")
        return article
        
    except NotFoundError as e:
        logger.warning(f"🚫 Article not found: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Article access denied: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except Exception as e:
        logger.error(f"🚨 Article retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve article"
        )


@router.get("/slug/{slug}", response_model=ArticleResponse)
@limiter.limit(os.getenv("ARTICLE_GET_RATE_LIMIT", "60/minute"))
async def get_article_by_slug(
    request: Request,
    slug: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get a specific article by slug.
    
    Rate limit: 60 requests per minute per IP
    Authentication: Optional (required for draft articles)
    """
    logger.info(f"📖 Article request: slug '{slug}' from IP: {request.client.host if request.client else 'unknown'}")
    
    try:
        article = article_service.get_article_by_slug(db, slug, current_user)
        
        logger.info(f"✅ Article retrieved: {article.title}")
        return article
        
    except NotFoundError as e:
        logger.warning(f"🚫 Article not found: slug '{slug}'")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Article access denied: slug '{slug}'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except Exception as e:
        logger.error(f"🚨 Article retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve article"
        )


@router.put("/{article_id}", response_model=ArticleResponse)
@limiter.limit(os.getenv("ARTICLE_UPDATE_RATE_LIMIT", "20/minute"))
async def update_article(
    request: Request,
    article_id: int,
    article_data: ArticleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing article.
    
    Rate limit: 20 updates per minute per IP
    Requires: Valid JWT token, article ownership or admin
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"✏️ Article update attempt: ID {article_id} by user: {current_user.username} from IP: {client_ip}")
    
    try:
        article = article_service.update_article(db, article_id, article_data, current_user)
        
        logger.info(f"✅ Article updated successfully: {article.title} by {current_user.username}")
        return article
        
    except NotFoundError as e:
        logger.warning(f"🚫 Article not found for update: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Article update permission denied: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except ValidationError as e:
        logger.warning(f"🚫 Article update validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Article update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Article update failed"
        )


@router.patch("/{article_id}/status", response_model=ArticleResponse)
@limiter.limit(os.getenv("ARTICLE_STATUS_RATE_LIMIT", "30/minute"))
async def update_article_status(
    request: Request,
    article_id: int,
    status_data: ArticleStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update article status (publish/unpublish/archive).
    
    Rate limit: 30 updates per minute per IP
    Requires: Valid JWT token, article ownership or admin
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🔄 Article status update: ID {article_id} to {status_data.status} by {current_user.username} from IP: {client_ip}")
    
    try:
        article_update = ArticleUpdate(
            status=status_data.status,
            scheduled_at=status_data.scheduled_at
        )
        
        article = article_service.update_article(db, article_id, article_update, current_user)
        
        logger.info(f"✅ Article status updated: {article.title} to {status_data.status}")
        return article
        
    except NotFoundError as e:
        logger.warning(f"🚫 Article not found for status update: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Article status update permission denied: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except ValidationError as e:
        logger.warning(f"🚫 Article status update validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"🚨 Article status update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Article status update failed"
        )


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(os.getenv("ARTICLE_DELETE_RATE_LIMIT", "10/minute"))
async def delete_article(
    request: Request,
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an article.
    
    Rate limit: 10 deletions per minute per IP
    Requires: Valid JWT token, article ownership or admin
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"🗑️ Article deletion attempt: ID {article_id} by user: {current_user.username} from IP: {client_ip}")
    
    try:
        success = article_service.delete_article(db, article_id, current_user)
        
        if success:
            logger.info(f"✅ Article deleted successfully: ID {article_id} by {current_user.username}")
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete article"
            )
            
    except NotFoundError as e:
        logger.warning(f"🚫 Article not found for deletion: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Article deletion permission denied: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except Exception as e:
        logger.error(f"🚨 Article deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Article deletion failed"
        )


@router.get("/user/{user_id}", response_model=PaginatedResponse)
@limiter.limit(os.getenv("USER_ARTICLES_RATE_LIMIT", "30/minute"))
async def get_user_articles(
    request: Request,
    user_id: int,
    status_filter: Optional[ArticleStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get articles by a specific user.
    
    Rate limit: 30 requests per minute per IP
    Authentication: Optional (required to see drafts)
    """
    logger.info(f"👤 User articles request: user ID {user_id} from IP: {request.client.host if request.client else 'unknown'}")
    
    try:
        articles = article_service.get_user_articles(
            db, user_id, status_filter, skip, limit, current_user
        )
        
        logger.info(f"✅ User articles retrieved: {len(articles.items)} items, {articles.total} total")
        return articles
        
    except Exception as e:
        logger.error(f"🚨 User articles retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user articles"
        )


# Convenience endpoints for common operations
@router.post("/{article_id}/publish", response_model=ArticleResponse)
@limiter.limit(os.getenv("ARTICLE_PUBLISH_RATE_LIMIT", "20/minute"))
async def publish_article(
    request: Request,
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Publish a draft article.
    
    Rate limit: 20 publishes per minute per IP
    Requires: Valid JWT token, article ownership or admin
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"📢 Article publish attempt: ID {article_id} by user: {current_user.username} from IP: {client_ip}")
    
    try:
        article = article_service.publish_article(db, article_id, current_user)
        
        logger.info(f"✅ Article published successfully: {article.title}")
        return article
        
    except NotFoundError as e:
        logger.warning(f"🚫 Article not found for publish: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Article publish permission denied: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except Exception as e:
        logger.error(f"🚨 Article publish error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Article publish failed"
        )


@router.post("/{article_id}/unpublish", response_model=ArticleResponse)
@limiter.limit(os.getenv("ARTICLE_UNPUBLISH_RATE_LIMIT", "20/minute"))
async def unpublish_article(
    request: Request,
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Unpublish a published article (move to draft).
    
    Rate limit: 20 unpublishes per minute per IP
    Requires: Valid JWT token, article ownership or admin
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"📝 Article unpublish attempt: ID {article_id} by user: {current_user.username} from IP: {client_ip}")
    
    try:
        article = article_service.unpublish_article(db, article_id, current_user)
        
        logger.info(f"✅ Article unpublished successfully: {article.title}")
        return article
        
    except NotFoundError as e:
        logger.warning(f"🚫 Article not found for unpublish: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    except PermissionError as e:
        logger.warning(f"🚫 Article unpublish permission denied: ID {article_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    except Exception as e:
        logger.error(f"🚨 Article unpublish error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Article unpublish failed"
        )