"""Requested Items service — business logic and DB operations."""

from beanie import PydanticObjectId

from app.api.requested_items.schemas import (
    ApproveRequestedItemRequest,
    CreateRequestedItemRequest,
    RequestedItemResponse,
)
from app.core.exceptions import NotFoundError
from app.models.catalog import CatalogItem
from app.models.enums import RequestedItemStatus, UserRole
from app.models.requested_item import RequestedItem
from app.models.user import User


class RequestedItemService:
    @staticmethod
    def serialize_item(item: RequestedItem) -> RequestedItemResponse:
        return RequestedItemResponse(
            id=str(item.id),
            name=item.name,
            requestedBy=item.requested_by,
            requestedById=item.requested_by_id,
            familyId=item.family_id,
            status=item.status,
            createdAt=item.created_at.isoformat() if item.created_at else None,
        )

    @staticmethod
    async def list_items(user: User) -> list[RequestedItemResponse]:
        if user.role == UserRole.ADMIN:
            items = await RequestedItem.find(
                RequestedItem.status == RequestedItemStatus.PENDING
            ).to_list()
        else:
            items = await RequestedItem.find(
                RequestedItem.requested_by_id == str(user.id)
            ).to_list()

        return [RequestedItemService.serialize_item(item) for item in items]

    @staticmethod
    async def request_item(user: User, body: CreateRequestedItemRequest) -> dict:
        item = RequestedItem(
            name=body.name,
            requested_by=user.display_name or user.email.split("@")[0],
            requested_by_id=str(user.id),
            family_id=user.family_id,
            status=RequestedItemStatus.PENDING,
        )
        await item.insert()
        return {"id": str(item.id), "name": item.name, "status": RequestedItemStatus.PENDING.value}

    @staticmethod
    async def approve_item(
        item_id: str, body: ApproveRequestedItemRequest
    ) -> dict:
        item = await RequestedItem.get(PydanticObjectId(item_id))
        if not item:
            raise NotFoundError("Requested item not found")

        catalog_item = CatalogItem(
            name=item.name,
            category=body.category,
            allowed_units=body.allowed_units,
        )
        await catalog_item.insert()

        await item.set({"status": RequestedItemStatus.APPROVED})

        return {
            "id": item_id,
            "catalogItemId": str(catalog_item.id),
            "message": "Approved and added to catalog",
        }

    @staticmethod
    async def reject_item(item_id: str) -> dict:
        item = await RequestedItem.get(PydanticObjectId(item_id))
        if not item:
            raise NotFoundError("Requested item not found")

        await item.set({"status": RequestedItemStatus.REJECTED})
        return {"id": item_id, "message": "Rejected"}
