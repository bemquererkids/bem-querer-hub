"""
Bem-Querer Hub - VERSÃO MÍNIMA PARA DEBUG
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Bem-Querer Hub API - DEBUG")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "API funcionando!"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "minimal"}

@app.get("/api/debug/env")
async def debug_env():
    import os
    return {
        "UAZAPI_BASE_URL": os.getenv("UAZAPI_BASE_URL", "NOT_SET"),
        "UAZAPI_TOKEN_SET": bool(os.getenv("UAZAPI_TOKEN")),
        "UAZAPI_INSTANCE": os.getenv("UAZAPI_INSTANCE", "NOT_SET"),
    }
