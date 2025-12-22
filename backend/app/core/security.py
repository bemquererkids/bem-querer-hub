"""
Multi-tenant Middleware
Injects clinic_id into request context based on authenticated user
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.database import get_supabase
from typing import Optional


security = HTTPBearer()


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce multi-tenancy
    Extracts clinic_id from authenticated user and adds to request state
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        # Allows crm and integrations to be accessed without token for Prototype/Demo
        public_paths = [
            "/", "/health", "/docs", "/openapi.json", 
            "/webhook/whatsapp", "/webhooks/whatsapp", 
            "/webhook/clinicorp", "/webhooks/clinicorp",
            "/chat/message"
        ]
        public_prefixes = ["/crm", "/integrations"]
        
        if request.url.path in public_paths or any(request.url.path.startswith(prefix) for prefix in public_prefixes):
            return await call_next(request)
        
        # Extract JWT token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Verify token with Supabase
            supabase = get_supabase()
            user_response = supabase.auth.get_user(token)
            
            if not user_response or not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            user_id = user_response.user.id
            
            # Fetch user's clinic_id from profiles table
            profile_response = supabase.table("profiles").select("clinic_id, role").eq("id", user_id).single().execute()
            
            if not profile_response.data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User profile not found"
                )
            
            # Inject clinic_id and user info into request state
            request.state.user_id = user_id
            request.state.clinic_id = profile_response.data["clinic_id"]
            request.state.user_role = profile_response.data["role"]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication error: {str(e)}"
            )
        
        response = await call_next(request)
        return response


def get_current_clinic_id(request: Request) -> str:
    """Dependency to get clinic_id from request state"""
    if not hasattr(request.state, "clinic_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinic context not available"
        )
    return request.state.clinic_id


def get_current_user_id(request: Request) -> str:
    """Dependency to get user_id from request state"""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    return request.state.user_id
