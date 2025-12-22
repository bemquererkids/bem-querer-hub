"""
Bem-Querer Hub - FastAPI Backend
Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.security import TenantMiddleware
from app.api import webhooks, crm, integration, clinicorp_webhook, chat

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

# Multi-tenant Middleware
app.add_middleware(TenantMiddleware)

# Include Routers
app.include_router(webhooks.router)
app.include_router(crm.router)
app.include_router(integration.router)
app.include_router(clinicorp_webhook.router)
app.include_router(chat.router)



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
