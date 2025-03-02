"""
API routes for SCIM User endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from typing import Optional, Dict, Any

from scim_server.schemas.user import UserSchema, UserListResponse
from scim_server.services.scim import SCIMService
from scim_server.utils.auth import EntraAuth

router = APIRouter(prefix="/scim/v2/Users", tags=["Users"])

@router.get("", response_model=UserListResponse)
async def get_users(
    request: Request,
    filter: Optional[str] = None,
    startIndex: int = 1,
    count: int = 100,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Get a list of users with optional filtering and pagination.
    """
    scim_service = SCIMService(token)
    return await scim_service.get_users(filter, startIndex, count)

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Get a specific user by ID.
    """
    scim_service = SCIMService(token)
    return await scim_service.get_user(user_id)

@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserSchema,
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Create a new user.
    """
    scim_service = SCIMService(token)
    return await scim_service.create_user(user.dict(exclude_unset=True))

@router.put("/{user_id}", response_model=UserSchema)
async def replace_user(
    user_id: str,
    user: UserSchema,
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Replace a user (PUT).
    """
    scim_service = SCIMService(token)
    return await scim_service.update_user(user_id, user.dict(exclude_unset=True))

@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    user: Dict[str, Any],
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Update a user (PATCH).
    """
    scim_service = SCIMService(token)
    return await scim_service.update_user(user_id, user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    request: Request,
    token: str = Depends(EntraAuth.get_access_token)
):
    """
    Delete a user.
    """
    scim_service = SCIMService(token)
    await scim_service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
