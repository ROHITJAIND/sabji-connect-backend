"""Health check routes."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    return {"status": "ok", "app": "Sabji Connect", "version": "1.0.0"}


@router.get("/health")
async def health():
    return {"status": "healthy"}
