
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

# Services
from app.services.gpt_service import get_gpt_service, GPTService

router = APIRouter(prefix="/api/chat", tags=["chat"])

# --- Models ---
class ChatMessageRequest(BaseModel):
    chat_id: str
    message: str

class ChatMessage(BaseModel):
    id: str
    content: str
    sender: str # "user" | "ai"
    timestamp: str

class Chat(BaseModel):
    id: str
    name: str
    lastMessage: str
    lastMessageTime: str
    unreadCount: int
    tags: List[str]
    status: str

# --- Mock DB for Demo (since Supabase might be empty/hard to seed quickly) ---
# In production, this reads/writes to 'chats' and 'messages' tables.
MOCK_CHATS = [
    {
        "id": "chat_demo_001",
        "name": "Carol - Chat Demo",
        "lastMessage": "Olá! Sou a Carol, assistente da Bem-Querer. Como posso ajudar?",
        "lastMessageTime": datetime.now().isoformat(),
        "unreadCount": 0,
        "tags": ["demo"],
        "status": "online"
    }
]

@router.get("/list", response_model=List[Chat])
async def list_chats():
    return MOCK_CHATS

@router.get("/{chat_id}/messages", response_model=List[ChatMessage])
async def get_messages(chat_id: str):
    # Find chat
    chat = next((c for c in MOCK_CHATS if c["id"] == chat_id), None)
    if not chat:
        return []
    return chat["messages"]

@router.post("/message")
async def send_message(
    req: ChatMessageRequest,
    gpt_service: GPTService = Depends(get_gpt_service)
):
    # 1. Find Chat
    chat = next((c for c in MOCK_CHATS if c["id"] == req.chat_id), None)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # 2. Add User Message
    user_msg = {
        "id": str(uuid.uuid4()),
        "content": req.message,
        "sender": "user",
        "timestamp": datetime.now().isoformat()
    }
    chat["messages"].append(user_msg)
    chat["lastMessage"] = req.message
    chat["timestamp"] = user_msg["timestamp"]
    
    # 3. Call AI (Carol) with Clinicorp Tools
    # Context: User wants to schedule
    ai_response = await gpt_service.process_message(
        message=req.message,
        chat_history=[{"content": m["content"], "sender_type": m["sender"]} for m in chat["messages"][:-1]],
        context={"patient_name": chat["patientName"], "clinic_id": "bemquerer"}
    )
    
    ai_text = ai_response.get("response", "Desculpe, não entendi.")
    
    # 4. Add AI Message
    ai_msg = {
        "id": str(uuid.uuid4()),
        "content": ai_text,
        "sender": "ai",
        "timestamp": datetime.now().isoformat()
    }
    chat["messages"].append(ai_msg)
    chat["lastMessage"] = ai_text
    
    return {
        "user_message": user_msg,
        "ai_message": ai_msg
    }
