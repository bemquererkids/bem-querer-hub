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
        
        # DEBUG: Log para diagnosticar
        logger.info(f"🔍 Triagem Debug: collected_data = {collected}")
        logger.info(f"🔍 Triagem Debug: agent_history length = {len(state.agent_history)}")
        logger.info(f"🔍 Triagem Debug: message = {message}")
        
        # WORKAROUND IMEDIATO: Se a mensagem contém palavras-chave específicas,
        # significa que NÃO é primeira vez (usuário está respondendo à pergunta)
        message_lower = message.lower()
        
        # Palavras que indicam resposta à pergunta "para você ou seu filho?"
        response_keywords = [
            "filho", "filha", "criança", "bebê", "meu filho", "minha filha",
            "para mim", "eu preciso", "meu dente", "para eu", "pra mim"
        ]
        
        is_responding_to_question = any(keyword in message_lower for keyword in response_keywords)
        
        # SOLUÇÃO: Só mostra saudação se:
        # 1. NÃO tem dados coletados E
        # 2. NÃO está respondendo à pergunta (não tem keywords)
        has_any_data = bool(collected and len(collected) > 0)
        
        logger.info(f"🔍 Triagem Debug: has_any_data = {has_any_data}")
        logger.info(f"🔍 Triagem Debug: is_responding_to_question = {is_responding_to_question}")
        
        # Se NÃO tem dados E NÃO está respondendo, é primeira interação
        if not has_any_data and not is_responding_to_question:
            logger.info("🔍 Triagem: Mostrando saudação (primeira interação)")
            response = f"{greeting}! 😊 Um prazer, sou a Carol, da equipe Bem-Querer Odontologia.\nSerá um prazer ajudá-lo(a)!\n\nA consulta é para você ou para seu filho(a)?"
            return response, None
        
        logger.info("🔍 Triagem: NÃO é primeira interação, processando normalmente")
        
        # 🤖 USAR GPT PARA CONVERSA NATURAL E INVESTIGATIVA
        # Em vez de regras rígidas, usar LLM para ser mais humana
        
        # Construir contexto do que já sabemos
        context_parts = []
        if collected.get("tipo"):
            context_parts.append(f"Tipo de paciente: {collected['tipo']}")
        if collected.get("nome"):
            context_parts.append(f"Nome: {collected['nome']}")
        if collected.get("idade"):
            context_parts.append(f"Idade: {collected['idade']}")
        if collected.get("dor_urgencia"):
            context_parts.append(f"Dor/urgência: {collected['dor_urgencia']}")
        if collected.get("motivo"):
            context_parts.append(f"Motivo: {collected['motivo']}")
        
        context_str = "\n".join(context_parts) if context_parts else "Nenhuma informação coletada ainda"
        
        # Prompt para GPT ser investigativa e acolhedora
        system_prompt = f"""Você é Carol, recepcionista da Bem-Querer Odontologia. Você está fazendo a triagem inicial.

INFORMAÇÕES JÁ COLETADAS:
{context_str}

SUA MISSÃO:
1. Seja ACOLHEDORA e EMPÁTICA (especialmente se for criança ou emergência)
2. Seja INVESTIGATIVA - faça perguntas para entender melhor o problema
3. Colete as informações necessárias de forma NATURAL (não robotizada):
   - Tipo de paciente (criança ou adulto)
   - Nome do paciente
   - Idade (se criança)
   - Se tem dor ou urgência
   - Motivo da consulta (detalhes do problema)

4. Se o paciente já deu informações, NÃO pergunte novamente
5. Se detectar urgência/dor, seja mais empática e rápida
6. Quando tiver TODAS as informações, diga que vai verificar horários

REGRAS:
- Use emojis com moderação (🦷 💙 😊)
- Seja breve mas calorosa
- Se for criança, use linguagem mais lúdica
- Se for urgência, priorize e seja rápida

Responda à mensagem do usuário de forma natural."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            gpt_response = response.choices[0].message.content
            
            # 🎯 EXTRAIR DADOS da resposta do usuário usando GPT
            # Usar GPT para entender o que o usuário disse e extrair informações
            extraction_prompt = f"""Analise esta mensagem do usuário e extraia informações:

