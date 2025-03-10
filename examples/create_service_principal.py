"""
Example of creating a service principal in Microsoft Entra ID.
"""

import asyncio
import os
from dotenv import load_dotenv
from scim_server.services.identity import EntraIdentityManager

# Load environment variables from .env file
load_dotenv()

async def create_service_principal_example():
    """
    Example of creating a service principal in Microsoft Entra ID.
    """
    # Initialize the identity manager
    manager = EntraIdentityManager()
    
    # First, create an application (service principals are associated with applications)
    app_data = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:Application"],
        "displayName": "Service Principal Example App",
        "description": "Application for service principal example",
        "signInAudience": "AzureADMyOrg"
    }
    
    try:
        # Create the application
        print("Creating application...")
        created_app = await manager.create_application(app_data)
        print(f"Created application: {created_app['id']}")
        print(f"Application ID (client ID): {created_app['appId']}")
        
        # Service principal data in SCIM format
        sp_data = {
            "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:ServicePrincipal"],
            "appId": created_app['appId'],
            "displayName": "Example Service Principal",
            "description": "Service principal for automation tasks",
            "appRoleAssignmentRequired": True,
            "tags": ["WindowsAzureActiveDirectoryIntegratedApp"]
        }
        
        # Create the service principal
        print("\nCreating service principal...")
        created_sp = await manager.create_service_principal(sp_data)
        print(f"Created service principal: {created_sp['id']}")
        print(f"Service principal details: {created_sp}")
        
        # Get the service principal
        print("\nRetrieving service principal...")
        sp = await manager.get_service_principal(created_sp['id'])
        print(f"Retrieved service principal: {sp['displayName']}")
        
        # Update the service principal
        print("\nUpdating service principal...")
        update_data = {
            "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:ServicePrincipal"],
            "displayName": "Updated Service Principal",
            "appRoleAssignmentRequired": False
        }
        updated_sp = await manager.update_service_principal(created_sp['id'], update_data)
        print(f"Updated service principal: {updated_sp['displayName']}")
        print(f"App role assignment required: {updated_sp['appRoleAssignmentRequired']}")
        
        # List service principals with pagination
        print("\nListing service principals (first page)...")
        sps = await manager.get_service_principals(start_index=1, count=5)
        print(f"Total service principals: {sps['totalResults']}")
        print(f"Service principals on first page: {len(sps['Resources'])}")
        
        # Delete the service principal and application (commented out to prevent actual deletion)
        # print("\nDeleting service principal and application...")
        # await manager.delete_service_principal(created_sp['id'])
        # await manager.delete_application(created_app['id'])
        # print("Service principal and application deleted successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(create_service_principal_example())
