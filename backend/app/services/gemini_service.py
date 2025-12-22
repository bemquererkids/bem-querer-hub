"""
Gemini AI Service
Handles all interactions with Google Gemini 2.0 for chat processing
"""
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini client"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # System prompt baseado no GEMINI.MD
        self.system_prompt = """
Você é a Carol, assistente virtual da Bem-Querer Odontologia.

## Sua Persona:
- Tom: Empático, acolhedor e eficiente
- Público: Mães preocupadas e pacientes ocupados
- Objetivo: Ajudar com agendamentos e tirar dúvidas sobre tratamentos odontológicos

## Regras Importantes:
1. NUNCA faça diagnósticos médicos ou prescreva tratamentos
2. NUNCA invente informações sobre disponibilidade de agenda
3. Se não souber algo, seja honesto e ofereça transferir para um humano
4. Mantenha respostas curtas e objetivas (máximo 2-3 frases)
5. Use linguagem natural e amigável, evite jargões técnicos

## Capacidades:
- Identificar intenções: Emergência, Agendamento, Dúvida, Reclamação
- Extrair informações: Nome da mãe vs. Nome do filho
- Classificar urgência: Baixa, Normal, Alta, Urgente

## Formato de Resposta:
Sempre retorne um JSON com:
{
    "response": "sua resposta em texto",
    "intent": "booking|emergency|question|complaint",
    "urgency": "low|normal|high|urgent",
    "extracted_data": {
        "patient_name": "nome do paciente",
        "guardian_name": "nome do responsável",
        "phone": "telefone se mencionado"
    },
    "needs_human": false
}
"""
    
    async def process_message(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate AI response
        
        Args:
            message: User's message text
            chat_history: Previous messages in the conversation
            context: Additional context (patient info, clinic info, etc.)
        
        Returns:
            Dict with response, intent, urgency, and extracted data
        """
        try:
            # Build conversation history
            conversation = []
            
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages for context
                    role = "user" if msg["sender_type"] == "user" else "model"
                    conversation.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })
            
            # Add current message
            conversation.append({
                "role": "user",
                "parts": [message]
            })
            
            # Add context if available
            context_str = ""
            if context:
                context_str = f"\n\nContexto adicional: {context}"
            
            # Generate response
            chat = self.model.start_chat(history=conversation[:-1])
            response = chat.send_message(
                self.system_prompt + context_str + "\n\nMensagem do usuário: " + message
            )
            
            # Parse response (expecting JSON)
            try:
                import json
                result = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback if AI doesn't return JSON
                logger.warning("AI response is not valid JSON, using fallback")
                result = {
                    "response": response.text,
                    "intent": "question",
                    "urgency": "normal",
                    "extracted_data": {},
                    "needs_human": False
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing message with Gemini: {str(e)}")
            return {
                "response": "Desculpe, estou com dificuldades técnicas. Vou transferir você para um atendente humano.",
                "intent": "question",
                "urgency": "normal",
                "extracted_data": {},
                "needs_human": True,
                "error": str(e)
            }
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text (for RAG/semantic search)
        
        Args:
            text: Text to generate embedding for
        
        Returns:
            List of floats representing the embedding vector
        """
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []
    
    async def classify_intent(self, message: str) -> str:
        """
        Quick intent classification without full conversation
        
        Args:
            message: User message
        
        Returns:
            Intent: booking, emergency, question, complaint
        """
        try:
            prompt = f"""
Classifique a intenção desta mensagem em uma palavra:
- booking (agendamento)
- emergency (emergência/dor)
- question (dúvida)
- complaint (reclamação)

Mensagem: "{message}"

Responda apenas com a palavra da classificação.
"""
            response = self.model.generate_content(prompt)
            intent = response.text.strip().lower()
            
            if intent not in ["booking", "emergency", "question", "complaint"]:
                return "question"  # Default
            
            return intent
            
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return "question"


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
