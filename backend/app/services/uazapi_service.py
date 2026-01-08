import requests
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class UazAPIService:
    """
    Service for interacting with UazAPI (Free Server logic)
    """
    
    def __init__(self, instance_name: str, token: str, base_url: str = None):
        self.instance_name = instance_name
        self.token = token
        self.base_url = base_url or os.getenv("UAZAPI_BASE_URL", "https://api.uazapi.com")
        
        # Ensure base url has no trailing slash
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

    def _get_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def send_message(self, to: str, text: str) -> Dict[str, Any]:
        """
        Send text message
        """
        endpoint = f"/send/text"
        url = self._get_url(endpoint)
        
        # Logic from debug_uaz.py: Pass token in Query Param
        params = {"token": self.token}
        
        payload = {
            "number": self.normalize_phone(to),
            "text": text,
            "options": {
                "delay": 2500,
                "presence": "composing"
            }
        }
        
        try:
            logger.info(f"📤 Sending UazAPI message to {to} via {self.instance_name}")
            response = requests.post(url, json=payload, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to send UazAPI message: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise

    def normalize_phone(self, phone: str) -> str:
        """
        Ensure phone format is correct DDI+DDD+NUMBER (5585999...)
        """
        # Remove non-digits
        clean = "".join(filter(str.isdigit, phone))
        
        # If starts with 55 and length is correct, ok
        if clean.startswith("55") and len(clean) >= 12:
            return clean
            
        # If no DDI, add 55 (brazil hardcoded for now)
        if len(clean) <= 11:
            return f"55{clean}"
            
        return clean

    def check_connection(self) -> bool:
        """
        Check if instance is connected
        """
        endpoint = f"/instance/connectionState/{self.instance_name}"
        url = self._get_url(endpoint)
        params = {"token": self.token}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Adapting to response format seen in debug
                state = data.get("instance", {}).get("state", "") or data.get("state", "")
                return state == "open" or data.get("status") == "connected"
            return False
        except Exception as e:
            logger.error(f"Check connection failed: {e}")
            return False

    def update_lead(self, phone: str, name: str = None, status: str = None) -> Dict[str, Any]:
        """
        Update Lead info in UazAPI Internal CRM
        Doc: https://docs.uazapi.com/tag/CRM
        """
        endpoint = "/chat/editLead"
        url = self._get_url(endpoint)
        params = {"token": self.token}
        
        # Ensure JID format (5511... @s.whatsapp.net or @c.us)
        # UazAPI doc usually prefers @s.whatsapp.net for individual chats
        clean_phone = self.normalize_phone(phone)
        if "@" not in clean_phone:
            # Default to whatsapp.net JID
            jid = f"{clean_phone}@s.whatsapp.net"
        else:
            jid = clean_phone
            
        payload = {
            "id": jid, # Correct key based on doc analysis
        }
        
        if name:
            payload["lead_name"] = name
        if status:
            payload["lead_status"] = status
            # Also try to sync as tag, just in case
            # payload["lead_tags"] = [status] 
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "token": self.token,
            "apikey": self.token,
            "Content-Type": "application/json"
        }
        
        try:
            # logger.info(f"🔄 Syncing Lead {phone} to UazAPI: {payload}")
            response = requests.post(url, json=payload, params=params, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to sync lead to UazAPI: {response.text}")
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Error syncing lead to UazAPI: {e}")
            return {}

    def add_tag(self, phone: str, tag: str) -> Dict[str, Any]:
        """
        Add a tag/label to a chat.
        Note: UazAPI might require label IDs, but let's try pushing to editLead tags first or legacy endpoint.
        """
        # Strategy: Use editLead to add tags as it handles string names better in internal CRM
        return self.update_lead(phone, status=tag) 
        
    def delete_message(self, phone: str, message_id: str) -> bool:
        """
        Revoke/Delete a message for everyone.
        Endpoint: /message/delete (POST)
        Payload: { "id": "...", "remoteJid": "..." }
        """
        endpoint = "/message/delete"
        url = self._get_url(endpoint)
        
        # Ensure JID
        clean_phone = self.normalize_phone(phone)
        if "@" not in clean_phone:
            jid = f"{clean_phone}@s.whatsapp.net"
        else:
            jid = clean_phone
            
        payload = {
            "id": message_id,
            "remoteJid": jid
        }
        
        headers = {
            "apikey": self.token,
            "token": self.token,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"🗑️ Revoking message {message_id} for {phone}")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Message revoked successfully")
                return True
            else:
                logger.warning(f"❌ Failed to revoke message: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error revoking message: {e}")
            return False


def get_uazapi_service() -> UazAPIService:
    """
    Get UazAPI service instance using environment variables
    This is a simple helper for endpoints that don't have clinic context
    """
    instance_name = os.getenv("UAZAPI_INSTANCE", "main")
    token = os.getenv("UAZAPI_TOKEN")
    base_url = os.getenv("UAZAPI_BASE_URL", "https://bemquerer.uazapi.com")
    
    if not token:
        raise ValueError("UAZAPI_TOKEN environment variable not set")
    
    return UazAPIService(
        instance_name=instance_name,
        token=token,
        base_url=base_url
    )

async def get_uazapi_service_for_clinic(clinic_id: str) -> UazAPIService:
    from app.core.database import get_supabase
    
    supabase = get_supabase()
    
    # 1. Get Integration Config
    res = supabase.table("clinic_integrations") \
        .select("*") \
        .eq("clinica_id", clinic_id) \
        .eq("type", "whatsapp") \
        .execute()
        
    if not res.data:
        raise ValueError("WhatsApp integration not configured for this clinic")
        
    config = res.data[0]
    
    # Check if it is UazAPI config (has instance_name)
    if not config.get("instance_name"):
         raise ValueError("This clinic is configured for Meta API, not UazAPI")
         
    return UazAPIService(
        instance_name=config.get("instance_name"),
        token=config.get("token") or config.get("api_key"),
        base_url=os.getenv("UAZAPI_BASE_URL", "https://bemquerer.uazapi.com")
    )
