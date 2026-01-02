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
        # Use Admin Client to bypass RLS (since webhook is unauthenticated)
        from app.core.database import SupabaseClient
        supabase = SupabaseClient.get_admin_client()
        
        result = supabase.table('whatsapp_instances').select('clinic_id').eq('instance_name', instance_name).execute()
        
        if not result.data or len(result.data) == 0:
            logger.warning(f"Instance '{instance_name}' not found in DB (or RLS blocked it). Using fallback.")
            # Fallback for testing/setup without Service Key
            return "00000000-0000-0000-0000-000000000001" 
            
        clinic_id = result.data[0]['clinic_id']
        logger.info(f"Mapped instance '{instance_name}' to clinic_id: {clinic_id}")
        return clinic_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error mapping instance to clinic: {e}")
        # Return fallback on error to keep system running
        return "00000000-0000-0000-0000-000000000001"

async def save_whatsapp_message(
    clinic_id: str,
    phone: str,
    contact_name: str,
    message_id: str,
    content: str,
    message_type: str = "text",
    media_url: str = None,
    timestamp: str = None,
    is_from_me: bool = False,
    instance_id: str = "main",
    provided_avatar_url: str = None # New argument
):
    """
    Saves WhatsApp message to database for chat integration.
    Creates or updates conversation and adds message.
    Multi-tenant: isolated by clinic_id.
    """
    logger.info(f"=== SAVE_WHATSAPP_MESSAGE CALLED ===")
    logger.info(f"clinic_id: {clinic_id}, phone: {phone}, content: {content[:50]}...")
    
    try:
        from app.core.database import SupabaseClient
        from app.services.uazapi_service import get_uazapi_service
        
        # Use Admin Client to bypass RLS
        supabase = SupabaseClient.get_admin_client()
        logger.info("Supabase Admin client obtained for saving message")
        
        # 1. Get or create conversation (filtered by clinic_id)
        logger.info(f"Querying conversation for phone={phone}, clinic_id={clinic_id}")
        conversation_res = supabase.table('whatsapp_conversations').select('*').eq('phone_number', phone).eq('clinic_id', clinic_id).execute()
        
        conversation_id = None
        current_avatar = provided_avatar_url
        
        if not conversation_res.data:
            # Create new conversation
            logger.info("Creating new conversation")
            
            # Fetch Avatar if not provided
            if not current_avatar:
                try:
                    uazapi = get_uazapi_service()
                    current_avatar = await uazapi.get_profile_picture(instance_id, phone)
                except Exception as e:
                    logger.warning(f"Failed to fetch avatar for new conv: {e}")

            new_conversation = {
                "clinic_id": clinic_id,
                "phone_number": phone,
                "contact_name": contact_name,
                "last_message": content,
                "last_message_at": timestamp or datetime.now().isoformat(),
                "unread_count": 0 if is_from_me else 1,
                "tags": [],
                "avatar": current_avatar
            }
            logger.info(f"Inserting conversation: {new_conversation}")
            conv_res = supabase.table('whatsapp_conversations').insert(new_conversation).execute()
            conversation_id = conv_res.data[0]['id']
            logger.info(f"Conversation created with ID: {conversation_id}")
        else:
            # Update existing conversation
            conversation_id = conversation_res.data[0]['id']
            current_unread = conversation_res.data[0].get('unread_count', 0)
            existing_avatar = conversation_res.data[0].get('avatar')
            
            # Update logic
            updates = {
                "last_message": content,
                "last_message_at": timestamp or datetime.now().isoformat(),
                "unread_count": current_unread + (0 if is_from_me else 1),
                "contact_name": contact_name, # Always update contact name to keep it fresh
                "updated_at": datetime.now().isoformat()
            }
            
            # Update avatar if provided or missing
            if provided_avatar_url:
                updates['avatar'] = provided_avatar_url
            elif not existing_avatar:
                 try:
                    uazapi = get_uazapi_service()
                    new_avatar = await uazapi.get_profile_picture(instance_id, phone)
                    if new_avatar:
                        updates['avatar'] = new_avatar
                 except Exception as e:
                    logger.warning(f"Failed to fetch avatar for update: {e}")

            logger.info(f"Updating existing conversation ID: {conversation_id}")
            supabase.table('whatsapp_conversations').update(updates).eq('id', conversation_id).execute()
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
        # Log specific Supabase error if available
        if hasattr(e, 'code'):
            logger.error(f"Supabase Error Code: {e.code}")
        if hasattr(e, 'details'):
            logger.error(f"Supabase Details: {e.details}")

        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # DO NOT RAISE. If saving message fails, we still want to try processing the lead?
        # Actually if we can't save the message, chat won't work. But determining WHY is key.
        # Let's swallow the error to prevent Webhook 500 loop, but user won't see msg.
        pass

