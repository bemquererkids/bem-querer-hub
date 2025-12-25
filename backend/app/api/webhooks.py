from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from app.core.database import get_supabase
from app.services.source_detector import LeadSourceDetector
from pydantic import BaseModel
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

async def get_clinic_id_from_instance(instance_name: str) -> str:
    """
    Maps UazAPI instance name to clinic_id.
    Returns clinic_id or raises HTTPException if not found.
    """
    try:
        supabase = get_supabase()
        result = supabase.table('whatsapp_instances').select('clinic_id').eq('instance_name', instance_name).execute()
        
        if not result.data or len(result.data) == 0:
            logger.error(f"Instance not found: {instance_name}")
            raise HTTPException(status_code=404, detail=f"Instance '{instance_name}' not found")
        
        clinic_id = result.data[0]['clinic_id']
        logger.info(f"Mapped instance '{instance_name}' to clinic_id: {clinic_id}")
        return clinic_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error mapping instance to clinic: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to identify clinic: {str(e)}")

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
    logger.info(f"=== SAVE_WHATSAPP_MESSAGE CALLED ===")
    logger.info(f"clinic_id: {clinic_id}, phone: {phone}, content: {content[:50]}...")
    
    try:
        supabase = get_supabase()
        logger.info("Supabase client obtained")
        
        # 1. Get or create conversation (filtered by clinic_id)
        logger.info(f"Querying conversation for phone={phone}, clinic_id={clinic_id}")
        conversation_res = supabase.table('whatsapp_conversations').select('*').eq('phone_number', phone).eq('clinic_id', clinic_id).execute()
        logger.info(f"Conversation query result: {len(conversation_res.data) if conversation_res.data else 0} rows")
        
        if not conversation_res.data:
            # Create new conversation
            logger.info("Creating new conversation")
            new_conversation = {
                "clinic_id": clinic_id,
                "phone_number": phone,
                "contact_name": contact_name,
                "last_message": content,
                "last_message_at": timestamp or datetime.now().isoformat(),
                "unread_count": 0 if is_from_me else 1,
                "tags": []
            }
            logger.info(f"Inserting conversation: {new_conversation}")
            conv_res = supabase.table('whatsapp_conversations').insert(new_conversation).execute()
            conversation_id = conv_res.data[0]['id']
            logger.info(f"Conversation created with ID: {conversation_id}")
        else:
            # Update existing conversation
            conversation_id = conversation_res.data[0]['id']
            current_unread = conversation_res.data[0].get('unread_count', 0)
            logger.info(f"Updating existing conversation ID: {conversation_id}")
            
            supabase.table('whatsapp_conversations').update({
                "last_message": content,
                "last_message_at": timestamp or datetime.now().isoformat(),
                "unread_count": current_unread + (0 if is_from_me else 1),
                "updated_at": datetime.now().isoformat()
            }).eq('id', conversation_id).execute()
            logger.info("Conversation updated")
        
        # 2. Save message
        logger.info(f"Saving message to conversation {conversation_id}")
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
        
        logger.info(f"Inserting message: {new_message}")
        supabase.table('whatsapp_messages').insert(new_message).execute()
        logger.info(f"✅ WhatsApp message saved: {message_id} from {phone} (clinic: {clinic_id})")
        
    except Exception as e:
        logger.error(f"❌ Error saving WhatsApp message: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't raise - we don't want to break the webhook if this fails

class UazApiMessage(BaseModel):
    # Modelo simplificado da UazAPI/Baileys
    remoteJid: str # Número do cliente (5511999999999@s.whatsapp.net)
    pushName: str # Nome no WhatsApp
    message: dict # Conteúdo (text, image, etc)
    instanceId: str

@router.post("/whatsapp")
async def receive_whatsapp_message(payload: dict, background_tasks: BackgroundTasks):
    """
    Receives notification from UazAPI (messages, history, connection, etc).
    Multi-tenant: Maps instance to clinic_id for data isolation.
    """
    try:
        event = payload.get('event', 'messages.upsert')
        instance_id = payload.get('instance', 'main')
        data = payload.get('data', {})
        
        # Get clinic_id from instance (multi-tenant mapping)
        try:
            clinic_id = await get_clinic_id_from_instance(instance_id)
        except HTTPException as e:
            logger.warning(f"Unknown instance '{instance_id}': {e.detail}")
            return {"status": "error", "message": f"Instance '{instance_id}' not registered"}

        # 1. Handle Historical Sync (MASSIVE HISTORY)
        if event == 'messaging-history.set':
            messages = data.get('messages', [])
            print(f"📦 Recebendo histórico: {len(messages)} mensagens (clinic: {clinic_id}).")
            for msg in messages:
                background_tasks.add_task(process_single_message_data, msg, instance_id, clinic_id)
            return {"status": "sync_started", "count": len(messages), "clinic_id": clinic_id}

        # 2. Handle Real-time Messages
        if event == 'messages.upsert':
            # Upsert sends a single message or array
            messages = data.get('messages', []) if isinstance(data.get('messages'), list) else [data]
            logger.info(f"📨 Processing {len(messages)} messages for clinic {clinic_id}")
            
            for message_data in messages:
                logger.info(f"Message data: {message_data.get('key', {})}")
                
                # Ignorar mensagens enviadas por MIM (fromMe)
                if message_data.get('key', {}).get('fromMe'):
                    logger.info("Skipping message fromMe=True")
                    continue
                
                logger.info(f"Adding background task for message")
                background_tasks.add_task(process_single_message_data, message_data, instance_id, clinic_id)
            
            logger.info(f"✅ {len(messages)} messages queued for processing")
            return {"status": "upsert_processed", "clinic_id": clinic_id}

        return {"status": "event_unhandled", "event": event}

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return {"status": "error", "detail": str(e)}

async def process_single_message_data(data: dict, instance_id: str, clinic_id: str):
    """
    Helper to extract details and queue the lead processor.
    Also saves message to WhatsApp tables for chat integration.
    Multi-tenant: uses clinic_id for data isolation.
    """
    try:
        remote_jid = data.get('key', {}).get('remoteJid')
        if not remote_jid or '@s.whatsapp.net' not in remote_jid:
            return

        push_name = data.get('pushName', 'Desconhecido')
        message_info = data.get('message', {})
        message_id = data.get('key', {}).get('id', str(uuid.uuid4()))
        timestamp = data.get('messageTimestamp')
        is_from_me = data.get('key', {}).get('fromMe', False)
        
        # Tentar extrair texto
        text_content = ""
        message_type = "text"
        media_url = None
        
        if 'conversation' in message_info:
            text_content = message_info['conversation']
        elif 'extendedTextMessage' in message_info:
            text_content = message_info['extendedTextMessage'].get('text', '')
        elif 'imageMessage' in message_info:
            text_content = message_info['imageMessage'].get('caption', '[Imagem]')
            message_type = "image"
            media_url = message_info['imageMessage'].get('url')
        elif 'videoMessage' in message_info:
            text_content = message_info['videoMessage'].get('caption', '[Vídeo]')
            message_type = "video"
            media_url = message_info['videoMessage'].get('url')
            
        if not text_content:
            return

        # Save to WhatsApp tables for chat integration
        await save_whatsapp_message(
            clinic_id=clinic_id,
            phone=remote_jid.split('@')[0],
            contact_name=push_name,
            message_id=message_id,
            content=text_content,
            message_type=message_type,
            media_url=media_url,
            timestamp=datetime.fromtimestamp(int(timestamp)).isoformat() if timestamp else None,
            is_from_me=is_from_me
        )

        # Process lead (existing functionality)
        if not is_from_me:
            await process_new_lead(remote_jid, push_name, text_content, instance_id)
    except Exception as e:
        logger.error(f"Error processing single message: {e}")

async def process_new_lead(phone: str, name: str, message: str, instance_id: str = "main"):
    """
    Lógica Principal:
    1. Verifica se paciente existe. Se não, cria.
    2. Detecta origem (Google/Insta).
    3. Salva mensagem do usuário.
    4. Cria Chat se não existir.
    5. Dispara IA carol para responder.
    6. Envia resposta via UazAPI.
    """
    from app.services.gpt_service import gpt_service
    from app.services.uazapi_service import get_uazapi_service
    from app.services.message_processor import get_message_processor
    
    supabase = get_supabase()
    uazapi = get_uazapi_service()
    clean_phone = phone.split('@')[0]
    
    # 1. Busca Paciente
    patient_res = supabase.table('patients').select('*').eq('phone', clean_phone).execute()
    
    patient_id = None
    clinic_id = "00000000-0000-0000-0000-000000000001" # Hardcoded demo clinic
    
    if not patient_res.data:
        # Detectar Origem
        source = LeadSourceDetector.detect(message)
        
        # Criar Novo Paciente
        new_patient = {
            "clinic_id": clinic_id,
            "full_name": name,
            "phone": clean_phone,
            "source": source,
            "created_at": datetime.now().isoformat()
        }
        res = supabase.table('patients').insert(new_patient).execute()
        if res.data:
            patient_id = res.data[0]['id']
            print(f"Novo Lead Criado: {name} via {source}")
    else:
        patient_id = patient_res.data[0]['id']
        print(f"Lead Recorrente: {name}")

    # 2. Busca ou Cria Chat
    chat_res = supabase.table('chats').select('*').eq('patient_id', patient_id).execute()
    chat_id = None
    
    if not chat_res.data:
        new_chat = {
            "clinic_id": clinic_id,
            "patient_id": patient_id,
            "whatsapp_number": clean_phone,
            "whatsapp_name": name,
            "status": "open",
            "intent": "qualifying",
            "last_message_at": datetime.now().isoformat()
        }
        c_res = supabase.table('chats').insert(new_chat).execute()
        chat_id = c_res.data[0]['id']
    else:
        chat_id = chat_res.data[0]['id']
        # Atualiza timestamp
        supabase.table('chats').update({"last_message_at": datetime.now().isoformat()}).eq('id', chat_id).execute()

    # 3. Salva Mensagem do Usuário
    new_msg = {
        "clinic_id": clinic_id,
        "chat_id": chat_id,
        "content": message,
        "sender_type": "user",
        "message_type": "text",
        "created_at": datetime.now().isoformat()
    }
    supabase.table('messages').insert(new_msg).execute()

    # 4. Obter histórico simplificado para a IA
    # Em um cenário real, pegaríamos as últimas X mensagens do Supabase
    history = [] # TODO: Implementar busca de histórico real se necessário
    
    # 5. Chamar GPT para Gerar Resposta
    print(f"🤖 Gerando resposta da Carol para {name}...")
    ai_response_text = await gpt_service.generate_response(
        message=message,
        history=history,
        persona_name="Carol"
    )

    # 6. Salvar Mensagem da IA no Banco
    ai_msg = {
        "clinic_id": clinic_id,
        "chat_id": chat_id,
        "content": ai_response_text,
        "sender_type": "ai",
        "message_type": "text",
        "created_at": datetime.now().isoformat()
    }
    supabase.table('messages').insert(ai_msg).execute()

    # 7. Enviar via WhatsApp (UazAPI)
    print(f"✉️ Enviando resposta via UazAPI para {clean_phone}...")
    try:
        await uazapi.send_message(
            instance=instance_id,
            phone=clean_phone,
            message=ai_response_text
        )
        print(f"✅ Resposta enviada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar WhatsApp: {e}")
        # Em produção, poderíamos retentar ou alertar um atendente humano