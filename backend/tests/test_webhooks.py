"""
Unit Tests for Webhook Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_webhook_health():
    """Test webhook health endpoint"""
    response = client.get("/webhook/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "webhooks"


def test_whatsapp_webhook_receives_event():
    """Test that webhook endpoint accepts events"""
    payload = {
        "event": "messages.upsert",
        "instance": "test-instance",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "test-message-id"
            },
            "message": {
                "conversation": "Olá, gostaria de agendar uma consulta"
            }
        }
    }
    
    response = client.post("/webhook/whatsapp", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
    assert data["event"] == "messages.upsert"


def test_whatsapp_webhook_invalid_payload():
    """Test webhook with invalid payload"""
    payload = {
        "invalid": "data"
    }
    
    response = client.post("/webhook/whatsapp", json=payload)
    
    # Should return 422 for validation error
    assert response.status_code == 422