class UazApiMessage(BaseModel):
    # Modelo simplificado da UazAPI/Baileys
    remoteJid: str # Número do cliente (5511999999999@s.whatsapp.net)
    pushName: str # Nome no WhatsApp
    message: dict # Conteúdo (text, image, etc)
    instanceId: str

@router.post("/whatsapp")
async def receive_whatsapp_message(request: Request, background_tasks: BackgroundTasks):
    """
    Receives notification from UazAPI (messages, history, connection, etc).
    Multi-tenant: Maps instance to clinic_id for data isolation.
    """
    try:
        # Parse payload
        try:
            payload = await request.json()
            logger.info(f"📥 [WEBHOOK RAW] Payload received: {payload}") 
        except Exception:
            logger.error("Failed to parse JSON payload")
            return {"status": "error", "message": "Invalid JSON"}

        # Parse UazAPI format
        event_type = payload.get('EventType', payload.get('event', 'messages'))
        instance_id = payload.get('owner', payload.get('instance', 'main'))
        
        logger.info(f"Event: {event_type}, Instance: {instance_id}")

        # UazAPI sends message directly, not nested in 'data'
        data = {}
        if 'message' in payload:
            # New UazAPI format
            message_data = payload.get('message', {})
            chat_data = payload.get('chat', {})
            
            # Extract Avatar & Name from Chat Object
            avatar_url = chat_data.get('imagePreview') or chat_data.get('image')
            chat_name = chat_data.get('name') or message_data.get('senderName', '')
            chat_phone = chat_data.get('phone') # Formatted phone if needed
            msg_source = message_data.get('source') # web, android, ios, etc.

            data = {
                'key': {
                    'remoteJid': message_data.get('chatid', message_data.get('sender', '')),
                    'fromMe': message_data.get('fromMe', False),
                    'id': message_data.get('messageid', message_data.get('id', ''))
                },
                'pushName': chat_name, # Prioritize chat.name
                'messageTimestamp': message_data.get('messageTimestamp', 0) // 1000,  # Convert to seconds
                'message': {
                    'conversation': message_data.get('content', message_data.get('text', ''))
                },
                'messageType': message_data.get('messageType', 'conversation'),
                'provided_avatar': avatar_url, # Injected field
                'message_source': msg_source,
                'formatted_phone': chat_phone
            }
        else:
            # Old format (if any)
            data = payload.get('data', {})
        
        # Get clinic_id from instance (multi-tenant mapping)
        try:
            clinic_id = await get_clinic_id_from_instance(instance_id)
        except HTTPException as e:
            logger.warning(f"Unknown instance '{instance_id}': {e.detail}")
            return {"status": "error", "message": f"Instance '{instance_id}' not registered"}

        # 1. Handle Historical Sync (MASSIVE HISTORY)
        if event_type == 'messaging-history.set':
            messages = data.get('messages', [])
            print(f"📦 Recebendo histórico: {len(messages)} mensagens (clinic: {clinic_id}).")
            for msg in messages:
                background_tasks.add_task(process_single_message_data, msg, instance_id, clinic_id)
            return {"status": "sync_started", "count": len(messages), "clinic_id": clinic_id}

        # 2. Handle Real-time Messages (UazAPI uses 'messages' event type)
        if event_type in ['messages.upsert', 'messages']:
            # Upsert sends a single message or array
            messages = data.get('messages', []) if isinstance(data.get('messages'), list) else [data]
            logger.info(f"📨 Processing {len(messages)} messages for clinic {clinic_id}")
            
            for message_data in messages:
                # Ignorar mensagens enviadas por MIM (fromMe)
                if message_data.get('key', {}).get('fromMe'):
                    logger.info("Skipping message fromMe=True")
                    continue
                
                background_tasks.add_task(process_single_message_data, message_data, instance_id, clinic_id)
            
            return {"status": "upsert_processed", "clinic_id": clinic_id}

        return {"status": "event_unhandled", "event": event_type}

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        import traceback
        return {
            "status": "error", 
            "detail": str(e),
            "traceback": traceback.format_exc()
        }


