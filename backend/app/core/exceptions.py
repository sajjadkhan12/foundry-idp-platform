"""Custom exceptions for the application"""
from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found"""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class AlreadyExistsException(AppException):
    """Resource already exists"""
    def __init__(self, resource: str, field: str = None):
        message = f"{resource} already exists"
        if field:
            message = f"{resource} with this {field} already exists"
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class PermissionDeniedException(AppException):
    """Permission denied"""
    def __init__(self, permission: str = None):
        message = "Permission denied"
        if permission:
            message = f"Permission denied: {permission} required"
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ValidationException(AppException):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class BusinessUnitRequiredException(AppException):
    """Business unit context required"""
    def __init__(self):
        super().__init__(
            "Business unit must be selected for this action",
            status.HTTP_400_BAD_REQUEST
        )


def exception_to_http(exc: AppException) -> HTTPException:
    """Convert AppException to HTTPException"""
    return HTTPException(status_code=exc.status_code, detail=exc.message)
