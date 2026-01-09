"""
Diagnóstico RAG - Verificar por que não está funcionando em produção
"""

import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🔍 DIAGNÓSTICO RAG")
print("=" * 70)
print()

# 1. Verificar se knowledge_base existe
print("1️⃣ Verificando diretório knowledge_base...")
print()

kb_path = Path(__file__).parent.parent / "knowledge_base"
print(f"   Caminho: {kb_path}")
print(f"   Existe: {kb_path.exists()}")

if kb_path.exists():
    md_files = list(kb_path.glob("*.md"))
    print(f"   Arquivos .md encontrados: {len(md_files)}")
    for f in md_files:
        print(f"      - {f.name}")
else:
    print("   ❌ ERRO: Diretório não existe!")
print()

# 2. Testar importação do serviço
print("2️⃣ Testando importação do Knowledge Base Service...")
print()

try:
    from app.services.knowledge_base_service import get_knowledge_base_service
    print("   ✅ Importação bem-sucedida")
    
    # Tentar inicializar
    kb_service = get_knowledge_base_service()
    print(f"   ✅ Serviço inicializado")
    print(f"   📚 Documentos carregados: {len(kb_service.documents)}")
    
    if kb_service.documents:
        print("   📋 Documentos:")
        for doc_id, doc in kb_service.documents.items():
            print(f"      - {doc['title']}")
    else:
        print("   ❌ ERRO: Nenhum documento carregado!")
    
except Exception as e:
    print(f"   ❌ ERRO na importação: {e}")
    import traceback
    traceback.print_exc()

print()

# 3. Testar busca
print("3️⃣ Testando busca...")
print()

try:
    from app.services.knowledge_base_service import get_knowledge_base_service
    
    kb_service = get_knowledge_base_service()
    query = "Quanto custa neuropediatria"
    
    print(f"   Query: {query}")
    results = kb_service.search(query, max_results=2)
    
    print(f"   Resultados: {len(results)}")
    
    if results:
        for r in results:
            print(f"      ✅ {r['title']} (score: {r['score']})")
    else:
        print("   ❌ Nenhum resultado encontrado!")
    
    # Testar contexto
    context = kb_service.get_context_for_query(query)
    print(f"   Contexto gerado: {len(context)} caracteres")
    
    if context:
        print("   ✅ Contexto OK")
        print(f"   Preview: {context[:200]}...")
    else:
        print("   ❌ Contexto vazio!")
    
except Exception as e:
    print(f"   ❌ ERRO na busca: {e}")
    import traceback
    traceback.print_exc()

print()

# 4. Testar integração com GPT Service
print("4️⃣ Testando integração com GPT Service...")
print()

try:
    from app.services.gpt_service import get_gpt_service
    
    gpt_service = get_gpt_service()
    print("   ✅ GPT Service inicializado")
    
    # Verificar se o código RAG está no arquivo
    import inspect
    source = inspect.getsource(gpt_service.process_message)
    
    if "knowledge_base_service" in source:
        print("   ✅ Código RAG encontrado no process_message")
    else:
        print("   ❌ Código RAG NÃO encontrado no process_message!")
    
    if "get_context_for_query" in source:
        print("   ✅ Chamada get_context_for_query encontrada")
    else:
        print("   ❌ Chamada get_context_for_query NÃO encontrada!")
    
except Exception as e:
    print(f"   ❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print()

# 5. Verificar variáveis de ambiente
print("5️⃣ Verificando variáveis de ambiente...")
print()

env_vars = [
    "OPENAI_API_KEY",
    "UAZAPI_INSTANCE_NAME",
    "UAZAPI_TOKEN"
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # Mostrar apenas primeiros caracteres
        masked = value[:20] + "..." if len(value) > 20 else value
        print(f"   ✅ {var}: {masked}")
    else:
        print(f"   ❌ {var}: NÃO DEFINIDA")

print()

# 6. Resumo
print("=" * 70)
print("📊 RESUMO DO DIAGNÓSTICO")
print("=" * 70)
print()

print("Se todos os itens acima estiverem ✅, o RAG deveria funcionar.")
print("Se algum item estiver ❌, esse é o problema!")
print()
print("Próximos passos:")
print("1. Corrigir itens com ❌")
print("2. Reiniciar o backend")
print("3. Testar novamente")
print()