async def process_single_message_data(data: dict, instance_id: str, clinic_id: str):
    """
    Helper to extract details and queue the lead processor.
    Also saves message to WhatsApp tables for chat integration.
    Multi-tenant: uses clinic_id for data isolation.
    """
    # try: REMOVED FOR DEBUGGING
    remote_jid = data.get('key', {}).get('remoteJid')
    if not remote_jid or '@s.whatsapp.net' not in remote_jid:
        return

    push_name = data.get('pushName', 'Desconhecido')
    message_info = data.get('message', {})
    message_id = data.get('key', {}).get('id', str(uuid.uuid4()))
    timestamp = data.get('messageTimestamp')
    is_from_me = data.get('key', {}).get('fromMe', False)
    provided_avatar = data.get('provided_avatar') # Extract injected avatar
    message_source = data.get('message_source') # Extract injected source
    
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
        logger.warning(f"⚠️ Message skipped: No content extracted from {message_info.keys()}")
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
        is_from_me=is_from_me,
        instance_id=instance_id,
        provided_avatar_url=provided_avatar # Pass to saver
    )

    # Process lead (existing functionality)
    if not is_from_me:
        await process_new_lead(
            phone=remote_jid.split('@')[0], 
            name=push_name, 
            message=text_content, 
            instance_id=instance_id,
            explicit_source=message_source,
            clinic_id=clinic_id
        )

