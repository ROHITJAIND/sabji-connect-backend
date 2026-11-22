"""Family model — maps to the 'families' collection in MongoDB."""

from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import Field


class Family(Document):
    name: str
    created_by: Optional[str] = None  # User ID of the Admin who created it
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "families"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Shah Family",
            }
        }
