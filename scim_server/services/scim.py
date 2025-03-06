"""
Core SCIM service for interacting with Microsoft Entra ID through Graph API.
"""

import httpx
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status

from scim_server.models.user import EntraUserMapping
from scim_server.models.group import EntraGroupMapping
from scim_server.utils.filtering import SCIMFilter

class SCIMService:
    """
    Service for SCIM operations using Microsoft Graph API as the backend.
    """
    
    def __init__(self, access_token: str):
        """
        Initialize with Microsoft Graph API access token.
        """
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.graph_api_base = "https://graph.microsoft.com/v1.0"
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None):
        """
        Make a request to Microsoft Graph API.
        """
        url = f"{self.graph_api_base}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method.lower() == "get":
                response = await client.get(url, headers=self.headers)
            elif method.lower() == "post":
                response = await client.post(url, headers=self.headers, json=data)
            elif method.lower() == "put" or method.lower() == "patch":
                response = await client.patch(url, headers=self.headers, json=data)
            elif method.lower() == "delete":
                response = await client.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                except:
                    error_message = response.text or "Unknown error"
                    
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Graph API error: {error_message}"
                )
                
            return response
    
    # User-related operations
    
    async def get_users(self, filter_str: Optional[str] = None, start_index: int = 1, count: int = 100):
        """
        Get users from Microsoft Entra ID.
        """
        # Convert SCIM filter to Graph API filter
        graph_filter = SCIMFilter.convert_to_graph_filter(filter_str)
        filter_param = f"$filter={graph_filter}" if graph_filter else ""
        
        # Add pagination - only use $top for now (first page only)
        if start_index != 1:
            # For now, we'll return an error for pagination beyond the first page
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pagination beyond the first page is not supported yet"
            )
        
        pagination = f"$top={count}"
        
        # Build query string
        query = f"?{filter_param}&{pagination}" if filter_param else f"?{pagination}"
        
        # Make request
        response = await self._make_request("get", f"/users{query}")
        graph_users = response.json().get("value", [])
        
        # Convert to SCIM format
        scim_users = [EntraUserMapping(user).to_scim_dict() for user in graph_users]
        
        return {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": len(scim_users),
            "startIndex": start_index,
            "itemsPerPage": count,
            "Resources": scim_users
        }
    
    async def get_user(self, user_id: str):
        """
        Get a specific user from Microsoft Entra ID.
        """
        response = await self._make_request("get", f"/users/{user_id}")
        graph_user = response.json()
        
        return EntraUserMapping(graph_user).to_scim_dict()
    
    async def create_user(self, user_data: Dict[str, Any]):
        """
        Create a user in Microsoft Entra ID.
        """
        # Convert SCIM user to Graph API format
        graph_user = EntraUserMapping.from_scim_dict(user_data)
        
        # Add required fields for user creation
        if "userPrincipalName" not in graph_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username (userPrincipalName) is required"
            )
            
        # Password is required for new users in Entra ID
        if "passwordProfile" not in graph_user:
            graph_user["passwordProfile"] = {
                "forceChangePasswordNextSignIn": True,
                "password": "TemporaryP@ss" + str(hash(graph_user["userPrincipalName"]))[:8]
            }
        
        # Make request to create user
        response = await self._make_request("post", "/users", graph_user)
        created_user = response.json()
        
        return EntraUserMapping(created_user).to_scim_dict()
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]):
        """
        Update a user in Microsoft Entra ID.
        """
        # Convert SCIM user to Graph API format
        graph_user = EntraUserMapping.from_scim_dict(user_data)
        
        # Make request to update user
        response = await self._make_request("patch", f"/users/{user_id}", graph_user)
        
        # Get updated user
        updated_user = await self._make_request("get", f"/users/{user_id}")
        return EntraUserMapping(updated_user.json()).to_scim_dict()
    
    async def delete_user(self, user_id: str):
        """
        Delete a user in Microsoft Entra ID.
        """
        await self._make_request("delete", f"/users/{user_id}")
        return True
    
    # Group-related operations
    
    async def get_groups(self, filter_str: Optional[str] = None, start_index: int = 1, count: int = 100):
        """
        Get groups from Microsoft Entra ID.
        """
        # Convert SCIM filter to Graph API filter
        graph_filter = SCIMFilter.convert_to_graph_filter(filter_str)
        filter_param = f"$filter={graph_filter}" if graph_filter else ""
        
        # Add pagination - only use $top for now (first page only)
        if start_index != 1:
            # For now, we'll return an error for pagination beyond the first page
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pagination beyond the first page is not supported yet"
            )
        
        pagination = f"$top={count}"
        
        # Build query string
        query = f"?{filter_param}&{pagination}" if filter_param else f"?{pagination}"
        
        # Make request
        response = await self._make_request("get", f"/groups{query}")
        graph_groups = response.json().get("value", [])
        
        # Convert to SCIM format
        scim_groups = [EntraGroupMapping(group).to_scim_dict() for group in graph_groups]
        
        return {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": len(scim_groups),
            "startIndex": start_index,
            "itemsPerPage": count,
            "Resources": scim_groups
        }
    
    async def get_group(self, group_id: str):
        """
        Get a specific group from Microsoft Entra ID.
        """
        response = await self._make_request("get", f"/groups/{group_id}")
        graph_group = response.json()
        
        return EntraGroupMapping(graph_group).to_scim_dict()
    
    async def create_group(self, group_data: Dict[str, Any]):
        """
        Create a group in Microsoft Entra ID.
        """
        # Convert SCIM group to Graph API format
        graph_group = EntraGroupMapping.from_scim_dict(group_data)
        
        # Add required fields for group creation
        if "displayName" not in graph_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Display name is required"
            )
            
        # Add security enabled flag (required for Entra ID)
        if "securityEnabled" not in graph_group:
            graph_group["securityEnabled"] = True
            
        if "mailEnabled" not in graph_group:
            graph_group["mailEnabled"] = False
        
        # Make request to create group
        response = await self._make_request("post", "/groups", graph_group)
        created_group = response.json()
        
        return EntraGroupMapping(created_group).to_scim_dict()
    
    async def update_group(self, group_id: str, group_data: Dict[str, Any]):
        """
        Update a group in Microsoft Entra ID.
        """
        # Convert SCIM group to Graph API format
        graph_group = EntraGroupMapping.from_scim_dict(group_data)
        
        # Make request to update group
        response = await self._make_request("patch", f"/groups/{group_id}", graph_group)
        
        # Get updated group
        updated_group = await self._make_request("get", f"/groups/{group_id}")
        return EntraGroupMapping(updated_group.json()).to_scim_dict()
    
    async def delete_group(self, group_id: str):
        """
        Delete a group in Microsoft Entra ID.
        """
        await self._make_request("delete", f"/groups/{group_id}")
        return True
