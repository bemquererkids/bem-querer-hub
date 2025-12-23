from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from app.core.database import get_supabase
from app.services.source_detector import LeadSourceDetector
from pydantic import BaseModel
from datetime import datetime
import uuid

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

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
    """
    try:
        event = payload.get('event', 'messages.upsert')
        instance_id = payload.get('instance', 'main')
        data = payload.get('data', {})

        # 1. Handle Historical Sync (MASSIVE HISTORY)
        if event == 'messaging-history.set':
            messages = data.get('messages', [])
            print(f"📦 Recebendo histórico: {len(messages)} mensagens.")
            for msg in messages:
                background_tasks.add_task(process_single_message_data, msg, instance_id)
            return {"status": "sync_started", "count": len(messages)}

        # 2. Handle Real-time Messages
        if event == 'messages.upsert':
            # Upsert sends a single message or array
            messages = data.get('messages', []) if isinstance(data.get('messages'), list) else [data]
            for message_data in messages:
                # Ignorar mensagens enviadas por MIM (fromMe)
                if message_data.get('key', {}).get('fromMe'):
                    continue
                
                background_tasks.add_task(process_single_message_data, message_data, instance_id)
            
            return {"status": "upsert_processed"}

        return {"status": "event_unhandled", "event": event}

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return {"status": "error", "detail": str(e)}

async def process_single_message_data(data: dict, instance_id: str):
    """
    Helper to extract details and queue the lead processor.
    """
    try:
        remote_jid = data.get('key', {}).get('remoteJid')
        if not remote_jid or '@s.whatsapp.net' not in remote_jid:
            return

        push_name = data.get('pushName', 'Desconhecido')
        message_info = data.get('message', {})
        
        # Tentar extrair texto
        text_content = ""
        if 'conversation' in message_info:
            text_content = message_info['conversation']
        elif 'extendedTextMessage' in message_info:
            text_content = message_info['extendedTextMessage'].get('text', '')
        elif 'imageMessage' in message_info:
            text_content = message_info['imageMessage'].get('caption', '[Imagem]')
        elif 'videoMessage' in message_info:
            text_content = message_info['videoMessage'].get('caption', '[Vídeo]')
            
        if not text_content:
            return

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