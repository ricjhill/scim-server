<#
.SYNOPSIS
    Populates an Entra ID (Azure AD) instance with test resources for each identity type.

.DESCRIPTION
    This script creates one instance of each identity type in Entra ID:
    - User
    - Group
    - Application
    - Service Principal
    
    It uses direct Microsoft Graph API calls with PowerShell's Invoke-RestMethod.

.PARAMETER ClientId
    The Application (client) ID of your app registration.

.PARAMETER ClientSecret
    The client secret of your app registration.

.PARAMETER TenantId
    The Directory (tenant) ID of your Entra ID instance.

.PARAMETER Domain
    Your Entra ID domain (e.g., yourdomain.onmicrosoft.com).

.PARAMETER ConfigFile
    Path to a JSON configuration file containing clientId, clientSecret, tenantId, and domain.

.PARAMETER Prefix
    Prefix for resource names (default: "Test").

.PARAMETER CleanupOnly
    Switch to only remove previously created resources.

.EXAMPLE
    .\populate-entra-id.ps1 -ClientId "your-client-id" -ClientSecret "your-client-secret" -TenantId "your-tenant-id" -Domain "yourdomain.onmicrosoft.com"

.EXAMPLE
    .\populate-entra-id.ps1 -ConfigFile "config.json"

.EXAMPLE
    .\populate-entra-id.ps1 -Prefix "Dev"

.EXAMPLE
    .\populate-entra-id.ps1 -CleanupOnly
#>

param (
    [string]$ClientId,
    [string]$ClientSecret,
    [string]$TenantId,
    [string]$Domain,
    [string]$ConfigFile,
    [string]$Prefix = "Test",
    [switch]$CleanupOnly
)

# Function to write colored output
function Write-ColorOutput {
    param (
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to handle errors
function Handle-Error {
    param (
        [System.Management.Automation.ErrorRecord]$ErrorRecord,
        [string]$Operation
    )
    
    Write-ColorOutput "Error during $Operation" "Red"
    
    try {
        $errorResponse = $ErrorRecord.ErrorDetails.Message | ConvertFrom-Json
        Write-ColorOutput "Error message: $($errorResponse.error.message)" "Red"
    }
    catch {
        Write-ColorOutput "Error message: $($ErrorRecord.Exception.Message)" "Red"
    }
}

# Load configuration
if ($ConfigFile -and (Test-Path $ConfigFile)) {
    try {
        $config = Get-Content $ConfigFile | ConvertFrom-Json
        if (-not $ClientId) { $ClientId = $config.clientId }
        if (-not $ClientSecret) { $ClientSecret = $config.clientSecret }
        if (-not $TenantId) { $TenantId = $config.tenantId }
        if (-not $Domain) { $Domain = $config.domain }
    }
    catch {
        Write-ColorOutput "Error loading configuration file: $_" "Red"
        exit 1
    }
}

# Check required parameters
if (-not $ClientId -or -not $ClientSecret -or -not $TenantId -or -not $Domain) {
    Write-ColorOutput "Missing required parameters. Please provide ClientId, ClientSecret, TenantId, and Domain." "Red"
    Write-ColorOutput "Use -ConfigFile to specify a configuration file, or provide parameters directly." "Red"
    exit 1
}

# Resource tracking file
$resourceFile = "entra-resources.json"

# Handle cleanup mode
if ($CleanupOnly) {
    if (Test-Path $resourceFile) {
        try {
            $resources = Get-Content $resourceFile | ConvertFrom-Json
            
            # Get access token
            Write-ColorOutput "Getting access token for cleanup..." "Yellow"
            $tokenBody = @{
                client_id     = $ClientId
                scope         = "https://graph.microsoft.com/.default"
                client_secret = $ClientSecret
                grant_type    = "client_credentials"
            }
            
            $tokenResponse = Invoke-RestMethod -Uri "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token" -Method Post -Body $tokenBody
            $accessToken = $tokenResponse.access_token
            
            $headers = @{
                "Authorization" = "Bearer $accessToken"
                "Content-Type"  = "application/json"
            }
            
            $graphApiBase = "https://graph.microsoft.com/v1.0"
            
            # Delete resources in reverse order
            if ($resources.servicePrincipal) {
                Write-ColorOutput "Deleting service principal: $($resources.servicePrincipal.displayName)..." "Yellow"
                try {
                    Invoke-RestMethod -Uri "$graphApiBase/servicePrincipals/$($resources.servicePrincipal.id)" -Headers $headers -Method Delete
                    Write-ColorOutput "Service principal deleted successfully." "Green"
                }
                catch {
                    Handle-Error -ErrorRecord $_ -Operation "service principal deletion"
                }
            }
            
            if ($resources.application) {
                Write-ColorOutput "Deleting application: $($resources.application.displayName)..." "Yellow"
                try {
                    Invoke-RestMethod -Uri "$graphApiBase/applications/$($resources.application.id)" -Headers $headers -Method Delete
                    Write-ColorOutput "Application deleted successfully." "Green"
                }
                catch {
                    Handle-Error -ErrorRecord $_ -Operation "application deletion"
                }
            }
            
            if ($resources.group) {
                Write-ColorOutput "Deleting group: $($resources.group.displayName)..." "Yellow"
                try {
                    Invoke-RestMethod -Uri "$graphApiBase/groups/$($resources.group.id)" -Headers $headers -Method Delete
                    Write-ColorOutput "Group deleted successfully." "Green"
                }
                catch {
                    Handle-Error -ErrorRecord $_ -Operation "group deletion"
                }
            }
            
            if ($resources.user) {
                Write-ColorOutput "Deleting user: $($resources.user.displayName)..." "Yellow"
                try {
                    Invoke-RestMethod -Uri "$graphApiBase/users/$($resources.user.id)" -Headers $headers -Method Delete
                    Write-ColorOutput "User deleted successfully." "Green"
                }
                catch {
                    Handle-Error -ErrorRecord $_ -Operation "user deletion"
                }
            }
            
            # Remove the resource file
            Remove-Item $resourceFile
            Write-ColorOutput "Cleanup completed successfully." "Green"
        }
        catch {
            Write-ColorOutput "Error during cleanup: $_" "Red"
            exit 1
        }
    }
    else {
        Write-ColorOutput "Resource file not found. Nothing to clean up." "Yellow"
    }
    
    exit 0
}

# Get current timestamp for unique naming
$timestamp = Get-Date -Format "yyyyMMddHHmmss"

# Get access token
Write-ColorOutput "Getting access token..." "Yellow"
$tokenBody = @{
    client_id     = $ClientId
    scope         = "https://graph.microsoft.com/.default"
    client_secret = $ClientSecret
    grant_type    = "client_credentials"
}

try {
    $tokenResponse = Invoke-RestMethod -Uri "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token" -Method Post -Body $tokenBody
    $accessToken = $tokenResponse.access_token
    Write-ColorOutput "Access token obtained successfully." "Green"
}
catch {
    Handle-Error -ErrorRecord $_ -Operation "authentication"
    exit 1
}

# Set up headers for all subsequent calls
$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type"  = "application/json"
}

# Base URL for Microsoft Graph API
$graphApiBase = "https://graph.microsoft.com/v1.0"

# Initialize resources object
$resources = @{}

# Create user
Write-ColorOutput "Creating user..." "Yellow"
$userPrincipalName = "$($Prefix.ToLower())User$timestamp@$Domain"
$userBody = @{
    accountEnabled    = $true
    displayName       = "$Prefix User"
    mailNickname      = "$($Prefix.ToLower())user$timestamp"
    userPrincipalName = $userPrincipalName
    passwordProfile   = @{
        forceChangePasswordNextSignIn = $true
        password                      = "Complex!Password$timestamp"
    }
} | ConvertTo-Json

try {
    $user = Invoke-RestMethod -Uri "$graphApiBase/users" -Headers $headers -Method Post -Body $userBody
    Write-ColorOutput "User created successfully: $($user.displayName) ($($user.id))" "Green"
    $resources.user = @{
        id              = $user.id
        displayName     = $user.displayName
        userPrincipalName = $user.userPrincipalName
    }
}
catch {
    Handle-Error -ErrorRecord $_ -Operation "user creation"
}

# Create group
Write-ColorOutput "Creating group..." "Yellow"
$groupBody = @{
    displayName     = "$Prefix Group $timestamp"
    mailNickname    = "$($Prefix.ToLower())group$timestamp"
    mailEnabled     = $false
    securityEnabled = $true
    description     = "Test group created by populate-entra-id.ps1"
} | ConvertTo-Json

try {
    $group = Invoke-RestMethod -Uri "$graphApiBase/groups" -Headers $headers -Method Post -Body $groupBody
    Write-ColorOutput "Group created successfully: $($group.displayName) ($($group.id))" "Green"
    $resources.group = @{
        id          = $group.id
        displayName = $group.displayName
    }
    
    # Add user to group if both were created successfully
    if ($user -and $group) {
        Write-ColorOutput "Adding user to group..." "Yellow"
        $memberBody = @{
            "@odata.id" = "$graphApiBase/directoryObjects/$($user.id)"
        } | ConvertTo-Json
        
        try {
            Invoke-RestMethod -Uri "$graphApiBase/groups/$($group.id)/members/`$ref" -Headers $headers -Method Post -Body $memberBody
            Write-ColorOutput "User added to group successfully." "Green"
        }
        catch {
            Handle-Error -ErrorRecord $_ -Operation "adding user to group"
        }
    }
}
catch {
    Handle-Error -ErrorRecord $_ -Operation "group creation"
}

# Create application
Write-ColorOutput "Creating application..." "Yellow"
$appBody = @{
    displayName    = "$Prefix Application $timestamp"
    signInAudience = "AzureADMyOrg"
    web            = @{
        redirectUris = @(
            "https://localhost:8000/auth/callback"
        )
        implicitGrantSettings = @{
            enableIdTokenIssuance     = $true
            enableAccessTokenIssuance = $true
        }
    }
    requiredResourceAccess = @(
        @{
            resourceAppId  = "00000003-0000-0000-c000-000000000000" # Microsoft Graph
            resourceAccess = @(
                @{
                    id   = "e1fe6dd8-ba31-4d61-89e7-88639da4683d" # User.Read
                    type = "Scope"
                }
            )
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $app = Invoke-RestMethod -Uri "$graphApiBase/applications" -Headers $headers -Method Post -Body $appBody
    Write-ColorOutput "Application created successfully: $($app.displayName) ($($app.id))" "Green"
    Write-ColorOutput "Application (client) ID: $($app.appId)" "Green"
    $resources.application = @{
        id          = $app.id
        displayName = $app.displayName
        appId       = $app.appId
    }
}
catch {
    Handle-Error -ErrorRecord $_ -Operation "application creation"
}

# Create service principal
if ($app) {
    Write-ColorOutput "Creating service principal..." "Yellow"
    $spBody = @{
        appId              = $app.appId
        displayName        = "$Prefix Service Principal $timestamp"
        accountEnabled     = $true
        appRoleAssignmentRequired = $false
    } | ConvertTo-Json
    
    try {
        $sp = Invoke-RestMethod -Uri "$graphApiBase/servicePrincipals" -Headers $headers -Method Post -Body $spBody
        Write-ColorOutput "Service principal created successfully: $($sp.displayName) ($($sp.id))" "Green"
        $resources.servicePrincipal = @{
            id          = $sp.id
            displayName = $sp.displayName
            appId       = $sp.appId
        }
    }
    catch {
        Handle-Error -ErrorRecord $_ -Operation "service principal creation"
    }
}

# Save resources to file for future cleanup
$resources | ConvertTo-Json -Depth 10 | Out-File $resourceFile
Write-ColorOutput "Resource details saved to $resourceFile" "Green"

# Output summary
Write-ColorOutput "`nSummary of Created Resources:" "Cyan"
Write-ColorOutput "----------------------------" "Cyan"

if ($resources.user) {
    Write-ColorOutput "User:" "White"
    Write-ColorOutput "  Display Name: $($resources.user.displayName)" "White"
    Write-ColorOutput "  ID: $($resources.user.id)" "White"
    Write-ColorOutput "  UPN: $($resources.user.userPrincipalName)" "White"
}

if ($resources.group) {
    Write-ColorOutput "`nGroup:" "White"
    Write-ColorOutput "  Display Name: $($resources.group.displayName)" "White"
    Write-ColorOutput "  ID: $($resources.group.id)" "White"
}

if ($resources.application) {
    Write-ColorOutput "`nApplication:" "White"
    Write-ColorOutput "  Display Name: $($resources.application.displayName)" "White"
    Write-ColorOutput "  ID: $($resources.application.id)" "White"
    Write-ColorOutput "  Application (client) ID: $($resources.application.appId)" "White"
}

if ($resources.servicePrincipal) {
    Write-ColorOutput "`nService Principal:" "White"
    Write-ColorOutput "  Display Name: $($resources.servicePrincipal.displayName)" "White"
    Write-ColorOutput "  ID: $($resources.servicePrincipal.id)" "White"
}

Write-ColorOutput "`nTo clean up these resources, run:" "Yellow"
Write-ColorOutput ".\populate-entra-id.ps1 -CleanupOnly -ClientId `"$ClientId`" -ClientSecret `"$ClientSecret`" -TenantId `"$TenantId`" -Domain `"$Domain`"" "Yellow"
Write-ColorOutput "Or if using a config file:" "Yellow"
Write-ColorOutput ".\populate-entra-id.ps1 -CleanupOnly -ConfigFile `"$ConfigFile`"" "Yellow"
