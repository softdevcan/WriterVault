"""
Repository layer for data access.
Implements Repository pattern for clean architecture.
"""

from .user_repository import user_repository

__all__ = ["user_repository"] 