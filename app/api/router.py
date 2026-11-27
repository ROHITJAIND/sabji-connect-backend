"""API router aggregation — imports each domain module router."""

from fastapi import APIRouter

from app.api.auth.routes import router as auth_router
from app.api.catalog.routes import router as catalog_router
from app.api.families.routes import router as families_router
from app.api.health.routes import router as health_router
from app.api.orders.routes import router as orders_router
from app.api.requested_items.routes import router as requested_items_router
from app.api.websocket.routes import router as websocket_router

# Base router for root / health check (mounted at root level)
base_router = APIRouter()
base_router.include_router(health_router)
base_router.include_router(websocket_router)

# API router — all domain endpoints mounted with /api prefix
api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(catalog_router)
api_router.include_router(families_router)
api_router.include_router(orders_router)
api_router.include_router(requested_items_router)
api_router.include_router(websocket_router)
