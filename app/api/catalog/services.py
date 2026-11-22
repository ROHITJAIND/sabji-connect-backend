"""Catalog service — business logic and DB operations."""

from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId

from app.api.catalog.schemas import (
    CatalogItemCreate,
    CatalogItemResponse,
    CatalogItemUpdate,
)
from app.api.websocket.services import ws_manager
from app.core.exceptions import NotFoundError
from app.models.catalog import CatalogItem


class CatalogService:
    @staticmethod
    def serialize_item(item: CatalogItem) -> CatalogItemResponse:
        return CatalogItemResponse(
            id=str(item.id),
            name=item.name,
            category=item.category,
            allowedUnits=item.allowed_units,
            imageUrl=item.image_url,
        )

    @staticmethod
    async def list_items(
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[CatalogItemResponse]:
        filters = {"is_active": True}
        if category and category != "All":
            filters["category"] = category

        items = await CatalogItem.find(filters).to_list()

        if search:
            search_lower = search.lower()
            items = [i for i in items if search_lower in i.name.lower()]

        return [CatalogService.serialize_item(item) for item in items]

    @staticmethod
    async def add_item(body: CatalogItemCreate) -> dict:
        item = CatalogItem(
            name=body.name,
            category=body.category,
            allowed_units=body.allowed_units,
            image_url=body.image_url,
        )
        await item.insert()

        await ws_manager.broadcast_to_all(
            "catalog_updated", {"action": "added", "id": str(item.id)}
        )
        return {"id": str(item.id), "name": item.name}

    @staticmethod
    async def update_item(item_id: str, body: CatalogItemUpdate) -> dict:
        item = await CatalogItem.get(PydanticObjectId(item_id))
        if not item:
            raise NotFoundError("Catalog item not found")

        update_data: dict = {"updated_at": datetime.now(timezone.utc)}
        if body.name is not None:
            update_data["name"] = body.name
        if body.category is not None:
            update_data["category"] = body.category
        if body.allowed_units is not None:
            update_data["allowed_units"] = body.allowed_units
        if body.image_url is not None:
            update_data["image_url"] = body.image_url

        await item.set(update_data)

        await ws_manager.broadcast_to_all(
            "catalog_updated", {"action": "updated", "id": item_id}
        )
        return {"id": item_id, "message": "Updated"}

    @staticmethod
    async def delete_item(item_id: str) -> dict:
        item = await CatalogItem.get(PydanticObjectId(item_id))
        if not item:
            raise NotFoundError("Catalog item not found")

        await item.set({"is_active": False, "updated_at": datetime.now(timezone.utc)})

        await ws_manager.broadcast_to_all(
            "catalog_updated", {"action": "deleted", "id": item_id}
        )
        return {"id": item_id, "message": "Deleted"}
