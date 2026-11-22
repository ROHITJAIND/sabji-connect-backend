"""CatalogItem model — maps to the 'catalog' collection in MongoDB."""

from datetime import datetime, timezone
from typing import Optional

from beanie import Document
from pydantic import Field


class CatalogItem(Document):
    name: str
    category: str = "Vegetables"
    allowed_units: list[str] = Field(default_factory=lambda: ["pieces"])
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "catalog"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Tomato",
                "category": "Vegetables",
                "allowed_units": ["kg", "pieces"],
                "image_url": "https://res.cloudinary.com/demo/image/upload/tomato.jpg",
            }
        }
