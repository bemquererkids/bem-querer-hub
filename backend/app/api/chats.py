from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_supabase

router = APIRouter(prefix="/api/chat", tags=["chats"])

# Configuration
CLINIC_ID_DEFAULT = "00000000-0000-0000-0000-000000000001"

# --- Models ---

class ChatModel(BaseModel):
    id: str  # Conversation ID (UUID)
    name: str # Contact Name
    lastMessage: str
    lastMessageTime: str
    unreadCount: int
    tags: List[str]
    status: str
    phone: str # Helper

class ChatMessageModel(BaseModel):
    id: str
    content: str
    sender: str # "user" (customer) or "agent" (me/system)
    timestamp: str
    status: str # sent, delivered, read

class SendMessageRequest(BaseModel):
    chat_id: str
    message: str

# --- Endpoints ---

@router.get("/list", response_model=List[ChatModel])
async def list_chats():
    """
    List conversations from whatsapp_conversations table
    """
    try:
        supabase = get_supabase()
        
        # Fetch conversations for this clinic
        res = supabase.table("whatsapp_conversations") \
            .select("*") \
            .eq("clinic_id", CLINIC_ID_DEFAULT) \
            .order("last_message_at", desc=True) \
            .execute()
            
        chats = []
        if res.data:
            for c in res.data:
                chats.append({
                    "id": c["id"],
                    "name": c.get("contact_name") or c.get("phone_number"),
                    "lastMessage": c.get("last_message") or "",
                    "lastMessageTime": c.get("last_message_at") or datetime.now().isoformat(),
                    "unreadCount": c.get("unread_count", 0),
                    "tags": c.get("tags") or [],
                    "status": "online",  # We could infer this from elsewhere
                    "phone": c.get("phone_number")
                })
        
        return chats
    except Exception as e:
        print(f"Error fetching chats: {e}")
        return []

@router.get("/{chat_id}/messages", response_model=List[ChatMessageModel])
async def get_messages(chat_id: str):
    """
    Get messages for a specific conversation
    """
    try:
        supabase = get_supabase()
        
        res = supabase.table("whatsapp_messages") \
            .select("*") \
            .eq("conversation_id", chat_id) \
            .order("timestamp", desc=False) \
            .execute()
            
        messages = []
        if res.data:
            for m in res.data:
                messages.append({
                    "id": m["id"], # UUID
                    "content": m.get("content") or "",
                    "sender": "agent" if m.get("is_from_me") else "user",
                    "timestamp": m.get("timestamp"),
                    "status": m.get("status") or "sent"
                })
                
        return messages
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

@router.post("/message")
async def send_message(request: SendMessageRequest):
    """
    Send a message via the active integration (UAZAPI or META)
    """
    try:
        supabase = get_supabase()
        
        # 1. Get Chat details to find the phone number
        chat_res = supabase.table("whatsapp_conversations") \
            .select("*") \
            .eq("id", request.chat_id) \
            .execute()
            
        if not chat_res.data:
            raise HTTPException(status_code=404, detail="Chat not found")
            
        chat = chat_res.data[0]
        phone = chat["phone_number"]
        clinic_id = chat["clinic_id"]
        
        # 2. Determine which Service to use (check integration config)
        # We check UAZAPI first by looking for instance_name
        # Or we can check which columns are populated in clinic_integrations
        
        int_res = supabase.table("clinic_integrations") \
            .select("*") \
            .eq("clinica_id", clinic_id) \
            .eq("type", "whatsapp") \
            .execute()
            
        config = int_res.data[0] if int_res.data else {}
        
        message_response = {}
        
        if config.get("instance_name"):
            # Use UAZAPI
            from app.services.uazapi_service import UazAPIService
            uaz_service = UazAPIService(
                instance_name=config["instance_name"],
                token=config["token"]
            )
            message_response = uaz_service.send_message(to=phone, text=request.message)
            
        elif config.get("phone_number_id"):
            # Use Meta (Legacy/Alternative)
            from app.services.meta_service import get_meta_service_for_clinic
            meta_service = await get_meta_service_for_clinic(clinic_id)
            message_response = await meta_service.send_message(to=phone, text=request.message)
            
        else:
             raise HTTPException(status_code=400, detail="No WhatsApp integration configured")
             
        # 3. Save to History (Optimistic or wait for webhook?)
        # Better to save it now so UI updates immediately, even if webhook comes later (dedup logic required later)
        # For now, simplistic insert
        
        new_msg = {
            "clinic_id": clinic_id,
            "conversation_id": request.chat_id,
            "message_id": str(datetime.now().timestamp()), # Temporary ID, webhook should update with real ID if possible
            "from_number": "system",
            "to_number": phone,
            "content": request.message,
            "timestamp": datetime.now().isoformat(),
            "status": "sent",
            "is_from_me": True
        }
        supabase.table("whatsapp_messages").insert(new_msg).execute()
        
        # Update conversation last message
        supabase.table("whatsapp_conversations").update({
            "last_message": request.message,
            "last_message_at": datetime.now().isoformat()
        }).eq("id", request.chat_id).execute()
        
        return {
            "status": "success",
            "content": request.message,
            "sender": "agent",
            "timestamp": new_msg["timestamp"]
        }

    except Exception as e:
        print(f"Send message failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
