from typing import Any, Optional
from fastapi import HTTPException, status


class DAAssistException(Exception):
    """Base exception for DAAssist application"""

    def __init__(self, message: str, status_code: int = 500, detail: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(DAAssistException):
    """Exception raised when a resource is not found"""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"resource": resource, "identifier": identifier},
        )


class UnauthorizedException(DAAssistException):
    """Exception raised for authentication failures"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(DAAssistException):
    """Exception raised for authorization failures"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class ValidationException(DAAssistException):
    """Exception raised for validation errors"""

    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(
            message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class ConflictException(DAAssistException):
    """Exception raised for conflict errors (e.g., duplicate key)"""

    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT, detail=detail)


class SyncException(DAAssistException):
    """Exception raised for synchronization errors with external systems"""

    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )
