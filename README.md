# SCIM Server

A System for Cross-domain Identity Management (SCIM) 2.0 server implementation using FastAPI and Microsoft Entra ID for identity management.

## Features

- **SCIM 2.0 Compliant**: Implements the SCIM 2.0 protocol for identity management
- **Microsoft Entra ID Integration**: Uses Microsoft Graph API as the backend identity store
- **User Management**: Complete CRUD operations for user resources
- **Group Management**: Complete CRUD operations for group resources
- **Authentication**: Secure authentication using Microsoft Entra ID
- **Filtering**: Support for SCIM filtering operations
- **Pagination**: Support for paginated results

## Architecture Overview

This SCIM server acts as a bridge between SCIM clients and Microsoft Entra ID (formerly Azure AD). It translates SCIM requests into Microsoft Graph API calls, allowing you to use Microsoft Entra ID as your identity provider while maintaining SCIM compatibility.

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

## Prerequisites

- Python 3.8 or higher
- Microsoft Entra ID tenant
- Registered application in Microsoft Entra ID with appropriate permissions
- Client ID and Client Secret for the registered application

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ricjhill/scim-server.git
   cd scim-server
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```
# Microsoft Entra ID Configuration
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
TENANT_ID=your_tenant_id
REDIRECT_URI=http://localhost:8000/auth/callback

# Application Settings
SESSION_SECRET=your_session_secret
DEBUG=True

# CORS Settings (optional)
# CORS_ORIGINS=http://localhost:3000,https://example.com
```

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| CLIENT_ID | The client ID of your registered application in Microsoft Entra ID |
| CLIENT_SECRET | The client secret of your registered application |
| TENANT_ID | Your Microsoft Entra ID tenant ID |
| REDIRECT_URI | The redirect URI for authentication callbacks |
| SESSION_SECRET | A secret key for session encryption |
| DEBUG | Set to "True" for development, "False" for production |
| CORS_ORIGINS | Comma-separated list of allowed origins for CORS (optional) |

## Usage

### Running the Server

Start the server with:

```bash
python -m scim_server.main
```

The server will be available at http://localhost:8000.

### Basic Usage

1. Navigate to http://localhost:8000 in your browser
2. You will be redirected to Microsoft Entra ID login
3. After successful authentication, you'll be redirected back to the server
4. You can now use the SCIM API endpoints

## API Endpoints

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /scim/v2/Users | Get a list of users |
| GET | /scim/v2/Users/{user_id} | Get a specific user |
| POST | /scim/v2/Users | Create a new user |
| PUT | /scim/v2/Users/{user_id} | Replace a user |
| PATCH | /scim/v2/Users/{user_id} | Update a user |
| DELETE | /scim/v2/Users/{user_id} | Delete a user |

### Group Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /scim/v2/Groups | Get a list of groups |
| GET | /scim/v2/Groups/{group_id} | Get a specific group |
| POST | /scim/v2/Groups | Create a new group |
| PUT | /scim/v2/Groups/{group_id} | Replace a group |
| PATCH | /scim/v2/Groups/{group_id} | Update a group |
| DELETE | /scim/v2/Groups/{group_id} | Delete a group |

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /login | Redirect to Microsoft Entra ID login |
| GET | /auth/callback | Handle authentication callback |
| GET | /logout | Log out and clear session |
| GET | / | Home page (requires authentication) |
| GET | /health | Health check endpoint |

## Authentication

This server uses Microsoft Entra ID for authentication. When a user accesses the server, they are redirected to the Microsoft Entra ID login page. After successful authentication, they are redirected back to the server with an authorization code, which is exchanged for an access token.

The access token is stored in the session and used for subsequent requests to the Microsoft Graph API.

## Setting Up Microsoft Entra ID with Test Data

### Creating a Test Tenant

1. Go to the [Microsoft Entra ID portal](https://entra.microsoft.com/)
2. If you don't have a tenant, create a free account
3. Navigate to "Tenants" and create a new tenant for testing

### Registering an Application

1. In your test tenant, go to "App registrations"
2. Click "New registration"
3. Enter a name for your application (e.g., "SCIM Server")
4. Set the redirect URI to `http://localhost:8000/auth/callback`
5. Click "Register"

### Configuring API Permissions

1. In your registered application, go to "API permissions"
2. Click "Add a permission"
3. Select "Microsoft Graph"
4. Select "Application permissions"
5. Add the following permissions:
   - User.ReadWrite.All
   - Group.ReadWrite.All
   - Directory.ReadWrite.All
6. Click "Add permissions"
7. Click "Grant admin consent for [your tenant]"

### Creating Client Secret

1. In your registered application, go to "Certificates & secrets"
2. Click "New client secret"
3. Enter a description and select an expiration period
4. Click "Add"
5. Copy the generated secret value (you won't be able to see it again)

### Creating Test Users and Groups

1. In your test tenant, go to "Users"
2. Click "New user" to create test users
3. Fill in the required information and click "Create"
4. Go to "Groups"
5. Click "New group" to create test groups
6. Fill in the required information and click "Create"
7. Add users to groups as needed

### Updating Configuration

Update your `.env` file with the following values:

```
CLIENT_ID=your_application_id
CLIENT_SECRET=your_client_secret
TENANT_ID=your_tenant_id
```

## Development

### Project Structure

```
scim_server/
├── api/                  # API endpoints
│   ├── users.py          # User endpoints
│   └── groups.py         # Group endpoints
├── models/               # Data models
│   ├── user.py           # User model
│   └── group.py          # Group model
├── schemas/              # Pydantic schemas
│   ├── user.py           # User schema
│   └── group.py          # Group schema
├── services/             # Business logic
│   └── scim.py           # SCIM service
├── utils/                # Utilities
│   ├── auth.py           # Authentication utilities
│   └── filtering.py      # SCIM filtering utilities
├── tests/                # Tests
│   └── scim-openapi.yml  # OpenAPI specification
├── config.py             # Configuration
└── main.py               # Application entry point
```

### Adding New Features

To add new features:

1. Update the appropriate model in `models/`
2. Update the corresponding schema in `schemas/`
3. Add the necessary service methods in `services/scim.py`
4. Add the API endpoints in `api/`

## Testing

### OpenAPI Specification

The server includes an OpenAPI specification in `scim_server/tests/scim-openapi.yml`. You can use this specification to test the API with tools like Postman or Swagger UI.

### Manual Testing

1. Start the server with `python -m scim_server.main`
2. Navigate to http://localhost:8000
3. Log in with your Microsoft Entra ID credentials
4. Use a tool like curl or Postman to test the API endpoints

Example curl command to get users:

```bash
curl -X GET "http://localhost:8000/scim/v2/Users" \
  -H "Cookie: session=your_session_cookie"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
