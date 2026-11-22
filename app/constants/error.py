"""Error code and type constants for Sabji Connect."""


class ErrorCode:
    """Machine-readable error codes returned in API responses."""

    APP_ERROR = "APP_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"


class ErrorType:
    """Human-readable error type categories."""

    APP = "ApplicationError"
    BAD_REQUEST = "BadRequestError"
    AUTHENTICATION = "AuthenticationError"
    FORBIDDEN = "ForbiddenError"
    NOT_FOUND = "NotFoundError"
    CONFLICT = "ConflictError"
    VALIDATION = "ValidationError"
