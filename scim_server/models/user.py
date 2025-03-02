"""
This module defines a User model for your SCIM server.

Note: Since we're using Microsoft Entra ID as our identity store, we don't need
traditional database models. Instead, we'll create utility classes to help
map between Graph API responses and SCIM models.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class EntraUserMapping:
    """
    A utility class to map between Microsoft Graph API user responses and SCIM user models.
    """
    graph_user: Dict[str, Any]
    
    def to_scim_dict(self) -> Dict[str, Any]:
        """Convert a Microsoft Graph user to SCIM user dictionary"""
        name = {
            "formatted": f"{self.graph_user.get('givenName', '')} {self.graph_user.get('surname', '')}".strip(),
            "familyName": self.graph_user.get("surname"),
            "givenName": self.graph_user.get("givenName")
        }
        
        emails = []
        if self.graph_user.get("mail"):
            emails.append({
                "value": self.graph_user.get("mail"),
                "type": "work",
                "primary": True
            })
        
        phone_numbers = []
        if self.graph_user.get("businessPhones"):
            for phone in self.graph_user.get("businessPhones"):
                phone_numbers.append({
                    "value": phone,
                    "type": "work"
                })
        
        # Construct the SCIM user
        scim_user = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": self.graph_user.get("id"),
            "externalId": self.graph_user.get("userPrincipalName"),
            "userName": self.graph_user.get("userPrincipalName"),
            "name": name,
            "displayName": self.graph_user.get("displayName"),
            "active": self.graph_user.get("accountEnabled", True)
        }
        
        if emails:
            scim_user["emails"] = emails
            
        if phone_numbers:
            scim_user["phoneNumbers"] = phone_numbers
            
        return scim_user
    
    @staticmethod
    def from_scim_dict(scim_user: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a SCIM user dictionary to Microsoft Graph user format"""
        graph_user = {
            "userPrincipalName": scim_user.get("userName"),
            "displayName": scim_user.get("displayName", ""),
            "accountEnabled": scim_user.get("active", True)
        }
        
        # Handle name components
        if scim_user.get("name"):
            name = scim_user.get("name")
            if name.get("givenName"):
                graph_user["givenName"] = name.get("givenName")
            if name.get("familyName"):
                graph_user["surname"] = name.get("familyName")
        
        # Handle email
        if scim_user.get("emails"):
            for email in scim_user.get("emails"):
                if email.get("primary", False) and email.get("value"):
                    graph_user["mail"] = email.get("value")
                    break
        
        return graph_user
