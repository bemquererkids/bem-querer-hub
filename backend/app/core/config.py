"""
Configuration Management using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""
    
    # Application
    APP_NAME: str = "Bem-Querer Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Supabase
    SUPABASE_URL: Optional[str] = "https://placeholder.supabase.co"
    SUPABASE_KEY: Optional[str] = "placeholder_key"
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # Google Gemini (Legacy - Keeping for compatibility if needed)
    GEMINI_API_KEY: Optional[str] = "placeholder_key"
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    # OpenAI (Main Brain)
    OPENAI_API_KEY: Optional[str] = "sk-placeholder"
    
    # UazAPI
    UAZAPI_BASE_URL: Optional[str] = "https://api.uazapi.com"
    UAZAPI_TOKEN: Optional[str] = "placeholder_token"
    
    # Clinicorp (Future Integration)
    CLINICORP_API_URL: Optional[str] = None
    CLINICORP_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: Optional[str] = "supersecret_fallback_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra='ignore' 
    )


settings = Settings()
