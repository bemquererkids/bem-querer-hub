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

# WhatsApp Status - Implementação direta
@main_router.get("/integrations/whatsapp/status")
async def whatsapp_status():
    try:
        base_url = os.getenv("UAZAPI_BASE_URL")
        token = os.getenv("UAZAPI_TOKEN")
        instance = os.getenv("UAZAPI_INSTANCE", "bemquerer")
        
        if not base_url or not token:
            return {
                "connected": False,
                "error": "Variáveis não configuradas",
                "base_url": base_url,
                "token_set": bool(token)
            }
        
        # Testar diferentes formatos de autenticação
        auth_formats = [
            {"apikey": token},  # Formato 1
            {"Authorization": f"Bearer {token}"},  # Formato 2
            {"x-api-key": token},  # Formato 3
        ]
        
        for idx, auth_header in enumerate(auth_formats):
            try:
                url = f"{base_url}/instance/status"
                headers = {**auth_header, "Content-Type": "application/json"}
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Verificar se está conectado
                        is_connected = False
                        if isinstance(data, dict):
                            is_connected = (
                                data.get("state") == "open" or 
                                data.get("status") == "connected" or
                                data.get("connected") == True
                            )
                        
                        return {
                            "connected": is_connected,
                            "status": data,
                            "auth_format_used": idx + 1,
                            "config": {
                                "base_url": base_url,
                                "instance": instance
                            }
                        }
            except:
                continue
        
        # Se nenhum formato funcionou
        return {
            "connected": False,
            "error": "Nenhum formato de autenticação funcionou",
            "tried_formats": len(auth_formats)
        }
        
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

# WhatsApp Connect - Implementação direta
@main_router.post("/integrations/whatsapp/connect")
async def whatsapp_connect():
    try:
        base_url = os.getenv("UAZAPI_BASE_URL")
        token = os.getenv("UAZAPI_TOKEN")
        instance = os.getenv("UAZAPI_INSTANCE", "bemquerer")
        
        if not base_url or not token:
            raise HTTPException(status_code=500, detail="Variáveis não configuradas")
        
        # Chamar UazAPI para gerar QR - endpoint correto
        url = f"{base_url}/instance/qrcode"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=headers)
            data = response.json()
            
            # Extrair QR Code
            qrcode = (
                data.get("qrcode") or 
                data.get("base64") or
                data.get("code") or
                data.get("pairingCode")
            )
            
            if not qrcode:
                raise HTTPException(
                    status_code=500, 
                    detail=f"QR Code não retornado. Resposta: {data}"
                )
            
            return {
                "success": True,
                "qrcode": qrcode,
                "instance": instance
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

app.include_router(main_router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Bem-Querer Hub API", "version": "1.0.0"}
