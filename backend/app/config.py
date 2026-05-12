"""
Database and application configuration
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings from environment variables"""

    def __init__(self):
        # Database
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://user:password@localhost:5432/sprintflow"
        )
        self.DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"
        
        # Connection pooling
        self.DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        self.DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
        self.DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
        self.DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))
        
        # JWT
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
        )
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        
        # Application
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.API_TITLE = "SprintFlow API"
        self.API_VERSION = "0.1.0"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

