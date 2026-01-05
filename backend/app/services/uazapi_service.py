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
        endpoint = f"/message/sendText/{self.instance_name}"
        url = self._get_url(endpoint)
        
        # Logic from debug_uaz.py: Pass token in Query Param
        params = {"token": self.token}
        
        payload = {
            "number": self.normalize_phone(to),
            "text": text,
            "options": {
                "delay": 1200,
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
