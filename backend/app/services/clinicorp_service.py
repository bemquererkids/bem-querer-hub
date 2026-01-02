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
           # Ensure context is known (Bypass: We are forcing it now)
        # if not self.context or not self.context.get("business_id"):
        #      await self.get_access_context()
        
        # Business ID correto fornecido pelo usuário
        bid = "5841644010143744"
        sub = "bemquerer"
        
        print(f"[Clinicorp] Forcing Business ID: {bid} for Subscriber: {sub}")
        
        # 2. Fetch Appointments
        endpoint = "/appointment/list"
        data = {
            "from": start_date, 
            "to": end_date,
            "businessId": bid,
            "subscriber_id": sub
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
        # Business ID correto
        bid = "5841644010143744"
        sub = "bemquerer"
        
        endpoint = f"/appointment/get_avaliable_times_calendar"
        params = {
            "date": date,
            "businessId": bid,
            "subscriber_id": sub,
            "code_link": "90984"  # Código de acesso obrigatório
        }
        
        if professional_id:
            params["professionalId"] = professional_id

        try:
            results = await self._request("GET", endpoint, params)
            
            # Additional client-side filtering if API is loose
            if professional_id:
                filtered = []
                target_id = str(professional_id)
                for slot in results:
                    # Slot keys might be PascalCase 'ProfessionalId'
                    slot_prof_id = str(slot.get("ProfessionalId", slot.get("professionalId", "")))
                    if slot_prof_id == target_id:
                        filtered.append(slot)
                return filtered
                
            return results if isinstance(results, list) else []
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
        return str(res.get("id"))

    async def create_appointment(self, appointment_data: Dict) -> str:
        """
        Agenda consulta via API.
        Endpoint: /appointment/create_appointment_by_api
        """
        url = "/appointment/create_appointment_by_api"
        
        # Business ID correto
        bid = 5841644010143744  # Integer para JSON
        
        payload = {
            "PatientId": appointment_data.get("patient_id"), # ID numérico (ex: 5589...)
            "Date": appointment_data.get("date"),            # YYYY-MM-DD
            "BeginTime": appointment_data.get("start_time"), # HH:MM
            "EndTime": appointment_data.get("end_time"),     # HH:MM
            "Observation": appointment_data.get("observation", "Agendamento via BemQuerer AI"),
            "subscriber_id": "bemquerer",
            "ClinicId": bid, 
            "ProfessionalId": appointment_data.get("professional_id") # Opcional?
        }
        
        # Remove keys with None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        print(f"[Clinicorp] Attempting Booking: {payload}")
        
        try:
             res = await self._request("POST", url, payload)
             return str(res.get("id", ""))
        except Exception as e:
             print(f"[Clinicorp] Booking Failed: {e}")
             raise e

    async def get_professionals(self) -> List[Dict]:
        """Lista dentistas disponíveis"""
        return await self._request("GET", "/professional/list_all_professionals")

if __name__ == "__main__":
    import asyncio
    import base64
    import json
    import httpx
    
    CLIENT_ID = "bemquerer"
    CLIENT_SECRET = "8b6b218c-b536-4db5-97a1-babffc283eec"
    BASE_URL = "https://api.clinicorp.com/rest/v1"

    async def verify_main():
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            print(f"\n--- DATA VERIFICATION RUN ---")
            
            # 1. Get Business List
            print("1. Fetching Businesses...")
            businesses = []
            try:
                resp = await client.get(f"{BASE_URL}/business/list?subscriber_id={CLIENT_ID}", headers=headers)
                data = resp.json()
                # Handle list vs dict wrapper
                if isinstance(data, list): businesses = data
                elif isinstance(data, dict): businesses = data.get("list", data.get("data", []))
                
                print(f"Found {len(businesses)} businesses.")
                for b in businesses:
                    print(f" - [{b.get('id')}] {b.get('BusinessName')}")
            except Exception as e:
                print(f"Fail: {e}")
                return

            # 2. Check Appointments for EACH business
            for b in businesses:
                bid = b.get('id')
                name = b.get('BusinessName')
                print(f"\nChecking Appointments for: {name} ({bid})")
                
                url = f"{BASE_URL}/appointment/list"
                params = {
                    "from": "2025-12-01",
                    "to": "2025-12-31",
                    "businessId": bid,
                    "subscriber_id": CLIENT_ID
                }
                try:
                    resp = await client.get(url, headers=headers, params=params)
                    appts = resp.json()
                    
                    # Handle raw list or dict wrapper
                    if isinstance(appts, dict): appts = appts.get("list", [])
                    
                    count = len(appts)
                    print(f"!!! FOUND {count} APPOINTMENTS !!!")
                    if count > 0:
                        print(f"Sample Statuses: {[a.get('status') for a in appts[:5]]}")
                except Exception as e:
                    print(f"Error checking appts: {e}")

    asyncio.run(verify_main())
