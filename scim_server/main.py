"""
Main application entry point for the SCIM server.
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import msal
import httpx
import uvicorn
import logging

from scim_server.config import settings
from scim_server.api.users import router as users_router
from scim_server.api.groups import router as groups_router
from scim_server.utils.auth import EntraAuth

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(

    title=settings.APP_NAME,
    description="SCIM server implementation using Microsoft Entra ID for identity management",
    version="0.1.0"
)

# Add session middleware for authentication
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    session_cookie="scim_session",      # Explicit cookie name
    max_age=60 * 60 * 24,               # 1 day in seconds
    same_site="lax",                    # More compatible with HTTP sites
    https_only=False                    # Set to True in production with HTTPS
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(users_router)
app.include_router(groups_router)

# Authentication routes
@app.get("/login")
async def login():
    """
    Redirect to Microsoft Entra ID login page.
    """
    auth_url = EntraAuth.get_auth_url()
    logger.debug(f"Redirecting to auth URL: {auth_url}")
    
    # Use direct RedirectResponse for the login page
    # This is a simple external redirect that doesn't need to set cookies
    return RedirectResponse(auth_url, status_code=302)


@app.get("/auth/callback")
async def auth_callback(request: Request, code: str):
    """
    Handle the Microsoft Entra ID authentication callback.
    """
    logger.debug(f"Auth callback received with code: {code[:10]}...")
    
    try:
        # Get token from code
        logger.debug("Attempting to exchange code for token...")
        token_result = await EntraAuth.get_token_from_code(code)
        
        if "error" in token_result:
            logger.error(f"Error in token response: {token_result.get('error')}")
            logger.error(f"Error description: {token_result.get('error_description')}")
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication failed", "details": token_result.get("error_description")}
            )
        
        logger.debug("Token exchange successful")
        logger.debug(f"Access token starts with: {token_result.get('access_token', '')[:10]}...")
        logger.debug(f"Token type: {token_result.get('token_type')}")
        logger.debug(f"Expires in: {token_result.get('expires_in')} seconds")
        
        # Get user info
        logger.debug("Attempting to retrieve user info from Graph API...")
        try:
            user_info = await EntraAuth.get_user_info(token_result["access_token"])
            logger.debug(f"User info retrieved: {user_info.get('displayName')} ({user_info.get('userPrincipalName')})")
        except Exception as e:
            logger.error(f"Error retrieving user info: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"error": "Failed to retrieve user information"}
            )
        
        # Store in session
        logger.debug("Storing token and user info in session...")
        request.session["token"] = {
            "access_token": token_result["access_token"],
            "expires_in": token_result.get("expires_in"),
            "token_type": token_result.get("token_type")
        }
        request.session["user"] = {
            "id": user_info.get("id"),
            "displayName": user_info.get("displayName"),
            "userPrincipalName": user_info.get("userPrincipalName")
        }

       # Force the session to be saved
        request.scope["session"] = request.session
        request.scope["session"].update({})  # Force a modification to ensure saving
 

        # Create a redirect response
        response = RedirectResponse(url="/", status_code=302)
        
        
        # Check if session was actually set
        logger.debug(f"Session contains token: {'token' in request.session }")
        logger.debug(f"Session contains user: {'user' in request.session}")
        
        # Log the response headers for debugging
        logger.debug("Response headers will be:")
        for header, value in response.headers.items():
            logger.debug(f"  {header}: {value}")
        
        
        # Log session size for debugging
        import json
        session_data = json.dumps(dict(request.session))
        logger.debug(f"Session data size: {len(session_data)} bytes")
        
        
        
      
        
        logger.debug("Redirecting to home page...")
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in auth callback: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error during authentication"}
        )

@app.get("/logout")
async def logout(request: Request):
    """
    Log out and clear session.
    """
    request.session.clear()
    return RedirectResponse("/")

# Debug routes
@app.get("/test-login")
async def test_login(request: Request):
    """
    Test endpoint that sets session without redirect.
    This is useful for testing if the session middleware is working correctly.
    """
    # Set some test data in the session
    request.session["test_user"] = {"name": "Test User", "role": "tester"}
    request.session["test_time"] = str(logging.Formatter().converter())
    
    # Force the session to be saved
    request.scope["session"] = request.session
    request.scope["session"].update({})  # Force a modification to ensure saving
    
    # Log what we're doing
    logger.debug("Setting test session data in /test-login endpoint")
    logger.debug(f"Session contains test_user: {'test_user' in request.session}")
    
    # Return a simple response
    return {
        "message": "Test session data set successfully",
        "next_steps": "Check /debug-session to verify the session data was saved",
        "session_keys": list(request.session.keys())
    }

@app.get("/debug-cookies")
async def debug_cookies(request: Request):
    """
    Debug endpoint to check all cookies and set a test cookie.
    """
    # Get all cookies
    all_cookies = request.cookies
    
    # Create a response with a test cookie
    response = JSONResponse({
        "all_cookies": {k: "Present" for k in all_cookies.keys()},
        "cookie_count": len(all_cookies),
        "request_headers": {k: v for k, v in request.headers.items()},
        "test_cookie_set": True
    })
    
    # Set a test cookie with the same settings as the session cookie
    response.set_cookie(
        key="test_cookie",
        value="test_value",
        max_age=300,  # 5 minutes
        httponly=True,
        samesite="lax",  # Match the session cookie setting
        secure=False
    )
    
    return response

@app.get("/debug-session")
async def debug_session(request: Request):
    """
    Debug endpoint to check session status.
    """
    # Check if session exists in request scope
    session_exists = "session" in request.scope
    
    # Get the session cookie
    session_cookie = request.cookies.get("scim_session", "Not found")
    
    # Get session data keys (without exposing sensitive values)
    session_data = {}
    if hasattr(request, "session"):
        session_data = {k: "Present" for k in request.session.keys()}
    
    # Check if user is in session
    user_in_session = "user" in request.session if hasattr(request, "session") else False
    
    # Check if token is in session
    token_in_session = "token" in request.session if hasattr(request, "session") else False
    
    return {
        "session_exists": session_exists,
        "session_cookie": "Present" if session_cookie != "Not found" else "Not found",
        "session_cookie_length": len(session_cookie) if session_cookie != "Not found" else 0,
        "session_data_keys": session_data,
        "user_in_session": user_in_session,
        "token_in_session": token_in_session
    }

# Main routes
@app.get("/")
async def root(user: dict = Depends(EntraAuth.get_current_user)):
    """
    Root endpoint that requires authentication.
    """
    return {
        "message": "SCIM Server is running",
        "user": user.get("displayName", user.get("userPrincipalName")),
        "scim_endpoints": {
            "users": "/scim/v2/Users",
            "groups": "/scim/v2/Groups"
        }
    }

@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom exception handler for HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
            "status": str(exc.status_code),
            "detail": exc.detail
        }
    )

if __name__ == "__main__":
    uvicorn.run("scim_server.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
