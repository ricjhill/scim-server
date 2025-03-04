"""
Main application entry point for the SCIM server.
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
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
    same_site="lax",                    # Allow cookies for redirects
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
    return RedirectResponse(EntraAuth.get_auth_url())


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
        request.session["token"] = token_result
        request.session["user"] = user_info


        # Force the session to be saved
        request.scope["session"] = request.session
        request.scope["session"].update({})  # Force a modification to ensure saving

        # Add debug for cookie
        logger.debug(f"Session cookie will be set")






        # Check if session was actually set
        logger.debug(f"Session contains token: {'token' in request.session}")
        logger.debug(f"Session contains user: {'user' in request.session}")
        
        logger.debug("Redirecting to home page...")








        return RedirectResponse("/")
        
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
