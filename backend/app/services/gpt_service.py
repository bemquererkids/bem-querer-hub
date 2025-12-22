"""
OpenAI GPT Service
Handles AI interaction with Function Calling for Clinicorp Integration.
"""
import openai
import json
from typing import List, Dict, Any
from app.core.config import settings
from app.services.clinicorp_service import ClinicorpClient
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
        context_data: str = ""
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
            }
        ]

        # 2. System Prompt
        system_prompt = f"""
        Você é {persona_name}, a recepcionista virtual da Bem-Querer Odontologia.
        Hoje é: {date.today().strftime('%Y-%m-%d')}.
        
        SEU OBJETIVO:
        Agendar consultas e tirar dúvidas.
        
        FERRAMENTAS:
        Use a função 'consultar_agenda' sempre que o cliente perguntar por horários.
        
        DIRETRIZES:
        - Seja breve e simpática (estilo WhatsApp).
        - Nunca invente horários. Consulte a ferramenta.
        - Se a ferramenta retornar vazio, diga que não há vagas e ofereça outro dia.
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
                    
                    if function_name == "consultar_agenda":
                        target_date = function_args.get("data")
                        print(f"🤖 IA solicitou agenda para: {target_date}")
                        
                        # Executa a busca REAL no Clinicorp
                        slots = await self.clinicorp.check_availability(target_date)
                        
                        # Formata resposta para a IA entender
                        if not slots:
                            tool_response = "Não há horários disponíveis nesta data."
                        else:
                            # Simplifica o JSON para economizar tokens
                            available_times = [s.get('time') for s in slots]
                            tool_response = f"Horários livres: {', '.join(available_times)}"

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