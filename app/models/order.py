"""Order model — maps to the 'orders' collection in MongoDB."""

from typing import Any, Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, model_validator
from app.models.base import BaseDocument
from app.models.enums import OrderStatus


class OrderItem(BaseModel):
    """An individual item within an order."""
    catalog_item_id: Optional[PydanticObjectId] = None
    name: str
    qty: Optional[float] = None
    unit: Optional[str] = "pieces"
    status: str = "pending"

    @model_validator(mode="before")
    @classmethod
    def clean_item_fields(cls, data: Any):
        if isinstance(data, dict):
            cid = data.get("catalog_item_id") or data.get("catalogId")
            if cid:
                try:
                    cid = PydanticObjectId(str(cid))
                except Exception:
                    cid = None
            qty = data.get("qty")
            if qty is None and "quantity" in data:
                qty = data["quantity"]
            return {
                "catalog_item_id": cid,
                "name": data.get("name") or "",
                "qty": qty,
                "unit": data.get("unit") or "pieces",
                "status": data.get("status") or "pending",
            }
        return data


class Order(Document, BaseDocument):
    status: OrderStatus = OrderStatus.DRAFT
    items: list[OrderItem] = Field(default_factory=list)
    created_by_name: str = "Family Member"
    family_id: Optional[str] = None
    order_date: str = ""  # ISO date string YYYY-MM-DD
    fulfilled_by: Optional[str] = None  # User ID of Sethji
    publish_trigger: Optional[str] = None  # Timestamp for push notification dedup
    total_expense: Optional[float] = 0.0
    batch_id: Optional[str] = None

    class Settings:
        name = "orders"
