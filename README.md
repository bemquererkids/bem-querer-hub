# 📚 Índice de Documentação - Bem Querer Hub

Este arquivo serve como índice central para toda a documentação do projeto.

---

## 📖 Documentação Principal

### 🎯 [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md)
**Documento principal do projeto**
- Visão geral completa
- Arquitetura do sistema
- Funcionalidades implementadas
- Status atual
- Próximos passos
- Documentação técnica

**Quando usar:** Para entender o projeto como um todo, arquitetura e status atual.

---

## 🗺️ Planejamento e Roadmap

### 📅 [ROADMAP_EXECUTIVO.md](./ROADMAP_EXECUTIVO.md)
**Roadmap de 9 semanas**
- 7 sprints planejados
- Cronograma detalhado
- ROI calculado (1.250% ao ano)
- Investimento vs. Retorno

**Quando usar:** Para planejar próximas implementações e entender prioridades.

---

## 🔧 Implementações e Melhorias

### 🤖 [RAG_IMPLEMENTATION_GUIDE.md](./RAG_IMPLEMENTATION_GUIDE.md)
**Guia completo de implementação do RAG**
- O que é RAG
- Como funciona
- Setup passo a passo
- Testes
- Troubleshooting
- Métricas de sucesso

**Quando usar:** Para entender ou modificar o sistema RAG.

### 📊 [RAG_STATUS_UPDATE.md](./RAG_STATUS_UPDATE.md)
**Status atual do RAG**
- Problema encontrado (API UazAPI não tem RAG)
- Solução implementada (RAG no backend)
- Próximas ações

**Quando usar:** Para entender por que implementamos RAG no backend.

---

## 📡 Integrações

### 🔌 [UAZAPI_ANALISE_COMPLETA.md](./UAZAPI_ANALISE_COMPLETA.md)
**Análise completa da API UazAPI**
- 15 categorias de endpoints
- 80+ endpoints documentados
- Exemplos práticos
- Casos de uso para clínica médica
- Funcionalidades exclusivas

**Quando usar:** Para explorar funcionalidades do UazAPI ou implementar novas integrações.

### 💡 [UAZAPI_MELHORIAS_PROPOSTAS.md](./UAZAPI_MELHORIAS_PROPOSTAS.md)
**Melhorias propostas usando UazAPI**
- Chatbot híbrido
- Typing indicators
- Sincronização bidirecional CRM
- Analytics dashboard
- Preview de mídia

**Quando usar:** Para planejar melhorias futuras.

### 🔧 [FIX_UAZAPI_WEBHOOK.md](./FIX_UAZAPI_WEBHOOK.md)
**Correções no webhook UazAPI**
- Problemas identificados
- Soluções implementadas
- Estrutura do payload
- Debug logs
- Commit history

**Quando usar:** Para debugar problemas com webhook ou entender correções feitas.

---

## 📁 Base de Conhecimento (RAG)

### 📄 Documentos de Conhecimento

Localizados em: `knowledge_base/`

1. **[01_especialidades_valores.md](./knowledge_base/01_especialidades_valores.md)**
   - Todas as especialidades médicas
   - Valores atualizados
   - Profissionais disponíveis
   - Convênios aceitos
   - Pacotes e promoções

2. **[02_preparos_exames.md](./knowledge_base/02_preparos_exames.md)**
   - Preparos para todos os exames
   - Exames de imagem, laboratoriais, cardiológicos, neurológicos
   - Orientações específicas
   - Dicas para pais

3. **[03_politicas_clinica.md](./knowledge_base/03_politicas_clinica.md)**
   - Política de agendamento
   - Política de cancelamento
   - Política de pagamento
   - LGPD e privacidade
   - Código de conduta

4. **[04_faq.md](./knowledge_base/04_faq.md)**
   - 50+ perguntas frequentes
   - Respostas detalhadas
   - Organizadas por categoria

**Quando usar:** Para atualizar informações que a IA Carol usa para responder.

---

## 🛠️ Scripts e Ferramentas

### Backend Scripts

Localizados em: `backend/`

1. **setup_rag.py**
   - Setup inicial do RAG
   - Upload de documentos
   - Configuração do agente IA
   - Testes automáticos

2. **setup_rag_production.py**
   - Setup para produção (com confirmação)
   - Credenciais hardcoded

3. **setup_rag_auto.py**
   - Setup automático (sem confirmação)
   - Usado para CI/CD

4. **test_rag.py**
   - Testes do sistema RAG
   - Verifica carregamento de documentos
   - Testa busca e contexto

5. **diagnose_rag.py**
   - Diagnóstico completo do RAG
   - Verifica todos os componentes
   - Identifica problemas

**Quando usar:** Para setup, testes ou diagnóstico do RAG.

