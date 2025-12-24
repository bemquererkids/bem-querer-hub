"""
Bem-Querer Hub - FastAPI Backend
Main Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.security import TenantMiddleware
from app.api import webhooks, crm, integration, clinicorp_webhook, chat, knowledge, conversations
from app.routers import whatsapp

app = FastAPI(
    title="Bem-Querer Hub API",
    description="Middleware para centralizar atendimento e vendas em clínicas odontológicas",
    version="1.0.0"
)

# CORS Configuration - MUST BE FIRST
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug Middleware - Catch all and print traceback
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        import traceback
        print("\n" + "="*50)
        print("❌ INTERNAL SERVER ERROR DETECTED")
        traceback.print_exc()
        print("="*50 + "\n")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "traceback": traceback.format_exc()},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )

# Multi-tenant Middleware
app.add_middleware(TenantMiddleware)

# Global API Router with /api prefix
from fastapi import APIRouter
main_router = APIRouter(prefix="/api")

# Include Routers with /api prefix
main_router.include_router(webhooks.router)
main_router.include_router(crm.router)
main_router.include_router(integration.router)
main_router.include_router(clinicorp_webhook.router)
main_router.include_router(chat.router)
main_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
main_router.include_router(knowledge.router)  # Knowledge Base (Documents & Embeddings)
main_router.include_router(conversations.router)  # Conversations with Carol

app.include_router(main_router)



@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Bem-Querer Hub API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "services": {
            "uazapi": "pending",
            "gemini": "pending",
            "clinicorp": "pending"
        }
    }
