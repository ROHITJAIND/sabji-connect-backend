"""Catalog routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.catalog.controllers import CatalogController
from app.api.catalog.schemas import (
    CatalogItemCreate,
    CatalogItemResponse,
    CatalogItemUpdate,
)
from app.core.auth.dependencies import CurrentUser, require_role

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("/", response_model=list[CatalogItemResponse])
async def list_catalog(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name"),
    user: CurrentUser = None,
):
    """List all active catalog items."""
    return await CatalogController.list_items(category, search)


@router.post("/", dependencies=[Depends(require_role("Admin"))])
async def add_catalog_item(body: CatalogItemCreate):
    """Admin-only: Add a new item to the catalog."""
    return await CatalogController.add_item(body)


@router.patch("/{item_id}", dependencies=[Depends(require_role("Admin"))])
async def update_catalog_item(item_id: str, body: CatalogItemUpdate):
    """Admin-only: Update a catalog item."""
    return await CatalogController.update_item(item_id, body)


@router.delete("/{item_id}", dependencies=[Depends(require_role("Admin"))])
async def delete_catalog_item(item_id: str):
    """Admin-only: Soft-delete a catalog item."""
    return await CatalogController.delete_item(item_id)
