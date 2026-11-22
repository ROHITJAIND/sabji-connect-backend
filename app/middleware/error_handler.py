"""Global exception handlers for FastAPI."""

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.core.logger import logger


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    """Handle known business-logic errors."""
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "errorCode": "HTTP_ERROR",
            "message": exc.detail,
            "type": "HTTPException",
            "status": exc.status_code,
        },
    )


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors from request parsing."""
    return JSONResponse(
        status_code=422,
        content={
            "errorCode": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "type": "ValidationError",
            "status": 422,
            "detail": exc.errors(),
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions — log and return 500."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "errorCode": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "type": "InternalError",
            "status": 500,
        },
    )
