"""
Embedding Service
Handles document embeddings and semantic search using OpenAI.
"""
import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.database import get_supabase
import tiktoken

class EmbeddingService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else "sk-placeholder"
        self.model = "text-embedding-3-small"  # 1536 dimensions, cheaper
        self.max_tokens = 500  # Chunk size
        self.supabase = get_supabase()
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto usando OpenAI.
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats (vetor de 1536 dimensões)
        """
        if "placeholder" in self.api_key or not self.api_key:
            # Mock mode: retorna vetor zerado
            return [0.0] * 1536
        
        try:
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.embeddings.create(
                model=self.model,
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            print(f"[Embedding Error] generate_embedding: {e}")
            return [0.0] * 1536
    
    def chunk_text(self, text: str, max_tokens: int = 500) -> List[str]:
        """
        Divide texto em chunks menores para embeddings.
        
        Args:
            text: Texto completo
            max_tokens: Máximo de tokens por chunk
            
        Returns:
            Lista de chunks de texto
        """
        try:
            encoding = tiktoken.encoding_for_model("gpt-4")
            tokens = encoding.encode(text)
            
            chunks = []
            for i in range(0, len(tokens), max_tokens):
                chunk_tokens = tokens[i:i + max_tokens]
                chunk_text = encoding.decode(chunk_tokens)
                chunks.append(chunk_text)
            
            return chunks
        except Exception as e:
            print(f"[Embedding Error] chunk_text: {e}")
            # Fallback: dividir por caracteres
            chunk_size = max_tokens * 4  # ~4 chars per token
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    async def embed_document(
        self,
        documento_id: str,
        texto: str,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Processa e armazena embeddings de um documento.
        
        Args:
            documento_id: UUID do documento
            texto: Conteúdo completo do documento
            metadata: Metadados adicionais
            
        Returns:
            Número de chunks criados
        """
        try:
            # Dividir em chunks
            chunks = self.chunk_text(texto, self.max_tokens)
            
            # Gerar embeddings para cada chunk
            for idx, chunk in enumerate(chunks):
                embedding = await self.generate_embedding(chunk)
                
                # Salvar no banco
                self.supabase.table("embeddings_conhecimento").insert({
                    "documento_id": documento_id,
                    "chunk_index": idx,
                    "chunk_text": chunk,
                    "embedding": embedding,
                    "metadata": metadata or {}
                }).execute()
            
            print(f"[Embedding] Documento {documento_id}: {len(chunks)} chunks processados")
            return len(chunks)
        except Exception as e:
            print(f"[Embedding Error] embed_document: {e}")
            return 0
    
    async def search_documents(
        self,
        query: str,
        clinica_id: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Busca semântica em documentos usando embeddings.
        
        Args:
            query: Pergunta do usuário
            clinica_id: UUID da clínica
            limit: Número máximo de resultados
            
        Returns:
            Lista de chunks relevantes com metadados
        """
        try:
            # Gerar embedding da query
            query_embedding = await self.generate_embedding(query)
            
            # Buscar documentos similares usando função SQL
            # Nota: Supabase Python client não suporta diretamente funções customizadas
            # Vamos usar RPC para chamar a função buscar_documentos_similares
            
            response = self.supabase.rpc(
                "buscar_documentos_similares",
                {
                    "p_embedding": query_embedding,
                    "p_clinica_id": clinica_id,
                    "p_limit": limit
                }
            ).execute()
            
            results = []
            for row in response.data:
                results.append({
                    "documento_id": row["documento_id"],
                    "titulo": row["titulo"],
                    "chunk_text": row["chunk_text"],
                    "similarity": row["similarity"]
                })
            
            return results
        except Exception as e:
            print(f"[Embedding Error] search_documents: {e}")
            return []
    
    async def get_relevant_context(
        self,
        query: str,
        clinica_id: str,
        max_chunks: int = 3
    ) -> str:
        """
        Retorna contexto formatado para incluir no prompt da IA.
        
        Args:
            query: Pergunta do usuário
            clinica_id: UUID da clínica
            max_chunks: Número máximo de chunks
            
        Returns:
            String formatada com contexto relevante
        """
        results = await self.search_documents(query, clinica_id, max_chunks)
        
        if not results:
            return "Nenhum documento relevante encontrado."
        
        context_parts = []
        for idx, result in enumerate(results, 1):
            context_parts.append(
                f"[Documento {idx}: {result['titulo']}]\n{result['chunk_text']}\n"
            )
        
        return "\n".join(context_parts)

# Singleton
embedding_service = EmbeddingService()
