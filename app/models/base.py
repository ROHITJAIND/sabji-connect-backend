"""Base model for all Beanie MongoDB documents in Sabji Connect."""

from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from beanie import Document, PydanticObjectId
from pydantic import Field, field_validator


class BaseDocument(Document):
    """
    Base document inherited by all collection models.
    Provides:
      - id: _id as PydanticObjectId (MongoDB BSON ObjectId)
      - created_by: PydanticObjectId (MongoDB BSON ObjectId)
      - updated_by: PydanticObjectId (MongoDB BSON ObjectId)
      - created_at: ISODate (Python datetime UTC)
      - updated_at: ISODate (Python datetime UTC)
    """

    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("created_by", "updated_by", mode="before")
    @classmethod
    def validate_object_id(cls, v):
        if not v:
            return None
        if isinstance(v, (PydanticObjectId, ObjectId)):
            return PydanticObjectId(str(v))
        if isinstance(v, str) and PydanticObjectId.is_valid(v):
            return PydanticObjectId(v)
        return None

    class Settings:
        is_root = True
