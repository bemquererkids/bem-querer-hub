"""
UazAPI Service
Handles communication with UazAPI (WhatsApp Gateway)
"""
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class UazAPIService:
    """Service for interacting with UazAPI"""
    
    def __init__(self):
        self.base_url = settings.UAZAPI_BASE_URL
        self.token = settings.UAZAPI_TOKEN
        self.headers = {
            "token": self.token,  # UazAPI uses 'token' header
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self,
        instance: str,
        phone: str,
        message: str,
        quoted_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a text message via UazAPI
        
        Args:
            instance: No longer used in URL path in v2.0, but kept for signature compatibility
            phone: Recipient phone number (with country code)
            message: Message text
            quoted_message_id: Optional message ID to quote/reply to
        
        Returns:
            API response with message ID
        """
        try:
            # v2.0 Endpoint: /send/text
            url = f"{self.base_url}/send/text"
            
            payload = {
                "number": phone,
                "text": message
            }
            
            if quoted_message_id:
                payload["replyid"] = quoted_message_id
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=15.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Error sending message via UazAPI: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            raise
    
    async def send_image(
        self,
        instance: str,
        phone: str,
        image_url: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send an image message"""
        try:
            # v2.0 Endpoint: /send/image
            url = f"{self.base_url}/send/image"
            
            payload = {
                "number": phone,
                "image": image_url
            }
            
            if caption:
                payload["caption"] = caption
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=20.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error sending image: {str(e)}")
            raise
    
    async def get_instance_status(self, instance: str) -> Dict[str, Any]:
        """
        Get WhatsApp instance connection status
        """
        try:
            # v2.0 Endpoint: /instance/status
            url = f"{self.base_url}/instance/status"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting instance status: {str(e)}")
            raise
    
    async def connect_instance(self, instance: str) -> Dict[str, Any]:
        """
        Generate/Retrieve QR code for WhatsApp connection
        """
        try:
            url = f"{self.base_url}/instance/connect"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json={},  # Body can be empty for QR
                    timeout=20.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error connecting instance: {str(e)}")
            raise

    async def configure_webhook_sync(self, instance: str, webhook_url: str) -> Dict[str, Any]:
        """
        Configure webhook to enable historical message sync
        """
        try:
            url = f"{self.base_url}/webhook"
            payload = {
                "enabled": True,
                "url": webhook_url,
                "events": ["messages", "history", "connection", "status"]
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error configuring webhook: {str(e)}")
            raise

    async def mark_as_read(
        self,
        instance: str,
        phone: str,
        message_id: str
    ) -> Dict[str, Any]:
        """Mark a message as read"""
        try:
            url = f"{self.base_url}/chat/markMessageAsRead/{instance}"
            
            payload = {
                "number": phone,
                "key": {
                    "id": message_id
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=5.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")
            raise


# Singleton instance
_uazapi_service: Optional[UazAPIService] = None


def get_uazapi_service() -> UazAPIService:
    """Get or create UazAPI service instance"""
    global _uazapi_service
    if _uazapi_service is None:
        _uazapi_service = UazAPIService()
    return _uazapi_service
