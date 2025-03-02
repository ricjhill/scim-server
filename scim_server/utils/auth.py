"""
Authentication utilities for integrating with Microsoft Entra ID.
"""

import msal
import jwt
import httpx
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from typing import Dict, Optional, List

from scim_server.config import settings

class EntraAuth:
    """
    Authentication utilities for Microsoft Entra ID integration.
    """
    
    @staticmethod
    def get_msal_app():
        """
        Get Microsoft Authentication Library (MSAL) confidential client application.
        """
        return msal.ConfidentialClientApplication(
            settings.CLIENT_ID,
            authority=settings.AUTHORITY,
            client_credential=settings.CLIENT_SECRET
        )
    
    @staticmethod
    def get_auth_url(redirect_uri: str = None, scopes: List[str] = None):
        """
        Get authorization URL for Microsoft Entra ID authentication.
        """
        if not redirect_uri:
            redirect_uri = settings.REDIRECT_URI
            
        if not scopes:
            scopes = settings.SCOPE
            
        msal_app = EntraAuth.get_msal_app()
        return msal_app.get_authorization_request_url(scopes, redirect_uri=redirect_uri)
    
    @staticmethod
    async def get_token_from_code(code: str, redirect_uri: str = None, scopes: List[str] = None):
        """
        Exchange authorization code for access token.
        """
        if not redirect_uri:
            redirect_uri = settings.REDIRECT_URI
            
        if not scopes:
            scopes = settings.SCOPE
            
        msal_app = EntraAuth.get_msal_app()
        result = msal_app.acquire_token_by_authorization_code(code, scopes, redirect_uri=redirect_uri)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error getting token: {result.get('error_description', result.get('error'))}",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return result
    
    @staticmethod
    async def get_user_info(token: str):
        """
        Get user information from Microsoft Graph API.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to get user info",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            return response.json()
    
    @staticmethod
    async def validate_token(token: str):
        """
        Validate access token from Microsoft Entra ID.
        """
        try:
            # For proper validation, you should use Microsoft's JWKS endpoint
            # This is a simplified version
            payload = jwt.decode(
                token,
                options={"verify_signature": False},  # In production, you should verify the signature
                audience=settings.CLIENT_ID
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    async def get_current_user(request: Request):
        """
        Dependency for FastAPI to get the current authenticated user.
        """
        if "user" not in request.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        if "token" not in request.session or "access_token" not in request.session["token"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Optionally validate token here for extra security
        
        return request.session["user"]
    
    @staticmethod
    async def get_access_token(request: Request):
        """
        Dependency for FastAPI to get the current access token.
        """
        if "token" not in request.session or "access_token" not in request.session["token"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        return request.session["token"]["access_token"]
