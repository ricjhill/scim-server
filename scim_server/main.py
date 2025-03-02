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

from scim_server.config import settings
from scim_server.api.users import router as users_router
from scim_server.api.groups import router as groups_router
from scim_server.utils.auth import EntraAuth

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="SCIM server implementation using Microsoft Entra ID for identity management",
    version="0.1.0"
)

# Add session middleware for authentication
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET
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
    Handle authentication callback from Microsoft Entra ID.
    """
    token_result = await EntraAuth.get_token_from_code(code)
    
    if "access_token" not in token_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )
    
    # Get user info and store in session
    user_info = await EntraAuth.get_user_info(token_result["access_token"])
    request.session["user"] = user_info
    request.session["token"] = token_result
    
    return RedirectResponse("/")

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
