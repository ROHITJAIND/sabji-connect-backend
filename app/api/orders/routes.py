"""Order routes."""

from typing import Optional

from fastapi import APIRouter

from app.api.orders.controllers import OrderController
from app.api.orders.schemas import CreateOrderRequest, OrderResponse
from app.core.auth.dependencies import CurrentUser

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=list[OrderResponse])
async def list_orders(user: CurrentUser):
    """List orders based on user role (Admin: all, Sethji: family active, Hukum: own)."""
    return await OrderController.list_orders(user)


@router.post("/", response_model=OrderResponse)
async def create_order(user: CurrentUser, body: Optional[CreateOrderRequest] = None):
    """Create a new Draft order."""
    return await OrderController.create_order(user, body)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, user: CurrentUser):
    """Get a single order by ID."""
    return await OrderController.get_order(order_id)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: str, body: dict, user: CurrentUser):
    """Update order fields (status, items, etc.)."""
    return await OrderController.update_order(order_id, body)


@router.delete("/{order_id}")
async def delete_order(order_id: str, user: CurrentUser):
    """Delete an order."""
    return await OrderController.delete_order(order_id, user)
