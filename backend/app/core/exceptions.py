"""
Custom exceptions for the application.
Provides specific error types for better error handling.
"""


class AppException(Exception):
    """Base exception class for application-specific errors."""
    
    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when data validation fails."""
    
    def __init__(self, message: str = "Data validation failed"):
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class PermissionError(AppException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message)


class AuthenticationError(AppException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class DuplicateError(AppException):
    """Raised when trying to create a duplicate resource."""
    
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message)


class ExternalServiceError(AppException):
    """Raised when external service calls fail."""
    
    def __init__(self, message: str = "External service error"):
        super().__init__(message)