Mensagem: "{message}"

Informações já coletadas: {context_str}

Extraia (retorne JSON):
{{
    "tipo": "kids" ou "adulto" ou null,
    "nome": "nome extraído" ou null,
    "idade": "idade" ou null,
    "tem_dor": true ou false ou null,
    "motivo": "descrição do problema" ou null,
    "tem_todas_informacoes": true ou false
}}

Retorne APENAS o JSON, sem explicações."""

            extraction_response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            # Parse JSON
            import json
            try:
                extracted = json.loads(extraction_response.choices[0].message.content)
                
                # Salvar dados extraídos
                if extracted.get("tipo") and not collected.get("tipo"):
                    state.collect_data("tipo", extracted["tipo"])
                    logger.info(f"🎯 GPT extracted tipo: {extracted['tipo']}")
                
                if extracted.get("nome") and not collected.get("nome"):
                    state.collect_data("nome", extracted["nome"])
                    logger.info(f"🎯 GPT extracted nome: {extracted['nome']}")
                
                if extracted.get("idade") and not collected.get("idade"):
                    state.collect_data("idade", extracted["idade"])
                    logger.info(f"🎯 GPT extracted idade: {extracted['idade']}")
                
                if extracted.get("tem_dor") is not None and not collected.get("dor_urgencia"):
                    state.collect_data("dor_urgencia", "sim" if extracted["tem_dor"] else "não")
                    logger.info(f"🎯 GPT extracted dor: {extracted['tem_dor']}")
                
                if extracted.get("motivo") and not collected.get("motivo"):
                    state.collect_data("motivo", extracted["motivo"])
                    logger.info(f"🎯 GPT extracted motivo: {extracted['motivo']}")
                
                # Se tem todas as informações, transicionar para próximo agente
                if extracted.get("tem_todas_informacoes"):
                    tipo = state.collected_data.get("tipo")
                    if tipo == "kids":
                        return gpt_response, AgentType.KIDS
                    else:
                        return gpt_response, AgentType.ADULTO
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse GPT extraction JSON")
            
            # Retornar resposta do GPT
            return gpt_response, None
            
        except Exception as e:
            logger.error(f"❌ GPT error in Triagem: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Não retornar - continuar para lógica de fallback
        
        # 🔧 FALLBACK: Lógica baseada em regras
        logger.info("Using rule-based logic (fallback or supplement)")
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
        
        # Tem tipo, nome (e idade se kids), extrair dor E motivo
        if not collected.get("dor_urgencia"):
            # Detectar se tem dor
            has_pain = any(word in message_lower for word in ["sim", "dor", "doendo", "incômodo", "incomodo", "inchado", "inflamado"])
            no_pain = any(word in message_lower for word in ["não", "nao", "sem dor", "não sinto"])
            
            if has_pain:
                state.collect_data("dor_urgencia", "sim")
                logger.info("Extracted dor_urgencia=sim")
                
                # 🎯 INTELIGENTE: Se a resposta tem mais de 5 palavras, provavelmente já explicou o motivo
                # Exemplo: "está com dor, está inchado o dente da frente"
                if len(message.split()) > 5:
                    # Extrair motivo da própria mensagem
                    state.collect_data("motivo", message.strip())
                    logger.info(f"🎯 Extracted motivo from pain description: {message.strip()}")
                    
                    # Pular pergunta do motivo e ir direto para próximo passo
                    tipo = collected.get("tipo")
                    if tipo == "kids":
                        next_agent = AgentType.KIDS
                    else:
                        next_agent = AgentType.ADULTO
                    
                    return "Entendi! Vou verificar os horários disponíveis. Um momento... 🦷", next_agent
                else:
                    # Resposta curta, perguntar mais detalhes
                    return "Entendi. Pode me contar mais sobre o que está acontecendo?", None
                    
            elif no_pain:
                state.collect_data("dor_urgencia", "não")
                logger.info("Extracted dor_urgencia=não")
                # Perguntar motivo
                return "Qual o motivo da consulta?", None
            else:
                # Não conseguiu detectar, assumir que não tem dor e perguntar motivo
                state.collect_data("dor_urgencia", "não")
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
