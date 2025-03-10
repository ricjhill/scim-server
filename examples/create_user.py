"""
Example of creating a user in Microsoft Entra ID.
"""

import asyncio
import os
from dotenv import load_dotenv
from scim_server.services.identity import EntraIdentityManager

# Load environment variables from .env file
load_dotenv()

async def create_user_example():
    """
    Example of creating a user in Microsoft Entra ID.
    """
    # Initialize the identity manager
    manager = EntraIdentityManager()
    
    # User data in SCIM format
    user_data = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "userName": "john.doe@example.com",
        "name": {
            "givenName": "John",
            "familyName": "Doe"
        },
        "displayName": "John Doe",
        "active": True,
        "emails": [
            {
                "value": "john.doe@example.com",
                "type": "work",
                "primary": True
            }
        ]
    }
    
    try:
        # Create the user
        print("Creating user...")
        created_user = await manager.create_user(user_data)
        print(f"Created user: {created_user['id']}")
        print(f"User details: {created_user}")
        
        # Get the user
        print("\nRetrieving user...")
        user = await manager.get_user(created_user['id'])
        print(f"Retrieved user: {user['displayName']}")
        
        # Update the user
        print("\nUpdating user...")
        update_data = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "name": {
                "givenName": "John",
                "familyName": "Doe-Smith"
            },
            "displayName": "John Doe-Smith"
        }
        updated_user = await manager.update_user(created_user['id'], update_data)
        print(f"Updated user: {updated_user['displayName']}")
        
        # List users with pagination
        print("\nListing users (first page)...")
        users = await manager.get_users(start_index=1, count=5)
        print(f"Total users: {users['totalResults']}")
        print(f"Users on first page: {len(users['Resources'])}")
        
        # Delete the user (commented out to prevent actual deletion)
        # print("\nDeleting user...")
        # await manager.delete_user(created_user['id'])
        # print("User deleted successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(create_user_example())
