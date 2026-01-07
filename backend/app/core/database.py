"""
Supabase Database Client Configuration
"""
from supabase import create_client, Client
from app.core.config import settings

# Version: 1.1.1 - Fixed proxy argument issue


# --------------------------------------------------
# Monkeypatch removed: httpx 0.28.1+ supports 'proxy' natively
# --------------------------------------------------

class MockSupabaseResponse:
    def __init__(self, data):
        self.data = data

class MockSupabaseQuery:
    def __init__(self, table_name):
        self.table_name = table_name
        self._filters = []
        self._data_to_set = {}
        
    def select(self, columns="*"):
        return self
        
    def eq(self, column, value):
        self._filters.append((column, value))
        return self
        
    def order(self, column, desc=False):
        return self
        
    def limit(self, count):
        return self
        
    def insert(self, data):
        self._data_to_set = data
        return self
        
    def update(self, data):
        self._data_to_set = data
        return self
        
    def execute(self):
        # Return Mock Data based on table
        if self.table_name == "chats":
            if self._data_to_set:
                # Return the data being inserted/updated as if it worked
                return MockSupabaseResponse([{"id": "mock_chat_new", **self._data_to_set}])
                
            return MockSupabaseResponse([
                {
                    "id": "mock_chat_1",
                    "intent": "booking",
                    "status": "open",
                    "last_message_at": "2025-12-21T10:00:00",
                    "patients": {
                        "full_name": "Ana (Simulada)",
                        "source": "google_ads"
                    }
                },
                {
                    "id": "mock_chat_2",
                    "intent": "question",
                    "status": "waiting_human",
                    "last_message_at": "2025-12-21T11:00:00",
                    "patients": {
                        "full_name": "Pedro (Simulado)",
                        "source": "instagram"
                    }
                }
            ])
        
        if self._data_to_set:
            # For insert/update on other tables
            return MockSupabaseResponse([{"id": f"mock_{self.table_name}_id", **self._data_to_set}])
            
        return MockSupabaseResponse([])

class MockSupabaseClient:
    def table(self, name):
        return MockSupabaseQuery(name)

class SupabaseClient:
    """Singleton Supabase Client"""
    
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            try:
                if "placeholder" in settings.SUPABASE_URL:
                     raise ValueError("Placeholder URL detected")
                     
                # Initialize without complex params first
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
            except Exception as e:
                print(f"❌ Failed to connect to Supabase: {e}")
                raise e
                
        return cls._instance
    
    @classmethod
    def get_admin_client(cls) -> Client:
        """Get Supabase client with service role key (bypasses RLS)"""
        if not settings.SUPABASE_SERVICE_KEY:
            raise ValueError(
                "SUPABASE_SERVICE_KEY is not configured. "
                "Please set this environment variable with your Supabase service_role key."
            )
        
        if "placeholder" in settings.SUPABASE_SERVICE_KEY:
            raise ValueError(
                "SUPABASE_SERVICE_KEY contains 'placeholder'. "
                "Please configure a real service_role key from Supabase."
            )
        
        return create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_KEY
        )


def get_supabase() -> Client:
    """Dependency injection for Supabase client"""
    return SupabaseClient.get_client()
