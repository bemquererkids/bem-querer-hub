"""
Production RAG Setup Script - Auto Mode

This script sets up RAG in production automatically without user confirmation.
Use with caution - this will modify production!
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.uazapi_rag_service import UazAPIRAGService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main production setup function"""
    
    print("=" * 70)
    print("🚀 PRODUCTION RAG SETUP - Bem Querer Kids (AUTO MODE)")
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
        # Initialize RAG service
        logger.info("🔌 Connecting to production UazAPI...")
        rag_service = UazAPIRAGService(
            instance_name=INSTANCE_NAME,
            token=TOKEN,
            base_url=BASE_URL
        )
        logger.info("✅ Connected to production!")
        print()
        
        # Path to knowledge base (in project root, not backend)
        kb_path = Path(__file__).parent.parent / "knowledge_base"
        
        if not kb_path.exists():
            logger.error(f"❌ Knowledge base directory not found: {kb_path}")
            return
        
        # List files
        md_files = sorted(kb_path.glob("*.md"))
        print(f"📚 Found {len(md_files)} knowledge documents:")
        for i, f in enumerate(md_files, 1):
            print(f"   {i}. {f.name}")
        print()
        
        # Upload knowledge base
        print("=" * 70)
        print("📤 UPLOADING TO PRODUCTION")
        print("=" * 70)
        print()
        
        results = []
        for i, md_file in enumerate(md_files, 1):
            try:
                print(f"[{i}/{len(md_files)}] Uploading {md_file.name}...")
                result = rag_service.upload_knowledge_from_file(str(md_file))
                results.append(result)
                print(f"   ✅ Success! ID: {result.get('id', 'unknown')}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                logger.error(f"Failed to upload {md_file.name}: {e}", exc_info=True)
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
                doc_id = result.get('id', 'unknown')
                print(f"   {i}. {title}")
                print(f"      Category: {category}")
                print(f"      ID: {doc_id}")
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
        print("   - Max Tokens: 500")
        print("   - RAG: Enabled")
        print()
        
        try:
            config_result = rag_service.configure_ai_agent(
                provider="openai",
                model="gpt-4",
                temperature=0.7,
                max_tokens=500
            )
            print("✅ AI agent configured successfully!")
            print()
        except Exception as e:
            print(f"⚠️  AI configuration may have failed: {e}")
            print("   (This is OK if the endpoint doesn't exist yet)")
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
        
        successful_tests = 0
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
                successful_tests += 1
                print()
            except Exception as e:
                print(f"   ⚠️  Test may not be available yet: {e}")
                print()
        
        # Final summary
        print("=" * 70)
        print("🎉 PRODUCTION RAG SETUP COMPLETE!")
        print("=" * 70)
        print()
        print("✅ Summary:")
        print(f"   - {len(results)}/{len(md_files)} documents uploaded successfully")
        print(f"   - AI agent configuration attempted")
        print(f"   - {successful_tests}/{len(test_queries)} test queries successful")
        print()
        print("📱 Next steps:")
        print("   1. Test with real WhatsApp messages")
        print("   2. Send: 'Quanto custa neuropediatria?'")
        print("   3. Send: 'Preciso fazer jejum para ultrassom?'")
        print("   4. Monitor Carol's responses")
        print()
        print("🎯 Carol is now a Bem Querer Kids specialist!")
        print()
        
        # List uploaded knowledge
        print("=" * 70)
        print("📚 VERIFYING UPLOADED KNOWLEDGE")
        print("=" * 70)
        print()
        
        try:
            knowledge_list = rag_service.list_knowledge()
            print(f"Total documents in production: {len(knowledge_list)}")
            print()
            for i, doc in enumerate(knowledge_list, 1):
                print(f"{i}. {doc.get('title', 'Unknown')}")
                print(f"   Category: {doc.get('category', 'N/A')}")
                print(f"   ID: {doc.get('id', 'N/A')}")
                print()
        except Exception as e:
            print(f"⚠️  Could not list knowledge: {e}")
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


if __name__ == "__main__":
    main()
