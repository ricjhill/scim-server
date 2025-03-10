"""
This module defines a Service Principal model for Microsoft Entra ID.

Note: Since we're using Microsoft Entra ID as our identity store, we don't need
traditional database models. Instead, we'll create utility classes to help
map between Graph API responses and SCIM models.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class EntraServicePrincipalMapping:
    """
    A utility class to map between Microsoft Graph API service principal responses and SCIM-like models.
    """
    graph_sp: Dict[str, Any]
    
    def to_scim_dict(self) -> Dict[str, Any]:
        """Convert a Microsoft Graph service principal to SCIM-like dictionary"""
        # Basic service principal properties
        scim_sp = {
            "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:ServicePrincipal"],
            "id": self.graph_sp.get("id"),
            "displayName": self.graph_sp.get("displayName"),
            "appId": self.graph_sp.get("appId"),
            "description": self.graph_sp.get("description"),
            "servicePrincipalType": self.graph_sp.get("servicePrincipalType"),
            "appOwnerOrganizationId": self.graph_sp.get("appOwnerOrganizationId"),
            "appRoleAssignmentRequired": self.graph_sp.get("appRoleAssignmentRequired", False),
            "homepage": self.graph_sp.get("homepage"),
            "logoutUrl": self.graph_sp.get("logoutUrl"),
            "replyUrls": self.graph_sp.get("replyUrls", []),
            "tags": self.graph_sp.get("tags", []),
            "accountEnabled": self.graph_sp.get("accountEnabled", True),
            "createdDateTime": self.graph_sp.get("createdDateTime")
        }
        
        # Add app roles if present
        if "appRoles" in self.graph_sp:
            scim_sp["appRoles"] = self.graph_sp["appRoles"]
            
        # Add oauth2 permissions if present
        if "oauth2PermissionScopes" in self.graph_sp:
            scim_sp["oauth2PermissionScopes"] = self.graph_sp["oauth2PermissionScopes"]
            
        return scim_sp
        
    @staticmethod
    def from_scim_dict(scim_sp: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a SCIM-like dictionary to Microsoft Graph service principal format"""
        # Basic service principal properties
        graph_sp = {
            "displayName": scim_sp.get("displayName", ""),
            "description": scim_sp.get("description", "")
        }
        
        # Add app ID if present (required for creating service principal from an application)
        if "appId" in scim_sp:
            graph_sp["appId"] = scim_sp["appId"]
            
        # Add app role assignment required if present
        if "appRoleAssignmentRequired" in scim_sp:
            graph_sp["appRoleAssignmentRequired"] = scim_sp["appRoleAssignmentRequired"]
            
        # Add tags if present
        if "tags" in scim_sp and scim_sp["tags"]:
            graph_sp["tags"] = scim_sp["tags"]
            
        # Add account enabled if present
        if "accountEnabled" in scim_sp:
            graph_sp["accountEnabled"] = scim_sp["accountEnabled"]
            
        # Add reply URLs if present
        if "replyUrls" in scim_sp and scim_sp["replyUrls"]:
            graph_sp["replyUrls"] = scim_sp["replyUrls"]
            
        # Add homepage if present
        if "homepage" in scim_sp:
            graph_sp["homepage"] = scim_sp["homepage"]
            
        # Add logout URL if present
        if "logoutUrl" in scim_sp:
            graph_sp["logoutUrl"] = scim_sp["logoutUrl"]
            
        return graph_sp
