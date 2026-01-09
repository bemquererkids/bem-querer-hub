"""
UazAPI RAG Service - Knowledge Base Integration

This service manages the integration with UazAPI's native RAG (Retrieval-Augmented Generation) system.
It uploads knowledge base documents and configures the AI agent to use them.
"""

import os
import logging
from typing import List, Dict, Optional
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class UazAPIRAGService:
    """Service for managing UazAPI RAG knowledge base"""
    
    def __init__(self, instance_name: str, token: str, base_url: str = None):
        self.instance_name = instance_name
        self.token = token
        self.base_url = base_url or os.getenv("UAZAPI_BASE_URL", "https://bemquerer.uazapi.com")
        self.headers = {
            "token": self.token,
            "Content-Type": "application/json"
        }
    
    def _get_url(self, endpoint: str) -> str:
        """Build full URL for endpoint"""
        return f"{self.base_url}/{self.instance_name}/{endpoint}"
    
    def upload_knowledge(self, title: str, content: str, category: str = "general") -> Dict:
        """
        Upload a knowledge document to UazAPI RAG system
        
        Args:
            title: Document title
            content: Document content (markdown supported)
            category: Category for organization
            
        Returns:
            Response from API
        """
        try:
            url = self._get_url("agent/knowledge")
            
            payload = {
                "title": title,
                "content": content,
                "category": category,
                "enabled": True
            }
            
            logger.info(f"📚 Uploading knowledge: {title} (category: {category})")
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"✅ Knowledge uploaded successfully: {title}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error uploading knowledge '{title}': {e}")
            raise
    
    def upload_knowledge_from_file(self, file_path: str, category: str = None) -> Dict:
        """
        Upload knowledge from a markdown file
        
        Args:
            file_path: Path to markdown file
            category: Category (if None, extracted from filename)
            
        Returns:
            Response from API
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read file content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from first heading or filename
            title = path.stem.replace('_', ' ').title()
            if content.startswith('# '):
                title = content.split('\n')[0].replace('# ', '').strip()
            
            # Use category from filename if not provided
            if category is None:
                # Extract category from filename (e.g., "01_especialidades_valores.md" -> "especialidades")
                parts = path.stem.split('_')
                category = parts[1] if len(parts) > 1 else "general"
            
            return self.upload_knowledge(title, content, category)
            
        except Exception as e:
            logger.error(f"❌ Error uploading file '{file_path}': {e}")
            raise
    
    def upload_knowledge_base_directory(self, directory_path: str) -> List[Dict]:
        """
        Upload all markdown files from a directory
        
        Args:
            directory_path: Path to directory containing markdown files
            
        Returns:
            List of responses from API
        """
        try:
            directory = Path(directory_path)
            
            if not directory.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            # Find all markdown files
            md_files = sorted(directory.glob("*.md"))
            
            if not md_files:
                logger.warning(f"⚠️ No markdown files found in {directory_path}")
                return []
            
            logger.info(f"📂 Found {len(md_files)} knowledge files to upload")
            
            results = []
            for md_file in md_files:
                try:
                    result = self.upload_knowledge_from_file(str(md_file))
                    results.append(result)
                except Exception as e:
                    logger.error(f"❌ Failed to upload {md_file.name}: {e}")
                    continue
            
            logger.info(f"✅ Successfully uploaded {len(results)}/{len(md_files)} files")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error uploading directory '{directory_path}': {e}")
            raise
    
    def list_knowledge(self) -> List[Dict]:
        """
        List all knowledge documents
        
        Returns:
            List of knowledge documents
        """
        try:
            url = self._get_url("agent/knowledge")
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            knowledge_list = response.json()
            logger.info(f"📚 Found {len(knowledge_list)} knowledge documents")
            
            return knowledge_list
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error listing knowledge: {e}")
            raise
    
    def delete_knowledge(self, knowledge_id: str) -> Dict:
        """
        Delete a knowledge document
        
        Args:
            knowledge_id: ID of the knowledge document
            
        Returns:
            Response from API
        """
        try:
            url = self._get_url(f"agent/knowledge/{knowledge_id}")
            
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"🗑️ Knowledge deleted: {knowledge_id}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error deleting knowledge '{knowledge_id}': {e}")
            raise
    
    def configure_ai_agent(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_prompt: str = None
    ) -> Dict:
        """
        Configure AI agent settings
        
        Args:
            provider: AI provider (openai, anthropic, google, deepseek)
            model: Model name
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            system_prompt: Custom system prompt
            
        Returns:
            Response from API
        """
        try:
            url = self._get_url("agent/config")
            
            default_prompt = """Você é Carol, a assistente virtual da Bem Querer Kids, uma clínica pediátrica especializada.