async def process_new_lead(
    phone: str, 
    name: str, 
    message: str, 
    instance_id: str = "main", 
    explicit_source: str = None,
    clinic_id: str = "00000000-0000-0000-0000-000000000001"
):
    """
    Lógica Principal:
    1. Verifica se paciente existe (TABELA: pacientes). Se não, cria. Se sim, ATUALIZA.
    2. Detecta origem (Google/Insta).
    3. (REMOVIDO) Atualizar conversa (já feito por save_whatsapp_message).
    4. Dispara IA carol para responder.
    5. Envia resposta via UazAPI.
    """
    from app.services.gpt_service import get_gpt_service
    from app.services.uazapi_service import get_uazapi_service
    from app.core.database import SupabaseClient
    
    # Use Admin Client for ALL operations to bypass RLS
    supabase = SupabaseClient.get_admin_client()
    uazapi = get_uazapi_service()
    gpt_service = get_gpt_service()
    clean_phone = phone # Already cleaned in caller
    
    # 1. Busca Paciente (pacientes)
    patient_res = supabase.table('pacientes').select('*').eq('telefone', clean_phone).execute()
    
    # Determine Source
    final_source = explicit_source if explicit_source else LeadSourceDetector.detect(message)
    
    if not patient_res.data:
        # Criar Novo Paciente
        new_patient = {
            "clinica_id": clinic_id, # Schema PT-BR usa clinica_id
            "nome": name,
            "telefone": clean_phone, 
            "origem": final_source
        }
        
        try:
            res = supabase.table('pacientes').insert(new_patient).execute()
            if res.data:
                print(f"✅ Novo Lead Criado: {name} via {final_source}")
        except Exception as e:
            print(f"⚠️ Erro no cadastro de paciente (ignorando para continuar chat): {e}")
            pass
    else:
        # Atualizar Paciente Existente
        patient_id = patient_res.data[0]['id']
        current_name = patient_res.data[0].get('nome')
        current_source = patient_res.data[0].get('origem')
        
        updates = {}
        if name and name != 'Desconhecido' and name != current_name:
            updates['nome'] = name
            
        if final_source and final_source != 'Indefinido' and not current_source:
             updates['origem'] = final_source
             
        if updates:
            try:
                supabase.table('pacientes').update(updates).eq('id', patient_id).execute()
                print(f"🔄 Lead Atualizado: {name} (Updates: {updates.keys()})")
            except Exception as e:
                print(f"⚠️ Erro ao atualizar lead: {e}")

    # 2. Busca Chat ID (whatsapp_conversations)
    # A conversa JÁ FOI CRIADA/ATUALIZADA por save_whatsapp_message antes desta função ser chamada.
    chat_res = supabase.table('whatsapp_conversations').select('id')\
        .eq('phone_number', clean_phone)\
        .eq('clinic_id', clinic_id)\
        .execute()
    
    if not chat_res.data:
        print(f"⚠️ Alerta: Conversa não encontrada para IA (phone={clean_phone}, clinic={clinic_id}). save_whatsapp_message falhou?")
        # Fallback: create minimal chat to allowing AI to function, but this shouldn't happen ideally
        new_chat = {
            "clinic_id": clinic_id,
            "phone_number": clean_phone,
            "contact_name": name,
            "last_message": message,
            "last_message_at": datetime.now().isoformat(),
            "unread_count": 1
        }
        c_res = supabase.table('whatsapp_conversations').insert(new_chat).execute()
        chat_id = c_res.data[0]['id']
    else:
        chat_id = chat_res.data[0]['id']
        # NÃO atualizamos unread_count aqui para evitar contagem dupla
    
    # 3. Salva Mensagem do Usuário (whatsapp_messages)
    # Ignorado, já salvo por save_whatsapp_message.

    # 4. Obter histórico simplificado para a IA (limit 5)
    history = []     
    try:
        hist_res = supabase.table('whatsapp_messages').select('content, is_from_me')\
            .eq('conversation_id', chat_id)\
            .order('created_at', desc=True)\
            .limit(5).execute()
        
        if hist_res.data:
            for h in reversed(hist_res.data):
                role = "assistant" if h['is_from_me'] else "user"
                history.append({"role": role, "content": h['content']})
    except: pass
    
    # 5. Chamar GPT (OpenAI) para Gerar Resposta
    print(f"🤖 Gerando resposta da Carol para {name}...")
    ai_response = await gpt_service.process_message(
        message=message,
        chat_history=history,
        context={"patient_name": name, "clinic_id": clinic_id}
    )
    ai_response_text = ai_response.get("response", "Desculpe, não entendi.")

    # 6. Salvar Mensagem da IA no Banco (whatsapp_messages)
    ai_msg = {
        "clinic_id": clinic_id,
        "conversation_id": chat_id,
        "message_id": f"AI-{uuid.uuid4()}",
        "from_number": "system",
        "to_number": clean_phone,
        "message_type": "text",
        "content": ai_response_text,
        "is_from_me": True
    }
    supabase.table('whatsapp_messages').insert(ai_msg).execute()

    # 6.1 ATUALIZAR CONVERSATION (Last Message)
    try:
        supabase.table('whatsapp_conversations').update({
            "last_message": ai_response_text,
            "last_message_at": datetime.now().isoformat(),
            # Não mudamos unread_count pois é mensagem enviada (is_from_me)
            # ou talvez zeramos? Geralmente se o sistema respondeu, não é mais unread para o sistema.
            # Mas se o sistema respondeu, o usuário ainda não leu?
            # A lógica de 'unread' é "não lido pelo ATENDENTE"?
            # Se a IA respondeu, tecnicamente foi "atendido". Vamos manter a lógica do save_message: +0.
            # Se for para marcar como lida pelo sistema, poderiamos setar 0.
            # Por enquanto, só atualizo o texto para aparecer no painel.
        }).eq('id', chat_id).execute()
    except Exception as e:
        print(f"⚠️ Falha ao atualizar last_message da conversa: {e}")

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
        raise e # DEBUG: Re-raise
        # Em produção, poderíamos retentar ou alertar um atendente humano

@router.post("/debug_force")
async def debug_force_reply(phone: str, message: str):
    """
    Forces the AI processing loop synchronously to capture errors.
    """
    try:
        await process_new_lead(
            phone=phone,
            name="Debug User",
            message=message,
            instance_id="debug_instance"
        )
        return {"status": "success", "message": "AI Flow completed without error"}
    except Exception as e:
        import traceback
        import httpx
        
        error_detail = str(e)
        if isinstance(e, httpx.HTTPStatusError):
             error_detail = f"HTTP {e.response.status_code}: {e.response.text}"
             
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": error_detail,
            "traceback": traceback.format_exc()
        }