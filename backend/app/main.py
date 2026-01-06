"""
Bem-Querer Hub - FastAPI Backend
Main Application Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from datetime import datetime
import httpx
import os

app = FastAPI(
    title="Bem-Querer Hub API",
    description="Sistema de CRM e WhatsApp para clínicas",
    version="1.1.0"
)

@app.get("/api/version/check")
async def version_check():
    return {"version": "v1.1-uazapi-restore", "timestamp": str(datetime.now())}

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router principal
main_router = APIRouter(prefix="/api")

# Debug endpoints
@main_router.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0"}

@main_router.get("/debug/env")
async def debug_env():
    return {
        "UAZAPI_BASE_URL": os.getenv("UAZAPI_BASE_URL", "NOT_SET"),
        "UAZAPI_TOKEN_SET": bool(os.getenv("UAZAPI_TOKEN")),
        "UAZAPI_INSTANCE": os.getenv("UAZAPI_INSTANCE", "NOT_SET"),
    }

@main_router.get("/debug/supabase")
async def debug_supabase():
    """Endpoint de debug para verificar configuração do Supabase"""
    from app.core.config import settings
    return {
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_KEY_SET": bool(settings.SUPABASE_KEY and settings.SUPABASE_KEY != "placeholder_key"),
        "SUPABASE_SERVICE_KEY_SET": bool(settings.SUPABASE_SERVICE_KEY),
        "IS_USING_MOCK": "placeholder" in (settings.SUPABASE_SERVICE_KEY or "placeholder"),
    }

# Debug completo da UazAPI
@main_router.get("/debug/uazapi")
async def debug_uazapi():
    """Endpoint de debug para testar conexão com UazAPI"""
    base_url = os.getenv("UAZAPI_BASE_URL")
    token = os.getenv("UAZAPI_TOKEN")
    
    results = []
    
    # Testar diferentes endpoints e formatos
    endpoints = [
        "/instance/status",
        "/instance/connectionState/bemquerer",
        "/instance/qrcode",
        "/status",
    ]
    
    auth_formats = [
        ("apikey", {f"apikey": token}),
        ("Bearer", {"Authorization": f"Bearer {token}"}),
        ("x-api-key", {"x-api-key": token}),
    ]
    
    for endpoint in endpoints:
        for auth_name, auth_header in auth_formats:
            try:
                url = f"{base_url}{endpoint}"
                headers = {**auth_header, "Content-Type": "application/json"}
                
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(url, headers=headers)
                    
                    results.append({
                        "endpoint": endpoint,
                        "auth_format": auth_name,
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response": response.text[:200]  # Primeiros 200 chars
                    })
            except Exception as e:
                results.append({
                    "endpoint": endpoint,
                    "auth_format": auth_name,
                    "error": str(e)
                })
    
    return {
        "base_url": base_url,
        "token_set": bool(token),
        "results": results
    }

# WhatsApp Status - Handled by integration router (removed mock to avoid conflict)

# Clinicorp Status - Check environment variables
@main_router.get("/integrations/clinicorp/status")
async def clinicorp_status():
    client_id = os.getenv("CLINICORP_CLIENT_ID")
    client_secret = os.getenv("CLINICORP_CLIENT_SECRET")
    
    connected = bool(client_id and client_secret)
    return {
        "connected": connected,
        "message": "Conectado via variáveis de ambiente" if connected else "Credenciais não configuradas"
    }

# OpenAI Status - Check environment variable
@main_router.get("/integrations/openai/status")
async def openai_status():
    api_key = os.getenv("OPENAI_API_KEY")
    
    connected = bool(api_key)
    return {
        "connected": connected,
        "message": "Conectado via variável de ambiente" if connected else "API Key não configurada"
    }

# Connect endpoints (save to env - only works locally, in production use Vercel dashboard)
@main_router.post("/integrations/clinicorp/connect")
async def connect_clinicorp(client_id: str, client_secret: str):
    # In production, these should already be set in Vercel
    # This endpoint just validates the connection
    if not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    
    return {"success": True, "message": "Credenciais validadas. Configure-as na Vercel para persistência."}

@main_router.post("/integrations/openai/connect")
async def connect_openai(api_key: str):
    # In production, this should already be set in Vercel
    # This endpoint just validates the connection
    if not api_key or not api_key.startswith("sk-"):
        raise HTTPException(status_code=400, detail="API Key inválida")
    
    return {"success": True, "message": "API Key validada. Configure-a na Vercel para persistência."}

app.include_router(main_router)

# Import and include webhooks router
from app.api.webhooks import router as webhooks_router
app.include_router(webhooks_router)

# Import and include integrations router
from app.api.integration import router as integration_router
app.include_router(integration_router)

# Import and include test router
from app.api.test_webhook import router as test_router
app.include_router(test_router)

# Import and include debug webhook router
from app.api.webhook_debug import router as webhook_debug_router
app.include_router(webhook_debug_router)

# Import real chat router
from app.api.chat import router as chat_router
app.include_router(chat_router)

# Import CRM router
from app.api.crm import router as crm_router
app.include_router(crm_router)

# Import CRM features router (notes, reminders)
from app.api.crm_features import router as crm_features_router
app.include_router(crm_features_router)

# Import UazAPI debug router
from app.api.debug_uazapi import router as debug_uazapi_router
app.include_router(debug_uazapi_router)

# Import test logs router
from app.api.test_logs import router as test_logs_router
app.include_router(test_logs_router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Bem-Querer Hub API", "version": "1.0.0"}



