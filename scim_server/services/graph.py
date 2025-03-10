"""
Extended service for interacting with Microsoft Graph API.
"""

import httpx
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status

from scim_server.models.user import EntraUserMapping
from scim_server.models.group import EntraGroupMapping
from scim_server.models.application import EntraApplicationMapping
from scim_server.models.service_principal import EntraServicePrincipalMapping
from scim_server.utils.filtering import SCIMFilter

class EntraGraphService:
    """
    Service for Microsoft Graph API operations with pagination support.
    """
    
    def __init__(self, access_token: str):
        """
        Initialize with Microsoft Graph API access token.
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.graph_api_base = "https://graph.microsoft.com/v1.0"
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None):
        """
        Make a request to Microsoft Graph API.
        """
        url = f"{self.graph_api_base}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
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
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Error connecting to Graph API: {str(e)}"
                )
    
    async def _paginated_request(self, endpoint: str, start_index: int = 1, count: int = 100, filter_str: Optional[str] = None):
        """
        Make a paginated request to Microsoft Graph API.
        """
        # Calculate skip based on start_index (SCIM is 1-based, Graph API is 0-based)
        skip = start_index - 1 if start_index > 1 else 0
        
        # Build query parameters
        params = []
        if filter_str:
            params.append(f"$filter={filter_str}")
        if skip > 0:
            params.append(f"$skip={skip}")
        params.append(f"$top={count}")
        params.append("$count=true")  # Request total count
        
        # Build query string
        query = "?" + "&".join(params) if params else ""
        
        # Make request
        response = await self._make_request("get", f"{endpoint}{query}")
        result = response.json()
        
        # Get total count if available
        total_count = result.get("@odata.count", len(result.get("value", [])))
        
        return {
            "value": result.get("value", []),
            "totalCount": total_count
        }
    
    # User-related operations
    
    async def get_users(self, filter_str: Optional[str] = None, start_index: int = 1, count: int = 100):
        """
        Get users from Microsoft Entra ID with pagination.
        """
        # Convert SCIM filter to Graph API filter if provided
        graph_filter = SCIMFilter.convert_to_graph_filter(filter_str) if filter_str else None
        
        # Make paginated request
        result = await self._paginated_request("/users", start_index, count, graph_filter)
        graph_users = result["value"]
        total_count = result["totalCount"]
        
        # Convert to SCIM format
        scim_users = [EntraUserMapping(user).to_scim_dict() for user in graph_users]
        
        return {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": total_count,
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
        Get groups from Microsoft Entra ID with pagination.
        """
        # Convert SCIM filter to Graph API filter if provided
        graph_filter = SCIMFilter.convert_to_graph_filter(filter_str) if filter_str else None
        
        # Make paginated request
        result = await self._paginated_request("/groups", start_index, count, graph_filter)
        graph_groups = result["value"]
        total_count = result["totalCount"]
        
        # Convert to SCIM format
        scim_groups = [EntraGroupMapping(group).to_scim_dict() for group in graph_groups]
        
        return {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": total_count,
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
    
    # Application-related operations
    
    async def get_applications(self, filter_str: Optional[str] = None, start_index: int = 1, count: int = 100):
        """
        Get applications from Microsoft Entra ID with pagination.
        """
        # Convert SCIM filter to Graph API filter if provided
        graph_filter = SCIMFilter.convert_to_graph_filter(filter_str) if filter_str else None
        
        # Make paginated request
        result = await self._paginated_request("/applications", start_index, count, graph_filter)
        graph_apps = result["value"]
        total_count = result["totalCount"]
        
        # Convert to SCIM format
        scim_apps = [EntraApplicationMapping(app).to_scim_dict() for app in graph_apps]
        
        return {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": total_count,
            "startIndex": start_index,
            "itemsPerPage": count,
            "Resources": scim_apps
        }
    
    async def get_application(self, app_id: str):
        """
        Get a specific application from Microsoft Entra ID.
        """
        response = await self._make_request("get", f"/applications/{app_id}")
        graph_app = response.json()
        
        return EntraApplicationMapping(graph_app).to_scim_dict()
    
    async def create_application(self, app_data: Dict[str, Any]):
        """
        Create an application in Microsoft Entra ID.
        """
        # Convert SCIM application to Graph API format
        graph_app = EntraApplicationMapping.from_scim_dict(app_data)
        
        # Add required fields for application creation
        if "displayName" not in graph_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Display name is required"
            )
        
        # Make request to create application
        response = await self._make_request("post", "/applications", graph_app)
        created_app = response.json()
        
        return EntraApplicationMapping(created_app).to_scim_dict()
    
    async def update_application(self, app_id: str, app_data: Dict[str, Any]):
        """
        Update an application in Microsoft Entra ID.
        """
        # Convert SCIM application to Graph API format
        graph_app = EntraApplicationMapping.from_scim_dict(app_data)
        
        # Make request to update application
        response = await self._make_request("patch", f"/applications/{app_id}", graph_app)
        
        # Get updated application
        updated_app = await self._make_request("get", f"/applications/{app_id}")
        return EntraApplicationMapping(updated_app.json()).to_scim_dict()
    
    async def delete_application(self, app_id: str):
        """
        Delete an application in Microsoft Entra ID.
        """
        await self._make_request("delete", f"/applications/{app_id}")
        return True
    
    # Service Principal-related operations
    
    async def get_service_principals(self, filter_str: Optional[str] = None, start_index: int = 1, count: int = 100):
        """
        Get service principals from Microsoft Entra ID with pagination.
        """
        # Convert SCIM filter to Graph API filter if provided
        graph_filter = SCIMFilter.convert_to_graph_filter(filter_str) if filter_str else None
        
        # Make paginated request
        result = await self._paginated_request("/servicePrincipals", start_index, count, graph_filter)
        graph_sps = result["value"]
        total_count = result["totalCount"]
        
        # Convert to SCIM format
        scim_sps = [EntraServicePrincipalMapping(sp).to_scim_dict() for sp in graph_sps]
        
        return {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": total_count,
            "startIndex": start_index,
            "itemsPerPage": count,
            "Resources": scim_sps
        }
    
    async def get_service_principal(self, sp_id: str):
        """
        Get a specific service principal from Microsoft Entra ID.
        """
        response = await self._make_request("get", f"/servicePrincipals/{sp_id}")
        graph_sp = response.json()
        
        return EntraServicePrincipalMapping(graph_sp).to_scim_dict()
    
    async def create_service_principal(self, sp_data: Dict[str, Any]):
        """
        Create a service principal in Microsoft Entra ID.
        """
        # Convert SCIM service principal to Graph API format
        graph_sp = EntraServicePrincipalMapping.from_scim_dict(sp_data)
        
        # Check if appId is provided (required for service principal creation)
        if "appId" not in graph_sp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application ID (appId) is required"
            )
        
        # Make request to create service principal
        response = await self._make_request("post", "/servicePrincipals", graph_sp)
        created_sp = response.json()
        
        return EntraServicePrincipalMapping(created_sp).to_scim_dict()
    
    async def update_service_principal(self, sp_id: str, sp_data: Dict[str, Any]):
        """
        Update a service principal in Microsoft Entra ID.
        """
        # Convert SCIM service principal to Graph API format
        graph_sp = EntraServicePrincipalMapping.from_scim_dict(sp_data)
        
        # Make request to update service principal
        response = await self._make_request("patch", f"/servicePrincipals/{sp_id}", graph_sp)
        
        # Get updated service principal
        updated_sp = await self._make_request("get", f"/servicePrincipals/{sp_id}")
        return EntraServicePrincipalMapping(updated_sp.json()).to_scim_dict()
    
    async def delete_service_principal(self, sp_id: str):
        """
        Delete a service principal in Microsoft Entra ID.
        """
        await self._make_request("delete", f"/servicePrincipals/{sp_id}")
        return True
