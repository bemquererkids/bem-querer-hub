"""
Unit Tests for Database Module
"""
import pytest
from unittest.mock import Mock, patch
from app.core.database import SupabaseClient


def test_supabase_client_singleton():
    """Test that SupabaseClient returns the same instance"""
    # Reset the singleton
    SupabaseClient._instance = None
    
    with patch('app.core.database.create_client') as mock_create:
        mock_client = Mock()
        mock_create.return_value = mock_client
        
        client1 = SupabaseClient.get_client()
        client2 = SupabaseClient.get_client()
        
        # Should be the same instance
        assert client1 is client2
        
        # create_client should only be called once
        assert mock_create.call_count == 1


def test_admin_client_requires_service_key():
    """Test that admin client requires service key"""
    with patch('app.core.database.settings') as mock_settings:
        mock_settings.SUPABASE_SERVICE_KEY = None
        
        with pytest.raises(ValueError, match="SUPABASE_SERVICE_KEY not configured"):
            SupabaseClient.get_admin_client()
