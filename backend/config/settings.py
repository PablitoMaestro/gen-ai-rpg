
import os

from pydantic_settings import BaseSettings


def get_env_file() -> str:
    """
    Intelligently determine which environment file to load.
    
    Uses .env.local for development and testing (local Supabase).
    Uses .env.production for production deployment.
    """
    # Check explicit ENVIRONMENT variable first
    env_var = os.getenv("ENVIRONMENT", "").lower()
    if env_var == "production":
        return ".env.production"

    # Check if running in production (common production indicators)
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RENDER") or os.getenv("HEROKU") or os.getenv("SCALEWAY_CONTAINER"):
        return ".env.production"

    # Default to local for development and tests
    return ".env.local"


class Settings(BaseSettings):
    # Environment
    environment: str = "development"

    # API Keys
    gemini_api_key: str
    elevenlabs_api_key: str | None = None

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str

    # Frontend URL for CORS
    frontend_url: str = "http://localhost:3000"

    # API Settings
    api_version: str = "1.0.0"
    api_title: str = "AI RPG Backend"
    api_description: str = "Backend API for AI-powered RPG game"

    class Config:
        env_file = get_env_file()
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()  # type: ignore
