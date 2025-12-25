"""
Bem-Querer Hub - FastAPI Backend
Main Application Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
import httpx
import os

app = FastAPI(
    title="Bem-Querer Hub API",
    description="Sistema de CRM e WhatsApp para clínicas",
    version="1.0.0"
)

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

# WhatsApp Status - Versão simplificada
@main_router.get("/integrations/whatsapp/status")
async def whatsapp_status():
    return {
        "connected": True,  # Mock temporário
        "message": "Use /api/debug/uazapi para ver detalhes da conexão"
    }

app.include_router(main_router)

# Import and include webhooks router
from app.api.webhooks import router as webhooks_router
app.include_router(webhooks_router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Bem-Querer Hub API", "version": "1.0.0"}
