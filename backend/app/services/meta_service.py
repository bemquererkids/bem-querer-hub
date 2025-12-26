"""
Meta WhatsApp Business Cloud API Service
Handles communication with Meta's official WhatsApp Business Platform
API Version: v18.0
Documentation: https://developers.facebook.com/docs/whatsapp/cloud-api
"""
import httpx
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class MetaWhatsAppService:
    """Service for interacting with Meta WhatsApp Business Cloud API"""
    
    # Meta Graph API Base URL
    GRAPH_API_BASE = "https://graph.facebook.com/v18.0"
    
    def __init__(self, phone_number_id: str, access_token: str):
        """
        Initialize Meta WhatsApp service
        
        Args:
            phone_number_id: WhatsApp Business Phone Number ID from Meta
            access_token: Permanent access token from System User
        """
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """
        Send a text message via Meta WhatsApp Business API
        
        Args:
            to: Recipient phone number (with country code, no + sign)
            text: Message text (max 4096 characters)
            preview_url: Whether to show URL preview
        
        Returns:
            API response with message ID
            
        Example:
            response = await service.send_message(
                to="5511999999999",
                text="Olá! Como posso ajudar?"
            )
        """
        try:
            url = f"{self.GRAPH_API_BASE}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {
                    "preview_url": preview_url,
                    "body": text
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"✅ Message sent to {to}: {result}")
                return result
                
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response else {}
            logger.error(f"❌ Meta API Error ({e.response.status_code}): {error_detail}")
            raise MetaAPIError(
                f"Failed to send message: {error_detail.get('error', {}).get('message', str(e))}",
                status_code=e.response.status_code,
                error_data=error_detail
            )
        except httpx.RequestError as e:
            logger.error(f"❌ Network Error: {str(e)}")
            raise MetaAPIError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected error sending message: {str(e)}")
            raise
    
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "pt_BR",
        components: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send a template message (pre-approved by Meta)
        
        Args:
            to: Recipient phone number
            template_name: Name of the approved template
            language_code: Language code (default: pt_BR)
            components: Template components (header, body, buttons)
        
        Returns:
            API response with message ID
        """
        try:
            url = f"{self.GRAPH_API_BASE}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }
            
            if components:
                payload["template"]["components"] = components
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"✅ Template message sent to {to}: {template_name}")
                return result
                
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response else {}
            logger.error(f"❌ Template send failed: {error_detail}")
            raise MetaAPIError(
                f"Failed to send template: {error_detail.get('error', {}).get('message', str(e))}",
                status_code=e.response.status_code,
                error_data=error_detail
            )
        except Exception as e:
            logger.error(f"❌ Error sending template: {str(e)}")
            raise
    
    async def send_media(
        self,
        to: str,
        media_type: str,
        media_id: Optional[str] = None,
        media_link: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send media message (image, video, document, audio)
        
        Args:
            to: Recipient phone number
            media_type: Type of media (image, video, document, audio)
            media_id: Media ID (if uploaded to Meta)
            media_link: Public URL to media (alternative to media_id)
            caption: Optional caption for image/video
        
        Returns:
            API response with message ID
        """
        try:
            url = f"{self.GRAPH_API_BASE}/{self.phone_number_id}/messages"
            
            media_object = {}
            if media_id:
                media_object["id"] = media_id
            elif media_link:
                media_object["link"] = media_link
            else:
                raise ValueError("Either media_id or media_link must be provided")
            
            if caption and media_type in ["image", "video"]:
                media_object["caption"] = caption
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": media_type,
                media_type: media_object
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"✅ Media sent to {to}: {media_type}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Error sending media: {str(e)}")
            raise
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark a message as read
        
        Args:
            message_id: WhatsApp message ID
        
        Returns:
            API response
        """
        try:
            url = f"{self.GRAPH_API_BASE}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"❌ Error marking message as read: {str(e)}")
            # Don't raise - this is not critical
            return {"success": False, "error": str(e)}
    
    async def get_media_url(self, media_id: str) -> str:
        """
        Get download URL for media
        
        Args:
            media_id: Media ID from incoming message
        
        Returns:
            Download URL
        """
        try:
            url = f"{self.GRAPH_API_BASE}/{media_id}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()
                
                return result.get("url", "")
                
        except Exception as e:
            logger.error(f"❌ Error getting media URL: {str(e)}")
            raise
    
    async def download_media(self, media_url: str) -> bytes:
        """
        Download media from Meta CDN
        
        Args:
            media_url: URL from get_media_url()
        
        Returns:
            Media bytes
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    media_url,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.content
                
        except Exception as e:
            logger.error(f"❌ Error downloading media: {str(e)}")
            raise


class MetaAPIError(Exception):
    """Custom exception for Meta API errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.error_data = error_data or {}
        super().__init__(self.message)


# =====================================================
# Service Factory with Database Integration
# =====================================================

async def get_meta_service_for_clinic(clinic_id: str) -> MetaWhatsAppService:
    """
    Get Meta WhatsApp service instance for a specific clinic
    Loads credentials from database
    
    Args:
        clinic_id: Clinic UUID
    
    Returns:
        Configured MetaWhatsAppService instance
    
    Raises:
        ValueError: If WhatsApp integration not configured
    """
    from app.core.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        # Query clinic_integrations for WhatsApp config
        result = supabase.table('clinic_integrations') \
            .select('phone_number_id, waba_id, access_token, verify_token') \
            .eq('clinica_id', clinic_id) \
            .eq('type', 'whatsapp') \
            .eq('is_active', True) \
            .execute()
        
        if not result.data or len(result.data) == 0:
            raise ValueError(f"WhatsApp integration not configured for clinic {clinic_id}")
        
        config = result.data[0]
        
        # Validate required fields
        if not config.get('phone_number_id') or not config.get('access_token'):
            raise ValueError("WhatsApp integration incomplete: missing phone_number_id or access_token")
        
        return MetaWhatsAppService(
            phone_number_id=config['phone_number_id'],
            access_token=config['access_token']
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize Meta service for clinic {clinic_id}: {e}")
        raise


# Singleton for default clinic (backward compatibility)
_default_meta_service: Optional[MetaWhatsAppService] = None


def get_meta_service() -> MetaWhatsAppService:
    """
    Get Meta WhatsApp service instance (singleton pattern)
    For backward compatibility - loads from default clinic
    
    Returns:
        MetaWhatsAppService instance
    """
    global _default_meta_service
    
    if _default_meta_service is None:
        # Try to load from environment variables first
        import os
        phone_number_id = os.getenv("META_PHONE_NUMBER_ID")
        access_token = os.getenv("META_ACCESS_TOKEN")
        
        if phone_number_id and access_token:
            _default_meta_service = MetaWhatsAppService(
                phone_number_id=phone_number_id,
                access_token=access_token
            )
        else:
            # Try to load from database for default clinic
            import asyncio
            from app.core.database import get_supabase
            
            try:
                supabase = get_supabase()
                result = supabase.table('clinic_integrations') \
                    .select('phone_number_id, access_token') \
                    .eq('type', 'whatsapp') \
                    .eq('is_active', True) \
                    .limit(1) \
                    .execute()
                
                if result.data and len(result.data) > 0:
                    config = result.data[0]
                    _default_meta_service = MetaWhatsAppService(
                        phone_number_id=config['phone_number_id'],
                        access_token=config['access_token']
                    )
                else:
                    raise ValueError("No WhatsApp integration configured")
            except Exception as e:
                logger.error(f"Failed to initialize default Meta service: {e}")
                raise ValueError("WhatsApp integration not configured. Please configure in Settings.")
    
    return _default_meta_service
