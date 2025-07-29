from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    
    These settings can be configured using environment variables.
    """
    # Base
    PROJECT_NAME: str = "atol-canopy"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "atol_db"
    POSTGRES_PORT: str = "5433"
    DATABASE_URI: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    # ATOL DB variables (alternative naming)
    ATOL_DB_HOST: Optional[str] = None
    ATOL_DB_PORT: Optional[str] = None
    ATOL_DB_NAME: Optional[str] = None
    ATOL_DB_USER: Optional[str] = None
    ATOL_DB_PASSWORD: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    CORS_ORIGINS: Optional[List[str]] = None
    
    # Model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Use ATOL_DB_ variables if provided
        if self.ATOL_DB_HOST:
            self.POSTGRES_SERVER = self.ATOL_DB_HOST
        if self.ATOL_DB_PORT:
            self.POSTGRES_PORT = self.ATOL_DB_PORT
        if self.ATOL_DB_NAME:
            self.POSTGRES_DB = self.ATOL_DB_NAME
        if self.ATOL_DB_USER:
            self.POSTGRES_USER = self.ATOL_DB_USER
        if self.ATOL_DB_PASSWORD:
            self.POSTGRES_PASSWORD = self.ATOL_DB_PASSWORD
            
        # Use CORS_ORIGINS if provided
        if self.CORS_ORIGINS:
            self.BACKEND_CORS_ORIGINS = self.CORS_ORIGINS
            
        # Use DATABASE_URL if provided
        if self.DATABASE_URL:
            self.DATABASE_URI = self.DATABASE_URL
        elif not self.DATABASE_URI:
            self.DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
