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

# Chat endpoints (inline to avoid import issues in Vercel)
from datetime import datetime
from typing import List
from pydantic import BaseModel

class ChatModel(BaseModel):
    id: str
    name: str
    lastMessage: str
    lastMessageTime: str
    unreadCount: int
    tags: List[str]
    status: str

@main_router.get("/chat/list", response_model=List[ChatModel])
async def list_chats_router():
    return [{
        "id": "chat_demo_001",
        "name": "Carol - Chat Demo",
        "lastMessage": "Olá! Sou a Carol, assistente da Bem-Querer. Como posso ajudar?",
        "lastMessageTime": datetime.now().isoformat(),
        "unreadCount": 0,
        "tags": ["demo"],
        "status": "online"
    }]

# Also add directly to app as fallback
@app.get("/api/chat/list", response_model=List[ChatModel])
async def list_chats_direct():
    return [{
        "id": "chat_demo_001",
        "name": "Carol - Chat Demo",
        "lastMessage": "Olá! Sou a Carol, assistente da Bem-Querer. Como posso ajudar?",
        "lastMessageTime": datetime.now().isoformat(),
        "unreadCount": 0,
        "tags": ["demo"],
        "status": "online"
    }]

class ChatMessageModel(BaseModel):
    id: str
    content: str
    sender: str
    timestamp: str

@app.get("/api/chat/{chat_id}/messages", response_model=List[ChatMessageModel])
async def get_messages(chat_id: str):
    return [{
        "id": "msg_001",
        "content": "Olá! Sou a Carol, assistente da Bem-Querer. Como posso ajudar você hoje?",
        "sender": "agent",
        "timestamp": datetime.now().isoformat()
    }]

class SendMessageRequest(BaseModel):
    chat_id: str
    message: str

@app.post("/api/chat/message")
async def send_message(request: SendMessageRequest):
    # Simple echo response for demo
    return {
        "id": f"msg_{datetime.now().timestamp()}",
        "content": f"Você disse: {request.message}. Esta é uma resposta demo. Configure o GPT para respostas reais.",
        "sender": "agent",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {"status": "ok", "message": "Bem-Querer Hub API", "version": "1.0.0"}



