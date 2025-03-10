"""
Example of creating a group in Microsoft Entra ID.
"""

import asyncio
import os
from dotenv import load_dotenv
from scim_server.services.identity import EntraIdentityManager

# Load environment variables from .env file
load_dotenv()

async def create_group_example():
    """
    Example of creating a group in Microsoft Entra ID.
    """
    # Initialize the identity manager
    manager = EntraIdentityManager()
    
    # Group data in SCIM format
    group_data = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "displayName": "Engineering Team",
        "description": "Engineering department team"
    }
    
    try:
        # Create the group
        print("Creating group...")
        created_group = await manager.create_group(group_data)
        print(f"Created group: {created_group['id']}")
        print(f"Group details: {created_group}")
        
        # Get the group
        print("\nRetrieving group...")
        group = await manager.get_group(created_group['id'])
        print(f"Retrieved group: {group['displayName']}")
        
        # Update the group
        print("\nUpdating group...")
        update_data = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
            "displayName": "Engineering Department"
        }
        updated_group = await manager.update_group(created_group['id'], update_data)
        print(f"Updated group: {updated_group['displayName']}")
        
        # List groups with pagination
        print("\nListing groups (first page)...")
        groups = await manager.get_groups(start_index=1, count=5)
        print(f"Total groups: {groups['totalResults']}")
        print(f"Groups on first page: {len(groups['Resources'])}")
        
        # Delete the group (commented out to prevent actual deletion)
        # print("\nDeleting group...")
        # await manager.delete_group(created_group['id'])
        # print("Group deleted successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(create_group_example())
