"""Family routes."""

from fastapi import APIRouter, Depends

from app.api.families.controllers import FamilyController
from app.api.families.schemas import (
    AddMemberToFamilyRequest,
    CreateFamilyRequest,
    FamilyMemberResponse,
    FamilyResponse,
    UpdateFamilyRequest,
)
from app.core.auth.dependencies import CurrentUser, require_role

router = APIRouter(prefix="/families", tags=["Families"])


@router.get("/", response_model=list[FamilyResponse])
async def list_families(user: CurrentUser):
    """List all families (Admin) or user's assigned family."""
    return await FamilyController.list_families(user)


@router.post("/", response_model=FamilyResponse, dependencies=[Depends(require_role("Admin"))])
async def create_family(body: CreateFamilyRequest, admin: CurrentUser):
    """Admin-only: Create a new family."""
    return await FamilyController.create_family(body, admin)


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(family_id: str, user: CurrentUser):
    """Get family details by family_id."""
    return await FamilyController.get_family(family_id)


@router.patch("/{family_id}", response_model=FamilyResponse, dependencies=[Depends(require_role("Admin"))])
async def update_family(family_id: str, body: UpdateFamilyRequest):
    """Admin-only: Update family name."""
    return await FamilyController.update_family(family_id, body)


@router.get("/{family_id}/members", response_model=list[FamilyMemberResponse])
async def get_family_members(family_id: str, user: CurrentUser):
    """Get all members belonging to a family."""
    return await FamilyController.get_family_members(family_id)


@router.post("/{family_id}/members", response_model=FamilyMemberResponse, dependencies=[Depends(require_role("Admin"))])
async def add_member_to_family(family_id: str, body: AddMemberToFamilyRequest):
    """Admin-only: Add a user to a family (updates user's family_id)."""
    return await FamilyController.add_member(family_id, body)


@router.delete("/{family_id}/members/{user_id}", dependencies=[Depends(require_role("Admin"))])
async def remove_member(family_id: str, user_id: str):
    """Admin-only: Remove a member from a family (clears family_id back to null)."""
    return await FamilyController.remove_member(family_id, user_id)


@router.delete("/{family_id}", dependencies=[Depends(require_role("Admin"))])
async def delete_family(family_id: str):
    """Admin-only: Delete a family and unassign all its members."""
    return await FamilyController.delete_family(family_id)
