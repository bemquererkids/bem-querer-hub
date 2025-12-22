"""
Unit Tests for Configuration Module
"""
import pytest
from app.core.config import Settings


def test_settings_defaults():
    """Test default settings values"""
    # Note: This will fail if .env is not configured
    # In real scenarios, use pytest fixtures with mock env vars
    settings = Settings(
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_KEY="test-key",
        GEMINI_API_KEY="test-gemini-key",
        UAZAPI_BASE_URL="https://test.uazapi.com",
        UAZAPI_TOKEN="test-token",
        SECRET_KEY="test-secret-key"
    )
    
    assert settings.APP_NAME == "Bem-Querer Hub"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.DEBUG == False
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30


def test_gemini_model_default():
    """Test Gemini model default value"""
    settings = Settings(
        SUPABASE_URL="https://test.supabase.co",
        SUPABASE_KEY="test-key",
        GEMINI_API_KEY="test-gemini-key",
        UAZAPI_BASE_URL="https://test.uazapi.com",
        UAZAPI_TOKEN="test-token",
        SECRET_KEY="test-secret-key"
    )
    
    assert settings.GEMINI_MODEL == "gemini-2.0-flash-exp"
