"""
Supabase Database Client Configuration
"""
from supabase import create_client, Client
from app.core.config import settings

class MockSupabaseResponse:
    def __init__(self, data):
        self.data = data

class MockSupabaseQuery:
    def __init__(self, table_name):
        self.table_name = table_name
        self._filters = []
        
    def select(self, columns):
        return self
        
    def eq(self, column, value):
        self._filters.append((column, value))
        return self
        
    def execute(self):
        # Return Mock Data based on table
        if self.table_name == "chats":
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
                     
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
            except Exception as e:
                print(f"Using Mock Supabase Client due to: {e}")
                return MockSupabaseClient()
                
        return cls._instance
    
    @classmethod
    def get_admin_client(cls) -> Client:
        """Get Supabase client with service role key (bypasses RLS)"""
        # For admin client, we might also want to mock or fail hard
        # Let's mock it too to be safe for now
        if not settings.SUPABASE_SERVICE_KEY or "placeholder" in settings.SUPABASE_SERVICE_KEY:
             return MockSupabaseClient()
        
        return create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_KEY
        )


def get_supabase() -> Client:
    """Dependency injection for Supabase client"""
    return SupabaseClient.get_client()
