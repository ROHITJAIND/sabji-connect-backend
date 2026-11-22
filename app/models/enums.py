"""Application Enums.

Defines typed enums for:
- UserRole: Admin, Hukum, Sethji
- OrderStatus: Draft, Published, Fulfilling, Archived
- ItemUnit / AllowedUnit: kg, grams, pieces, packets, bunches, liters, ml, boxes, dozens, bottles, plates
- ItemCategory: Vegetables, Fruits, Household, Packaged, Cosmetics, Others
- RequestedItemStatus: pending, approved, rejected
"""

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    HUKUM = "Hukum"
    SETHJI = "Sethji"


class OrderStatus(str, Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"
    FULFILLING = "Fulfilling"
    ARCHIVED = "Archived"


class ItemUnit(str, Enum):
    KG = "kg"
    GRAMS = "grams"
    PIECES = "pieces"
    PACKETS = "packets"
    BUNCHES = "bunches"
    LITERS = "liters"
    ML = "ml"
    BOXES = "boxes"
    DOZENS = "dozens"
    BOTTLES = "bottles"
    PLATES = "plates"


# Alias for explicit domain naming
AllowedUnit = ItemUnit


class ItemCategory(str, Enum):
    VEGETABLES = "Vegetables"
    FRUITS = "Fruits"
    HOUSEHOLD = "Household"
    PACKAGED = "Packaged"
    COSMETICS = "Cosmetics"
    OTHERS = "Others"


class RequestedItemStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
