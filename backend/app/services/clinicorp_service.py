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
    
    BASE_URL = "https://api.clinicorp.com/rest/v1"
    # Old OAuth URL (kept for reference or legacy support if needed)
    # AUTH_URL = "https://auth.clinicorp.com/oauth/token"
    
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

    def _get_basic_auth_header(self) -> Dict[str, str]:
        """Generates Basic Auth Header"""
        import base64
        # Username is client_id (e.g. 'bemquerer'), Password is client_secret (Token)
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        return {"Authorization": f"Basic {base64_auth}"}

    async def _get_valid_token(self) -> str:
        """
        Legacy OAuth Token getter.
        For Basic Auth, we don't need this, but we keep the structure compatible.
        """
        if self.api_token:
            return self.api_token
        return "" # Basic Auth doesn't use Bearer token flow normally

    async def _request(self, method: str, endpoint: str, data: Dict = None) -> Any:
        """Authenticated Request Wrapper"""
        # --- MOCK MODE ---
        if self.client_id == "mock":
            return self._mock_response(method, endpoint, data)
        # -----------------

        # Use Basic Auth Header
        headers = {**self.headers, **self._get_basic_auth_header()}
        
        # Try both base URLs if necessary or specific one for API Key
        url = f"{self.BASE_URL}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            # Inject params for GET
            params = data if method == "GET" else None
            json_body = data if method != "GET" else None
            
            response = await client.request(method, url, params=params, json=json_body, headers=headers)
            
            # Logic for OAuth refresh removed/suspended for Basic Auth focus
            # if response.status_code == 401: ...
            
            # Handle 404 gracefully for some endpoints
            if response.status_code == 404:
                 print(f"[Clinicorp] Endpoint not found: {url}")
                 return [] if method == "GET" else {}

            response.raise_for_status()
            return response.json()

    # ==========================================
    # Public Methods (Business Logic)
    # ==========================================

    async def get_access_context(self) -> Dict[str, str]:
        """
        Discover the valid subscriber_id and business_id for this account.
        Endpoint: /group/list_subscribers_clinics
        """
        res = await self._request("GET", "/group/list_subscribers_clinics")
        
        # Expecting a list of clinics
        if isinstance(res, list) and len(res) > 0:
            first_unit = res[0]
            self.context = { # Store for debug visibility
                "subscriber_id": first_unit.get("SubscriberBussinessUID"),
                "business_id": first_unit.get("CompanyId")
            }
            return self.context
        
        # Fallback if structure is different (some APIs wrap in 'data')
        if isinstance(res, dict) and "data" in res:
             data_list = res.get("data", [])
             if data_list and len(data_list) > 0:
                  first_unit = data_list[0]
                  self.context = {
                    "subscriber_id": first_unit.get("SubscriberBussinessUID"),
                    "business_id": first_unit.get("CompanyId")
                }
                  return self.context
        
        print(f"[Clinicorp] No subscribers/clinics found in discovery. Response structure: {type(res)}")
        self.discovery_raw = str(res)[:300] # Capture raw for debug
        
        # --- FALLBACK: Explicit Business List ---
        # If discovery is empty, try listing businesses for the client_id directly
        # This handles cases where user has access (API User) but is not the generic subscriber owner.
        print(f"[Clinicorp] Attempting fallback: /business/list?subscriber_id={self.client_id}")
        try:
             # Force casting subscriber_id to ensure it's passed
             res_fallback = await self._request("GET", "/business/list", {"subscriber_id": self.client_id})
             
             # Support List or Dict wrapper for fallback
             fallback_list = []
             if isinstance(res_fallback, list): fallback_list = res_fallback
             elif isinstance(res_fallback, dict): fallback_list = res_fallback.get("list", res_fallback.get("data", []))
             
             if len(fallback_list) > 0:
                 first = fallback_list[0]
                 print(f"[Clinicorp] Fallback Success. Business Found: {first.get('BusinessName')}")
                 self.context = {
                     "subscriber_id": self.client_id, # We assume client_id IS the subscriber
                     "business_id": first.get("id")   # Use 'id' from business list
                 }
                 return self.context
             else:
                 print(f"[Clinicorp] Fallback returned empty list.")
                 self.discovery_raw += f" | Fallback: {str(res_fallback)[:100]}"
                 
        except Exception as e:
            print(f"[Clinicorp] Fallback failed: {e}")
            self.discovery_raw += f" | Fallback Error: {str(e)}"
            
        return {}

    async def get_appointments(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch appointments within date range using auto-discovered context.
        """
        # 1. Discover Context
        context = await self.get_access_context()
        if not context:
            print("[Clinicorp] Failed to discover context (subscriber_id).")
            return []
            
        subscriber_id = context.get("subscriber_id")
        business_id = context.get("business_id")
        
        # 2. Fetch Appointments
        endpoint = "/appointment/list"
        data = {
            "from": start_date,
            "to": end_date,
            "businessId": business_id,
            "subscriber_id": subscriber_id
        }
        
        res = await self._request("GET", endpoint, data)
        return res if isinstance(res, list) else res.get("list", [])
    
    async def get_patients(self) -> List[Dict]:
        """
        Use discovery as the connectivity check.
        Returns the raw list of clinics found.
        """
        return await self._request("GET", "/group/list_subscribers_clinics")

    async def get_financials(self, start_date: str, end_date: str) -> Dict[str, float]:
        """
        Get financial summary. Endpoint is hypothetical or custom.
        For now, let's try to list receipts if possible, or return mock.
        Docs don't show clear financial summary. 
        """
        # Discover context to be safe
        context = await self.get_access_context()
        if not context: return {"sales_count": 0, "revenue": 0.0}
        
        try:
            # Hipótese de endpoint. Se falhar (404), o _request retorna {}
            # Endpoint comum em sistemas médicos: /financial/list_receipts, /report/financial
            res = await self._request("GET", f"/financial/list_receipts?start={start_date}&end={end_date}")
            
            total_revenue = 0.0
            sales_count = 0
            
            if isinstance(res, list):
                for item in res:
                    total_revenue += float(item.get("value", 0))
                    sales_count += 1
            elif isinstance(res, dict) and "data" in res:
                 for item in res["data"]:
                    total_revenue += float(item.get("value", 0))
                    sales_count += 1
                    
            return {"revenue": total_revenue, "sales_count": sales_count}
            
        except Exception as e:
            print(f"[Clinicorp] Error fetching financials: {e}")
            return {"revenue": 0.0, "sales_count": 0}

    async def check_availability(self, date: str, professional_id: Optional[str] = None) -> List[Dict]:
        """
        Consulta horários disponíveis.
        Endpoint: /appointment/get_avaliable_times_calendar
        """
        endpoint = f"/appointment/get_avaliable_times_calendar?date={date}&subscriber_id=bemquerer&code_link=90984"
        if professional_id:
            endpoint += f"&professionalId={professional_id}"
            
        try:
            results = await self._request("GET", endpoint)
            
            # --- CLIENT SIDE FILTERING ---
            # API seems to ignore professionalId param or returns mixed results sometimes.
            # We enforce filtering here to be safe.
            if professional_id:
                filtered = []
                target_id = str(professional_id)
                for slot in results:
                    # Slot keys might be PascalCase 'ProfessionalId'
                    slot_prof_id = str(slot.get("ProfessionalId", slot.get("professionalId", "")))
                    if slot_prof_id == target_id:
                        filtered.append(slot)
                return filtered
                
            return results
        except Exception as e:
            print(f"[Clinicorp] Error checking availability: {e}")
            return []

    async def create_patient(self, patient_data: Dict) -> str:
        """
        Cria paciente e retorna o ID do Clinicorp.
        POST /patient/create
        """
        # API requires PascalCase for Name and subscriber_id in body
        payload = {
            "Name": patient_data["full_name"],
            "Cpf": patient_data.get("cpf"),
            "Phone": patient_data.get("phone"),
            "Email": patient_data.get("email"),
            "BirthDate": patient_data.get("birth_date"),
            "subscriber_id": "bemquerer" # Required in body
        }
        # Removing None values to avoid potential "null" string issues
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # Endpoint is /patient/create
        res = await self._request("POST", "/patient/create", payload)
        return str(res["id"])

    async def create_appointment(self, appointment_data: Dict) -> str:
        """
        Agenda consulta via API.
        Endpoint: /appointment/create_appointment_by_api
        
        ATENCAO: Atualmente este endpoint retorna erro "Necessário ID da Clínica".
        A implementação abaixo está PREPARADA mas aguardando correcao do parametro ClinicId.
        """
        url = "/appointment/create_appointment_by_api"
        payload = {
            "PatientId": appointment_data.get("patient_id"), # ID numérico (ex: 5589...)
            "Date": appointment_data.get("date"),            # YYYY-MM-DD
            "BeginTime": appointment_data.get("start_time"), # HH:MM
            "EndTime": appointment_data.get("end_time"),     # HH:MM
            "Observation": appointment_data.get("observation", "Agendamento via BemQuerer"),
            "subscriber_id": "bemquerer",
            # TODO: Descobrir o nome correto deste campo
            # "ClinicId": 90984, 
        }
        
        # Por enquanto, loga e retorna erro para não quebrar silenciosamente
        print(f"[Clinicorp] Warning: Tentatina de agendamento. Endpoint incompleto. Payload: {payload}")
        
        try:
             res = await self._request("POST", url, payload)
             return str(res.get("id", ""))
        except Exception as e:
             raise NotImplementedError(f"Falha na criação de agendamento (Parâmetro de Clínica pendente). Detalhes: {e}")

    async def get_professionals(self) -> List[Dict]:
        """Lista dentistas disponíveis"""
        return await self._request("GET", "/professional/list_all_professionals")

if __name__ == "__main__":
    import asyncio
    import base64
    
    # Credentials from User
    CLIENT_ID = "bemquerer"
    CLIENT_SECRET = "8b6b218c-b536-4db5-97a1-babffc283eec"
    BASE_URL = "https://api.clinicorp.com/rest/v1"

    async def debug_main():
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            print("\n--- DEBUG RUN ---")
            print(f"Auth Header: Basic {b64_auth[:10]}...")
            
            # 1. Discovery
            url = f"{BASE_URL}/group/list_subscribers_clinics"
            print(f"GET {url}")
            try:
                resp = await client.get(url, headers=headers)
                print(f"Status: {resp.status_code}")
                print(f"Raw Body: {resp.text}")
            except Exception as e:
                print(f"Error: {e}")
                
            # 2. Security List (Fallback check)
            url2 = f"{BASE_URL}/security/list_users?subscriber_id=bemquerer"
            print(f"\nGET {url2}")
            try:
                resp = await client.get(url2, headers=headers)
                print(f"Status: {resp.status_code}")
                print(f"Raw Body: {resp.text[:1000]}") 
                
                # Check for clues
                if "SubscriberBussinessUID" in resp.text:
                    print(">>> Found SubscriberBussinessUID in users list!")
            except Exception as e:
                print(f"Error: {e}")

            # 3. Business List with param
            url3 = f"{BASE_URL}/business/list?subscriber_id=bemquerer"
            print(f"\nGET {url3}")
            try:
                resp = await client.get(url3, headers=headers)
                print(f"Status: {resp.status_code}")
                print(f"Raw Body: {resp.text[:1000]}")
            except Exception as e:
                print(f"Error: {e}")

            # 4. DIRECT APPOINTMENT TEST (The Golden Test)
            # Using ID found in user's JSON: 5841644010143744
            print("\n4. GET /appointment/list (Magic ID Test)")
            # Dates: 2025-12-01 to 2025-12-31 (like dashboard)
            url4 = f"{BASE_URL}/appointment/list?from=2025-12-01&to=2025-12-31&businessId=5841644010143744&subscriber_id=bemquerer"
            try:
                resp = await client.get(url4, headers=headers)
                print(f"Status: {resp.status_code}")
                print(f"Body: {resp.text[:1000]}")
            except Exception as e:
                print(f"Error: {e}")

    asyncio.run(debug_main())
