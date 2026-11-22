"""Order model — maps to the 'orders' collection in MongoDB."""

from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """An individual item within an order."""
    catalog_item_id: str
    name: str
    quantity: float = 1
    unit: str = "pieces"
    is_purchased: bool = False
    actual_quantity: Optional[float] = None
    actual_price: Optional[float] = None
    is_out_of_stock: bool = False
    image_url: Optional[str] = None


class Order(Document):
    status: str = "Draft"  # Draft | Published | Fulfilling | Archived
    items: list[OrderItem] = Field(default_factory=list)
    created_by: str  # User ID
    created_by_name: str = "Family Member"
    family_id: Optional[str] = None
    order_date: str = ""  # ISO date string YYYY-MM-DD
    fulfilled_by: Optional[str] = None  # User ID of Sethji
    publish_trigger: Optional[str] = None  # Timestamp for push notification dedup
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "orders"
