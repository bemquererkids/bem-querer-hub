
"""
GPT Service (OpenAI)
Handles all interactions with OpenAI GPT-4/Turbo for chat processing
"""
from openai import AsyncOpenAI
from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging
import os
import json
from datetime import datetime
import asyncio

# Optional Clinicorp Import
try:
    from app.services.clinicorp_service import ClinicorpClient
    HAS_CLINICORP = True
except ImportError:
    HAS_CLINICORP = False

logger = logging.getLogger(__name__)

class GPTService:
    """Service for interacting with OpenAI GPT"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        # 1. Try Config/Env
        api_key = settings.OPENAI_API_KEY
        
        # 2. Try JSON Persistence (if configured via UI)
        if not api_key or "placeholder" in api_key:
            api_key = self._load_key_from_json()
            
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview" 

        # --- Base System Prompt ---
        # Note: We inject current date dynamically in process_message
        self.system_prompt_template = """
Você é a Carol, assistente virtual da Bem-Querer Odontologia.

## Sua Persona:
- Tom: Empático, acolhedor e eficiente.
- Público: Mães preocupadas e pacientes ocupados.
- Objetivo: Ajudar com agendamentos e tirar dúvidas.

## Ferramentas (Tools):
- Use `check_availability` para consultar horários.
- Use `list_professionals` SEMPRE que perguntarem por dentistas, especialistas ou profissionais.
- **REGRA CRÍTICA**: NUNCA INVENTE NOMES. Se você não usar a ferramenta, diga que não sabe.
- Converta datas relativas para AAAA-MM-DD.
- **ATENÇÃO À DATA**: Se o usuário pedir um dia/mês que já passou neste ano, assuma que ele se refere ao ano que vem (ex: se hoje é 25/12/2025 e pedem 05/01, é 2026).

## Fluxo Conversacional para Agendamentos:

### 1. SEMPRE Investigar Preferências PRIMEIRO:
- **OBRIGATÓRIO**: Se o usuário pedir "horário" sem especificar período, você DEVE perguntar: "Você prefere pela manhã, tarde ou noite?"
- NÃO busque horários antes de saber a preferência
- Se mencionar profissional específico, confirme antes de buscar

### 2. Ao Apresentar Horários Disponíveis:
- **REGRA CRÍTICA**: Ofereça APENAS 2 sugestões, NUNCA mais
- Escolha horários espaçados dentro do período solicitado
- Formato: "Tenho disponível às 9:00 com Dra. Vanessa ou às 11:00 com Dra. Katia"
- **PROIBIDO**: Listar 3, 4, 5 ou mais opções

### 3. Se NÃO houver 2 opções no mesmo dia:
- Busque o PRÓXIMO dia disponível no MESMO período (manhã/tarde/noite)
- Combine dias: "Tenho às 10:00 hoje com Dra. Katia, ou amanhã às 9:00 com Dra. Vanessa"

### 4. Definição de Períodos:
- **Manhã**: 08:00 às 11:59
- **Tarde**: 12:00 às 17:59
- **Noite**: 18:00 às 19:00 (último horário)

### 5. Quando o Profissional NÃO atende no dia solicitado:
- Informe educadamente: "A Dra. [Nome] não atende às [dia da semana]. Ela atende às [dias que atende]."
- Ofereça alternativa: "Posso verificar horários com ela nesses dias, ou prefere outro profissional?"

