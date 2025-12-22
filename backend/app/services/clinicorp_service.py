"""
Clinicorp Integration Service
Implements OAuth2 Flow and API Adapters
"""
import httpx
import time
from typing import Dict, Any, List, Optional
from app.core.config import settings

class ClinicorpClient:
    """
    Adapter for Clinicorp API with automatic token management.
    Scoping: This should be instantiated per clinic/tenant.
    """
    
    BASE_URL = "https://api.clinicorp.com/v1"  # Confirm base URL with docs
    AUTH_URL = "https://auth.clinicorp.com/oauth/token"
    
    def __init__(self, clinic_id: str, integration_config: Dict[str, Any]):
        self.clinic_id = clinic_id
        self.client_id = integration_config.get("client_id")
        self.client_secret = integration_config.get("client_secret")
        # Support for Direct API Token (User provided "Token API" in secret field)
        self.api_token = self.client_secret if self.client_secret and len(self.client_secret) < 100 else None
        
        self.access_token = integration_config.get("access_token")
        self.refresh_token = integration_config.get("refresh_token")
        self.token_expires_at = integration_config.get("token_expires_at", 0)
        
        # Headers default
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _get_valid_token(self) -> str:
        """Checks if token is valid, refreshes if necessary"""
        # DIRECT TOKEN MODE: If we have a static API token, use it directly.
        if self.api_token:
            return self.api_token

        if time.time() < self.token_expires_at - 60: # 60s buffer
            return self.access_token
            
        return await self._refresh_token()

    async def _refresh_token(self) -> str:
        """Performs OAuth2 Refresh Token Grant"""
        # ... existing OAuth logic ...
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                response = await client.post(self.AUTH_URL, json=payload)
                response.raise_for_status()
                
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"] # Updates refresh token (rotation)
                self.token_expires_at = time.time() + data["expires_in"]
                
                return self.access_token
                
            except Exception as e:
                print(f"[Clinicorp] Error refreshing token: {e}")
                # Fallback: If refresh fails, maybe the secret IS the token?
                if self.client_secret:
                     return self.client_secret
                raise

    async def _request(self, method: str, endpoint: str, data: Dict = None) -> Any:
        """Authenticated Request Wrapper"""
        # --- MOCK MODE ---
        if self.client_id == "mock":
            return self._mock_response(method, endpoint, data)
        # -----------------

        token = await self._get_valid_token()
        headers = {**self.headers, "Authorization": f"Bearer {token}"}
        
        # Try both base URLs if necessary or specific one for API Key
        url = f"{self.BASE_URL}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, json=data, headers=headers)
            
            if response.status_code == 401:
                # If unauthorized, and we are using OAuth, try refresh.
                if not self.api_token:
                    token = await self._refresh_token()
                    headers["Authorization"] = f"Bearer {token}"
                    response = await client.request(method, url, json=data, headers=headers)
            
            # Handle 404 gracefully for some endpoints
            if response.status_code == 404:
                 print(f"[Clinicorp] Endpoint not found: {url}")
                 return [] if method == "GET" else {}

            response.raise_for_status()
            return response.json()

    # ==========================================
    # Public Methods (Business Logic)
    # ==========================================

    async def get_appointments(self, date: str) -> List[Dict]:
        """
        Lista agendamentos de uma data.
        Endpoint: /appointment/get_appointment
        Params: subscriber_id, code_link
        """
        base_params = "subscriber_id=bemquerer&code_link=90984"
        try:
            return await self._request("GET", f"/appointment/get_appointment?date={date}&{base_params}")
        except Exception as e:
            print(f"[Clinicorp] Error fetching appointments: {e}")
            return []

    async def check_availability(self, date: str, professional_id: Optional[str] = None) -> List[Dict]:
        """
        Consulta horários disponíveis.
        Endpoint: /appointment/get_avaliable_times_calendar
        """
        endpoint = f"/appointment/get_avaliable_times_calendar?date={date}&subscriber_id=bemquerer&code_link=90984"
        if professional_id:
            endpoint += f"&professionalId={professional_id}"
            
        try:
            return await self._request("GET", endpoint)
        except Exception as e:
            print(f"[Clinicorp] Error checking availability: {e}")
            return []

    async def create_patient(self, patient_data: Dict) -> str:
        """
        Cria paciente e retorna o ID do Clinicorp.
        POST /patients
        """
        payload = {
            "name": patient_data["full_name"],
            "cpf": patient_data.get("cpf"),
            "phone": patient_data.get("phone"),
            "email": patient_data.get("email"),
            "birthdate": patient_data.get("birth_date")
        }
        res = await self._request("POST", "/patients", payload)
        return res["id"]

    async def create_appointment(self, appointment_data: Dict) -> str:
        """
        Agenda consulta.
        POST /appointments
        """
        res = await self._request("POST", "/appointments", appointment_data)
        return res["id"]

    async def get_professionals(self) -> List[Dict]:
        """Lista dentistas disponíveis"""
        return await self._request("GET", "/professionals")
