# Microsoft Entra ID Identity Management

A Python library for programmatically creating and managing different identity types in Microsoft Entra ID (formerly Azure AD) using the Microsoft Graph API.

## Features

- Create, read, update, and delete operations for:
  - Users
  - Groups
  - Applications
  - Service Principals
- SCIM-compatible data format
- Pagination support for listing operations
- Proper error handling
- Convenient helper methods

## Architecture Overview

This SCIM server acts as a bridge between SCIM clients and Microsoft Entra ID . It translates SCIM requests into Microsoft Graph API calls allowing you to use Microsoft Entra ID as your identity provider while maintaining SCIM compatibility.

```
┌─────────────┐     ┌─────────────┐     ┌───────────────────────────┐
│             │     │             │     │                           │
│ SCIM Client │───▶│ SCIM Server │────▶│ Microsoft Entra ID        │
│             │     │             │     │ (via Microsoft Graph API) │
└─────────────┘     └─────────────┘     └───────────────────────────┘
```

The server handles:
- Authentication with Microsoft Entra ID
- Mapping between SCIM resources and Microsoft Graph API resources
- SCIM filtering and pagination
- Error handling and response formatting

## Requirements

- Python 3.8+
- Microsoft Entra ID tenant
- Application registration with appropriate permissions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/entra-identity-manager.git
cd entra-identity-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Microsoft Entra ID credentials:
```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
TENANT_ID=your_tenant_id
```

## Configuration

The library uses a Pydantic Settings class to manage configuration. The following settings are required:

| Setting | Description | Default |
|---------|-------------|---------|
| CLIENT_ID | Application (client) ID | From environment variable |
| CLIENT_SECRET | Client secret | From environment variable |
| TENANT_ID | Directory (tenant) ID | From environment variable |
| AUTHORITY | Authority URL | https://login.microsoftonline.com/{TENANT_ID} |
| REDIRECT_URI | Redirect URI for auth code flow | http://localhost:8000/auth/callback |
| SCOPE | Default scopes | ["User.Read", "User.ReadBasic.All", "Directory.Read.All"] |

## Required Permissions

Your application registration in Microsoft Entra ID needs the following API permissions:

- Microsoft Graph API:
  - User.ReadWrite.All
  - Group.ReadWrite.All
  - Application.ReadWrite.All
  - Directory.ReadWrite.All

For service principal operations, you'll also need:
- Microsoft Graph API:
  - AppRoleAssignment.ReadWrite.All

## Usage Examples

### Creating a User

```python
from scim_server.services.identity import EntraIdentityManager

async def create_user():
    manager = EntraIdentityManager()
    
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
    
    created_user = await manager.create_user(user_data)
    print(f"Created user: {created_user['id']}")
```

### Creating a Group

```python
from scim_server.services.identity import EntraIdentityManager

async def create_group():
    manager = EntraIdentityManager()
    
    group_data = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "displayName": "Engineering Team",
        "description": "Engineering department team"
    }
    
    created_group = await manager.create_group(group_data)
    print(f"Created group: {created_group['id']}")
```

### Creating an Application

```python
from scim_server.services.identity import EntraIdentityManager

async def create_application():
    manager = EntraIdentityManager()
    
    app_data = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:Application"],
        "displayName": "Sample API Client",
        "description": "Sample application for API access",
        "signInAudience": "AzureADMyOrg",
        "web": {
            "redirectUris": ["https://localhost:8000/auth/callback"]
        }
    }
    
    created_app = await manager.create_application(app_data)
    print(f"Created application: {created_app['id']}")
    print(f"Application ID (client ID): {created_app['appId']}")
```

### Creating a Service Principal

```python
from scim_server.services.identity import EntraIdentityManager

async def create_service_principal():
    manager = EntraIdentityManager()
    
    # First create an application
    app_data = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:Application"],
        "displayName": "Service Principal Example App",
        "signInAudience": "AzureADMyOrg"
    }
    
    created_app = await manager.create_application(app_data)
    
    # Then create a service principal for the application
    sp_data = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:ServicePrincipal"],
        "appId": created_app['appId'],
        "displayName": "Example Service Principal"
    }
    
    created_sp = await manager.create_service_principal(sp_data)
    print(f"Created service principal: {created_sp['id']}")
```

