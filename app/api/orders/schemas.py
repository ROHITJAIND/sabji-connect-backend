"""Order schemas."""

from typing import Any, Optional
from pydantic import BaseModel, Field
from app.models.enums import ItemUnit, OrderStatus


class OrderItemSchema(BaseModel):
    catalog_item_id: str
    name: str
    quantity: float = 1
    unit: ItemUnit = ItemUnit.PIECES
    is_purchased: bool = False
    actual_quantity: Optional[float] = None
    actual_price: Optional[float] = None
    is_out_of_stock: bool = False
    image_url: Optional[str] = None


class CreateOrderRequest(BaseModel):
    order_date: Optional[str] = None


class OrderResponse(BaseModel):
    id: str
    status: OrderStatus
    items: list[dict[str, Any]]
    createdBy: str
    createdByName: str
    familyId: Optional[str] = None
    orderDate: str
    fulfilledBy: Optional[str] = None
    publishTrigger: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
