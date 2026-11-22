"""RequestedItem model — maps to the 'requested_items' collection in MongoDB."""

from typing import Optional
from app.models.base import BaseDocument
from app.models.enums import RequestedItemStatus


class RequestedItem(BaseDocument):
    name: str
    requested_by: str  # Display name of the requester
    requested_by_id: str  # User ID
    family_id: Optional[str] = None
    status: RequestedItemStatus = RequestedItemStatus.PENDING

    class Settings:
        name = "requested_items"
