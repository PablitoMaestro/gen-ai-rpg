from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    
    # API Keys
    gemini_api_key: str
    elevenlabs_api_key: Optional[str] = None
    
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
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()