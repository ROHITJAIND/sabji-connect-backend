"""Catalog controller — delegates to CatalogService."""

from typing import Optional

from app.api.catalog.schemas import (
    CatalogItemCreate,
    CatalogItemResponse,
    CatalogItemUpdate,
)
from app.api.catalog.services import CatalogService


class CatalogController:
    @staticmethod
    async def list_items(
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[CatalogItemResponse]:
        return await CatalogService.list_items(category, search)

    @staticmethod
    async def add_item(body: CatalogItemCreate) -> dict:
        return await CatalogService.add_item(body)

    @staticmethod
    async def update_item(item_id: str, body: CatalogItemUpdate) -> dict:
        return await CatalogService.update_item(item_id, body)

    @staticmethod
    async def delete_item(item_id: str) -> dict:
        return await CatalogService.delete_item(item_id)
