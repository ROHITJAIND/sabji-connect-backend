"""Order schemas."""

from typing import Any, Optional
from pydantic import BaseModel, Field
from app.models.enums import ItemUnit, OrderStatus


class OrderItemSchema(BaseModel):
    catalog_item_id: Optional[str] = None
    name: str
    qty: Optional[float] = None
    unit: Optional[str] = "pieces"
    status: str = "pending"


class CreateOrderRequest(BaseModel):
    order_date: Optional[str] = None
    family_id: Optional[str] = None
    items: Optional[list[dict[str, Any]]] = None
    status: Optional[OrderStatus] = None
    publish_trigger: Optional[str] = None


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
    totalExpense: Optional[float] = 0.0
    batchId: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
