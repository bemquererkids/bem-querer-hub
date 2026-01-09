
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

        # Dynamic prompt loading - will be loaded per request based on clinic_id
        self.system_prompt_template = None
        self.context_config = self._load_context_config()
    
    async def _load_ai_config_from_db(self, clinic_id: str) -> str:
        """
        Load AI configuration from database and generate prompt
        Falls back to hardcoded Bem-Querer prompt if not found
        """
        try:
            from app.core.database import get_supabase
            from app.services.ai_config_service import AIConfigService
            
            supabase = get_supabase()
            
            # Try to load from database
            result = supabase.table("ai_configurations") \
                .select("config") \
                .eq("clinic_id", clinic_id) \
                .eq("is_active", True) \
                .single() \
                .execute()
            
            if result.data:
                logger.info(f"Loaded AI config from database for clinic {clinic_id}")
                return AIConfigService.generate_system_prompt(result.data["config"])
            
        except Exception as e:
            logger.warning(f"Failed to load AI config from database: {e}")
        
        # Fallback to Bem-Querer hardcoded prompt
        try:
            from app.services.carol_prompt_bemquerer import get_carol_prompt
            logger.info("Using fallback Bem-Querer prompt")
            return get_carol_prompt()
        except ImportError:
            logger.warning("Carol prompt file not found, using basic prompt")
            return self._get_basic_prompt_template()

    def _load_key_from_json(self) -> Optional[str]:
        # 1. Try Env Var first (Security Best Practice)
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key: return env_key

        # 2. Try JSON file (Legacy/Local)
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "clinic_integrations.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    key = data.get("openai", {}).get("api_key")
                    if key and "OPENAI_API_KEY_HERE" not in key:
                        return key
        except: pass
        return None

    def _load_context_config(self) -> Dict[str, str]:
        # Default fallback
        defaults = {
            "assistant_name": "Carol",
            "clinic_name": "Bem-Querer Odontologia",
            "tone": "Empático, acolhedor e eficiente.",
            "target_audience": "Mães preocupadas e pacientes ocupados."
        }
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "clinic_integrations.json")
            if os.path.exists(path):
                with open(path, "r", encoding='utf-8') as f: # Ensure utf-8
                    data = json.load(f)
                    persona = data.get("ai_persona", {})
                    defaults.update(persona)
        except Exception as e:
            logger.warning(f"Failed to load AI persona config: {e}")
        return defaults

    def _get_basic_prompt_template(self) -> str:
        """Fallback basic prompt if Carol's specialized prompt is not available"""
        return """
Você é Carol, assistente virtual da Bem-Querer Odontologia.
Use as ferramentas disponíveis para ajudar com agendamentos.
Data Atual: {current_date}
"""

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
            },
            {
                "type": "function",
                "function": {
                    "name": "create_appointment",
                    "description": "Agendar uma consulta no sistema Clinicorp (Finalizar Agendamento).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "AAAA-MM-DD"},
                            "time": {"type": "string", "description": "HH:MM (Horário de início)"},
                            "patient_name": {"type": "string", "description": "Nome do paciente"},
                            "patient_phone": {"type": "string", "description": "Telefone do paciente (apenas números)"},
                            "professional_id": {"type": "integer", "description": "ID do profissional (se souber)"},
                            "observation": {"type": "string", "description": "Observação opcional"}
                        },
                        "required": ["date", "time", "patient_name", "patient_phone"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "consult_knowledge_base",
                    "description": "Consulta a Base de Conhecimento da clínica para responder perguntas sobre PREÇOS, ENDEREÇO, CONVÊNIOS, PROCEDIMENTOS e DÚVIDAS GERAIS.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "O tema ou pergunta principal (ex: 'preço clareamento', 'aceita convenio', 'onde fica').",
                            }
                        },
                        "required": ["query"],
                    },
                }
            }
        ] if HAS_CLINICORP else None

    async def _execute_tool(self, tool_name: str, tool_args: dict):
        if tool_name == "create_appointment":
             # New Tool for Booking
             logger.info(f"Tool Execution: create_appointment({tool_args})")
             try:
                 c_creds = self._load_clinicorp_creds()
                 cl_client = ClinicorpClient(clinic_id="gpt_tool", integration_config=c_creds)
                 
                 # Prepare payload
                 # We need patient_id. If not provided, we might need a 'find_patient' tool or 'create_patient' logic.
                 # For now, assuming the AI has context or will ask.
                 # Actually, for MVP, let's assume we might need to Create Patient implicitly or passed in args?
                 # The schema below will ask for name/phone to create if needed?
                 # Let's keep it simple: Map args to create_appointment
                 
                 # Since AI might not have PatientId, we usually need a flow:
                 # 1. Create Patient (or Update) -> Get ID
                 # 2. Book
                 
                 # For this step, I'll implement a 'Smart Booking' that tries to create patient first.
                 patient_data = {
                     "full_name": tool_args.get("patient_name"),
                     "phone": tool_args.get("patient_phone"),
                     "email": tool_args.get("patient_email")
                 }
                 
                 # 1. Create/Get Patient
                 try:
                     logger.info(f"Creating/Finding patient: {patient_data}")
                     patient_id = await cl_client.create_patient(patient_data)
                 except Exception as pe:
                     return f"Erro ao identificar paciente: {pe}"

                 # 2. Book
                 appt_data = {
                     "patient_id": patient_id,
                     "professional_id": tool_args.get("professional_id"),
                     "date": tool_args.get("date"),
                     "start_time": tool_args.get("time"),
                     "end_time": tool_args.get("end_time"), # Agent needs to calculate end time? Or we default to +30m
                     "observation": f"Agendado via IA. Obs: {tool_args.get('observation', '')}"
                 }
                 
                 # Logic to calculate end_time if missing (Default 30 min)
                 if not appt_data["end_time"]:
                      from datetime import datetime, timedelta
                      fmt = "%H:%M"
                      start_dt = datetime.strptime(appt_data["start_time"], fmt)
                      end_dt = start_dt + timedelta(minutes=30) # Default slot
                      appt_data["end_time"] = end_dt.strftime(fmt)
                 
                 appt_id = await cl_client.create_appointment(appt_data)
                 return f"Agendamento Confirmado! ID: {appt_id}. Data: {appt_data['date']} às {appt_data['start_time']}."
                 
             except Exception as e:
                 return f"Falha ao agendar: {str(e)}"

        elif tool_name == "check_availability":
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

        elif tool_name == "consult_knowledge_base":
            query = tool_args.get("query", "").lower()
            logger.info(f"Tool Execution: consult_knowledge_base('{query}')")
            
            try:
                # Load Data
                kb_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge_base.json")
                if not os.path.exists(kb_path):
                     return "Base de conhecimento vazia."
                
                with open(kb_path, "r", encoding="utf-8") as f:
                    kb_data = json.load(f)

                from rapidfuzz import process, fuzz

                # Prepare list of contents and keywords for searching
                candidates = []
                for item in kb_data:
                    # Combine category, keywords and a bit of content for search context
                    search_text = f"{item['category']} {' '.join(item.get('keywords', []))} {item['content'][:50]}"
                    candidates.append((search_text, item))

                # Fuzzy Search
                # Limit=3 returns top 3 matches
                results = process.extract(
                    query, 
                    [c[0] for c in candidates], 
                    scorer=fuzz.WRatio, 
                    limit=3
                )

                # Filter by score (e.g., > 60)
                relevant_items = []
                for match_text, score, index in results:
                    if score > 60:
                        relevant_items.append(candidates[index][1])

                if not relevant_items:
                    return "Não encontrei informações específicas sobre isso na minha base de conhecimento."

                # Format Response
                response_text = "Encontrei as seguintes informações:\n"
                for item in relevant_items:
                    response_text += f"- [{item['category']}] {item['content']}\n"
                
                return response_text

            except Exception as e:
                logger.error(f"Error consulting knowledge base: {e}")
                return f"Erro ao consultar base de conhecimento: {str(e)}"

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
            # 1. Load AI Configuration dynamically from database
            clinic_id = context.get("clinic_id", "00000000-0000-0000-0000-000000000001") if context else "00000000-0000-0000-0000-000000000001"
            system_prompt = await self._load_ai_config_from_db(clinic_id)
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # 🔍 RAG: Search knowledge base for relevant context
            knowledge_context = None
            try:
                from app.services.knowledge_base_service import get_knowledge_base_service
                
                kb_service = get_knowledge_base_service()
                knowledge_context = kb_service.get_context_for_query(message, max_tokens=2000)
                
                if knowledge_context:
                    logger.info(f"📚 RAG: Found relevant knowledge from files")
                else:
                    logger.info(f"📚 RAG: No relevant knowledge found in files")
            except Exception as e:
                logger.warning(f"⚠️ RAG file search failed: {e}")
            
            # 📦 Fallback: Use embedded knowledge if file-based RAG failed
            if not knowledge_context:
                try:
                    from app.services.embedded_knowledge import search_embedded_knowledge
                    knowledge_context = search_embedded_knowledge(message)
                    if knowledge_context:
                        logger.info(f"📦 RAG: Using embedded knowledge (fallback)")
                except Exception as e:
                    logger.warning(f"⚠️ Embedded knowledge failed: {e}")
            
            # Add knowledge context if found (from either source)
            if knowledge_context:
                messages.append({
                    "role": "system",
                    "content": f"{knowledge_context}\n\nUSE AS INFORMAÇÕES ACIMA para responder com precisão. Se a informação estiver nos documentos, cite-a. Se não estiver, seja honesta."
                })
            
            
            if context:
                # Add patient context
                patient_context = {k: v for k, v in context.items() if k != "clinic_id"}
                if patient_context:
                    messages.append({"role": "system", "content": f"Contexto do Paciente: {patient_context}"})
            
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
            import traceback
            # DEBUG: Return error as message to see what happened
            return {"response": f"⚠️ DEBUG ERROR:\\n{str(e)}\\n\\n{traceback.format_exc()}"}

    def _load_clinicorp_creds(self):
        # HARDCODED FALLBACK FOR RELIABILITY
        return {
            "client_id": "bemquerer",
            "client_secret": "8b6b218c-b536-4db5-97a1-babffc283eec"
        }

# Singleton
_gpt_service: Optional[GPTService] = None

def get_gpt_service() -> GPTService:
    global _gpt_service
    if _gpt_service is None:
        _gpt_service = GPTService()
    return _gpt_service
