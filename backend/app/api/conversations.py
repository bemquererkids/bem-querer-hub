"""
Conversation API Router
Endpoints for managing conversation threads with Carol.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.gpt_service import gpt_service
from app.core.database import get_supabase_client
from datetime import datetime

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

# Schemas
class MessageRequest(BaseModel):
    thread_id: Optional[str] = None
    message: str
    clinica_id: str
    user_id: Optional[str] = None

class MessageResponse(BaseModel):
    thread_id: str
    message_id: str
    response: str
    created_at: str

class ThreadResponse(BaseModel):
    id: str
    titulo: str
    status: str
    criado_em: str
    atualizado_em: str

# Endpoints
@router.post("/chat")
async def chat_with_carol(request: MessageRequest):
    """
    Enviar mensagem para a Carol e receber resposta.
    Cria nova thread se thread_id não for fornecido.
    """
    try:
        supabase = get_supabase_client()
        
        # 1. Criar ou usar thread existente
        if not request.thread_id:
            # Criar nova thread
            thread_response = supabase.rpc(
                "criar_thread",
                {
                    "p_clinica_id": request.clinica_id,
                    "p_user_id": request.user_id,
                    "p_titulo": "Nova Conversa",
                    "p_canal": "chat"
                }
            ).execute()
            
            thread_id = thread_response.data
        else:
            thread_id = request.thread_id
        
        # 2. Buscar histórico da thread
        history_response = supabase.rpc(
            "obter_historico_thread",
            {
                "p_thread_id": thread_id,
                "p_limit": 20
            }
        ).execute()
        
        # Formatar histórico para OpenAI
        history = []
        for msg in history_response.data:
            if msg["role"] in ["user", "assistant"]:
                history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # 3. Salvar mensagem do usuário
        user_msg_response = supabase.rpc(
            "adicionar_mensagem",
            {
                "p_thread_id": thread_id,
                "p_role": "user",
                "p_content": request.message,
                "p_metadata": {},
                "p_tokens": None
            }
        ).execute()
        
        user_message_id = user_msg_response.data
        
        # 4. Gerar resposta da Carol
        carol_response = await gpt_service.generate_response(
            message=request.message,
            history=history,
            persona_name="Carol",
            context_data="",
            clinica_id=request.clinica_id
        )
        
        # 5. Salvar resposta da Carol
        assistant_msg_response = supabase.rpc(
            "adicionar_mensagem",
            {
                "p_thread_id": thread_id,
                "p_role": "assistant",
                "p_content": carol_response,
                "p_metadata": {},
                "p_tokens": None
            }
        ).execute()
        
        assistant_message_id = assistant_msg_response.data
        
        return {
            "thread_id": thread_id,
            "message_id": assistant_message_id,
            "response": carol_response,
            "created_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"[Chat Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads")
async def list_threads(clinica_id: str, limit: int = 50):
    """
    Listar threads de conversa de uma clínica.
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("conversation_threads").select(
            "id, titulo, status, criado_em, atualizado_em"
        ).eq(
            "clinica_id", clinica_id
        ).order(
            "atualizado_em", desc=True
        ).limit(limit).execute()
        
        return {"threads": response.data}
    
    except Exception as e:
        print(f"[List Threads Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads/{thread_id}/messages")
async def get_thread_messages(thread_id: str):
    """
    Obter todas as mensagens de uma thread.
    """
    try:
        supabase = get_supabase_client()
        response = supabase.rpc(
            "obter_historico_thread",
            {
                "p_thread_id": thread_id,
                "p_limit": 100
            }
        ).execute()
        
        return {"messages": response.data}
    
    except Exception as e:
        print(f"[Get Messages Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/threads/{thread_id}")
async def archive_thread(thread_id: str):
    """
    Arquivar thread (soft delete).
    """
    try:
        supabase = get_supabase_client()
        supabase.table("conversation_threads").update({
            "status": "arquivada"
        }).eq("id", thread_id).execute()
        
        return {"success": True, "message": "Thread arquivada"}
    
    except Exception as e:
        print(f"[Archive Thread Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))
