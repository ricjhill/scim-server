import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Entra ID (Azure AD) configuration
    CLIENT_ID: str = os.environ.get("CLIENT_ID", "")
    CLIENT_SECRET: str = os.environ.get("CLIENT_SECRET", "")
    TENANT_ID: str = os.environ.get("TENANT_ID", "")
    AUTHORITY: Optional[str] = None
    REDIRECT_URI: str = os.environ.get("REDIRECT_URI", "http://localhost:8000/auth/callback")
    SCOPE: List[str] = ["User.Read", "User.ReadBasic.All", "Directory.Read.All"]
    
    # Application settings
    APP_NAME: str = "SCIM Server"
    SESSION_SECRET: str = os.environ.get("SESSION_SECRET", os.urandom(24).hex())
    DEBUG: bool = os.environ.get("DEBUG", "True").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        
    def __init__(self, **data):
        super().__init__(**data)
        if self.TENANT_ID:
            self.AUTHORITY = f"https://login.microsoftonline.com/{self.TENANT_ID}"

# Create settings instance
settings = Settings()
