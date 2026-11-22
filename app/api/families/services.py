"""Family service — business logic and DB operations."""

from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId

from app.api.families.schemas import (
    AddMemberToFamilyRequest,
    CreateFamilyRequest,
    FamilyMemberResponse,
    FamilyResponse,
    UpdateFamilyRequest,
)
from app.core.exceptions import NotFoundError
from app.models.family import Family
from app.models.user import User


class FamilyService:
    @staticmethod
    async def list_families(user: User) -> list[FamilyResponse]:
        if user.role == "Admin":
            families = await Family.find_all().to_list()
        elif user.family_id:
            family = await Family.get(PydanticObjectId(user.family_id))
            families = [family] if family else []
        else:
            families = []

        return [FamilyResponse(id=str(f.id), name=f.name) for f in families]

    @staticmethod
    async def create_family(body: CreateFamilyRequest, admin: User) -> FamilyResponse:
        family = Family(name=body.name, created_by=str(admin.id))
        await family.insert()
        return FamilyResponse(id=str(family.id), name=family.name)

    @staticmethod
    async def get_family(family_id: str) -> FamilyResponse:
        family = await Family.get(PydanticObjectId(family_id))
        if not family:
            raise NotFoundError("Family not found")
        return FamilyResponse(id=str(family.id), name=family.name)

    @staticmethod
    async def update_family(family_id: str, body: UpdateFamilyRequest) -> FamilyResponse:
        family = await Family.get(PydanticObjectId(family_id))
        if not family:
            raise NotFoundError("Family not found")
        family.name = body.name.strip()
        family.updated_at = datetime.now(timezone.utc)
        await family.save()
        return FamilyResponse(id=str(family.id), name=family.name)

    @staticmethod
    async def get_family_members(family_id: str) -> list[FamilyMemberResponse]:
        members = await User.find(User.family_id == family_id, User.is_active == True).to_list()
        return [
            FamilyMemberResponse(
                id=str(m.id),
                email=m.email,
                displayName=m.display_name,
                role=m.role,
                avatarUrl=m.avatar_url,
                isActive=m.is_active,
            )
            for m in members
        ]

    @staticmethod
    async def add_member(family_id: str, body: AddMemberToFamilyRequest) -> FamilyMemberResponse:
        family = await Family.get(PydanticObjectId(family_id))
        if not family:
            raise NotFoundError("Family not found")

        user = await User.get(PydanticObjectId(body.user_id))
        if not user or not user.is_active:
            raise NotFoundError("User not found or deactivated")

        await user.set(
            {
                "family_id": family_id,
                "updated_at": datetime.now(timezone.utc),
            }
        )

        return FamilyMemberResponse(
            id=str(user.id),
            email=user.email,
            displayName=user.display_name,
            role=user.role,
            avatarUrl=user.avatar_url,
            isActive=user.is_active,
        )

    @staticmethod
    async def remove_member(family_id: str, user_id: str) -> dict:
        member = await User.get(PydanticObjectId(user_id))
        if not member or member.family_id != family_id:
            raise NotFoundError("Member not found in this family")

        await member.set(
            {
                "family_id": None,
                "updated_at": datetime.now(timezone.utc),
            }
        )
        return {"id": user_id, "message": "User removed from family"}

    @staticmethod
    async def delete_family(family_id: str) -> dict:
        family = await Family.get(PydanticObjectId(family_id))
        if not family:
            raise NotFoundError("Family not found")

        # Unassign any users belonging to this family
        members = await User.find(User.family_id == family_id).to_list()
        for m in members:
            await m.set({"family_id": None, "updated_at": datetime.now(timezone.utc)})

        await family.delete()
        return {"id": family_id, "message": "Family deleted and members unassigned"}
