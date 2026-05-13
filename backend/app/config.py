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
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        extra_cors_origins = os.getenv("CORS_ORIGINS", "")
        self.CORS_ORIGINS = [
            origin.strip()
            for origin in ([frontend_url] + extra_cors_origins.split(","))
            if origin and origin.strip()
        ]

        # OpenRouter AI assistant
        self.OPENROUTER_ENABLED = os.getenv("OPENROUTER_ENABLED", "False").lower() == "true"
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
        self.OPENROUTER_BASE_URL = os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        )
        self.OPENROUTER_MODEL = os.getenv(
            "OPENROUTER_MODEL",
            "nvidia/nemotron-3-super-120b-a12b:free",
        )
        self.OPENROUTER_TIMEOUT_SECONDS = float(
            os.getenv("OPENROUTER_TIMEOUT_SECONDS", "45")
        )
        self.OPENROUTER_MAX_RETRIES = int(os.getenv("OPENROUTER_MAX_RETRIES", "2"))
        self.OPENROUTER_RETRY_BACKOFF_SECONDS = float(
            os.getenv("OPENROUTER_RETRY_BACKOFF_SECONDS", "1.5")
        )
        self.OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")
        self.OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", self.API_TITLE)
        
        # GitLab Integration
        self.GITLAB_API_BASE_URL = os.getenv(
            "GITLAB_API_BASE_URL",
            "https://gitlab.com"
        )
        self.GITLAB_SYNC_INTERVAL_MINUTES = int(
            os.getenv("GITLAB_SYNC_INTERVAL_MINUTES", "15")
        )
        self.GITLAB_ENABLE_AUTO_SYNC = os.getenv(
            "GITLAB_ENABLE_AUTO_SYNC",
            "True"
        ).lower() == "true"
        self.TOKEN_ENCRYPTION_KEY = os.getenv("TOKEN_ENCRYPTION_KEY", "")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

