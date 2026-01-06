from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Response
from fastapi.responses import PlainTextResponse
from app.core.database import get_supabase
from app.services.source_detector import LeadSourceDetector
from pydantic import BaseModel
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


# =====================================================
# META CLOUD API WEBHOOK
# =====================================================

@router.get("/whatsapp")
async def verify_meta_webhook(request: Request):
    """
    Meta WhatsApp Cloud API - Webhook Verification (GET)
    
    Meta sends a GET request to verify the webhook URL.
    We must validate the verify_token and return the challenge.
    
    Query Parameters:
        hub.mode: Should be "subscribe"
        hub.verify_token: Token configured in Meta Developer Console
        hub.challenge: Random string to echo back
    
    Documentation: https://developers.facebook.com/docs/graph-api/webhooks/getting-started
    """
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logger.info(f"📞 Meta webhook verification request: mode={mode}, token={token[:10] if token else 'None'}...")
        
        if not mode or not token or not challenge:
            logger.warning(f"❌ Missing verification parameters: mode={mode}, token={bool(token)}, challenge={bool(challenge)}")
            raise HTTPException(status_code=400, detail="Missing parameters")
        
        if mode != "subscribe":
            logger.warning(f"❌ Invalid mode: {mode}")
            raise HTTPException(status_code=403, detail="Invalid mode")
        
        # Validate token against database
        try:
            supabase = get_supabase()
            logger.info(f"🔍 Querying database for verify_token: {token}")
            
            # Get ALL whatsapp records and filter in Python to avoid query issues
            result = supabase.table('clinic_integrations') \
                .select('*') \
                .eq('type', 'whatsapp') \
                .execute()
            
            logger.info(f"📊 Database query result: {len(result.data) if result.data else 0} total whatsapp records")
            
            if result.data:
                for record in result.data:
                    logger.info(f"   Record: verify_token={record.get('verify_token')}, is_active={record.get('is_active')}, match={record.get('verify_token') == token}")
            
            # Filter by token AND active status in Python
            matching_records = [
                r for r in (result.data or []) 
                if r.get('verify_token') == token and r.get('is_active') == True
            ]
            
            logger.info(f"🎯 Matching records after filter: {len(matching_records)}")
            
            if not matching_records:
                logger.warning(f"❌ No active matching verify_token found. Received: {token}")
                raise HTTPException(status_code=403, detail="Verification token mismatch")
            
            clinic_id = matching_records[0]['clinica_id']
            logger.info(f"✅ Webhook verified for clinic: {clinic_id}")
            
            # Return challenge as plain text (Meta requirement)
            return PlainTextResponse(content=challenge, status_code=200)
            
        except HTTPException:
            raise
        except Exception as db_error:
            logger.error(f"❌ Database error: {db_error}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Webhook verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp")
