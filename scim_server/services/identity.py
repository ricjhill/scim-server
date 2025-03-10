"""
Unified manager for Microsoft Entra ID identity types.
"""

import msal
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status

from scim_server.config import settings
from scim_server.utils.auth import EntraAuth
from scim_server.services.graph import EntraGraphService

class EntraIdentityManager:
    """
    Unified manager for Microsoft Entra ID identity types.
    
    This class provides a simplified interface for creating and managing
    different identity types in Microsoft Entra ID (formerly Azure AD)
    using the Microsoft Graph API.
    """
    
    def __init__(self):
        """
        Initialize the identity manager.
        """
        self.settings = settings
        self.msal_app = EntraAuth.get_msal_app()
    
    async def get_client_credentials_token(self):
        """
        Get an access token using client credentials flow.
        
        Returns:
            str: The access token for Microsoft Graph API.
            
        Raises:
            HTTPException: If token acquisition fails.
        """
        result = self.msal_app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error acquiring token: {result.get('error_description', result.get('error'))}"
            )
            
        return result["access_token"]
    
    async def _get_graph_service(self):
        """
        Get an instance of the Graph service with a valid token.
        
        Returns:
            EntraGraphService: An initialized Graph service instance.
        """
        token = await self.get_client_credentials_token()
        return EntraGraphService(token)
    
    # User methods
    
    async def get_users(self, filter_str: Optional[str] = None, start_index: int = 1, count: int = 100):
        """
        Get users from Microsoft Entra ID with pagination.
        
        Args:
            filter_str (Optional[str]): SCIM filter string.
            start_index (int): Start index for pagination (1-based).
            count (int): Number of items per page.
            
        Returns:
            Dict[str, Any]: SCIM-formatted list response with users.
        """
        service = await self._get_graph_service()
        return await service.get_users(filter_str, start_index, count)
    
    async def get_user(self, user_id: str):
        """
        Get a specific user from Microsoft Entra ID.
        
        Args:
            user_id (str): The ID of the user to retrieve.
            
        Returns:
            Dict[str, Any]: SCIM-formatted user object.
        """
        service = await self._get_graph_service()
        return await service.get_user(user_id)
    
    async def create_user(self, user_data: Dict[str, Any]):
        """
        Create a user in Microsoft Entra ID.
        
        Args:
            user_data (Dict[str, Any]): SCIM-formatted user data.
            
        Returns:
            Dict[str, Any]: SCIM-formatted created user object.
            
        Raises:
            HTTPException: If user creation fails.
        """
        service = await self._get_graph_service()
        return await service.create_user(user_data)
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]):
        """
        Update a user in Microsoft Entra ID.
        
        Args:
            user_id (str): The ID of the user to update.
            user_data (Dict[str, Any]): SCIM-formatted user data.
            
        Returns:
            Dict[str, Any]: SCIM-formatted updated user object.
        """
        service = await self._get_graph_service()
        return await service.update_user(user_id, user_data)
    
    async def delete_user(self, user_id: str):
        """
        Delete a user in Microsoft Entra ID.
        
        Args:
            user_id (str): The ID of the user to delete.
            
        Returns:
            bool: True if deletion was successful.
        """
        service = await self._get_graph_service()
        return await service.delete_user(user_id)
    
    # Group methods
    
    async def get_groups(self, filter_str: Optional[str] = None, start_index: int = 1, count: int = 100):
        """
        Get groups from Microsoft Entra ID with pagination.
        
        Args:
            filter_str (Optional[str]): SCIM filter string.
            start_index (int): Start index for pagination (1-based).
            count (int): Number of items per page.
            
        Returns:
            Dict[str, Any]: SCIM-formatted list response with groups.
        """
        service = await self._get_graph_service()
        return await service.get_groups(filter_str, start_index, count)
    
    async def get_group(self, group_id: str):
        """
        Get a specific group from Microsoft Entra ID.
        
        Args:
            group_id (str): The ID of the group to retrieve.
            
        Returns:
            Dict[str, Any]: SCIM-formatted group object.
        """
        service = await self._get_graph_service()
        return await service.get_group(group_id)
    
    async def create_group(self, group_data: Dict[str, Any]):
        """
        Create a group in Microsoft Entra ID.
        
        Args:
            group_data (Dict[str, Any]): SCIM-formatted group data.
            
        Returns:
            Dict[str, Any]: SCIM-formatted created group object.
            
        Raises:
            HTTPException: If group creation fails.
        """
        service = await self._get_graph_service()
        return await service.create_group(group_data)
    
    async def update_group(self, group_id: str, group_data: Dict[str, Any]):
        """
        Update a group in Microsoft Entra ID.
        
        Args:
            group_id (str): The ID of the group to update.
            group_data (Dict[str, Any]): SCIM-formatted group data.
            
        Returns:
            Dict[str, Any]: SCIM-formatted updated group object.
        """
        service = await self._get_graph_service()
        return await service.update_group(group_id, group_data)
    
    async def delete_group(self, group_id: str):
        """
        Delete a group in Microsoft Entra ID.
        
        Args:
            group_id (str): The ID of the group to delete.
            
        Returns:
            bool: True if deletion was successful.
        """
        service = await self._get_graph_service()
        return await service.delete_group(group_id)
    
    # Application methods
    
    async def get_applications(self, filter_str: Optional[str] = None, start_index: int = 1, count: int = 100):
        """
        Get applications from Microsoft Entra ID with pagination.
        
        Args:
            filter_str (Optional[str]): SCIM filter string.
            start_index (int): Start index for pagination (1-based).
            count (int): Number of items per page.
            
        Returns:
            Dict[str, Any]: SCIM-formatted list response with applications.
        """
        service = await self._get_graph_service()
        return await service.get_applications(filter_str, start_index, count)
    
    async def get_application(self, app_id: str):
        """
        Get a specific application from Microsoft Entra ID.
        
        Args:
            app_id (str): The ID of the application to retrieve.
            
        Returns:
            Dict[str, Any]: SCIM-formatted application object.
        """
        service = await self._get_graph_service()
        return await service.get_application(app_id)
    
    async def create_application(self, app_data: Dict[str, Any]):
        """
        Create an application in Microsoft Entra ID.
        
        Args:
            app_data (Dict[str, Any]): SCIM-formatted application data.
            
        Returns:
            Dict[str, Any]: SCIM-formatted created application object.
            
        Raises:
            HTTPException: If application creation fails.
        """
        service = await self._get_graph_service()
        return await service.create_application(app_data)
    
    async def update_application(self, app_id: str, app_data: Dict[str, Any]):
        """
        Update an application in Microsoft Entra ID.
        
        Args:
            app_id (str): The ID of the application to update.
            app_data (Dict[str, Any]): SCIM-formatted application data.
            
        Returns:
            Dict[str, Any]: SCIM-formatted updated application object.
        """
        service = await self._get_graph_service()
        return await service.update_application(app_id, app_data)
    
    async def delete_application(self, app_id: str):
        """
        Delete an application in Microsoft Entra ID.
        
        Args:
            app_id (str): The ID of the application to delete.
            
        Returns:
            bool: True if deletion was successful.
        """
        service = await self._get_graph_service()
        return await service.delete_application(app_id)
    
    # Service Principal methods
    
    async def get_service_principals(self, filter_str: Optional[str] = None, start_index: int = 1, count: int = 100):
        """
        Get service principals from Microsoft Entra ID with pagination.
        
        Args:
            filter_str (Optional[str]): SCIM filter string.
            start_index (int): Start index for pagination (1-based).
            count (int): Number of items per page.
            
        Returns:
            Dict[str, Any]: SCIM-formatted list response with service principals.
        """
        service = await self._get_graph_service()
        return await service.get_service_principals(filter_str, start_index, count)
    
    async def get_service_principal(self, sp_id: str):
        """
        Get a specific service principal from Microsoft Entra ID.
        
        Args:
            sp_id (str): The ID of the service principal to retrieve.
            
        Returns:
            Dict[str, Any]: SCIM-formatted service principal object.
        """
        service = await self._get_graph_service()
        return await service.get_service_principal(sp_id)
    
    async def create_service_principal(self, sp_data: Dict[str, Any]):
        """
        Create a service principal in Microsoft Entra ID.
        
        Args:
            sp_data (Dict[str, Any]): SCIM-formatted service principal data.
            
        Returns:
            Dict[str, Any]: SCIM-formatted created service principal object.
            
        Raises:
            HTTPException: If service principal creation fails.
        """
        service = await self._get_graph_service()
        return await service.create_service_principal(sp_data)
    
    async def update_service_principal(self, sp_id: str, sp_data: Dict[str, Any]):
        """
        Update a service principal in Microsoft Entra ID.
        
        Args:
            sp_id (str): The ID of the service principal to update.
            sp_data (Dict[str, Any]): SCIM-formatted service principal data.
            
        Returns:
            Dict[str, Any]: SCIM-formatted updated service principal object.
        """
        service = await self._get_graph_service()
        return await service.update_service_principal(sp_id, sp_data)
    
    async def delete_service_principal(self, sp_id: str):
        """
        Delete a service principal in Microsoft Entra ID.
        
        Args:
            sp_id (str): The ID of the service principal to delete.
            
        Returns:
            bool: True if deletion was successful.
        """
        service = await self._get_graph_service()
        return await service.delete_service_principal(sp_id)
    
    # Convenience methods
    
    async def create_application_with_service_principal(self, app_data: Dict[str, Any]):
        """
        Create an application and its corresponding service principal in Microsoft Entra ID.
        
        This is a convenience method that creates an application and then automatically
        creates a service principal for that application.
        
        Args:
            app_data (Dict[str, Any]): SCIM-formatted application data.
            
        Returns:
            Dict[str, Any]: A dictionary containing both the created application and service principal.
        """
        # Create the application
        app = await self.create_application(app_data)
        
        # Create a service principal for the application
        sp_data = {
            "appId": app.get("appId"),
            "displayName": app.get("displayName")
        }
        
        try:
            sp = await self.create_service_principal(sp_data)
            
            return {
                "application": app,
                "servicePrincipal": sp
            }
        except Exception as e:
            # If service principal creation fails, delete the application to avoid orphaned resources
            await self.delete_application(app.get("id"))
            raise e