---

## 📊 Status e Desenvolvimento

### 🚀 [DEVELOPMENT_STATUS.md](./DEVELOPMENT_STATUS.md)
**Status de desenvolvimento (legado)**
- Funcionalidades implementadas
- Bugs conhecidos
- Próximos passos

**Quando usar:** Para referência histórica.

---

## 🗂️ Estrutura de Arquivos

```
sistemabemquerer-v2/
│
├── 📚 DOCUMENTAÇÃO
│   ├── README.md                          # Índice (este arquivo)
│   ├── PROJECT_DOCUMENTATION.md           # ⭐ Documento principal
│   ├── ROADMAP_EXECUTIVO.md               # Roadmap 9 semanas
│   ├── RAG_IMPLEMENTATION_GUIDE.md        # Guia RAG
│   ├── RAG_STATUS_UPDATE.md               # Status RAG
│   ├── UAZAPI_ANALISE_COMPLETA.md         # Análise UazAPI
│   ├── UAZAPI_MELHORIAS_PROPOSTAS.md      # Melhorias UazAPI
│   ├── FIX_UAZAPI_WEBHOOK.md              # Fix webhook
│   └── DEVELOPMENT_STATUS.md              # Status (legado)
│
├── 📁 CÓDIGO
│   ├── backend/                           # Backend FastAPI
│   │   ├── app/                           # Aplicação
│   │   │   ├── api/                       # Endpoints
│   │   │   ├── services/                  # Serviços
│   │   │   └── core/                      # Core
│   │   ├── knowledge_base/                # Base de conhecimento
│   │   ├── setup_rag.py                   # Setup RAG
│   │   ├── test_rag.py                    # Testes RAG
│   │   └── diagnose_rag.py                # Diagnóstico RAG
│   │
│   └── frontend/                          # Frontend React
│       └── src/                           # Código fonte
│
└── 🔧 CONFIGURAÇÃO
    ├── railway.json                       # Config Railway
    ├── .env                               # Variáveis de ambiente
    └── requirements.txt                   # Dependências Python
```

---

## 🎯 Guia Rápido

### Para Desenvolvedores Novos

1. Leia: **PROJECT_DOCUMENTATION.md** (visão geral)
2. Leia: **ROADMAP_EXECUTIVO.md** (próximos passos)
3. Configure ambiente local
4. Execute: `python backend/test_rag.py` (testar RAG)

### Para Adicionar Funcionalidades

1. Consulte: **ROADMAP_EXECUTIVO.md** (prioridades)
2. Consulte: **UAZAPI_ANALISE_COMPLETA.md** (APIs disponíveis)
3. Consulte: **PROJECT_DOCUMENTATION.md** (arquitetura)
4. Implemente
5. Teste
6. Documente

### Para Debugar Problemas

1. Consulte: **FIX_UAZAPI_WEBHOOK.md** (problemas conhecidos)
2. Execute: `python backend/diagnose_rag.py` (diagnóstico)
3. Verifique logs do Railway
4. Consulte: **PROJECT_DOCUMENTATION.md** (arquitetura)

### Para Atualizar Base de Conhecimento

1. Edite arquivos em: `knowledge_base/`
2. Execute: `python backend/setup_rag_auto.py`
3. Faça commit e push
4. Aguarde deploy (Railway)
5. Teste no WhatsApp

---

## 📞 Suporte

**Dúvidas sobre documentação?**
- Consulte: **PROJECT_DOCUMENTATION.md** primeiro
- Verifique índice acima para documento específico
- Entre em contato: luiz.bezerra@santodi.com.br

---

## 📝 Convenções

### Emojis nos Documentos

- 📚 Documentação
- 🎯 Objetivos/Metas
- ✅ Concluído/Funcionando
- 🔄 Em andamento
- 🚧 Em desenvolvimento
- 📋 Backlog/Planejado
- ⚠️ Atenção/Importante
- 🔧 Técnico/Configuração
- 💡 Dica/Sugestão
- 🚀 Deploy/Lançamento
- 📊 Métricas/Analytics
- 🤖 IA/Automação
- 💬 Chat/Mensagens
- 📞 Suporte/Contato

### Status nos Documentos

- ✅ **Funcionando em Produção**
- 🔄 **Em Deploy**
- 🚧 **Em Desenvolvimento**
- 📋 **Planejado/Backlog**
- ❌ **Bloqueado/Problema**

---

## 🔄 Atualização da Documentação

**Última atualização:** 08/01/2026 22:55

**Responsável:** Luiz Fernando Bezerra

**Próxima revisão:** Semanal (toda segunda-feira)

---

**💡 Dica:** Mantenha este arquivo sempre atualizado quando adicionar nova documentação!
