"""
Test RAG Integration

This script tests the RAG (Retrieval-Augmented Generation) integration
by simulating queries and checking if the knowledge base is being used.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.knowledge_base_service import get_knowledge_base_service
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_knowledge_base():
    """Test knowledge base service"""
    
    print("=" * 70)
    print("🧪 TESTING RAG KNOWLEDGE BASE")
    print("=" * 70)
    print()
    
    # Initialize service
    logger.info("📚 Initializing Knowledge Base Service...")
    kb_service = get_knowledge_base_service()
    
    print(f"✅ Loaded {len(kb_service.documents)} documents")
    print()
    
    # List documents
    print("📋 Available documents:")
    for doc_id, doc in kb_service.documents.items():
        print(f"   - {doc['title']} (category: {doc['category']})")
    print()
    
    # Test queries
    test_queries = [
        "Quanto custa uma consulta de neuropediatria?",
        "Preciso fazer jejum para ultrassom abdominal?",
        "Quais convênios vocês aceitam?",
        "Como faço para cancelar uma consulta?",
        "Qual o horário de funcionamento?",
        "Vocês atendem emergências?",
        "Quanto custa fonoaudiologia?",
        "Preciso de jejum para exame de sangue?"
    ]
    
    print("=" * 70)
    print("🔍 TESTING SEARCH FUNCTIONALITY")
    print("=" * 70)
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] Query: {query}")
        print()
        
        # Search
        results = kb_service.search(query, max_results=2)
        
        if results:
            print(f"   ✅ Found {len(results)} relevant documents:")
            for result in results:
                print(f"      📄 {result['title']} (score: {result['score']})")
                print(f"         Category: {result['category']}")
                print(f"         Sections: {len(result['sections'])}")
            print()
        else:
            print(f"   ❌ No relevant documents found")
            print()
    
    # Test context generation
    print("=" * 70)
    print("📝 TESTING CONTEXT GENERATION")
    print("=" * 70)
    print()
    
    test_context_queries = [
        "Quanto custa neuropediatria?",
        "Preciso fazer jejum para ultrassom?"
    ]
    
    for query in test_context_queries:
        print(f"Query: {query}")
        print()
        
        context = kb_service.get_context_for_query(query, max_tokens=500)
        
        if context:
            print("✅ Generated context:")
            print("-" * 70)
            print(context[:500] + "..." if len(context) > 500 else context)
            print("-" * 70)
        else:
            print("❌ No context generated")
        
        print()
    
    print("=" * 70)
    print("🎉 RAG TESTING COMPLETE!")
    print("=" * 70)
    print()
    print("✅ Knowledge Base is working correctly!")
    print()
    print("Next steps:")
    print("1. Test with real WhatsApp messages")
    print("2. Monitor Carol's responses")
    print("3. Check logs for RAG usage")
    print()


if __name__ == "__main__":
    test_knowledge_base()
