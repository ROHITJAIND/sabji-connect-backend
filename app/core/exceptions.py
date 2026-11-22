"""Structured application exceptions for Sabji Connect."""

from http import HTTPStatus
from typing import Any, Optional

from app.constants.error import ErrorCode, ErrorType


class AppError(Exception):
    """Base application error. All custom errors inherit from this."""

    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: str = ErrorCode.APP_ERROR,
        error_type: str = ErrorType.APP,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.error_type = error_type
        self.details = details
        self.is_operational = True

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "errorCode": self.error_code,
            "message": self.message,
            "type": self.error_type,
            "status": self.status_code,
        }
        if self.details:
            result["detail"] = self.details
        return result


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code=ErrorCode.BAD_REQUEST,
            error_type=ErrorType.BAD_REQUEST,
            details=details,
        )


class AuthenticationError(AppError):
    def __init__(self, message: str = "Not authenticated", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_code=ErrorCode.UNAUTHORIZED,
            error_type=ErrorType.AUTHENTICATION,
            details=details,
        )


class NotAuthorizedError(AppError):
    def __init__(self, message: str = "Not authorized", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
            error_code=ErrorCode.FORBIDDEN,
            error_type=ErrorType.FORBIDDEN,
            details=details,
        )


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            error_code=ErrorCode.NOT_FOUND,
            error_type=ErrorType.NOT_FOUND,
            details=details,
        )


class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
            error_code=ErrorCode.CONFLICT,
            error_type=ErrorType.CONFLICT,
            details=details,
        )


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            error_code=ErrorCode.VALIDATION_ERROR,
            error_type=ErrorType.VALIDATION,
            details=details,
        )
