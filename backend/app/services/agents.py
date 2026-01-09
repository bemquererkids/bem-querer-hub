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
        
        # Determinar saudação baseada no horário
        from datetime import datetime
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "Bom dia"
        elif 12 <= hour < 18:
            greeting = "Boa tarde"
        else:
            greeting = "Boa noite"
        
        # Verificar se é primeira mensagem (apresentação)
        is_first_message = len(state.agent_history) <= 1
        
        prompt = f"""
Você é a Carol, da equipe Bem-Querer Odontologia.

HORÁRIO ATUAL: {greeting}

PRIMEIRA MENSAGEM: {is_first_message}

DADOS JÁ COLETADOS:
{json.dumps(collected, indent=2, ensure_ascii=False)}

MENSAGEM DO PACIENTE: "{message}"

---

INSTRUÇÕES:

{"SE FOR A PRIMEIRA MENSAGEM (saudação inicial):" if is_first_message else "CONTINUAÇÃO DA CONVERSA:"}

{'''APRESENTAÇÃO OBRIGATÓRIA (apenas na primeira mensagem):
"{greeting}! 😊 Um prazer, sou a Carol, da equipe Bem-Querer Odontologia. 
Será um prazer ajudá-lo(a)!

A consulta é para você ou para seu filho(a)?"

IMPORTANTE: Use exatamente essa apresentação na primeira mensagem!
''' if is_first_message else '''
DADOS NECESSÁRIOS (se não tiver):
1. tipo: É para criança (kids) ou adulto?
2. nome: Nome do paciente
3. idade: Idade (se criança)
4. motivo: Motivo da consulta
5. dor_urgencia: Está sentindo dor ou incômodo no momento? (sim/não)

PERGUNTAS A FAZER (uma por vez, na ordem):
- Se não tem tipo: "A consulta é para você ou para seu filho(a)?"
- Se não tem nome: "Qual o nome [dele/dela/seu]?"
- Se não tem idade (e é criança): "Qual a idade [dele/dela]?"
- Se não tem dor_urgencia: "Está sentindo alguma dor ou incômodo no momento?"
- Se não tem motivo: "Qual o motivo da consulta?"

SEJA NATURAL:
- Faça UMA pergunta por vez
- Se a mensagem responde algo, EXTRAIA a informação
- Use emojis moderados (💙, 🦷, 😊)
- Tom amigável e acolhedor
'''}

QUANDO TRANSFERIR:
- Se tem: tipo (kids/adulto) + nome + motivo + dor_urgencia → PRONTO para transferir
- Se tipo = kids → Próximo agente: "kids"
- Se tipo = adulto → Próximo agente: "adulto"

RETORNE JSON:
{{
  "response": "sua resposta ao paciente",
  "extracted_data": {{
    "tipo": "kids|adulto|null",
    "nome": "nome ou null",
    "idade": "idade ou null",
    "motivo": "motivo ou null",
    "dor_urgencia": "sim|não|null"
  }},
  "ready_to_transfer": true|false,
  "next_agent": "kids|adulto|null"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Salvar dados extraídos
            for key, value in result["extracted_data"].items():
                if value and value != "null":
                    state.collect_data(key, value)
            
            # Atualizar tipo de paciente se descobriu
            if result["extracted_data"].get("tipo"):
                tipo = result["extracted_data"]["tipo"]
                state.set_patient_type(PatientType.KIDS if tipo == "kids" else PatientType.ADULTO)
            
            # Determinar próximo agente
            if result["ready_to_transfer"] and result["next_agent"]:
                next_agent = AgentType(result["next_agent"])
            else:
                next_agent = None  # Continua na triagem
            
            return result["response"], next_agent
            
        except Exception as e:
            logger.error(f"Triagem error: {e}")
            # Fallback com apresentação
            from datetime import datetime
            hour = datetime.now().hour
            if 5 <= hour < 12:
                greeting = "Bom dia"
            elif 12 <= hour < 18:
                greeting = "Boa tarde"
            else:
                greeting = "Boa noite"
            
            return f"{greeting}! 😊 Um prazer, sou a Carol, da equipe Bem-Querer Odontologia.\n\nA consulta é para você ou para seu filho(a)?", None


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