## Data Atual:
{current_date}
"""

    def _load_key_from_json(self) -> Optional[str]:
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "clinic_integrations.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    return data.get("openai", {}).get("api_key")
        except: pass
        return None

    def _get_tools_schema(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_availability",
                    "description": "Verifica horários disponíveis na agenda para uma data específica.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Data no formato YYYY-MM-DD",
                            },
                            "professional_name": {
                                "type": "string",
                                "description": "Nome do profissional (opcional) para filtrar a agenda.",
                            }
                        },
                        "required": ["date"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_professionals",
                    "description": "OBRIGATÓRIO: Busca a lista REAL de profissionais da clínica. Use antes de citar qualquer nome.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                }
            }
        ] if HAS_CLINICORP else None

    async def _execute_tool(self, tool_name: str, tool_args: dict):
        if tool_name == "check_availability":
            date_str = tool_args.get("date")
            prof_name_query = tool_args.get("professional_name")
            
            logger.info(f"Tool Execution: check_availability({date_str}, {prof_name_query})")
            
            try:
                c_creds = self._load_clinicorp_creds()
                if not c_creds:
                    return "Erro: Integração Clinicorp não configurada."
                
                cl_client = ClinicorpClient(clinic_id="gpt_tool", integration_config=c_creds)
                
                # Resolve Professional ID if name provided
                prof_id = None
                if prof_name_query:
                    all_profs = await cl_client.get_professionals()
                    
                    # Clean query logic
                    msg_clean = prof_name_query.lower()
                    for prefix in ["dr.", "dra.", "dr ", "dra ", "doutor ", "doutora "]:
                        msg_clean = msg_clean.replace(prefix, "")
                    msg_clean = msg_clean.strip()
                    
                    # Match logic
                    params = msg_clean.split() # ["vanessa", "battistini"] or just ["vanessa"]
                    
                    for p in all_profs:
                        p_name_lower = p.get("name", "").lower()
                        # Checks if ALL parts of the query are in the professional's name
                        # e.g. "Vanessa" in "Vanessa Battistini" -> True
                        # e.g. "Vanessa Silva" in "Vanessa Battistini" -> False
                        if all(part in p_name_lower for part in params):
                            prof_id = str(p["id"])
                            break
                            
                    if not prof_id:
                        # Fallback: Try to list available names to help user
                        avail_names = ", ".join([p["name"] for p in all_profs[:3]])
                        return f"Não encontrei nenhum profissional com o nome '{prof_name_query}'. Tente usar apenas o primeiro nome (Ex: {avail_names}...)."

                # Call Clinicorp
                slots = await cl_client.check_availability(date_str, professional_id=prof_id)
                
                # --- ENRICH SLOTS WITH PROFESSIONAL NAMES ---
                # The API returns ProfessionalId but not ProfessionalName
                # We need to fetch professionals and create a lookup map
                prof_map = {}
                try:
                    all_profs = await cl_client.get_professionals()
                    prof_map = {str(p["id"]): p.get("name", "Profissional") for p in all_profs}
                except Exception as prof_err:
                    logger.warning(f"Failed to fetch professionals for name enrichment: {prof_err}")
                
                # FILE LOGGING PROTOCOL
                try:
                    with open("debug_ai_usage.log", "a") as f:
                        f.write(f"\n[{datetime.now()}] Tool: check_availability\n")
                        f.write(f"DateStr Asked: {date_str}\n")
                        f.write(f"Prof Name: {prof_name_query} -> ID: {prof_id}\n")
                        f.write(f"Slots Found: {len(slots)}\n")
                        f.write(f"Raw Slots: {json.dumps(slots)}\n")
                except: pass
                
                logger.info(f"DEBUG: Slots found for {prof_name_query} (ID {prof_id}): {slots}")
                
                if slots:
                    # Format slots for AI digestion WITH professional names
                    formatted_slots = []
                    for s in slots:
                        time_range = f"{s['From']} às {s['To']}"
                        prof_id_in_slot = str(s.get('ProfessionalId', ''))
                        prof_name_in_slot = prof_map.get(prof_id_in_slot, "Profissional")
                        formatted_slots.append(f"{time_range} com {prof_name_in_slot}")
                    
                    return f"Horários Disponíveis em {date_str}: {', '.join(formatted_slots)}"
                else:
                    return f"Sem horários livres para {date_str} {'com '+prof_name_query if prof_id else ''}. (A resposta da API retornou lista vazia)."
            except Exception as e:
                return f"Erro ao consultar Clinicorp: {str(e)}"
        
        elif tool_name == "list_professionals":
            logger.info("Tool Execution: list_professionals()")
            try:
                c_creds = self._load_clinicorp_creds()
                if not c_creds:
                    return "Erro: Integração incompleta."
                
                cl_client = ClinicorpClient(clinic_id="gpt_tool", integration_config=c_creds)
                profs = await cl_client.get_professionals()
                
                # Format for GPT
                # Typically returns list of dicts. We want concise info.
                if profs:
                    summary = [f"{p.get('name', 'Sem Nome')} (ID: {p.get('id')})" for p in profs]
                    return f"Profissionais Disponíveis: {', '.join(summary)}"
                return "Nenhum profissional encontrado."
            except Exception as e:
                return f"Erro ao listar profissionais: {str(e)}"

        return "Ferramenta desconhecida."

    async def process_message(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user message with Tool Calling loop
        """
        try:
            # 1. Prepare Messages
            current_date_str = datetime.now().strftime("%Y-%m-%d (%A)")
            system_prompt = self.system_prompt_template.format(current_date=current_date_str)
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if context:
                messages.append({"role": "system", "content": f"Contexto do Paciente: {context}"})
            
            if chat_history:
                for msg in chat_history[-6:]:
                    role = "user" if msg.get("sender_type") == "user" else "assistant"
                    messages.append({"role": role, "content": msg["content"]})
            
            messages.append({"role": "user", "content": message})

            # 2. First GPT Call (Decide Tool)
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tools_schema(),
                tool_choice="auto",
                temperature=0.7
            )
            
            response_msg = completion.choices[0].message
            tool_calls = response_msg.tool_calls

            # 3. Handle Tool Calls
            if tool_calls:
                messages.append(response_msg) # Extend conversation with assistant's tool-call intent
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute
                    tool_result = await self._execute_tool(function_name, function_args)
                    
                    # Append result
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_result,
                    })
                
                # 4. Second GPT Call (Generate Answer based on Tool Result)
                final_completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7
                )
                response_text = final_completion.choices[0].message.content
                used_tool = True
            else:
                response_text = response_msg.content
                used_tool = False

            return {
                "response": response_text,
                "intent": "chat",
                "used_tool": used_tool
            }

        except Exception as e:
            logger.error(f"GPT Error: {e}")
            return {"response": "Desculpe, tive um problema técnico ao processar sua solicitação."}

    def _load_clinicorp_creds(self):
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "clinic_integrations.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    return data.get("clinicorp", {})
        except: pass
        return None

# Singleton
_gpt_service: Optional[GPTService] = None

def get_gpt_service() -> GPTService:
    global _gpt_service
    if _gpt_service is None:
        _gpt_service = GPTService()
    return _gpt_service
