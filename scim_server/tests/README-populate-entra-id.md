# Entra ID Population Script

This directory contains a PowerShell script for populating an Entra ID (Azure AD) instance with test resources for each identity type. This is useful for setting up a test environment for the SCIM server.

## Prerequisites

1. **PowerShell 5.1 or higher** - The script uses PowerShell's built-in capabilities
2. **Admin access to an Entra ID tenant** - You need permissions to create resources
3. **Application registration with appropriate permissions**:
   - Create an app registration in Entra ID
   - Grant it these API permissions:
     - `User.ReadWrite.All`
     - `Group.ReadWrite.All`
     - `Application.ReadWrite.All`
     - `Directory.ReadWrite.All`
   - Generate a client secret

## Setup Instructions

1. **Download the script** to your local machine
2. **Edit the script** to add your tenant-specific information:
   ```powershell
   # Replace these values with your own
   $clientId = "your-client-id"
   $clientSecret = "your-client-secret" 
   $tenantId = "your-tenant-id"
   $domain = "yourdomain.onmicrosoft.com"  # Your Entra ID domain
   ```

3. **Alternatively, create a config.json file** in the same directory:
   ```json
   {
     "clientId": "your-client-id",
     "clientSecret": "your-client-secret",
     "tenantId": "your-tenant-id",
     "domain": "yourdomain.onmicrosoft.com"
   }
   ```

## Running the Script

### Basic Usage

```powershell
# Run with values from the script
.\populate-entra-id.ps1

# Or specify values as parameters
.\populate-entra-id.ps1 -ClientId "your-client-id" -ClientSecret "your-client-secret" -TenantId "your-tenant-id" -Domain "yourdomain.onmicrosoft.com"

# Or use a config file
.\populate-entra-id.ps1 -ConfigFile "path\to\config.json"
```

### Script Parameters

- `-ClientId` - Application (client) ID from your app registration
- `-ClientSecret` - Secret from your app registration
- `-TenantId` - Directory (tenant) ID
- `-Domain` - Your Entra ID domain (e.g., yourdomain.onmicrosoft.com)
- `-ConfigFile` - Path to a JSON configuration file (optional)
- `-Prefix` - Prefix for resource names (default: "Test")
- `-CleanupOnly` - Switch to only remove previously created resources

### Examples

```powershell
# Create resources with a custom prefix
.\populate-entra-id.ps1 -Prefix "Dev"

# Clean up previously created resources
.\populate-entra-id.ps1 -CleanupOnly
```

## Understanding the Output

The script will:
1. Display progress as it creates each resource
2. Output a summary of all created resources with their IDs
3. Save resource details to `entra-resources.json` for future reference or cleanup
4. Display any errors encountered during creation

## What Gets Created

The script creates one instance of each identity type:

1. **User** - A basic user account with a random password
2. **Group** - A security group with the created user as a member
3. **Application** - An application registration with basic web settings
4. **Service Principal** - A service principal associated with the created application

## Troubleshooting

- **Authentication errors**: Verify your client ID, secret, and tenant ID
- **Permission errors**: Ensure your app registration has the required permissions and admin consent
- **Resource creation failures**: Check the error messages for specific issues
- **Execution policy**: If you can't run the script, you may need to adjust PowerShell's execution policy:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

## Cleaning Up

To remove all resources created by the script:
```powershell
.\populate-entra-id.ps1 -CleanupOnly
```

This will read the `entra-resources.json` file and delete all resources in reverse order (service principals first, then applications, groups, and users).

## Using with the SCIM Server

After running this script, you can use the created resources to test the SCIM server:

1. The created user can be used to authenticate with the SCIM server
2. The created group can be used to test group operations
3. The created application and service principal can be used to test application operations

## Script Details

The script uses direct Microsoft Graph API calls with PowerShell's `Invoke-RestMethod`. It does not use any external modules or dependencies, making it easy to run on any system with PowerShell.

For more details on the script's functionality, see the comments in the script file.
