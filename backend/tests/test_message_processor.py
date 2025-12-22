"""
Unit Tests for Message Processor
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.message_processor import MessageProcessor, get_message_processor


@pytest.mark.asyncio
async def test_message_processor_singleton():
    """Test that get_message_processor returns the same instance"""
    processor1 = get_message_processor()
    processor2 = get_message_processor()
    
    assert processor1 is processor2


@pytest.mark.asyncio
async def test_process_incoming_message_creates_chat():
    """Test that processing a message creates a chat if it doesn't exist"""
    processor = MessageProcessor()
    
    with patch.object(processor.supabase, 'table') as mock_table:
        # Mock chat creation
        mock_select = Mock()
        mock_select.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
        
        mock_insert = Mock()
        mock_insert.insert.return_value.execute.return_value.data = [{
            "id": "chat-123",
            "clinic_id": "clinic-1",
            "whatsapp_number": "5511999999999",
            "status": "open"
        }]
        
        mock_table.side_effect = [mock_select, mock_insert]
        
        with patch.object(processor.gemini, 'process_message', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = {
                "response": "Olá!",
                "intent": "question",
                "urgency": "normal",
                "needs_human": False
            }
            
            with patch.object(processor, '_get_chat_history', new_callable=AsyncMock) as mock_history:
                mock_history.return_value = []
                
                with patch.object(processor, '_store_message', new_callable=AsyncMock):
                    with patch.object(processor, '_update_chat_metadata', new_callable=AsyncMock):
                        result = await processor.process_incoming_message(
                            clinic_id="clinic-1",
                            whatsapp_number="5511999999999",
                            message_content="Olá"
                        )
                        
                        assert result["success"] == True
                        assert "response" in result


@pytest.mark.asyncio
async def test_process_incoming_message_error_handling():
    """Test error handling in message processing"""
    processor = MessageProcessor()
    
    with patch.object(processor, '_get_or_create_chat', new_callable=AsyncMock) as mock_chat:
        mock_chat.side_effect = Exception("Database error")
        
        result = await processor.process_incoming_message(
            clinic_id="clinic-1",
            whatsapp_number="5511999999999",
            message_content="Test"
        )
        
        assert result["success"] == False
        assert "error" in result
