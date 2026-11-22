"""Requested Items routes."""

from fastapi import APIRouter, Depends

from app.api.requested_items.controllers import RequestedItemController
from app.api.requested_items.schemas import (
    ApproveRequestedItemRequest,
    CreateRequestedItemRequest,
    RequestedItemResponse,
)
from app.core.auth.dependencies import CurrentUser, require_role

router = APIRouter(prefix="/requested-items", tags=["Requested Items"])


@router.get("/", response_model=list[RequestedItemResponse])
async def list_requested_items(user: CurrentUser):
    """List requested items (Admin: all pending, Hukum: own requests)."""
    return await RequestedItemController.list_items(user)


@router.post("/")
async def request_custom_item(body: CreateRequestedItemRequest, user: CurrentUser):
    """Hukum: request a custom item not present in the catalog."""
    return await RequestedItemController.request_item(user, body)


@router.patch("/{item_id}/approve", dependencies=[Depends(require_role("Admin"))])
async def approve_requested_item(
    item_id: str,
    body: ApproveRequestedItemRequest = ApproveRequestedItemRequest(),
):
    """Admin: approve a requested item and add it to the catalog."""
    return await RequestedItemController.approve_item(item_id, body)


@router.patch("/{item_id}/reject", dependencies=[Depends(require_role("Admin"))])
async def reject_requested_item(item_id: str):
    """Admin: reject a requested item."""
    return await RequestedItemController.reject_item(item_id)
