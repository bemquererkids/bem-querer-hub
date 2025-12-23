from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.services.gpt_service import gpt_service
from app.core.database import get_supabase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    history: list = [] # Simplificado para demo

@router.get("/list")
async def list_chats():
    """
    Returns list of active chats for the frontend.
    """
    supabase = get_supabase()
    try:
        # Fetch chats with patient info
        # Using a more robust fetch approach
        res = supabase.table('chats').select('*').order('last_message_at', desc=True).execute()
        
        formatted_chats = []
        for chat in res.data:
            # Try to fetch patient name separately or via mock-safe way
            # If the join patients(full_name) failed we fetch separately
            patient_name = chat.get('whatsapp_name', 'Paciente')
            patient_id = chat.get('patient_id')
            
            if patient_id:
                try:
                    p_res = supabase.table('patients').select('full_name').eq('id', patient_id).single().execute()
                    if p_res.data:
                        patient_name = p_res.data['full_name']
                except:
                    pass

            formatted_chats.append({
                "id": str(chat.get('id', '')),
                "name": patient_name,
                "lastMessage": chat.get('last_message', "Ver conversa..."),
                "lastMessageTime": chat.get('last_message_at', datetime.now().isoformat()),
                "unreadCount": chat.get('unread_count', 0),
                "tags": [chat.get('intent', 'question')],
                "status": "online"
            })
            
        return formatted_chats
    except Exception as e:
        logger.error(f"Error listing chats: {str(e)}")
        # Return mock data as a last resort to keep the UI from breaking for the user
        return [
            {
                "id": "mock-1",
                "name": "Paciente de Teste",
                "lastMessage": "Aguardando sincronização...",
                "lastMessageTime": datetime.now().isoformat(),
                "unreadCount": 0,
                "tags": ["sync"],
                "status": "online"
            }
        ]

@router.get("/{chat_id}/messages")
async def get_messages(chat_id: str):
    """
    Returns message history for a specific chat.
    """
    supabase = get_supabase()
    try:
        res = supabase.table('messages').select('*').eq('chat_id', chat_id).order('created_at', desc=False).execute()
        
        formatted_messages = []
        for msg in res.data:
            formatted_messages.append({
                "id": str(msg.get('id', '')),
                "content": msg.get('content', ''),
                "sender": 'user' if msg.get('sender_type') == 'user' else 'agent',
                "timestamp": msg.get('created_at', datetime.now().isoformat()),
                "type": msg.get('message_type', 'text')
            })
            
        return formatted_messages
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        return []

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
