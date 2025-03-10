"""
Example of creating an application in Microsoft Entra ID.
"""

import asyncio
import os
from dotenv import load_dotenv
from scim_server.services.identity import EntraIdentityManager

# Load environment variables from .env file
load_dotenv()

async def create_application_example():
    """
    Example of creating an application in Microsoft Entra ID.
    """
    # Initialize the identity manager
    manager = EntraIdentityManager()
    
    # Application data in SCIM format
    app_data = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:Application"],
        "displayName": "Sample API Client",
        "description": "Sample application for API access",
        "signInAudience": "AzureADMyOrg",
        "web": {
            "redirectUris": ["https://localhost:8000/auth/callback"],
            "implicitGrantSettings": {
                "enableAccessTokenIssuance": True,
                "enableIdTokenIssuance": True
            }
        },
        "requiredResourceAccess": [
            {
                "resourceAppId": "00000003-0000-0000-c000-000000000000",  # Microsoft Graph
                "resourceAccess": [
                    {
                        "id": "e1fe6dd8-ba31-4d61-89e7-88639da4683d",  # User.Read
                        "type": "Scope"
                    }
                ]
            }
        ]
    }
    
    try:
        # Create the application
        print("Creating application...")
        created_app = await manager.create_application(app_data)
        print(f"Created application: {created_app['id']}")
        print(f"Application ID (client ID): {created_app['appId']}")
        print(f"Application details: {created_app}")
        
        # Get the application
        print("\nRetrieving application...")
        app = await manager.get_application(created_app['id'])
        print(f"Retrieved application: {app['displayName']}")
        
        # Update the application
        print("\nUpdating application...")
        update_data = {
            "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:Application"],
            "displayName": "Updated API Client",
            "web": {
                "redirectUris": [
                    "https://localhost:8000/auth/callback",
                    "https://myapp.example.com/auth/callback"
                ]
            }
        }
        updated_app = await manager.update_application(created_app['id'], update_data)
        print(f"Updated application: {updated_app['displayName']}")
        print(f"Updated redirect URIs: {updated_app['web']['redirectUris']}")
        
        # List applications with pagination
        print("\nListing applications (first page)...")
        apps = await manager.get_applications(start_index=1, count=5)
        print(f"Total applications: {apps['totalResults']}")
        print(f"Applications on first page: {len(apps['Resources'])}")
        
        # Create a service principal for the application
        print("\nCreating service principal for the application...")
        sp_data = {
            "appId": created_app['appId'],
            "displayName": created_app['displayName']
        }
        created_sp = await manager.create_service_principal(sp_data)
        print(f"Created service principal: {created_sp['id']}")
        
        # Alternative: Use the convenience method to create both in one call
        print("\nCreating another application with service principal in one call...")
        app_data["displayName"] = "Another Sample API Client"
        result = await manager.create_application_with_service_principal(app_data)
        print(f"Created application: {result['application']['id']}")
        print(f"Created service principal: {result['servicePrincipal']['id']}")
        
        # Delete the application and service principal (commented out to prevent actual deletion)
        # print("\nDeleting application and service principal...")
        # await manager.delete_service_principal(created_sp['id'])
        # await manager.delete_application(created_app['id'])
        # await manager.delete_application(result['application']['id'])
        # print("Application and service principal deleted successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(create_application_example())
