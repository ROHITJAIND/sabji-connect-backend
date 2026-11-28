"""CatalogItem model — maps to the 'catalog' collection in MongoDB."""

from typing import Optional
from beanie import Document
from pydantic import Field
from app.models.base import BaseDocument
from app.models.enums import ItemCategory, ItemUnit


class CatalogItem(Document, BaseDocument):
    name: str
    category: ItemCategory = ItemCategory.VEGETABLES
    allowed_units: list[ItemUnit] = Field(default_factory=lambda: [ItemUnit.PIECES])
    image_url: Optional[str] = None
    is_active: bool = True

    class Settings:
        name = "catalog"
