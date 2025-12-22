"""
Chat API Endpoint
Connects Frontend Chat Window with GPT Service.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gpt_service import gpt_service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    history: list = [] # Simplificado para demo

@router.post("/message")
async def send_message(req: ChatRequest):
    """
    Receives user message and returns AI response.
    """
    try:
        response = await gpt_service.generate_response(
            message=req.message,
            history=req.history
        )
        return {"response": response}
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
