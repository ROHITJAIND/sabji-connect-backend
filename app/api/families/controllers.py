"""Family controller — delegates to FamilyService."""

from app.api.families.schemas import (
    AddMemberToFamilyRequest,
    CreateFamilyRequest,
    FamilyMemberResponse,
    FamilyResponse,
    UpdateMemberRoleRequest,
)
from app.api.families.services import FamilyService
from app.models.user import User


class FamilyController:
    @staticmethod
    async def list_families(user: User) -> list[FamilyResponse]:
        return await FamilyService.list_families(user)

    @staticmethod
    async def create_family(body: CreateFamilyRequest, admin: User) -> FamilyResponse:
        return await FamilyService.create_family(body, admin)

    @staticmethod
    async def get_family(family_id: str) -> FamilyResponse:
        return await FamilyService.get_family(family_id)

    @staticmethod
    async def get_family_members(family_id: str) -> list[FamilyMemberResponse]:
        return await FamilyService.get_family_members(family_id)

    @staticmethod
    async def add_member(family_id: str, body: AddMemberToFamilyRequest) -> FamilyMemberResponse:
        return await FamilyService.add_member(family_id, body)

    @staticmethod
    async def update_member_role(
        family_id: str, user_id: str, body: UpdateMemberRoleRequest
    ) -> dict:
        return await FamilyService.update_member_role(family_id, user_id, body)

    @staticmethod
    async def remove_member(family_id: str, user_id: str) -> dict:
        return await FamilyService.remove_member(family_id, user_id)

    @staticmethod
    async def delete_family(family_id: str) -> dict:
        return await FamilyService.delete_family(family_id)
