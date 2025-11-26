from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Custom Authenticator"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/authenticator"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    APP_MASTER_KEY: str = "change-this-to-a-secure-random-key-in-production"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