### Creating an Application with Service Principal in One Call

```python
from scim_server.services.identity import EntraIdentityManager

async def create_app_with_sp():
    manager = EntraIdentityManager()
    
    app_data = {
        "schemas": ["urn:ietf:params:scim:schemas:extension:entra:2.0:Application"],
        "displayName": "Sample API Client",
        "signInAudience": "AzureADMyOrg"
    }
    
    result = await manager.create_application_with_service_principal(app_data)
    print(f"Created application: {result['application']['id']}")
    print(f"Created service principal: {result['servicePrincipal']['id']}")
```

### Pagination Support

```python
from scim_server.services.identity import EntraIdentityManager

async def list_users_with_pagination():
    manager = EntraIdentityManager()
    
    # Get first page (5 items per page)
    page1 = await manager.get_users(start_index=1, count=5)
    print(f"Total users: {page1['totalResults']}")
    print(f"Users on first page: {len(page1['Resources'])}")
    
    # Get second page
    page2 = await manager.get_users(start_index=6, count=5)
    print(f"Users on second page: {len(page2['Resources'])}")
```

## Error Handling

The library includes comprehensive error handling. All methods that interact with the Microsoft Graph API will throw appropriate exceptions with detailed error messages.

```python
from scim_server.services.identity import EntraIdentityManager
from fastapi import HTTPException

async def handle_errors():
    manager = EntraIdentityManager()
    
    try:
        # Try to get a non-existent user
        user = await manager.get_user("non-existent-id")
    except HTTPException as e:
        print(f"Error status code: {e.status_code}")
        print(f"Error message: {e.detail}")
```

## Using the SCIM Server via Browser

### Starting the Server

To start the SCIM server locally:

```bash
# Navigate to the project directory
cd scim-server

# Start the server
python -m scim_server.main
```

The server will start on http://localhost:8000 by default.

### Authentication

1. Open your browser and navigate to http://localhost:8000/login
2. You'll be redirected to the Microsoft Entra ID login page
3. Sign in with your Microsoft credentials
4. After successful authentication, you'll be redirected back to the SCIM server

### Exploring Endpoints

Once authenticated, you can access:

- **Home Page**: http://localhost:8000/ - Shows basic server information and available endpoints
- **Users Endpoint**: http://localhost:8000/scim/v2/Users - For user operations
- **Groups Endpoint**: http://localhost:8000/scim/v2/Groups - For group operations

### Testing API Endpoints

You can use browser tools or extensions like [Postman](https://www.postman.com/) or [REST Client for VS Code](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) to test the API endpoints:

#### Example: Get Users
- **URL**: http://localhost:8000/scim/v2/Users
- **Method**: GET
- **Headers**: 
  - Authorization: Bearer {your_access_token}

#### Example: Create User
- **URL**: http://localhost:8000/scim/v2/Users
- **Method**: POST
- **Headers**: 
  - Authorization: Bearer {your_access_token}
  - Content-Type: application/json
- **Body**:
```json
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "userName": "john.doe@example.com",
  "name": {
    "givenName": "John",
    "familyName": "Doe"
  },
  "displayName": "John Doe",
  "active": true,
  "emails": [
    {
      "value": "john.doe@example.com",
      "type": "work",
      "primary": true
    }
  ]
}
```

### Debugging

For troubleshooting, you can use these debug endpoints:

- **Session Debug**: http://localhost:8000/debug-session - Shows session information
- **Cookies Debug**: http://localhost:8000/debug-cookies - Shows cookie information
- **Health Check**: http://localhost:8000/health - Checks if the server is running properly

## Complete Examples

For complete examples, see the `examples` directory:

- `examples/create_user.py` - Creating and managing users
- `examples/create_group.py` - Creating and managing groups
- `examples/create_application.py` - Creating and managing applications
- `examples/create_service_principal.py` - Creating and managing service principals

## License

MIT
