"""
Knowledge Base Service - Simple RAG Implementation

This service searches through markdown documents in the knowledge_base directory
and provides relevant context to the AI.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Service for searching and retrieving knowledge from markdown documents"""
    
    def __init__(self, knowledge_base_path: str = None):
        """
        Initialize knowledge base service
        
        Args:
            knowledge_base_path: Path to knowledge base directory
        """
        if knowledge_base_path is None:
            # Default to knowledge_base in project root
            # backend/app/services/knowledge_base_service.py -> project_root/knowledge_base
            current_file = Path(__file__)
            backend_dir = current_file.parent.parent.parent  # Go up to backend/
            project_root = backend_dir.parent  # Go up to project root
            knowledge_base_path = project_root / "knowledge_base"
        
        self.kb_path = Path(knowledge_base_path)
        self.documents = {}
        self._load_documents()
    
    def _load_documents(self):
        """Load all markdown documents from knowledge base"""
        if not self.kb_path.exists():
            logger.warning(f"Knowledge base path does not exist: {self.kb_path}")
            return
        
        md_files = list(self.kb_path.glob("*.md"))
        logger.info(f"📚 Loading {len(md_files)} knowledge documents...")
        
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract metadata
                doc_id = md_file.stem
                title = self._extract_title(content)
                category = self._extract_category(doc_id)
                
                self.documents[doc_id] = {
                    'id': doc_id,
                    'title': title,
                    'category': category,
                    'content': content,
                    'file_path': str(md_file)
                }
                
                logger.info(f"   ✅ Loaded: {title}")
                
            except Exception as e:
                logger.error(f"   ❌ Failed to load {md_file.name}: {e}")
        
        logger.info(f"✅ Knowledge base loaded: {len(self.documents)} documents")
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content (first # heading)"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line.replace('# ', '').strip()
        return "Untitled"
    
    def _extract_category(self, doc_id: str) -> str:
        """Extract category from document ID (e.g., '01_especialidades_valores' -> 'especialidades')"""
        parts = doc_id.split('_')
        if len(parts) > 1:
            # Remove number prefix
            return parts[1] if parts[0].isdigit() else parts[0]
        return "general"
    
    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search for relevant documents based on query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant document sections with scores
        """
        query_lower = query.lower()
        results = []
        
        # Keywords to search for
        keywords = self._extract_keywords(query_lower)
        
        for doc_id, doc in self.documents.items():
            content_lower = doc['content'].lower()
            
            # Calculate relevance score
            score = 0
            
            # Exact phrase match (highest score)
            if query_lower in content_lower:
                score += 100
            
            # Keyword matches
            for keyword in keywords:
                if keyword in content_lower:
                    # Count occurrences
                    count = content_lower.count(keyword)
                    score += count * 10
            
            # Category bonus (if query mentions category)
            if doc['category'] in query_lower:
                score += 50
            
            if score > 0:
                # Extract relevant sections
                relevant_sections = self._extract_relevant_sections(
                    doc['content'],
                    keywords,
                    query_lower
                )
                
                results.append({
                    'doc_id': doc_id,
                    'title': doc['title'],
                    'category': doc['category'],
                    'score': score,
                    'sections': relevant_sections
                })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top results
        return results[:max_results]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        # Remove common words
        stop_words = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'dos', 'das',
            'em', 'no', 'na', 'nos', 'nas', 'para', 'com', 'por', 'é', 'são',
            'que', 'qual', 'quais', 'como', 'quando', 'onde', 'quanto', 'quem',
            'me', 'te', 'se', 'lhe', 'nos', 'vos', 'lhes', 'meu', 'minha',
            'seu', 'sua', 'nosso', 'nossa', 'deles', 'delas', 'este', 'esta',
            'esse', 'essa', 'aquele', 'aquela', 'isto', 'isso', 'aquilo',
            'e', 'ou', 'mas', 'porém', 'contudo', 'todavia', 'entretanto'
        }
        
        # Split and clean
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def _extract_relevant_sections(
        self,
        content: str,
        keywords: List[str],
        query: str,
        context_lines: int = 3
    ) -> List[str]:
        """
        Extract relevant sections from document content
        
        Args:
            content: Document content
            keywords: Keywords to search for
            query: Original query
            context_lines: Number of lines of context to include
            
        Returns:
            List of relevant text sections
        """
        lines = content.split('\n')
        relevant_sections = []
        
        # Find lines containing keywords or query
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains query or keywords
            is_relevant = query in line_lower or any(kw in line_lower for kw in keywords)
            
            if is_relevant:
                # Extract section with context
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                section = '\n'.join(lines[start:end])
                
                # Avoid duplicates
                if section not in relevant_sections:
                    relevant_sections.append(section)
        
        # If no specific sections found, return first few paragraphs
        if not relevant_sections:
            # Get first 500 characters
            relevant_sections.append(content[:500] + "...")
        
        return relevant_sections
    
    def get_context_for_query(self, query: str, max_tokens: int = 2000) -> str:
        """
        Get formatted context for AI based on query
        
        Args:
            query: User query
            max_tokens: Maximum tokens for context (approximate)
            
        Returns:
            Formatted context string
        """
        results = self.search(query, max_results=3)
        
        if not results:
            return ""
        
        context_parts = []
        context_parts.append("=== INFORMAÇÕES DA BEM QUERER KIDS ===\n")
        
        for result in results:
            context_parts.append(f"\n📄 Fonte: {result['title']}\n")
            
            for section in result['sections'][:2]:  # Max 2 sections per document
                context_parts.append(section)
                context_parts.append("\n---\n")
        
        context = '\n'.join(context_parts)
        
        # Approximate token count (1 token ≈ 4 characters)
        if len(context) > max_tokens * 4:
            context = context[:max_tokens * 4] + "\n\n[...conteúdo truncado...]"
        
        return context
    
    def reload(self):
        """Reload all documents from disk"""
        logger.info("🔄 Reloading knowledge base...")
        self.documents = {}
        self._load_documents()


# Global instance
_knowledge_base_service = None


def get_knowledge_base_service() -> KnowledgeBaseService:
    """Get singleton instance of knowledge base service"""
    global _knowledge_base_service
    
    if _knowledge_base_service is None:
        _knowledge_base_service = KnowledgeBaseService()
    
    return _knowledge_base_service
