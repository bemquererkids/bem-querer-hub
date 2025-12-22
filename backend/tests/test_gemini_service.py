"""
Unit Tests for Gemini Service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.gemini_service import GeminiService, get_gemini_service


@pytest.mark.asyncio
async def test_gemini_service_singleton():
    """Test that get_gemini_service returns the same instance"""
    service1 = get_gemini_service()
    service2 = get_gemini_service()
    
    assert service1 is service2


@pytest.mark.asyncio
async def test_classify_intent_booking():
    """Test intent classification for booking messages"""
    service = GeminiService()
    
    with patch.object(service.model, 'generate_content') as mock_generate:
        mock_response = Mock()
        mock_response.text = "booking"
        mock_generate.return_value = mock_response
        
        intent = await service.classify_intent("Gostaria de agendar uma consulta")
        
        assert intent == "booking"


@pytest.mark.asyncio
async def test_classify_intent_emergency():
    """Test intent classification for emergency messages"""
    service = GeminiService()
    
    with patch.object(service.model, 'generate_content') as mock_generate:
        mock_response = Mock()
        mock_response.text = "emergency"
        mock_generate.return_value = mock_response
        
        intent = await service.classify_intent("Meu filho está com muita dor de dente")
        
        assert intent == "emergency"


@pytest.mark.asyncio
async def test_process_message_returns_dict():
    """Test that process_message returns expected structure"""
    service = GeminiService()
    
    with patch.object(service.model, 'start_chat') as mock_chat:
        mock_chat_instance = Mock()
        mock_response = Mock()
        mock_response.text = '{"response": "Olá! Como posso ajudar?", "intent": "question", "urgency": "normal", "extracted_data": {}, "needs_human": false}'
        mock_chat_instance.send_message.return_value = mock_response
        mock_chat.return_value = mock_chat_instance
        
        result = await service.process_message("Olá")
        
        assert "response" in result
        assert "intent" in result
        assert "urgency" in result
        assert result["intent"] == "question"


@pytest.mark.asyncio
async def test_process_message_error_handling():
    """Test that errors are handled gracefully"""
    service = GeminiService()
    
    with patch.object(service.model, 'start_chat') as mock_chat:
        mock_chat.side_effect = Exception("API Error")
        
        result = await service.process_message("Test message")
        
        assert result["needs_human"] == True
        assert "error" in result
