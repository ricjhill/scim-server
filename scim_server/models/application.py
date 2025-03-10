"""
This module defines an Application model for Microsoft Entra ID.

Note: Since we're using Microsoft Entra ID as our identity store, we don't need
traditional database models. Instead, we'll create utility classes to help
map between Graph API responses and SCIM models.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class EntraApplicationMapping:
    """
    A utility class to map between Microsoft Graph API application responses and SCIM-like models.
    """
    graph_application: Dict[str, Any]
    
    def to_scim_dict(self) -> Dict[str, Any]:
        """Convert a Microsoft Graph application to SCIM-like dictionary"""
        # Basic application properties
        scim_app = {
            "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:Application"],
            "id": self.graph_application.get("id"),
            "displayName": self.graph_application.get("displayName"),
            "appId": self.graph_application.get("appId"),
            "description": self.graph_application.get("description"),
            "identifierUris": self.graph_application.get("identifierUris", []),
            "web": {
                "redirectUris": self.graph_application.get("web", {}).get("redirectUris", []),
                "implicitGrantSettings": self.graph_application.get("web", {}).get("implicitGrantSettings", {})
            },
            "signInAudience": self.graph_application.get("signInAudience"),
            "publisherDomain": self.graph_application.get("publisherDomain"),
            "createdDateTime": self.graph_application.get("createdDateTime"),
            "isEnabled": not self.graph_application.get("disabledByMicrosoftStatus", False)
        }
        
        # Add required resource access if present
        if "requiredResourceAccess" in self.graph_application:
            scim_app["requiredResourceAccess"] = self.graph_application["requiredResourceAccess"]
            
        return scim_app
        
    @staticmethod
    def from_scim_dict(scim_app: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a SCIM-like dictionary to Microsoft Graph application format"""
        # Basic application properties
        graph_app = {
            "displayName": scim_app.get("displayName", ""),
            "description": scim_app.get("description", "")
        }
        
        # Add identifier URIs if present
        if "identifierUris" in scim_app and scim_app["identifierUris"]:
            graph_app["identifierUris"] = scim_app["identifierUris"]
            
        # Add web configuration if present
        if "web" in scim_app and scim_app["web"]:
            graph_app["web"] = {}
            
            if "redirectUris" in scim_app["web"] and scim_app["web"]["redirectUris"]:
                graph_app["web"]["redirectUris"] = scim_app["web"]["redirectUris"]
                
            if "implicitGrantSettings" in scim_app["web"] and scim_app["web"]["implicitGrantSettings"]:
                graph_app["web"]["implicitGrantSettings"] = scim_app["web"]["implicitGrantSettings"]
        
        # Add sign-in audience if present
        if "signInAudience" in scim_app:
            graph_app["signInAudience"] = scim_app["signInAudience"]
            
        # Add required resource access if present
        if "requiredResourceAccess" in scim_app:
            graph_app["requiredResourceAccess"] = scim_app["requiredResourceAccess"]
            
        return graph_app
