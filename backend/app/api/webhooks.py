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
    Recebe notificação de nova mensagem via UazAPI.
    """
    try:
        # Extrair dados básicos (adaptar conforme o payload real da sua versão da UazAPI)
        # Assumindo estrutura padrão do Baileys/UazAPI
        data = payload.get('data', {})
        message_info = data.get('message', {})
        
        # Ignorar mensagens enviadas por MIM (fromMe)
        if data.get('key', {}).get('fromMe'):
            return {"status": "ignored", "reason": "from_me"}

        remote_jid = data.get('key', {}).get('remoteJid')
        push_name = data.get('pushName', 'Desconhecido')
        
        # Tentar extrair texto
        text_content = ""
        if 'conversation' in message_info:
            text_content = message_info['conversation']
        elif 'extendedTextMessage' in message_info:
            text_content = message_info['extendedTextMessage'].get('text', '')
            
        if not text_content:
            return {"status": "ignored", "reason": "no_text"}

        # Processar em Background para não travar a API
        background_tasks.add_task(process_new_lead, remote_jid, push_name, text_content)

        return {"status": "processing"}

    except Exception as e:
        print(f"Erro no webhook: {e}")
        # Retornar 200 para a API não ficar tentando reenviar infinitamente em caso de erro de parse
        return {"status": "error", "detail": str(e)}

async def process_new_lead(phone: str, name: str, message: str):
    """
    Lógica Principal:
    1. Verifica se paciente existe. Se não, cria.
    2. Detecta origem (Google/Insta).
    3. Salva mensagem.
    4. Cria Chat se não existir.
    """
    supabase = get_supabase()
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
            "source": source, # AQUI ESTÁ A MÁGICA DO MARKETING
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

    # 3. Salva Mensagem
    new_msg = {
        "clinic_id": clinic_id,
        "chat_id": chat_id,
        "content": message,
        "sender_type": "user",
        "message_type": "text",
        "created_at": datetime.now().isoformat()
    }
    supabase.table('messages').insert(new_msg).execute()