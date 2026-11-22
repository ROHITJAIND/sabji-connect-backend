"""RequestedItem model — maps to the 'requested_items' collection in MongoDB."""

from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import Field


class RequestedItem(Document):
    name: str
    requested_by: str  # Display name of the requester
    requested_by_id: str  # User ID
    family_id: Optional[str] = None
    status: str = "pending"  # pending | approved | rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "requested_items"
