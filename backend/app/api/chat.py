from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import SupabaseClient
from app.services.uazapi_service import get_uazapi_service
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# --- Models ---
class SendMessageRequest(BaseModel):
    conversation_id: str
    message: str

class ChatMessage(BaseModel):
    id: str
    content: str
    is_from_me: bool
    created_at: str
    message_type: Optional[str] = None

class Conversation(BaseModel):
    id: str
    name: str  # Changed from contact_name to match frontend
    phoneNumber: Optional[str] = None # Added for frontend display
    lastMessage: Optional[str] = None  # Changed from last_message
    lastMessageTime: Optional[str] = None  # Changed from last_message_at
    unreadCount: int = 0  # Changed from unread_count
    tags: List[str] = []  # Added for frontend
    avatar: Optional[str] = None  # Added for frontend

# --- Endpoints ---

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations():
    """
    List all WhatsApp conversations, ordered by most recent
    """
    try:
        supabase = SupabaseClient.get_admin_client()
        
        response = supabase.table("whatsapp_conversations") \
            .select("*") \
            .order("last_message_at", desc=True) \
            .limit(50) \
            .execute()
        
        if not response.data:
            return []
        
        return [
            Conversation(
                id=conv["id"],
                name=conv.get("contact_name") or conv.get("phone_number", "Desconhecido"),
                phoneNumber=conv.get("phone_number"),
                lastMessage=conv.get("last_message") or "",
                lastMessageTime=conv.get("last_message_at") or "",
                unreadCount=conv.get("unread_count", 0),
                tags=[],
                avatar=f"https://ui-avatars.com/api/?name={conv.get('contact_name', 'U')}&background=random"
            )
            for conv in response.data
        ]
        
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{conversation_id}", response_model=List[ChatMessage])
async def get_messages(conversation_id: str):
    """
    Get all messages for a specific conversation
    """
    try:
        supabase = SupabaseClient.get_admin_client()
        
        response = supabase.table("whatsapp_messages") \
            .select("*") \
            .eq("conversation_id", conversation_id) \
            .order("created_at", desc=False) \
            .limit(100) \
            .execute()
        
        if not response.data:
            return []
        
        return [
            ChatMessage(
                id=msg["message_id"],
                content=msg.get("content", ""),
                is_from_me=msg.get("is_from_me", False),
                created_at=msg.get("created_at", ""),
                message_type=msg.get("message_type")
            )
            for msg in response.data
            # Filter out debug logs
            if msg.get("message_type") != "debug_log"
        ]
        
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_message(request: SendMessageRequest):
    """
    Send a WhatsApp message to a conversation
    """
    try:
        supabase = SupabaseClient.get_admin_client()
        
        # 1. Get conversation details
        conv_response = supabase.table("whatsapp_conversations") \
            .select("*") \
            .eq("id", request.conversation_id) \
            .single() \
            .execute()
        
        if not conv_response.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation = conv_response.data
        phone_number = conversation.get("phone_number")
        
        if not phone_number:
            raise HTTPException(status_code=400, detail="Phone number not found in conversation")
        
        # 2. Send message via UazAPI
        uazapi = get_uazapi_service()
        
        try:
            await uazapi.send_message(
                instance="main",  # Not used in v2.0
                phone=phone_number,
                message=request.message
            )
        except Exception as send_error:
            logger.error(f"Failed to send message via UazAPI: {send_error}")
            raise HTTPException(status_code=500, detail=f"Falha ao enviar mensagem: {str(send_error)}")
        
        # 3. Save message to database
        message_id = str(uuid.uuid4())
        clinic_id = conversation.get("clinic_id", "00000000-0000-0000-0000-000000000001")
        
        message_data = {
            "message_id": message_id,
            "conversation_id": request.conversation_id,
            "clinic_id": clinic_id,
            "from_number": "system",  # Sent by system
            "to_number": phone_number,
            "content": request.message,
            "is_from_me": True,  # Sent by us
            "message_type": "text",
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("whatsapp_messages").insert(message_data).execute()
        
        # 4. Update conversation last_message
        supabase.table("whatsapp_conversations") \
            .update({
                "last_message": request.message,
                "last_message_at": datetime.now().isoformat()
            }) \
            .eq("id", request.conversation_id) \
            .execute()
        
        return {
            "success": True,
            "message_id": message_id,
            "message": "Mensagem enviada com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read/{conversation_id}")
async def mark_as_read(conversation_id: str):
    """
    Mark a conversation as read (reset unread_count to 0)
    """
    try:
        supabase = SupabaseClient.get_admin_client()
        
        supabase.table("whatsapp_conversations") \
            .update({"unread_count": 0}) \
            .eq("id", conversation_id) \
            .execute()
            
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Error marking as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))
