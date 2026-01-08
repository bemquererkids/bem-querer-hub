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

class SendMediaRequest(BaseModel):
    conversation_id: str
    media_url: str
    media_type: str  # image, audio, document
    caption: Optional[str] = None
    filename: Optional[str] = None

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
            .not_.ilike("contact_name", "Paciente Teste%") \
            .not_.ilike("contact_name", "Paciente Seed%") \
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
                tags=conv.get("tags") or [],
                avatar=conv.get("avatar") or f"https://ui-avatars.com/api/?name={conv.get('contact_name', 'U')}&background=random"
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
        
        # Deduplicate messages by message_id (in case of duplicates in DB)
        seen_ids = set()
        unique_messages = []
        
        for msg in response.data:
            # Skip debug logs
            if msg.get("message_type") == "debug_log":
                continue
                
            msg_id = msg["message_id"]
            if msg_id not in seen_ids:
                seen_ids.add(msg_id)
                unique_messages.append(ChatMessage(
                    id=msg_id,
                    content=msg.get("content", ""),
                    is_from_me=msg.get("is_from_me", False),
                    created_at=msg.get("created_at", ""),
                    message_type=msg.get("message_type")
                ))
        
        return unique_messages
        
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
        
        # 2. Send message via UazAPI (non-blocking - log error but continue)
        real_wa_id = None
        try:
            uazapi = get_uazapi_service()
            logger.info(f"Sending message to {phone_number} via UazAPI")
            # UazAPIService.send_message is synchronous in the current implementation
            res = uazapi.send_message(
                to=phone_number,
                text=request.message
            )
            logger.info(f"Message sent successfully to {phone_number}")
            
            # Try to extract real ID
            if res and isinstance(res, dict):
                 if 'key' in res and 'id' in res['key']:
                     real_wa_id = res['key']['id']
                 elif 'id' in res:
                     real_wa_id = res.get('id')
                 elif 'messageId' in res:
                     real_wa_id = res.get('messageId')
                     
        except Exception as send_error:
            # Log error but don't fail - message will still be saved to DB
            logger.warning(f"Failed to send message via UazAPI (continuing anyway): {send_error}")
        
        # 3. Save message to database
        # Use Real ID if available, otherwise UUID
        message_id = real_wa_id if real_wa_id else str(uuid.uuid4())
        
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
        
        logger.info(f"Saving message to database: {message_id}")
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


@router.post("/send-media")
async def send_media(request: SendMediaRequest):
    """
    Send a media message (image, audio, document)
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
        
        # 2. Send via UazAPI
        uazapi = get_uazapi_service()
        instance = "main"
        
        try:
            if request.media_type == 'image':
                await uazapi.send_image(instance, phone_number, request.media_url, request.caption)
            elif request.media_type == 'audio':
                await uazapi.send_audio(instance, phone_number, request.media_url)
            elif request.media_type == 'document':
                await uazapi.send_document(instance, phone_number, request.media_url, request.filename, request.caption)
            else:
                 raise HTTPException(status_code=400, detail="Invalid media type")
        except Exception as send_error:
            logger.error(f"Failed to send media via UazAPI: {send_error}")
            raise HTTPException(status_code=500, detail=f"Falha ao enviar mídia: {str(send_error)}")
        
        # 3. Save message to database
        message_id = str(uuid.uuid4())
        clinic_id = conversation.get("clinic_id", "00000000-0000-0000-0000-000000000001")
        
        content_preview = {
            'image': '📷 Imagem',
            'audio': '🎵 Áudio',
            'document': '📄 Documento'
        }.get(request.media_type, 'Anexo')

        if request.caption:
            content_preview += f": {request.caption}"
        
        message_data = {
            "message_id": message_id,
            "conversation_id": request.conversation_id,
            "clinic_id": clinic_id,
            "from_number": "system",
            "to_number": phone_number,
            "content": request.media_url,
            "is_from_me": True,
            "message_type": request.media_type,
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("whatsapp_messages").insert(message_data).execute()
        
        # 4. Update conversation last_message
        supabase.table("whatsapp_conversations") \
            .update({
                "last_message": content_preview,
                "last_message_at": datetime.now().isoformat()
            }) \
            .eq("id", request.conversation_id) \
            .execute()
        
        return {
            "success": True,
            "message_id": message_id,
            "message": "Mídia enviada com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Error sending media: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/messages/{message_id}")
async def delete_message(message_id: str):
    """
    Delete a message (Revoke for everyone if sent by us, or just delete from DB)
    """
    try:
        supabase = SupabaseClient.get_admin_client()
        
        # 1. Get message details to verify ownership and get phone number
        msg_res = supabase.table("whatsapp_messages") \
            .select("*, whatsapp_conversations(phone_number)") \
            .eq("message_id", message_id) \
            .single() \
            .execute()
            
        if not msg_res.data:
            # Try finding by 'id' if 'message_id' failed (legacy support)
            msg_res = supabase.table("whatsapp_messages") \
                .select("*, whatsapp_conversations(phone_number)") \
                .eq("id", message_id) \
                .single() \
                .execute()
                
        if not msg_res.data:
            raise HTTPException(status_code=404, detail="Message not found")
            
        message = msg_res.data
        is_from_me = message.get("is_from_me")
        # Extract phone safely
        phone = None
        if message.get("whatsapp_conversations"):
             phone = message.get("whatsapp_conversations", {}).get("phone_number")
        if not phone:
             phone = message.get("to_number") if is_from_me else message.get("from_number")
        
        # 2. If message is from us, try to revoke on WhatsApp
        # We assume the ID stored in DB is the correct ID to revoke
        if is_from_me and phone:
            try:
                uaz = get_uazapi_service()
                logger.info(f"Attempting to revoke message {message_id} on WhatsApp...")
                uaz.delete_message(phone, message_id)
            except Exception as e:
                logger.warning(f"Failed to revoke on WhatsApp: {e}")

        # 3. Delete from Database
        supabase.table("whatsapp_messages").delete().eq("message_id", message_id).execute()
        
        return {"success": True}

    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation (Locally and on WhatsApp potentially)
    """
    try:
        supabase = SupabaseClient.get_admin_client()
        
        # 1. Get conversation to find phone number
        conv_res = supabase.table("whatsapp_conversations") \
            .select("*") \
            .eq("id", conversation_id) \
            .single() \
            .execute()
        
        if not conv_res.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        phone = conv_res.data.get("phone_number")
        
        # 2. Try to delete on WhatsApp (Clears chat history on device)
        if phone:
            try:
                uaz = get_uazapi_service()
                # delete_chat needs to be implemented in UazAPIService or use direct request
                uaz.delete_chat(phone) 
            except Exception as e:
                logger.warning(f"Failed to delete chat on WhatsApp (continuing locally): {e}")

        # 3. Delete from Database
        # Manually delete messages first to be safe
        supabase.table("whatsapp_messages").delete().eq("conversation_id", conversation_id).execute()
        supabase.table("whatsapp_conversations").delete().eq("id", conversation_id).execute()
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
