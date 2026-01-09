"""
Script to initialize UazAPI RAG Knowledge Base

This script uploads all knowledge base documents to UazAPI and configures the AI agent.
Run this once to set up the RAG system.

Usage:
    python setup_rag.py
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.uazapi_rag_service import get_rag_service
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def main():
    """Main setup function"""
    
    print("=" * 60)
    print("🚀 UazAPI RAG Knowledge Base Setup")
    print("=" * 60)
    print()
    
    try:
        # Get RAG service
        logger.info("📡 Connecting to UazAPI...")
        rag_service = get_rag_service()
        logger.info("✅ Connected successfully!")
        print()
        
        # Path to knowledge base directory
        kb_path = Path(__file__).parent / "knowledge_base"
        
        if not kb_path.exists():
            logger.error(f"❌ Knowledge base directory not found: {kb_path}")
            return
        
        # List existing knowledge (optional - to see what's already there)
        print("📚 Checking existing knowledge base...")
        try:
            existing = rag_service.list_knowledge()
            if existing:
                print(f"   Found {len(existing)} existing documents")
                print()
                
                # Ask if user wants to delete existing
                response = input("   Delete existing documents? (y/N): ").strip().lower()
                if response == 'y':
                    print("   🗑️ Deleting existing documents...")
                    for doc in existing:
                        try:
                            rag_service.delete_knowledge(doc['id'])
                            print(f"      ✅ Deleted: {doc.get('title', doc['id'])}")
                        except Exception as e:
                            print(f"      ❌ Failed to delete {doc['id']}: {e}")
                    print()
            else:
                print("   No existing documents found")
                print()
        except Exception as e:
            logger.warning(f"⚠️ Could not list existing knowledge: {e}")
            print()
        
        # Upload knowledge base
        print("📤 Uploading knowledge base documents...")
        print()
        
        results = rag_service.upload_knowledge_base_directory(str(kb_path))
        
        print()
        print("=" * 60)
        print(f"✅ Upload complete! {len(results)} documents uploaded")
        print("=" * 60)
        print()
        
        # Show uploaded documents
        if results:
            print("📋 Uploaded documents:")
            for i, result in enumerate(results, 1):
                title = result.get('title', 'Unknown')
                category = result.get('category', 'general')
                print(f"   {i}. {title} (category: {category})")
            print()
        
        # Configure AI agent
        print("🤖 Configuring AI agent...")
        print()
        
        config_result = rag_service.configure_ai_agent(
            provider="openai",
            model="gpt-4",
            temperature=0.7,
            max_tokens=500
        )
        
        print("✅ AI agent configured successfully!")
        print()
        
        # Test RAG system
        print("=" * 60)
        print("🧪 Testing RAG System")
        print("=" * 60)
        print()
        
        test_queries = [
            "Quanto custa uma consulta de neuropediatria?",
            "Preciso fazer jejum para ultrassom?",
            "Quais convênios vocês aceitam?",
            "Como faço para cancelar uma consulta?"
        ]
        
        for query in test_queries:
            print(f"❓ Query: {query}")
            try:
                response = rag_service.test_rag_query(query)
                answer = response.get('answer', 'No answer')
                sources = response.get('sources', [])
                
                print(f"💬 Answer: {answer[:200]}...")
                if sources:
                    print(f"📚 Sources: {', '.join([s.get('title', 'Unknown') for s in sources])}")
                print()
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
        
        print("=" * 60)
        print("🎉 RAG Setup Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Test the AI in production")
        print("2. Monitor responses for accuracy")
        print("3. Add more documents as needed")
        print()
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}", exc_info=True)
        print()
        print("=" * 60)
        print("❌ Setup Failed!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Please check:")
        print("1. UAZAPI_INSTANCE_NAME is set in .env")
        print("2. UAZAPI_TOKEN is set in .env")
        print("3. UazAPI instance is active and connected")
        print()


if __name__ == "__main__":
    main()
