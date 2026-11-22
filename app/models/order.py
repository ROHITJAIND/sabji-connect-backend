"""Order model — maps to the 'orders' collection in MongoDB."""

from typing import Optional
from pydantic import BaseModel, Field
from app.models.base import BaseDocument
from app.models.enums import ItemUnit, OrderStatus


class OrderItem(BaseModel):
    """An individual item within an order."""
    catalog_item_id: str
    name: str
    quantity: float = 1
    unit: ItemUnit = ItemUnit.PIECES
    is_purchased: bool = False
    actual_quantity: Optional[float] = None
    actual_price: Optional[float] = None
    is_out_of_stock: bool = False
    image_url: Optional[str] = None


class Order(BaseDocument):
    status: OrderStatus = OrderStatus.DRAFT
    items: list[OrderItem] = Field(default_factory=list)
    created_by_name: str = "Family Member"
    family_id: Optional[str] = None
    order_date: str = ""  # ISO date string YYYY-MM-DD
    fulfilled_by: Optional[str] = None  # User ID of Sethji
    publish_trigger: Optional[str] = None  # Timestamp for push notification dedup

    class Settings:
        name = "orders"
