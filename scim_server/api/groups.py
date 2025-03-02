"""
API routes for SCIM Group endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from typing import Optional, Dict, Any

from scim_server.schemas.group import GroupSchema, GroupListResponse
from scim_server.services.scim import SCIMService
from scim_server.utils.auth import EntraAuth

router = APIRouter(prefix="/scim/v2/Groups", tags=["Groups"])

@router.get("", response_model=GroupListResponse)
async def get_groups(
    request: Request,
    filter: Optional[str] = None,
    startIndex: int = 1,
    count: int = 100,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Get a list of groups with optional filtering and pagination.
    """
    scim_service = SCIMService(token)
    return await scim_service.get_groups(filter, startIndex, count)

@router.get("/{group_id}", response_model=GroupSchema)
async def get_group(
    group_id: str,
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Get a specific group by ID.
    """
    scim_service = SCIMService(token)
    return await scim_service.get_group(group_id)

@router.post("", response_model=GroupSchema, status_code=status.HTTP_201_CREATED)
async def create_group(
    group: GroupSchema,
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Create a new group.
    """
    scim_service = SCIMService(token)
    return await scim_service.create_group(group.dict(exclude_unset=True))

@router.put("/{group_id}", response_model=GroupSchema)
async def replace_group(
    group_id: str,
    group: GroupSchema,
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Replace a group (PUT).
    """
    scim_service = SCIMService(token)
    return await scim_service.update_group(group_id, group.dict(exclude_unset=True))

@router.patch("/{group_id}", response_model=GroupSchema)
async def update_group(
    group_id: str,
    group: Dict[str, Any],
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Update a group (PATCH).
    """
    scim_service = SCIMService(token)
    return await scim_service.update_group(group_id, group)

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: str,
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Delete a group.
    """
    scim_service = SCIMService(token)
    await scim_service.delete_group(group_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
