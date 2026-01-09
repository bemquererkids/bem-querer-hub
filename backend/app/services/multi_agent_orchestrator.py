"""
Multi-Agent Orchestrator

Orquestra a comunicação entre agentes e gerencia o fluxo da conversa
"""

from typing import Dict, Any, Optional
from openai import AsyncOpenAI
import logging
from app.core.config import settings
from app.services.conversation_manager import (
    get_conversation_manager, ConversationState, AgentType
)
from app.services.agents import create_agent
from app.services.embedded_knowledge import search_embedded_knowledge

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """Orquestrador de múltiplos agentes"""
    
    def __init__(self):
        # Inicializar OpenAI client
        api_key = settings.OPENAI_API_KEY
        if not api_key or "placeholder" in api_key:
            # Try JSON persistence
            api_key = self._load_key_from_json()
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.conversation_manager = get_conversation_manager()
    
    def _load_key_from_json(self) -> Optional[str]:
        """Load API key from JSON file"""
        import os
        import json
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "clinic_integrations.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    key = data.get("openai", {}).get("api_key")
                    if key and "OPENAI_API_KEY_HERE" not in key:
                        return key
        except:
            pass
        return None
    
    async def process_message(
        self,
        message: str,
        phone: str,
        clinic_id: str,
        chat_history: Optional[list] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem através do sistema multi-agent
        
        Args:
            message: Mensagem do usuário
            phone: Telefone do usuário
            clinic_id: ID da clínica
            chat_history: Histórico de mensagens
            context: Contexto adicional
            
        Returns:
            {
                "response": "resposta do agente",
                "current_agent": "agente atual",
                "patient_type": "kids|adulto|indefinido",
                "intent": "intenção",
                "human_takeover": bool
            }
        """
        
        try:
            # 1. Obter ou criar estado da conversa
            state = self.conversation_manager.get_or_create(phone, clinic_id)
            
            # 2. Verificar se humano assumiu
            if state.human_takeover:
                logger.info(f"Conversation {phone}: Human has taken over, not responding")
                return {
                    "response": None,
                    "current_agent": "humano",
                    "patient_type": state.patient_type.value,
                    "intent": state.intent.value,
                    "human_takeover": True,
                    "message": "Humano assumiu a conversa"
                }
            
            # 3. Verificar gatilhos de handoff para humano
            if self._should_handoff_to_human(message):
                state.handoff_to_human("Gatilho detectado na mensagem")
                self.conversation_manager.save(state)
                
                # TODO: Notificar equipe
                
                return {
                    "response": "Vou transferir você para nossa equipe agora. Um atendente vai te responder em instantes! 💙",
                    "current_agent": "humano",
                    "patient_type": state.patient_type.value,
                    "intent": state.intent.value,
                    "human_takeover": True
                }
            
            # 4. Processar com agente atual
            # Determinar agente atual
            current_agent_type = state.current_agent
            logger.info(f"Processing with agent: {current_agent_type.value}")
            
            try:
                # Tentar criar o agente
                try:
                    agent = create_agent(current_agent_type, self.client)
                except ValueError as e:
                    logger.error(f"❌ Erro ao criar agente {current_agent_type}: {e}")
                    logger.warning("⚠️ Fazendo fallback para TRIAGEM")
                    # Fallback para Triagem se agente não existir
                    current_agent_type = AgentType.TRIAGEM
                    state.current_agent = AgentType.TRIAGEM
                    agent = create_agent(AgentType.TRIAGEM, self.client)
                    
            except Exception as e:
                 logger.critical(f"🔥 Erro crítico ao criar agente (fallback falhou): {e}")
                 return {
                    "response": "Desculpe, estamos com uma instabilidade momentânea. Pode tentar novamente em 1 minuto? 🔧",
                    "current_agent": "error",
                    "patient_type": state.patient_type.value,
                    "intent": state.intent.value,
                    "human_takeover": False,
                    "error": str(e)
                 }

            # Adicionar contexto RAG se necessário
            if context is None: # Ensure context is a dict if not provided
                context = {}
            
            knowledge_context = None
            if current_agent_type != AgentType.ROUTER:
                try:
                    from app.services.knowledge_base_service import get_knowledge_base_service
                    
                    kb_service = get_knowledge_base_service()
                    knowledge_context = kb_service.get_context_for_query(message, max_tokens=1500)
                    
                    if knowledge_context:
                        logger.info(f"📚 RAG: Found relevant knowledge for query")
                        if context is None:
                            context = {}
                        context["knowledge"] = knowledge_context
                    else:
                        logger.info(f"📚 RAG: No relevant knowledge found")
                        
                except Exception as e:
                    logger.warning(f"⚠️ RAG search failed: {e}")
                    # Fallback to embedded knowledge
                    try:
                        knowledge_context = search_embedded_knowledge(
                            message,
                            patient_age=state.patient_type.value if state.patient_type != "indefinido" else None
                        )
                        if context is None:
                            context = {}
                        context["knowledge"] = knowledge_context
                    except Exception as e2:
                        logger.warning(f"⚠️ Embedded knowledge also failed: {e2}")
            
            # Processar mensagem
            response, next_agent = await agent.process(message, state, context)
            
            # 5. Transição de agente se necessário
            if next_agent and next_agent != current_agent_type:
                state.transition_to(next_agent, "Agent decision")
                
                # Se transicionou, processar com novo agente
                if response is None:  # Router não responde
                    new_agent = create_agent(next_agent, self.client)
                    response, _ = await new_agent.process(message, state, context)
            
            # 6. Salvar estado
            self.conversation_manager.save(state)
            
            # 7. Retornar resposta
            return {
                "response": response,
                "current_agent": state.current_agent.value,
                "patient_type": state.patient_type.value,
                "intent": state.intent.value,
                "human_takeover": state.human_takeover,
                "collected_data": state.collected_data
            }
            
        except Exception as e:
            logger.error(f"Multi-agent orchestrator error: {e}", exc_info=True)
            
            # Fallback: resposta genérica
            return {
                "response": "Desculpe, tive um problema técnico. Pode repetir sua mensagem? 💙",
                "current_agent": "error",
                "patient_type": "indefinido",
                "intent": "indefinido",
                "human_takeover": False,
                "error": str(e)
            }
    
    def _should_handoff_to_human(self, message: str) -> bool:
        """Verifica se deve transferir para humano"""
        message_lower = message.lower()
        
        # Gatilhos explícitos
        explicit_triggers = [
            "quero falar com atendente",
            "falar com humano",
            "falar com pessoa",
            "atendente humano",
            "não quero robô",
            "quero falar com alguém",
            "falar com atendente de verdade"
        ]
        
        # Insatisfação
        dissatisfaction_triggers = [
            "não está entendendo",
            "não está ajudando",
            "péssimo atendimento",
            "horrível",
            "não resolve",
            "não funciona"
        ]
        
        # Reclamação
        complaint_triggers = [
            "reclamação",
            "reclamar",
            "insatisfeito",
            "problema com"
        ]
        
        all_triggers = explicit_triggers + dissatisfaction_triggers + complaint_triggers
        
        for trigger in all_triggers:
            if trigger in message_lower:
                logger.warning(f"Human handoff trigger detected: '{trigger}'")
                return True
        
        return False


# Singleton global
_orchestrator = None


def get_multi_agent_orchestrator() -> MultiAgentOrchestrator:
    """Obtém o orquestrador multi-agent"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator()
    return _orchestrator
