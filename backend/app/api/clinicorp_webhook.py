
"""
Clinicorp Webhook Handler
Receives real-time events from Clinicorp (Appointments, Patient Updates, etc.)
"""
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import json

router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.post("/clinicorp")
async def clinicorp_webhook(request: Request):
    """
    Receives events from Clinicorp.
    Expected Payload: JSON with entity type and data.
    """
    try:
        payload = await request.json()
        
        # Log for debugging (Show what Clinicorp sent us)
        print("\n--- [WEBHOOK] Evento Recebido do Clinicorp ---")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("----------------------------------------------\n")
        
        # TODO: Process the event
        # 1. Identify event type (appointment.created, status.changed, etc.)
        # 2. Update local database (appointments table)
        # 3. Notify Frontend (WebSocket)
        
        return {"status": "received", "message": "Webhook processed successfully"}
        
    except Exception as e:
        print(f"[WEBHOOK ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

