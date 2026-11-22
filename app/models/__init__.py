"""Beanie document models for Sabji Connect."""

from app.models.base import BaseDocument
from app.models.user import User
from app.models.family import Family
from app.models.catalog import CatalogItem
from app.models.order import Order, OrderItem
from app.models.requested_item import RequestedItem
from app.models.enums import (
    AllowedUnit,
    ItemCategory,
    ItemUnit,
    OrderStatus,
    RequestedItemStatus,
    UserRole,
)

DOCUMENT_MODELS: list = [
    User,
    Family,
    CatalogItem,
    Order,
    RequestedItem,
]

__all__ = [
    "BaseDocument",
    "User",
    "Family",
    "CatalogItem",
    "Order",
    "OrderItem",
    "RequestedItem",
    "UserRole",
    "OrderStatus",
    "ItemUnit",
    "AllowedUnit",
    "ItemCategory",
    "RequestedItemStatus",
    "DOCUMENT_MODELS",
]
