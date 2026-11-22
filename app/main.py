"""
Sabji Connect — FastAPI application entry point.

Family grocery management backend with JWT auth,
MongoDB (Beanie ODM), WebSocket real-time updates,
designed for Android mobile clients.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

import app.middleware.error_handler as ERROR_HANDLER
from app.api.router import api_router, base_router
from app.core.config import env
from app.core.db import db_manager
from app.core.exceptions import AppError
from app.core.logger import logger, setup_logger
from app.middleware.cors import setup_cors
from app.middleware.request_logger import RequestLoggerMiddleware
from app.models import DOCUMENT_MODELS


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info("Starting Sabji Connect")

    try:
        await db_manager.connect()
        await db_manager.init_beanie_models(DOCUMENT_MODELS)

        logger.info("Application startup complete")
        yield

    finally:
        logger.info("Shutting down application")
        try:
            await db_manager.close()
        except Exception:
            logger.exception("Failed to close database connections")

        logger.info("Application shutdown complete")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app: FastAPI = FastAPI(
        title=env.APP_NAME,
        version=env.APP_VERSION,
        description="Family grocery management API for Sabji Connect",
        lifespan=lifespan,
    )

    setup_logger()
    setup_cors(app)
    app.add_middleware(RequestLoggerMiddleware)

    @app.middleware("http")
    async def add_no_cache_headers(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    # Exception handlers
    app.add_exception_handler(RequestValidationError, ERROR_HANDLER.handle_validation_error)
    app.add_exception_handler(AppError, ERROR_HANDLER.handle_app_error)
    app.add_exception_handler(HTTPException, ERROR_HANDLER.handle_http_exception)
    app.add_exception_handler(Exception, ERROR_HANDLER.global_exception_handler)

    # Routers
    app.include_router(base_router)
    app.include_router(api_router, prefix="/api")

    return app


app: FastAPI = create_application()
