"""Order schemas."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class OrderItemSchema(BaseModel):
    catalog_item_id: str
    name: str
    quantity: float = 1
    unit: str = "pieces"
    is_purchased: bool = False
    actual_quantity: Optional[float] = None
    actual_price: Optional[float] = None
    is_out_of_stock: bool = False
    image_url: Optional[str] = None


class CreateOrderRequest(BaseModel):
    order_date: Optional[str] = None


class OrderResponse(BaseModel):
    id: str
    status: str
    items: list[dict[str, Any]]
    createdBy: str
    createdByName: str
    familyId: Optional[str] = None
    orderDate: str
    fulfilledBy: Optional[str] = None
    publishTrigger: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
