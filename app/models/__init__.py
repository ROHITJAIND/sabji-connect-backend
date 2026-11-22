"""Beanie document models for Sabji Connect."""

from app.models.user import User
from app.models.family import Family
from app.models.catalog import CatalogItem
from app.models.order import Order
from app.models.requested_item import RequestedItem

DOCUMENT_MODELS: list = [
    User,
    Family,
    CatalogItem,
    Order,
    RequestedItem,
]