async def receive_meta_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Meta WhatsApp Cloud API - Message Reception (POST)
    
    Receives incoming messages, status updates, and other events from Meta.
    
    Payload Structure:
    {
      "object": "whatsapp_business_account",
      "entry": [{
        "id": "WABA_ID",
        "changes": [{
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "5511999999999",
              "phone_number_id": "123456789"
            },
            "contacts": [{"profile": {"name": "John"}, "wa_id": "5511888888888"}],
            "messages": [{
              "from": "5511888888888",
              "id": "wamid.XXX",
              "timestamp": "1234567890",
              "type": "text",
              "text": {"body": "Hello"}
            }],
            "statuses": [...]  // Delivery/read receipts
          },
          "field": "messages"
        }]
      }]
    }
    """
    try:
        payload = await request.json()
        logger.info(f"📨 Meta webhook received: {payload.get('object')}")
        
        # Validate webhook object type
        if payload.get("object") != "whatsapp_business_account":
            logger.warning(f"⚠️ Unexpected object type: {payload.get('object')}")
            return {"status": "ignored", "reason": "not_whatsapp_business_account"}
        
        # Process each entry
        entries = payload.get("entry", [])
        for entry in entries:
            waba_id = entry.get("id")
            changes = entry.get("changes", [])
            
            for change in changes:
                field = change.get("field")
                value = change.get("value", {})
                
                # Only process message events
                if field != "messages":
                    logger.info(f"⚠️ Skipping non-message field: {field}")
                    continue
                
                # Extract metadata
                metadata = value.get("metadata", {})
                phone_number_id = metadata.get("phone_number_id")
                
                # Get clinic_id from phone_number_id
                clinic_id = await get_clinic_id_from_phone_number(phone_number_id)
                if not clinic_id:
                    logger.warning(f"❌ Unknown phone_number_id: {phone_number_id}")
                    continue
                
                # Process messages
                messages = value.get("messages", [])
                for message in messages:
                    logger.info(f"📩 Processing message: {message.get('id')}")
                    background_tasks.add_task(
                        process_meta_message,
                        message=message,
                        clinic_id=clinic_id,
                        phone_number_id=phone_number_id
                    )
                
                # Process statuses (optional - for delivery/read receipts)
                statuses = value.get("statuses", [])
                for status in statuses:
                    logger.info(f"📊 Status update: {status.get('id')} -> {status.get('status')}")
                    # TODO: Update message status in database if needed
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}", exc_info=True)
        # Return 200 even on error to prevent Meta from retrying
        return {"status": "error", "message": str(e)}

# =====================================================
# UAZAPI WEBHOOK
# =====================================================

@router.post("/uazapi")
async def receive_uazapi_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    UazAPI Webhook - Receives messages from UazAPI
    Format: {'EventType': 'messages', 'message': {...}, 'chat': {...}}
    """
    try:
        payload = await request.json()
        logger.info(f"📨 UazAPI Webhook received: EventType={payload.get('EventType')}")
        
        # Only process message events
        if payload.get('EventType') != 'messages':
            logger.info(f"Ignoring non-message event: {payload.get('EventType')}")
            return {"status": "ignored"}
        
        message_data = payload.get('message', {})
        chat_data = payload.get('chat', {})
        
        # Check if message is from me
        if message_data.get('fromMe', False):
            logger.info("Ignoring message from me")
            return {"status": "ignored"}
        
        # Extract message details
        text_content = message_data.get('text') or message_data.get('content', '')
        sender = message_data.get('sender', '')  # 5511993308484@s.whatsapp.net
        phone = sender.split('@')[0] if '@' in sender else sender
        name = chat_data.get('name') or message_data.get('senderName', 'Desconhecido')
        
        # Get REAL message ID from UazAPI to prevent ghosting/duplicates
        # It's usually in key.id or just id
        uaz_id = message_data.get('id') or (message_data.get('key', {}).get('id'))
        if not uaz_id:
            # Fallback to a hash of content/timestamp if ID is somehow missing
            uaz_id = f"uazapi_{datetime.now().timestamp()}"
        
        logger.info(f"🆔 UazAPI Message ID: {uaz_id}")

        if not text_content or not phone:
            logger.warning(f"Missing text or phone: text={text_content}, phone={phone}")
            return {"status": "error", "message": "Missing required fields"}
        
        # Hardcoded clinic for now
        CLINIC_ID_DEFAULT = "00000000-0000-0000-0000-000000000001"
        
        logger.info(f"✅ Processing message from {name} ({phone}): {text_content[:50]}")
        logger.info(f"📦 Sending to background task with message_id: {uaz_id}")
        
        # Save and Process in background
        background_tasks.add_task(
            process_uazapi_message,
            clinic_id=CLINIC_ID_DEFAULT,
            phone=phone,
            name=name,
            message=text_content,
            message_id=uaz_id
        )
        
        return {"status": "success"}

    except Exception as e:
        logger.error(f"UazAPI Webhook Error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

async def process_uazapi_message(clinic_id: str, phone: str, name: str, message: str, message_id: str):
    try:
        logger.info(f"🔄 [process_uazapi_message] Starting for message_id: {message_id}")
        
        # Save to WhatsApp tables
        logger.info(f"💾 [process_uazapi_message] Calling save_whatsapp_message...")
        await save_whatsapp_message(
            clinic_id=clinic_id,
            phone=phone,
            contact_name=name,
            message_id=message_id,
            content=message,
            message_type="text",
            is_from_me=False
        )
        logger.info(f"✅ [process_uazapi_message] Message saved successfully")
        
        # Trigger AI
        await process_new_lead(
            phone=phone,
            name=name,
            message=message,
            clinic_id=clinic_id,
            phone_number_id="uazapi" # Flag for source
        )
    except Exception as e:
        logger.error(f"Error processing UazAPI message: {e}")



async def get_clinic_id_from_phone_number(phone_number_id: str) -> str:
    """
    Maps Meta phone_number_id to clinic_id
    
    Args:
        phone_number_id: Meta WhatsApp Business Phone Number ID
    
    Returns:
        clinic_id or None if not found
    """
    try:
        supabase = get_supabase()
        result = supabase.table('clinic_integrations') \
            .select('clinica_id') \
            .eq('phone_number_id', phone_number_id) \
            .eq('type', 'whatsapp') \
            .eq('is_active', True) \
            .execute()
        
        if result.data and len(result.data) > 0:
            clinic_id = result.data[0]['clinica_id']
            logger.info(f"✅ Mapped phone_number_id {phone_number_id} to clinic {clinic_id}")
            return clinic_id
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error mapping phone_number_id: {e}")
        return None


async def process_meta_message(message: dict, clinic_id: str, phone_number_id: str):
    """
    Process a single message from Meta webhook
    
    Args:
        message: Message object from Meta webhook
        clinic_id: Clinic UUID
        phone_number_id: Meta phone number ID
    """
    try:
        # Extract message details
        from_number = message.get("from")  # Sender's WhatsApp number
        message_id = message.get("id")  # WhatsApp message ID (wamid.XXX)
        timestamp = message.get("timestamp")  # Unix timestamp
        message_type = message.get("type")  # text, image, video, document, audio, etc.
        
        logger.info(f"📝 Processing {message_type} message from {from_number}")
        
        # Extract contact name (if available)
        contact_name = "Desconhecido"
        # Note: Contact info is in the parent 'value' object, not in individual message
        # We'll need to pass it from the webhook handler or fetch from database
        
        # Extract message content based on type
        text_content = ""
        media_url = None
        
        if message_type == "text":
            text_content = message.get("text", {}).get("body", "")
        
        elif message_type == "image":
            image_data = message.get("image", {})
            media_url = image_data.get("id")  # Media ID to download later
            text_content = image_data.get("caption", "[Imagem]")
        
        elif message_type == "video":
            video_data = message.get("video", {})
            media_url = video_data.get("id")
            text_content = video_data.get("caption", "[Vídeo]")
        
        elif message_type == "document":
            doc_data = message.get("document", {})
            media_url = doc_data.get("id")
            text_content = f"[Documento: {doc_data.get('filename', 'arquivo')}]"
        
        elif message_type == "audio":
            audio_data = message.get("audio", {})
            media_url = audio_data.get("id")
            text_content = "[Áudio]"
        
        elif message_type == "button":
            # Button reply
            button_data = message.get("button", {})
            text_content = button_data.get("text", "")
        
        elif message_type == "interactive":
            # Interactive message reply (list, button)
            interactive_data = message.get("interactive", {})
            if interactive_data.get("type") == "button_reply":
                text_content = interactive_data.get("button_reply", {}).get("title", "")
            elif interactive_data.get("type") == "list_reply":
                text_content = interactive_data.get("list_reply", {}).get("title", "")
        
        else:
            logger.warning(f"⚠️ Unsupported message type: {message_type}")
            text_content = f"[Mensagem não suportada: {message_type}]"
        
        if not text_content:
            logger.info("⚠️ Empty message content, skipping")
            return
        
        # Save to WhatsApp tables
        await save_whatsapp_message(
            clinic_id=clinic_id,
            phone=from_number,
            contact_name=contact_name,
            message_id=message_id,
            content=text_content,
            message_type=message_type,
            media_url=media_url,
            timestamp=datetime.fromtimestamp(int(timestamp)).isoformat() if timestamp else None,
            is_from_me=False
        )
        
        # Process as lead (trigger AI Carol)
        await process_new_lead(
            phone=from_number,
            name=contact_name,
            message=text_content,
            clinic_id=clinic_id,
            phone_number_id=phone_number_id
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing Meta message: {e}", exc_info=True)


async def save_whatsapp_message(
    clinic_id: str,
    phone: str,
    contact_name: str,
    message_id: str,
    content: str,
    message_type: str = "text",
    media_url: str = None,
    timestamp: str = None,
    is_from_me: bool = False
):
    """
    Saves WhatsApp message to database for chat integration.
    Creates or updates conversation and adds message.
    Multi-tenant: isolated by clinic_id.
    """
    logger.info(f"💾 Saving WhatsApp message: {content[:50]}...")
    
    try:
        supabase = get_supabase()
        
        # 0. Check for existing message_id to prevent duplicates
        existing_msg = supabase.table('whatsapp_messages') \
            .select('id') \
            .eq('message_id', message_id) \
            .execute()
            
        if existing_msg.data:
            logger.info(f"⏭️ Message {message_id} already exists, skipping save.")
            return

        # 1. Get or create conversation
        conversation_res = supabase.table('whatsapp_conversations') \
            .select('*') \
            .eq('phone_number', phone) \
            .eq('clinic_id', clinic_id) \
            .execute()
        if not conversation_res.data:
            # Create new conversation
            new_conversation = {
                "clinic_id": clinic_id,
                "phone_number": phone,
                "contact_name": contact_name,
                "last_message": content,
                "last_message_at": timestamp or datetime.now().isoformat(),
                "unread_count": 0 if is_from_me else 1,
                "tags": []
            }
            conv_res = supabase.table('whatsapp_conversations').insert(new_conversation).execute()
            conversation_id = conv_res.data[0]['id']
            logger.info(f"✅ New conversation created: {conversation_id}")
        else:
            # Update existing conversation
            conversation_id = conversation_res.data[0]['id']
            current_unread = conversation_res.data[0].get('unread_count', 0)
            
            supabase.table('whatsapp_conversations').update({
                "last_message": content,
                "last_message_at": timestamp or datetime.now().isoformat(),
                "unread_count": current_unread + (0 if is_from_me else 1),
                "updated_at": datetime.now().isoformat()
            }).eq('id', conversation_id).execute()
            logger.info(f"✅ Conversation updated: {conversation_id}")
        
        # 2. Save message
        new_message = {
            "clinic_id": clinic_id,
            "conversation_id": conversation_id,
            "message_id": message_id,
            "from_number": phone if not is_from_me else "system",
            "to_number": "system" if not is_from_me else phone,
            "message_type": message_type,
            "content": content,
            "media_url": media_url,
            "timestamp": timestamp or datetime.now().isoformat(),
            "status": "delivered" if is_from_me else "received",
            "is_from_me": is_from_me
        }
        
        supabase.table('whatsapp_messages').insert(new_message).execute()
        logger.info(f"✅ Message saved: {message_id}")
        
    except Exception as e:
        logger.error(f"❌ Error saving WhatsApp message: {e}", exc_info=True)


async def process_new_lead(
    phone: str,
    name: str,
    message: str,
    clinic_id: str,
    phone_number_id: str
):
    """
    Process new lead and trigger AI Carol response
    
    Flow:
    1. Check if patient exists, if not create
    2. Detect source (Google/Instagram)
    3. Save user message
    4. Create/update chat
    5. Trigger AI Carol
    6. Send response via Meta API
    """
    from app.services.gpt_service import get_gpt_service
    from app.services.meta_service import get_meta_service_for_clinic
    
    supabase = get_supabase()
    gpt_service = get_gpt_service()
    
    # Clean phone number (remove @s.whatsapp.net if present)
    clean_phone = phone.split('@')[0]
    
    logger.info(f"🔍 Processing lead: {name} ({clean_phone})")
    
    # 1. Get or create patient
    patient_res = supabase.table('pacientes') \
        .select('*') \
        .eq('telefone', clean_phone) \
        .eq('clinica_id', clinic_id) \
        .execute()
    
    if not patient_res.data:
        # Detect source
        source = LeadSourceDetector.detect(message)
        
        # Create new patient
        new_patient = {
            "clinica_id": clinic_id,
            "nome_completo": name,
            "telefone": clean_phone,
            "origem_campanha": source,
            "criado_em": datetime.now().isoformat()
        }
        res = supabase.table('pacientes').insert(new_patient).execute()
        patient_id = res.data[0]['id']
        logger.info(f"✅ New patient created: {name} via {source}")
    else:
        patient_id = patient_res.data[0]['id']
        logger.info(f"✅ Existing patient: {name}")
    
    
    # 2. Get or create WhatsApp conversation
    chat_res = supabase.table('whatsapp_conversations') \
        .select('*') \
        .eq('phone_number', clean_phone) \
        .execute()
    
    if not chat_res.data:
        new_chat = {
            "phone_number": clean_phone,
            "contact_name": name,
            "last_message": message[:100],
            "last_message_at": datetime.now().isoformat(),
            "unread_count": 1
        }
        c_res = supabase.table('whatsapp_conversations').insert(new_chat).execute()
        conversation_id = c_res.data[0]['id']
    else:
        conversation_id = chat_res.data[0]['id']
        supabase.table('whatsapp_conversations').update({
            "last_message": message[:100],
            "last_message_at": datetime.now().isoformat(),
            "unread_count": chat_res.data[0].get('unread_count', 0) + 1
        }).eq('id', conversation_id).execute()
    
    
    # 3. Save user message - REMOVED (Saved earlier by save_whatsapp_message)
    # The webhook already called save_whatsapp_message before calling process_new_lead
    
    # 4. Get chat history
    history_res = supabase.table('whatsapp_messages') \
        .select('*') \
        .eq('conversation_id', conversation_id) \
        .order('timestamp', desc=False) \
        .limit(10) \
        .execute()
    
    history = history_res.data if history_res.data else []
    
    # 5. Generate AI response
    logger.info(f"🤖 Generating AI response for {name}...")
    ai_response = await gpt_service.process_message(
        message=message,
        chat_history=history,
        context={"patient_name": name, "clinic_id": clinic_id}
    )
    ai_response_text = ai_response.get("response", "Desculpe, não entendi.")
    
    # 6. Save AI message
    ai_msg = {
        "conversation_id": conversation_id,
        "clinic_id": clinic_id,
        "message_id": f"ai_{datetime.now().timestamp()}",
        "from_number": "sistema",
        "to_number": clean_phone,
        "content": ai_response_text,
        "is_from_me": True,
        "timestamp": datetime.now().isoformat()
    }
    supabase.table('whatsapp_messages').insert(ai_msg).execute()
    
    # 7. Send via Meta API
    # 7. Send Response
    logger.info(f"📤 Sending response to {clean_phone}...")
    try:
        # Determine service based on phone_number_id (or check active config)
        if phone_number_id == "uazapi":
            from app.services.uazapi_service import get_uazapi_service_for_clinic
            service = await get_uazapi_service_for_clinic(clinic_id)
            service.send_message(to=clean_phone, text=ai_response_text)
        else:
            # Default to Meta
            meta_service = await get_meta_service_for_clinic(clinic_id)
            await meta_service.send_message(to=clean_phone, text=ai_response_text)
            
        logger.info(f"✅ Response sent successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp message: {e}")
        # Don't raise - we don't want to break the webhook