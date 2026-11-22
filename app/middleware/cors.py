"""CORS middleware configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import env


def setup_cors(app: FastAPI) -> None:
    """Add CORS middleware — allow all origins in dev, restricted in prod."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=env.CORS_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
