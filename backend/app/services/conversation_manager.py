"""
Multi-Agent Conversation Manager

Gerencia o estado das conversas e a transição entre agentes.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Tipos de agentes disponíveis"""
    ROUTER = "router"
    TRIAGEM = "triagem"
    KIDS = "kids"
    ADULTO = "adulto"
    AGENDAMENTO = "agendamento"
    HUMANO = "humano"


class PatientType(Enum):
    """Tipo de paciente"""
    KIDS = "kids"
    ADULTO = "adulto"
    INDEFINIDO = "indefinido"


class Intent(Enum):
    """Intenção do paciente"""
    EMERGENCIA = "emergencia"
    AGENDAMENTO = "agendamento"
    DUVIDA = "duvida"
    INSTITUCIONAL = "institucional"
    INDEFINIDO = "indefinido"


class ConversationState:
    """Estado de uma conversa"""
    
    def __init__(self, phone: str, clinic_id: str):
        self.phone = phone
        self.clinic_id = clinic_id
        self.current_agent = AgentType.ROUTER
        self.patient_type = PatientType.INDEFINIDO
        self.intent = Intent.INDEFINIDO
        self.human_takeover = False
        self.collected_data = {}
        self.agent_history = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def transition_to(self, agent: AgentType, reason: str = ""):
        """Transiciona para outro agente"""
        self.agent_history.append({
            "from": self.current_agent.value,
            "to": agent.value,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        self.current_agent = agent
        self.updated_at = datetime.now()
        logger.info(f"Conversation {self.phone}: {self.current_agent.value} → {agent.value} ({reason})")
    
    def set_patient_type(self, patient_type: PatientType):
        """Define o tipo de paciente"""
        self.patient_type = patient_type
        self.updated_at = datetime.now()
        logger.info(f"Conversation {self.phone}: Patient type set to {patient_type.value}")
    
    def set_intent(self, intent: Intent):
        """Define a intenção"""
        self.intent = intent
        self.updated_at = datetime.now()
        logger.info(f"Conversation {self.phone}: Intent set to {intent.value}")
    
    def collect_data(self, key: str, value: Any):
        """Coleta um dado"""
        self.collected_data[key] = value
        self.updated_at = datetime.now()
        logger.info(f"Conversation {self.phone}: Collected {key} = {value}")
    
    def has_data(self, key: str) -> bool:
        """Verifica se tem um dado"""
        return key in self.collected_data and self.collected_data[key]
    
    def get_data(self, key: str, default=None):
        """Obtém um dado"""
        return self.collected_data.get(key, default)
    
    def handoff_to_human(self, reason: str = ""):
        """Transfere para humano"""
        self.human_takeover = True
        self.transition_to(AgentType.HUMANO, reason)
        logger.warning(f"Conversation {self.phone}: Handed off to human ({reason})")
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            "phone": self.phone,
            "clinic_id": self.clinic_id,
            "current_agent": self.current_agent.value,
            "patient_type": self.patient_type.value,
            "intent": self.intent.value,
            "human_takeover": self.human_takeover,
            "collected_data": self.collected_data,
            "agent_history": self.agent_history,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationState':
        """Cria a partir de dicionário"""
        state = cls(data["phone"], data["clinic_id"])
        state.current_agent = AgentType(data["current_agent"])
        state.patient_type = PatientType(data["patient_type"])
        state.intent = Intent(data["intent"])
        state.human_takeover = data["human_takeover"]
        state.collected_data = data["collected_data"]
        state.agent_history = data["agent_history"]
        state.created_at = datetime.fromisoformat(data["created_at"])
        state.updated_at = datetime.fromisoformat(data["updated_at"])
        return state


class ConversationManager:
    """Gerenciador de conversas com persistência no Supabase"""
    
    def __init__(self):
        # Cache em memória para performance
        self._conversations: Dict[str, ConversationState] = {}
    
    def get_or_create(self, phone: str, clinic_id: str) -> ConversationState:
        """Obtém ou cria uma conversa (com persistência no Supabase)"""
        key = f"{clinic_id}:{phone}"
        
        # 1. Verificar cache em memória primeiro
        if key in self._conversations:
            logger.info(f"📦 Loaded from cache: {phone}")
            return self._conversations[key]
        
        # 2. Tentar carregar do Supabase
        try:
            from app.core.database import get_supabase
            supabase = get_supabase()
            
            result = supabase.table("conversation_states") \
                .select("*") \
                .eq("phone", phone) \
                .eq("clinic_id", clinic_id) \
                .execute()
            
            if result.data and len(result.data) > 0:
                # Restaurar estado do banco
                data = result.data[0]
                state = ConversationState.from_dict({
                    "phone": data["phone"],
                    "clinic_id": data["clinic_id"],
                    "current_agent": data["current_agent"],
                    "patient_type": data["patient_type"],
                    "intent": data["intent"],
                    "human_takeover": data["human_takeover"],
                    "collected_data": data["collected_data"] or {},
                    "agent_history": data["agent_history"] or [],
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"]
                })
                
                # Adicionar ao cache
                self._conversations[key] = state
                logger.info(f"💾 Loaded from Supabase: {phone} (collected_data: {state.collected_data})")
                return state
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to load from Supabase: {e}")
        
        # 3. Criar novo estado se não encontrou
        state = ConversationState(phone, clinic_id)
        self._conversations[key] = state
        logger.info(f"✨ Created new conversation for {phone}")
        
        # Salvar no banco imediatamente
        self.save(state)
        
        return state
    
    def get(self, phone: str, clinic_id: str) -> Optional[ConversationState]:
        """Obtém uma conversa"""
        key = f"{clinic_id}:{phone}"
        return self._conversations.get(key)
    
    def save(self, state: ConversationState):
        """Salva uma conversa no Supabase"""
        key = f"{state.clinic_id}:{state.phone}"
        self._conversations[key] = state
        
        # Persistir no Supabase
        try:
            from app.core.database import get_supabase
            supabase = get_supabase()
            
            data = {
                "phone": state.phone,
                "clinic_id": state.clinic_id,
                "current_agent": state.current_agent.value,
                "patient_type": state.patient_type.value,
                "intent": state.intent.value,
                "human_takeover": state.human_takeover,
                "collected_data": state.collected_data,
                "agent_history": state.agent_history,
                "updated_at": datetime.now().isoformat()
            }
            
            # Upsert (insert or update)
            supabase.table("conversation_states").upsert(data, on_conflict="phone,clinic_id").execute()
            
            logger.info(f"💾 Saved to Supabase: {state.phone} (collected_data: {state.collected_data})")
            
        except Exception as e:
            logger.error(f"❌ Failed to save to Supabase: {e}")

    
    def delete(self, phone: str, clinic_id: str):
        """Deleta uma conversa"""
        key = f"{clinic_id}:{phone}"
        if key in self._conversations:
            del self._conversations[key]
            logger.info(f"Deleted conversation for {phone}")
    
    def reset(self, phone: str, clinic_id: str):
        """Reseta uma conversa"""
        state = self.get(phone, clinic_id)
        if state:
            state.current_agent = AgentType.ROUTER
            state.patient_type = PatientType.INDEFINIDO
            state.intent = Intent.INDEFINIDO
            state.collected_data = {}
            state.agent_history = []
            state.human_takeover = False
            self.save(state)
            logger.info(f"Reset conversation for {phone}")


# Singleton global
_conversation_manager = ConversationManager()


def get_conversation_manager() -> ConversationManager:
    """Obtém o gerenciador de conversas"""
    return _conversation_manager
