"""
Base Repository for common database operations.
Minimal implementation for inheritance compatibility.
"""
from typing import Generic, TypeVar, Type
from app.config.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Base repository class with minimal implementation."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model