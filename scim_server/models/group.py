"""
This module defines a Group model for your SCIM server.

Note: Since we're using Microsoft Entra ID as our identity store, we don't need
traditional database models. Instead, we'll create utility classes to help
map between Graph API responses and SCIM models.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class EntraGroupMapping:
    """
    A utility class to map between Microsoft Graph API group responses and SCIM group models.
    """
    graph_group: Dict[str, Any]
    
    def to_scim_dict(self) -> Dict[str, Any]:
        """Convert a Microsoft Graph group to SCIM group dictionary"""
        # Construct the SCIM group
        scim_group = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
            "id": self.graph_group.get("id"),
            "displayName": self.graph_group.get("displayName"),
        }
        
        # Handle members if present in the graph response
        if "members@odata.bind" in self.graph_group:
            members = []
            for member_url in self.graph_group["members@odata.bind"]:
                # Extract user ID from directory object URL
                user_id = member_url.split("/")[-1]
                members.append({"value": user_id})
            
            if members:
                scim_group["members"] = members
                
        return scim_group
    
    @staticmethod
    def from_scim_dict(scim_group: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a SCIM group dictionary to Microsoft Graph group format"""
        graph_group = {
            "displayName": scim_group.get("displayName", "")
        }
        
        # Handle members
        if scim_group.get("members"):
            members = []
            for member in scim_group.get("members"):
                if member.get("value"):
                    members.append(f"https://graph.microsoft.com/v1.0/directoryObjects/{member.get('value')}")
            
            if members:
                graph_group["members@odata.bind"] = members
        
        return graph_group