PERSONALIDADE:
- Seja empática, acolhedora e profissional
- Use linguagem clara e acessível
- Demonstre cuidado genuíno com as crianças
- Seja paciente e atenciosa com os pais

DIRETRIZES:
1. NUNCA dê diagnósticos médicos - apenas profissionais podem fazer isso
2. SEMPRE consulte a base de conhecimento antes de responder
3. Se não souber algo, seja honesta e ofereça transferir para atendente
4. Priorize agendamentos e facilite o processo
5. Confirme informações importantes (data, horário, nome)

RESPOSTAS:
- Seja objetiva mas calorosa
- Use emojis com moderação (🎈, 💙, 😊)
- Ofereça opções claras quando possível
- Finalize sempre perguntando se pode ajudar em mais algo

Lembre-se: Você representa a Bem Querer Kids. Cada interação é uma oportunidade de demonstrar nosso cuidado e profissionalismo."""

            payload = {
                "provider": provider,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "system_prompt": system_prompt or default_prompt,
                "use_knowledge_base": True,  # Enable RAG
                "knowledge_search_threshold": 0.7  # Similarity threshold
            }
            
            logger.info(f"🤖 Configuring AI agent: {provider}/{model}")
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"✅ AI agent configured successfully")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error configuring AI agent: {e}")
            raise
    
    def test_rag_query(self, query: str) -> Dict:
        """
        Test a query against the RAG system
        
        Args:
            query: Test question
            
        Returns:
            AI response with knowledge sources
        """
        try:
            url = self._get_url("agent/test")
            
            payload = {
                "query": query,
                "include_sources": True  # Show which documents were used
            }
            
            logger.info(f"🧪 Testing RAG query: {query}")
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"✅ RAG response generated")
            if result.get('sources'):
                logger.info(f"📚 Used {len(result['sources'])} knowledge sources")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error testing RAG query: {e}")
            raise


def get_rag_service() -> UazAPIRAGService:
    """
    Get RAG service instance using environment variables
    """
    instance_name = os.getenv("UAZAPI_INSTANCE_NAME")
    token = os.getenv("UAZAPI_TOKEN")
    base_url = os.getenv("UAZAPI_BASE_URL")
    
    if not instance_name or not token:
        raise ValueError("UAZAPI_INSTANCE_NAME and UAZAPI_TOKEN must be set")
    
    return UazAPIRAGService(instance_name, token, base_url)


def get_rag_service_for_clinic(clinic_id: str) -> UazAPIRAGService:
    """
    Get RAG service instance for a specific clinic
    
    Args:
        clinic_id: Clinic UUID
        
    Returns:
        UazAPIRAGService instance
    """
    from app.core.database import get_supabase
    
    try:
        supabase = get_supabase()
        
        # Get UazAPI credentials for clinic
        result = supabase.table('clinic_integrations') \
            .select('instance_name, token, base_url') \
            .eq('clinica_id', clinic_id) \
            .eq('type', 'uazapi') \
            .eq('is_active', True) \
            .execute()
        
        if not result.data:
            raise ValueError(f"No active UazAPI integration found for clinic {clinic_id}")
        
        config = result.data[0]
        
        return UazAPIRAGService(
            instance_name=config['instance_name'],
            token=config['token'],
            base_url=config.get('base_url')
        )
        
    except Exception as e:
        logger.error(f"Error getting RAG service for clinic {clinic_id}: {e}")
        raise
