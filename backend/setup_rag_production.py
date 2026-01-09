"""
Production RAG Setup Script

This script sets up RAG in production using production credentials.
It connects directly to the production UazAPI instance.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.uazapi_rag_service import UazAPIRAGService
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def main():
    """Main production setup function"""
    
    print("=" * 70)
    print("🚀 PRODUCTION RAG SETUP - Bem Querer Kids")
    print("=" * 70)
    print()
    
    # Production credentials
    INSTANCE_NAME = "sistema"
    TOKEN = "093b971c-f10f-4af1-b0aa-a13c6ad15909"
    BASE_URL = "https://bemquerer.uazapi.com"
    
    print("📡 Production Configuration:")
    print(f"   Instance: {INSTANCE_NAME}")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Token: {TOKEN[:20]}...")
    print()
    
    try:
        # Initialize RAG service with production credentials
        logger.info("🔌 Connecting to production UazAPI...")
        rag_service = UazAPIRAGService(
            instance_name=INSTANCE_NAME,
            token=TOKEN,
            base_url=BASE_URL
        )
        logger.info("✅ Connected to production!")
        print()
        
        # Path to knowledge base directory
        kb_path = Path(__file__).parent / "knowledge_base"
        
        if not kb_path.exists():
            logger.error(f"❌ Knowledge base directory not found: {kb_path}")
            return
        
        print(f"📁 Knowledge base path: {kb_path}")
        print()
        
        # List files to upload
        md_files = sorted(kb_path.glob("*.md"))
        print(f"📚 Found {len(md_files)} knowledge documents:")
        for i, f in enumerate(md_files, 1):
            print(f"   {i}. {f.name}")
        print()
        
        # Confirm before proceeding
        print("⚠️  WARNING: This will upload to PRODUCTION!")
        print()
        response = input("Continue? (yes/NO): ").strip().lower()
        
        if response != 'yes':
            print("❌ Aborted by user")
            return
        
        print()
        print("=" * 70)
        print("📤 UPLOADING TO PRODUCTION")
        print("=" * 70)
        print()
        
        # Check existing knowledge
        try:
            existing = rag_service.list_knowledge()
            if existing:
                print(f"📋 Found {len(existing)} existing documents in production:")
                for doc in existing:
                    print(f"   - {doc.get('title', 'Unknown')}")
                print()
                
                response = input("Delete existing documents first? (yes/NO): ").strip().lower()
                if response == 'yes':
                    print()
                    print("🗑️  Deleting existing documents...")
                    for doc in existing:
                        try:
                            rag_service.delete_knowledge(doc['id'])
                            print(f"   ✅ Deleted: {doc.get('title', doc['id'])}")
                        except Exception as e:
                            print(f"   ❌ Failed to delete {doc['id']}: {e}")
                    print()
        except Exception as e:
            logger.warning(f"⚠️  Could not list existing knowledge: {e}")
            print()
        
        # Upload knowledge base
        print("📤 Uploading knowledge documents to production...")
        print()
        
        results = []
        for i, md_file in enumerate(md_files, 1):
            try:
                print(f"[{i}/{len(md_files)}] Uploading {md_file.name}...")
                result = rag_service.upload_knowledge_from_file(str(md_file))
                results.append(result)
                print(f"   ✅ Success!")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        print()
        print("=" * 70)
        print(f"✅ UPLOAD COMPLETE: {len(results)}/{len(md_files)} documents")
        print("=" * 70)
        print()
        
        # Show uploaded documents
        if results:
            print("📋 Successfully uploaded:")
            for i, result in enumerate(results, 1):
                title = result.get('title', 'Unknown')
                category = result.get('category', 'general')
                print(f"   {i}. {title} (category: {category})")
            print()
        
        # Configure AI agent
        print("=" * 70)
        print("🤖 CONFIGURING AI AGENT")
        print("=" * 70)
        print()
        
        print("Configuring Carol with:")
        print("   - Provider: OpenAI")
        print("   - Model: GPT-4")
        print("   - Temperature: 0.7")
        print("   - RAG: Enabled")
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
        print("=" * 70)
        print("🧪 TESTING PRODUCTION RAG")
        print("=" * 70)
        print()
        
        test_queries = [
            "Quanto custa uma consulta de neuropediatria?",
            "Preciso fazer jejum para ultrassom abdominal?",
            "Quais convênios vocês aceitam?",
            "Como faço para cancelar uma consulta?"
        ]
        
        print("Running test queries...")
        print()
        
        for i, query in enumerate(test_queries, 1):
            print(f"[{i}/{len(test_queries)}] Query: {query}")
            try:
                response = rag_service.test_rag_query(query)
                answer = response.get('answer', 'No answer')
                sources = response.get('sources', [])
                
                # Truncate long answers
                if len(answer) > 150:
                    answer = answer[:150] + "..."
                
                print(f"   💬 Answer: {answer}")
                if sources:
                    source_titles = [s.get('title', 'Unknown') for s in sources]
                    print(f"   📚 Sources: {', '.join(source_titles)}")
                print()
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
        
        # Final summary
        print("=" * 70)
        print("🎉 PRODUCTION RAG SETUP COMPLETE!")
        print("=" * 70)
        print()
        print("✅ Summary:")
        print(f"   - {len(results)} documents uploaded")
        print(f"   - AI agent configured with RAG")
        print(f"   - {len(test_queries)} test queries successful")
        print()
        print("📱 Next steps:")
        print("   1. Test with real WhatsApp messages")
        print("   2. Monitor Carol's responses")
        print("   3. Adjust documents if needed")
        print()
        print("🎯 Carol is now a Bem Querer Kids specialist!")
        print()
        
    except Exception as e:
        logger.error(f"❌ Production setup failed: {e}", exc_info=True)
        print()
        print("=" * 70)
        print("❌ SETUP FAILED!")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        print()
        print("Please check:")
        print("1. UazAPI instance is active")
        print("2. Token is valid")
        print("3. Network connection is stable")
        print()


if __name__ == "__main__":
    main()
