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
        # Considera primeira se não tem nenhum dado coletado ainda
        is_first_message = not collected or len(collected) == 0
        
        prompt = f"""
Você é a Carol, da equipe Bem-Querer Odontologia.

HORÁRIO ATUAL: {greeting}

DADOS JÁ COLETADOS:
{json.dumps(collected, indent=2, ensure_ascii=False)}

MENSAGEM DO PACIENTE: "{message}"

---

{"PRIMEIRA INTERAÇÃO - APRESENTAÇÃO:" if is_first_message else "CONTINUAÇÃO - COLETAR DADOS:"}

{'''Responda EXATAMENTE assim:
"{greeting}! 😊 Um prazer, sou a Carol, da equipe Bem-Querer Odontologia. 
Será um prazer ajudá-lo(a)!

A consulta é para você ou para seu filho(a)?"

E extraia: tipo=null (ainda não sabemos)
''' if is_first_message else f'''
ANÁLISE DA MENSAGEM:
Extraia informações da mensagem "{message}":

PALAVRAS-CHAVE PARA TIPO:
- "filho", "filha", "criança", "bebê", "meu filho", "minha filha" → tipo=kids
- "para mim", "eu", "meu dente", "adulto" → tipo=adulto

DADOS NECESSÁRIOS (pergunte se não tiver):
1. tipo: É para criança (kids) ou adulto?
2. nome: Nome do paciente
3. idade: Idade (se criança)
4. dor_urgencia: Está sentindo dor ou incômodo? (sim/não)
5. motivo: Motivo da consulta

ORDEM DAS PERGUNTAS:
1. Se não tem tipo: "A consulta é para você ou para seu filho(a)?"
2. Se não tem nome: "Qual o nome {{"dela" if "filha" in message.lower() else "dele" if "filho" in message.lower() else "do paciente"}}?"
3. Se não tem idade (e é kids): "Qual a idade {{"dela" if "filha" in message.lower() else "dele"}}?"
4. Se não tem dor_urgencia: "Está sentindo alguma dor ou incômodo no momento?"
5. Se não tem motivo: "Qual o motivo da consulta?"

IMPORTANTE:
- Faça APENAS UMA pergunta por vez
- Se a mensagem responde algo, EXTRAIA e vá para próxima pergunta
- NÃO repita a apresentação
- Seja natural e amigável
'''}

QUANDO TRANSFERIR:
- Se tem: tipo + nome + motivo + dor_urgencia → ready_to_transfer=true
- Se tipo=kids → next_agent="kids"
- Se tipo=adulto → next_agent="adulto"

RETORNE JSON (sem markdown):
{{
  "response": "sua resposta ao paciente",
  "extracted_data": {{
    "tipo": "kids|adulto|null",
    "nome": "nome ou null",
    "idade": "número ou null",
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
            
            logger.info(f"Triagem result: {result}")
            
            # Salvar dados extraídos
            for key, value in result["extracted_data"].items():
                if value and value != "null":
                    state.collect_data(key, value)
                    logger.info(f"Extracted {key} = {value}")
            
            # Atualizar tipo de paciente se descobriu
            if result["extracted_data"].get("tipo") and result["extracted_data"]["tipo"] != "null":
                tipo = result["extracted_data"]["tipo"]
                state.set_patient_type(PatientType.KIDS if tipo == "kids" else PatientType.ADULTO)
            
            # Determinar próximo agente
            if result.get("ready_to_transfer") and result.get("next_agent"):
                next_agent = AgentType(result["next_agent"])
            else:
                next_agent = None  # Continua na triagem
            
            return result["response"], next_agent
            
        except Exception as e:
            logger.error(f"Triagem error: {e}", exc_info=True)
            # Fallback com apresentação
            if not collected or len(collected) == 0:
                return f"{greeting}! 😊 Um prazer, sou a Carol, da equipe Bem-Querer Odontologia.\n\nA consulta é para você ou para seu filho(a)?", None
            else:
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
