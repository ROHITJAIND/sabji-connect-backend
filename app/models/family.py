"""Family model — maps to the 'families' collection in MongoDB."""

from bson import ObjectId
from beanie import Document, PydanticObjectId
from pydantic import Field, field_validator
from app.models.base import BaseDocument


class Family(Document, BaseDocument):
    name: str
    members: list[PydanticObjectId] = Field(default_factory=list)

    @field_validator("members", mode="before")
    @classmethod
    def validate_members(cls, v):
        if not v:
            return []
        res = []
        for item in v:
            if isinstance(item, (PydanticObjectId, ObjectId)):
                res.append(PydanticObjectId(str(item)))
            elif isinstance(item, str) and PydanticObjectId.is_valid(item):
                res.append(PydanticObjectId(item))
        return res

    class Settings:
        name = "families"
