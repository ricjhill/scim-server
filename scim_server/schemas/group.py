from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Meta(BaseModel):
    resourceType: str = "Group"
    created: Optional[datetime] = None
    lastModified: Optional[datetime] = None
    location: Optional[str] = None
    version: Optional[str] = None

class Member(BaseModel):
    value: str
    display: Optional[str] = None
    type: Optional[str] = None
    $ref: Optional[str] = None

class GroupSchema(BaseModel):
    schemas: List[str] = ["urn:ietf:params:scim:schemas:core:2.0:Group"]
    id: Optional[str] = None
    externalId: Optional[str] = None
    meta: Optional[Meta] = None
    displayName: str
    members: Optional[List[Member]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
                "id": "e9e30dba-f08f-4109-8486-d5c6a331660a",
                "displayName": "Employees",
                "members": [
                    {
                        "value": "2819c223-7f76-453a-919d-413861904646",
                        "display": "John Doe"
                    }
                ]
            }
        }

class GroupListResponse(BaseModel):
    schemas: List[str] = ["urn:ietf:params:scim:api:messages:2.0:ListResponse"]
    totalResults: int
    startIndex: int = 1
    itemsPerPage: int = 100
    Resources: List[GroupSchema]
