from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Meta(BaseModel):
    resourceType: str = "User"
    created: Optional[datetime] = None
    lastModified: Optional[datetime] = None
    location: Optional[str] = None
    version: Optional[str] = None

class Name(BaseModel):
    formatted: Optional[str] = None
    familyName: Optional[str] = None
    givenName: Optional[str] = None
    middleName: Optional[str] = None
    honorificPrefix: Optional[str] = None
    honorificSuffix: Optional[str] = None

class Email(BaseModel):
    value: str
    display: Optional[str] = None
    type: Optional[str] = "work"
    primary: Optional[bool] = None

class PhoneNumber(BaseModel):
    value: str
    display: Optional[str] = None
    type: Optional[str] = "work"
    primary: Optional[bool] = None

class Address(BaseModel):
    formatted: Optional[str] = None
    streetAddress: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postalCode: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = "work"
    primary: Optional[bool] = None

class UserSchema(BaseModel):
    schemas: List[str] = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    id: Optional[str] = None
    externalId: Optional[str] = None
    meta: Optional[Meta] = None
    userName: str
    name: Optional[Name] = None
    displayName: Optional[str] = None
    nickName: Optional[str] = None
    profileUrl: Optional[str] = None
    title: Optional[str] = None
    userType: Optional[str] = None
    preferredLanguage: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    active: Optional[bool] = True
    emails: Optional[List[Email]] = None
    phoneNumbers: Optional[List[PhoneNumber]] = None
    addresses: Optional[List[Address]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
                "id": "2819c223-7f76-453a-919d-413861904646",
                "externalId": "user123",
                "userName": "john.doe@example.com",
                "name": {
                    "formatted": "John Doe",
                    "familyName": "Doe",
                    "givenName": "John"
                },
                "displayName": "John Doe",
                "emails": [
                    {
                        "value": "john.doe@example.com",
                        "type": "work",
                        "primary": True
                    }
                ],
                "active": True
            }
        }

class UserListResponse(BaseModel):
    schemas: List[str] = ["urn:ietf:params:scim:api:messages:2.0:ListResponse"]
    totalResults: int
    startIndex: int = 1
    itemsPerPage: int = 100
    Resources: List[UserSchema]
