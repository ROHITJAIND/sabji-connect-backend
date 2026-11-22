"""Requested Items controller — delegates to RequestedItemService."""

from app.api.requested_items.schemas import (
    ApproveRequestedItemRequest,
    CreateRequestedItemRequest,
    RequestedItemResponse,
)
from app.api.requested_items.services import RequestedItemService
from app.models.user import User


class RequestedItemController:
    @staticmethod
    async def list_items(user: User) -> list[RequestedItemResponse]:
        return await RequestedItemService.list_items(user)

    @staticmethod
    async def request_item(user: User, body: CreateRequestedItemRequest) -> dict:
        return await RequestedItemService.request_item(user, body)

    @staticmethod
    async def approve_item(
        item_id: str, body: ApproveRequestedItemRequest
    ) -> dict:
        return await RequestedItemService.approve_item(item_id, body)

    @staticmethod
    async def reject_item(item_id: str) -> dict:
        return await RequestedItemService.reject_item(item_id)
