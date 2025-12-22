"""
Message Processing Service
Handles business logic for processing WhatsApp messages
"""
from typing import Dict, Any, Optional
from app.core.database import get_supabase
from app.services.gemini_service import get_gemini_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Process incoming WhatsApp messages and generate responses"""
    
    def __init__(self):
        self.gemini = get_gemini_service()
        self.supabase = get_supabase()
    
    async def process_incoming_message(
        self,
        clinic_id: str,
        whatsapp_number: str,
        message_content: str,
        message_type: str = "text",
        uazapi_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming WhatsApp message
        
        Args:
            clinic_id: Clinic ID (tenant)
            whatsapp_number: Sender's WhatsApp number
            message_content: Message text
            message_type: Type of message (text, audio, image, etc.)
            uazapi_message_id: UazAPI message ID
        
        Returns:
            Dict with response and metadata
        """
        try:
            # 1. Find or create chat
            chat = await self._get_or_create_chat(clinic_id, whatsapp_number)
            
            # 2. Get chat history for context
            chat_history = await self._get_chat_history(chat["id"])
            
            # 3. Store incoming message
            await self._store_message(
                clinic_id=clinic_id,
                chat_id=chat["id"],
                content=message_content,
                message_type=message_type,
                sender_type="user",
                uazapi_message_id=uazapi_message_id
            )
            
            # 4. Process with AI
            ai_response = await self.gemini.process_message(
                message=message_content,
                chat_history=chat_history,
                context={
                    "clinic_id": clinic_id,
                    "chat_status": chat.get("status"),
                    "patient_id": chat.get("patient_id")
                }
            )
            
            # 5. Update chat metadata
            await self._update_chat_metadata(
                chat_id=chat["id"],
                intent=ai_response.get("intent"),
                urgency=ai_response.get("urgency"),
                needs_human=ai_response.get("needs_human", False)
            )
            
            # 6. Store AI response
            await self._store_message(
                clinic_id=clinic_id,
                chat_id=chat["id"],
                content=ai_response["response"],
                message_type="text",
                sender_type="ai",
                ai_confidence=0.85  # TODO: Get from AI response
            )
            
            # 7. Generate embedding for semantic search (async, non-blocking)
            # TODO: Implement background task for embedding generation
            
            return {
                "success": True,
                "response": ai_response["response"],
                "intent": ai_response.get("intent"),
                "urgency": ai_response.get("urgency"),
                "needs_human": ai_response.get("needs_human", False),
                "chat_id": chat["id"]
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro. Por favor, tente novamente."
            }
    
    async def _get_or_create_chat(
        self,
        clinic_id: str,
        whatsapp_number: str
    ) -> Dict[str, Any]:
        """Find existing chat or create new one"""
        try:
            # Try to find existing open chat
            response = self.supabase.table("chats").select("*").eq(
                "clinic_id", clinic_id
            ).eq(
                "whatsapp_number", whatsapp_number
            ).eq(
                "status", "open"
            ).order("created_at", desc=True).limit(1).execute()
            
            if response.data:
                return response.data[0]
            
            # Create new chat
            new_chat = {
                "clinic_id": clinic_id,
                "whatsapp_number": whatsapp_number,
                "status": "open",
                "intent": "question",  # Default
                "urgency": "normal"
            }
            
            response = self.supabase.table("chats").insert(new_chat).execute()
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error getting/creating chat: {str(e)}")
            raise
    
    async def _get_chat_history(
        self,
        chat_id: str,
        limit: int = 10
    ) -> list:
        """Get recent messages from chat"""
        try:
            response = self.supabase.table("messages").select(
                "content, sender_type, created_at"
            ).eq(
                "chat_id", chat_id
            ).order("created_at", desc=True).limit(limit).execute()
            
            # Reverse to get chronological order
            return list(reversed(response.data)) if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    async def _store_message(
        self,
        clinic_id: str,
        chat_id: str,
        content: str,
        message_type: str,
        sender_type: str,
        sender_id: Optional[str] = None,
        uazapi_message_id: Optional[str] = None,
        ai_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """Store message in database"""
        try:
            message_data = {
                "clinic_id": clinic_id,
                "chat_id": chat_id,
                "content": content,
                "message_type": message_type,
                "sender_type": sender_type,
                "sender_id": sender_id,
                "uazapi_message_id": uazapi_message_id,
                "ai_confidence": ai_confidence
            }
            
            response = self.supabase.table("messages").insert(message_data).execute()
            
            # Update chat's last_message_at
            self.supabase.table("chats").update({
                "last_message_at": datetime.utcnow().isoformat()
            }).eq("id", chat_id).execute()
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error storing message: {str(e)}")
            raise
    
    async def _update_chat_metadata(
        self,
        chat_id: str,
        intent: Optional[str] = None,
        urgency: Optional[str] = None,
        needs_human: bool = False
    ) -> None:
        """Update chat metadata based on AI analysis"""
        try:
            update_data = {}
            
            if intent:
                update_data["intent"] = intent
            
            if urgency:
                update_data["urgency"] = urgency
            
            if needs_human:
                update_data["status"] = "waiting_human"
            
            if update_data:
                self.supabase.table("chats").update(update_data).eq(
                    "id", chat_id
                ).execute()
                
        except Exception as e:
            logger.error(f"Error updating chat metadata: {str(e)}")


# Singleton instance
_message_processor: Optional[MessageProcessor] = None


def get_message_processor() -> MessageProcessor:
    """Get or create message processor instance"""
    global _message_processor
    if _message_processor is None:
        _message_processor = MessageProcessor()
    return _message_processor
