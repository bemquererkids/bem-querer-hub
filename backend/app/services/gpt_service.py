"""
OpenAI GPT Service
Handles AI interaction with Function Calling for Analytics, RAG, and Clinicorp Integration.
"""
import openai
import json
from typing import List, Dict, Any
from app.core.config import settings
from app.services.clinicorp_service import ClinicorpClient
from app.services.analytics_service import analytics_service
from app.services.embedding_service import embedding_service
from datetime import date

class GPTClient:
    def __init__(self):
        # Fetch API Key from Environment
        self.api_key = settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else "sk-placeholder"
        self.model = "gpt-4-turbo-preview" # Better for function calling
        
        # Initialize Clients
        self.clinicorp = ClinicorpClient(clinic_id="bemquerer", integration_config={
            "client_id": "bemquerer",
            "client_secret": "8b6b218c-b536-4db5-97a1-babffc283eec"
        })

    async def generate_response(
        self, 
        message: str, 
        history: List[Dict[str, str]], 
        persona_name: str = "Carol",
        context_data: str = "",
        clinica_id: str = None
    ) -> str:
        """
        Generates a response using OpenAI Chat Completion with Tools.
        """
        if "placeholder" in self.api_key or not self.api_key:
            return f"[MOCK IA] Olá! Sou a {persona_name}. Configure a OPENAI_API_KEY no .env para eu ficar inteligente!"

        client = openai.AsyncOpenAI(api_key=self.api_key)

        # 1. Define Tools (Capabilities)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "consultar_agenda",
                    "description": "Consulta horários disponíveis na agenda para uma data específica.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "string",
                                "description": "Data no formato YYYY-MM-DD (ex: 2025-12-22). Se for hoje, use a data atual.",
                            },
                        },
                        "required": ["data"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "consultar_metricas",
                    "description": "Consulta métricas e estatísticas do CRM (leads, agendamentos, comparecimentos, vendas, conversões).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tipo_metrica": {
                                "type": "string",
                                "enum": ["leads", "agendamentos", "comparecimentos", "vendas", "conversao"],
                                "description": "Tipo de métrica a consultar"
                            },
                            "periodo": {
                                "type": "string",
                                "enum": ["hoje", "semana", "mes", "mes_passado", "ano"],
                                "description": "Período de análise"
                            }
                        },
                        "required": ["tipo_metrica", "periodo"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "consultar_documentos",
                    "description": "Busca informações em documentos da clínica (preços, políticas, procedimentos, FAQ).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pergunta": {
                                "type": "string",
                                "description": "Pergunta sobre preços, políticas ou procedimentos"
                            }
                        },
                        "required": ["pergunta"],
                    },
                },
            }
        ]

        # 2. System Prompt
        system_prompt = f"""
        Você é {persona_name}, a assistente virtual analítica da Bem-Querer Odontologia.
        Hoje é: {date.today().strftime('%Y-%m-%d')}.
        
        SUAS CAPACIDADES:
        1. Consultar métricas do CRM (leads, conversões, vendas, comparecimentos)
        2. Buscar informações em documentos (preços, políticas, procedimentos)
        3. Verificar agenda de horários disponíveis
        
        DIRETRIZES:
        - Use as ferramentas disponíveis para fornecer dados precisos
        - Seja objetiva, analítica e contextual
        - Cite fontes quando usar documentos: [Fonte: Nome do Documento]
        - Forneça insights quando relevante (ex: "acima da média de 75%")
        - Sugira ações práticas quando apropriado
        - Seja breve e simpática (estilo WhatsApp)
        
        EXEMPLOS:
        Pergunta: "Quantos leads tivemos este mês?"
        Ação: Use consultar_metricas(tipo_metrica="leads", periodo="mes")
        
        Pergunta: "Quanto custa um implante?"
        Ação: Use consultar_documentos(pergunta="preço implante dental")
        
        Pergunta: "Tem horário amanhã?"
        Ação: Use consultar_agenda(data="YYYY-MM-DD")
        """

        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]

        try:
            # 3. First Call to LLM
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.5
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # 4. Handle Tool Calls
            if tool_calls:
                messages.append(response_message) # Add AI's intent to history

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    tool_response = ""
                    
                    if function_name == "consultar_agenda":
                        target_date = function_args.get("data")
                        print(f"🤖 IA solicitou agenda para: {target_date}")
                        
                        # Executa a busca REAL no Clinicorp
                        slots = await self.clinicorp.check_availability(target_date)
                        
                        # Formata resposta para a IA entender
                        if not slots:
                            tool_response = "Não há horários disponíveis nesta data."
                        else:
                            available_times = [s.get('time') for s in slots]
                            tool_response = f"Horários livres: {', '.join(available_times)}"
                    
                    elif function_name == "consultar_metricas":
                        tipo = function_args.get("tipo_metrica")
                        periodo = function_args.get("periodo")
                        print(f"🤖 IA solicitou métricas: {tipo} ({periodo})")
                        
                        # Executa query analítica
                        if not clinica_id:
                            tool_response = "Erro: clinica_id não fornecido"
                        else:
                            result = await analytics_service.get_metric(tipo, periodo, clinica_id)
                            tool_response = json.dumps(result, ensure_ascii=False)
                    
                    elif function_name == "consultar_documentos":
                        pergunta = function_args.get("pergunta")
                        print(f"🤖 IA solicitou documentos: {pergunta}")
                        
                        # Busca semântica (RAG)
                        if not clinica_id:
                            tool_response = "Erro: clinica_id não fornecido"
                        else:
                            results = await embedding_service.search_documents(pergunta, clinica_id, limit=3)
                            
                            if not results:
                                tool_response = "Nenhum documento relevante encontrado na base de conhecimento."
                            else:
                                # Formatar resultados
                                formatted = []
                                for r in results:
                                    formatted.append(f"[{r['titulo']}]: {r['chunk_text']}")
                                tool_response = "\n\n".join(formatted)

                    # Add Tool Response to History
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_response,
                    })

                # 5. Second Call (Final Response)
                final_response = await client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                return final_response.choices[0].message.content
            
            return response_message.content

        except Exception as e:
            print(f"[GPT Error] {e}")
            return "Desculpe, estou com uma instabilidade técnica. Pode repetir?"

# Singleton
gpt_service = GPTClient()