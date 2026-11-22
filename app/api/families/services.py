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
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.family import Family
from app.models.user import User


class FamilyService:
    @staticmethod
    async def list_families(user: User) -> list[FamilyResponse]:
        if user.role == "Admin":
            families = await Family.find_all().to_list()
        else:
            fids = list(user.family_ids or [])
            if user.family_id and user.family_id not in fids:
                fids.append(user.family_id)
            if not fids:
                return []
            obj_ids = [PydanticObjectId(fid) for fid in fids if PydanticObjectId.is_valid(fid)]
            families = await Family.find({"_id": {"$in": obj_ids}}).to_list()

        return [FamilyResponse(id=str(f.id), name=f.name, members=[str(m) for m in (f.members or [])]) for f in families]

    @staticmethod
    async def create_family(body: CreateFamilyRequest, admin: User) -> FamilyResponse:
        family = Family(
            name=body.name,
            created_by=admin.id,
            updated_by=admin.id,
            members=[],
        )
        await family.insert()
        return FamilyResponse(id=str(family.id), name=family.name, members=[])

    @staticmethod
    async def get_family(family_id: str) -> FamilyResponse:
        family = await Family.get(PydanticObjectId(family_id))
        if not family:
            raise NotFoundError("Family not found")
        return FamilyResponse(
            id=str(family.id),
            name=family.name,
            members=[str(m) for m in (family.members or [])],
        )

    @staticmethod
    async def update_family(family_id: str, body: UpdateFamilyRequest) -> FamilyResponse:
        family = await Family.get(PydanticObjectId(family_id))
        if not family:
            raise NotFoundError("Family not found")
        family.name = body.name.strip()
        family.updated_at = datetime.now(timezone.utc)
        await family.save()
        return FamilyResponse(
            id=str(family.id),
            name=family.name,
            members=[str(m) for m in (family.members or [])],
        )

    @staticmethod
    async def get_family_members(family_id: str) -> list[FamilyMemberResponse]:
        family = await Family.get(PydanticObjectId(family_id))
        if not family:
            raise NotFoundError("Family not found")

        member_oids = family.members or []
        members = await User.find(
            {
                "$or": [
                    {"_id": {"$in": member_oids}},
                    {"family_ids": family_id},
                    {"family_id": family_id},
                ],
                "is_active": True,
            }
        ).to_list()
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
            if m.role != "Admin"
        ]

    @staticmethod
    async def add_member(family_id: str, body: AddMemberToFamilyRequest) -> FamilyMemberResponse:
        family = await Family.get(PydanticObjectId(family_id))
        if not family:
            raise NotFoundError("Family not found")

        user = await User.get(PydanticObjectId(body.user_id))
        if not user or not user.is_active:
            raise NotFoundError("User not found or deactivated")

        if user.role == "Admin":
            raise BadRequestError("Admins cannot be assigned to a specific family; they have global access to all families.")

        # Update Family members list with user's ObjectId
        user_oid = user.id if isinstance(user.id, PydanticObjectId) else PydanticObjectId(str(user.id))
        fam_members = list(family.members or [])
        if user_oid not in fam_members:
            fam_members.append(user_oid)
            family.members = fam_members
            family.updated_at = datetime.now(timezone.utc)
            await family.save()

        # Update User's family_ids list
        fids = list(user.family_ids or [])
        if user.family_id and user.family_id not in fids:
            fids.append(user.family_id)
        if family_id not in fids:
            fids.append(family_id)

        await user.set(
            {
                "family_ids": fids,
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
        if not member:
            raise NotFoundError("User not found")

        # Update Family members list
        family = await Family.get(PydanticObjectId(family_id))
        if family:
            user_oid = member.id if isinstance(member.id, PydanticObjectId) else PydanticObjectId(str(member.id))
            fam_members = [m for m in (family.members or []) if m != user_oid]
            family.members = fam_members
            family.updated_at = datetime.now(timezone.utc)
            await family.save()

        # Update User's family_ids list
        fids = [f for f in (member.family_ids or []) if f != family_id]
        new_primary = fids[0] if fids else None

        await member.set(
            {
                "family_ids": fids,
                "family_id": new_primary,
                "updated_at": datetime.now(timezone.utc),
            }
        )
        return {"id": user_id, "message": "User removed from family"}

    @staticmethod
    async def delete_family(family_id: str) -> dict:
        family = await Family.get(PydanticObjectId(family_id))
        if not family:
            raise NotFoundError("Family not found")

        affected_users = await User.find(
            {"$or": [{"family_ids": family_id}, {"family_id": family_id}]}
        ).to_list()
        for m in affected_users:
            fids = [f for f in (m.family_ids or []) if f != family_id]
            new_primary = fids[0] if fids else None
            await m.set({
                "family_ids": fids,
                "family_id": new_primary,
                "updated_at": datetime.now(timezone.utc),
            })

        await family.delete()
        return {"id": family_id, "message": "Family deleted and members unassigned"}
