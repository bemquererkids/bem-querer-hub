"""
Multi-Agent System - Agentes Especializados

Router Agent: Analisa e roteia mensagens
Triagem Agent: Coleta dados básicos
"""

from typing import Dict, Any, Tuple, Optional
from openai import AsyncOpenAI
import json
import logging
from app.services.conversation_manager import (
    ConversationState, AgentType, PatientType, Intent
)

logger = logging.getLogger(__name__)


class BaseAgent:
    """Classe base para agentes"""
    
    def __init__(self, client: AsyncOpenAI, agent_type: AgentType):
        self.client = client
        self.agent_type = agent_type
        self.model = "gpt-4-turbo-preview"
    
    async def process(
        self,
        message: str,
        state: ConversationState,
        context: Optional[Dict] = None
    ) -> Tuple[str, Optional[AgentType]]:
        """
        Processa uma mensagem
        
        Returns:
            (resposta, próximo_agente)
        """
        raise NotImplementedError


class RouterAgent(BaseAgent):
    """
    Router Agent - Orquestrador
    
    Analisa a mensagem e decide qual agente deve processar
    """
    
    def __init__(self, client: AsyncOpenAI):
        super().__init__(client, AgentType.ROUTER)
    
    async def process(
        self,
        message: str,
        state: ConversationState,
        context: Optional[Dict] = None
    ) -> Tuple[str, Optional[AgentType]]:
        """Analisa e roteia"""
        
        prompt = f"""
Você é um roteador inteligente. Analise a mensagem e determine:

MENSAGEM: "{message}"

ANÁLISE NECESSÁRIA:

1. TIPO DE PACIENTE:
   - kids: criança (0-12 anos), palavras: "filho", "filha", "bebê", "criança"
   - adulto: adulto (13+), palavras: "meu dente", "para mim", "eu preciso"
   - indefinido: não ficou claro

2. INTENÇÃO:
   - emergencia: trauma, dor aguda, sangramento, "socorro", "urgente"
   - agendamento: quer agendar, "marcar consulta", "agendar"
   - duvida: pergunta sobre tratamento, valor, "quanto custa"
   - institucional: horário, endereço, convênio, "onde fica"
   - indefinido: não ficou claro

3. HANDOFF PARA HUMANO:
   - Se pedir explicitamente: "falar com atendente", "falar com humano"
   - Se for reclamação: "péssimo", "horrível"
   - Se estiver insatisfeito: "não está entendendo"

RETORNE APENAS JSON (sem markdown):
{{
  "patient_type": "kids|adulto|indefinido",
  "intent": "emergencia|agendamento|duvida|institucional|indefinido",
  "needs_human": true|false,
  "confidence": 0.0-1.0,
  "next_agent": "triagem|kids|adulto|humano",
  "reasoning": "breve explicação"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Atualizar estado
            if result["patient_type"] != "indefinido":
                state.set_patient_type(PatientType(result["patient_type"]))
            
            if result["intent"] != "indefinido":
                state.set_intent(Intent(result["intent"]))
            
            # Determinar próximo agente
            if result["needs_human"]:
                next_agent = AgentType.HUMANO
            else:
                next_agent = AgentType(result["next_agent"])
            
            logger.info(f"Router: {result['reasoning']} → {next_agent.value}")
            
            # Router não responde, apenas roteia
            return None, next_agent
            
        except Exception as e:
            logger.error(f"Router error: {e}")
            # Fallback: vai para triagem
            return None, AgentType.TRIAGEM


class TriagemAgent(BaseAgent):
    """
    Triagem Agent - Primeira Interação
    
    Coleta dados básicos de forma natural
    """
    
    def __init__(self, client: AsyncOpenAI):
        super().__init__(client, AgentType.TRIAGEM)
    
    async def process(
        self,
        message: str,
        state: ConversationState,
        context: Optional[Dict] = None
    ) -> Tuple[str, Optional[AgentType]]:
        """Coleta dados e decide próximo agente"""
        
        # Construir contexto
        collected = state.collected_data
        
        # Determinar saudação baseada no horário (Brasil/São Paulo)
        from datetime import datetime
        import pytz
        
        # Usar fuso horário do Brasil
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        hour = now.hour
        
        if 5 <= hour < 12:
            greeting = "Bom dia"
        elif 12 <= hour < 18:
            greeting = "Boa tarde"
        else:
            greeting = "Boa noite"
        
        # Verificar se é primeira mensagem
        is_first_message = not collected or len(collected) == 0
        
        # Se for primeira mensagem, apenas apresentar
        if is_first_message:
            response = f"{greeting}! 😊 Um prazer, sou a Carol, da equipe Bem-Querer Odontologia.\nSerá um prazer ajudá-lo(a)!\n\nA consulta é para você ou para seu filho(a)?"
            return response, None
        
        # Não é primeira mensagem - extrair dados e perguntar
        message_lower = message.lower()
        
        # Extrair tipo se não tiver
        if not collected.get("tipo"):
            if any(word in message_lower for word in ["filho", "filha", "criança", "bebê", "meu filho", "minha filha"]):
                state.collect_data("tipo", "kids")
                logger.info("Extracted tipo=kids from message")
                # Perguntar nome
                if "filha" in message_lower:
                    return "Qual o nome dela? 🦷", None
                else:
                    return "Qual o nome dele? 🦷", None
            elif any(word in message_lower for word in ["para mim", "eu preciso", "meu dente", "para eu"]):
                state.collect_data("tipo", "adulto")
                logger.info("Extracted tipo=adulto from message")
                return "Qual o seu nome?", None
            else:
                # Não conseguiu detectar, perguntar novamente
                return "A consulta é para você ou para seu filho(a)?", None
        
        # Tem tipo, extrair nome se não tiver
        if not collected.get("nome"):
            # Tentar extrair nome da mensagem
            # Por enquanto, considerar a mensagem inteira como nome
            state.collect_data("nome", message.strip())
            logger.info(f"Extracted nome={message.strip()}")
            
            # Se for kids, perguntar idade
            if collected.get("tipo") == "kids":
                return "Qual a idade?", None
            else:
                # Se for adulto, perguntar dor
                return "Está sentindo alguma dor ou incômodo no momento?", None
        
        # Tem tipo e nome, verificar idade (se kids)
        if collected.get("tipo") == "kids" and not collected.get("idade"):
            # Tentar extrair idade
            import re
            numbers = re.findall(r'\d+', message)
            if numbers:
                idade = numbers[0]
                state.collect_data("idade", idade)
                logger.info(f"Extracted idade={idade}")
            
            # Perguntar dor
            return "Está sentindo alguma dor ou incômodo no momento?", None
        
        # Tem tipo, nome (e idade se kids), extrair dor
        if not collected.get("dor_urgencia"):
            if any(word in message_lower for word in ["sim", "dor", "doendo", "incômodo", "incomodo"]):
                state.collect_data("dor_urgencia", "sim")
                logger.info("Extracted dor_urgencia=sim")
            elif any(word in message_lower for word in ["não", "nao", "sem dor", "não sinto"]):
                state.collect_data("dor_urgencia", "não")
                logger.info("Extracted dor_urgencia=não")
            else:
                # Assumir que não tem dor
                state.collect_data("dor_urgencia", "não")
            
            # Perguntar motivo
            return "Qual o motivo da consulta?", None
        
        # Tem tudo menos motivo
        if not collected.get("motivo"):
            state.collect_data("motivo", message.strip())
            logger.info(f"Extracted motivo={message.strip()}")
            
            # Pronto para transferir!
            tipo = collected.get("tipo")
            if tipo == "kids":
                next_agent = AgentType.KIDS
            else:
                next_agent = AgentType.ADULTO
            
            # Como ainda não temos Kids/Adulto Agent, dar uma resposta
            return "Entendi! Vou verificar os horários disponíveis. Um momento... 🦷", next_agent
        
        # Fallback
        return "Desculpe, pode repetir? 😊", None


# Factory para criar agentes
def create_agent(agent_type: AgentType, client: AsyncOpenAI) -> BaseAgent:
    """Cria um agente"""
    if agent_type == AgentType.ROUTER:
        return RouterAgent(client)
    elif agent_type == AgentType.TRIAGEM:
        return TriagemAgent(client)
    # TODO: Adicionar outros agentes
    else:
        raise ValueError(f"Agent type {agent_type} not implemented yet")
