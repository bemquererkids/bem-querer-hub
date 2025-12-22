# GEMINI.MD - Contexto Global do Projeto: Bem-Querer Hub

## 1. Visão Geral do Produto

O **Bem-Querer Hub** é uma plataforma SaaS B2B "Middleware" projetada para centralizar o atendimento, vendas e gestão de relacionamento em clínicas odontológicas (com foco inicial em Odontopediatria).

O sistema atua como o "cérebro comercial", preenchendo a lacuna entre a aquisição de leads (Ads) e o software de gestão clínica (Clinicorp), eliminando a "tela dupla" e automatizando o funil.

### O Fluxo "Connect-Engage-Convert":
1.  **Centralize (Omnichannel):** Agrega múltiplas instâncias de WhatsApp via **UazAPI**, permitindo múltiplos atendentes no mesmo número e identificação de origem de Leads (UTMs).
2.  **Qualify (AI Triagem):** O **Google Gemini 2.0** atua como uma "Recepcionista Virtual Empática", identificando intenções (Emergência vs. Dúvida) e extraindo dados (Nome Mãe vs. Nome Filho).
3.  **Sync (Integração):** Sincronização bidirecional com o Clinicorp para checar disponibilidade de agenda e confirmar status de agendamentos.
4.  **Recover (Automação):** Fluxos de recuperação de No-Shows baseados nos status de mensagem (Lido/Não Respondido) fornecidos pela UazAPI.

**Slogan:** *"Mais sorrisos, menos telas. A inteligência que sua recepção precisa."*

## 2. Stack Tecnológica

* **Frontend (Web/Dashboard):** React 18 (Vite) + TailwindCSS + ShadCN/UI + React Query (Cache & State).
* **Chat Engine (Gateway):** **UazAPI** (Integração via REST e Webhooks).
    * *Função:* Garantir conexão estável com WhatsApp (WABA/Baileys) e evitar banimentos.
* **Backend:** Python 3.11+ com framework **FastAPI** (Alta performance para IA e processamento assíncrono de Webhooks).
* **Database:** PostgreSQL 15+ (Arquitetura Multi-tenant com Row-Level Security).
* **Vector Database:** PGVector (Integrado ao Postgres) para memória de longo prazo da IA (RAG).
* **AI Engine:** Google Gemini 2.0 Flash (Baixa latência para respostas em tempo real).
* **Infraestrutura:** Docker & Docker Compose (Ambiente AWS ou DigitalOcean).

## 3. Diretrizes de Desenvolvimento (Best Practices)

1.  **Arquitetura Multi-Tenant Rígida:**
    * **Mandatório:** Todas as tabelas críticas (`patients`, `chats`, `appointments`) devem ter a coluna `clinic_id`.
    * Middleware de segurança no FastAPI deve injetar o `clinic_id` automaticamente no contexto da requisição.
2.  **Integração com UazAPI (Webhook Pattern):**
    * **Idempotência:** O endpoint `/webhook/whatsapp` deve estar preparado para receber eventos duplicados sem criar mensagens repetidas.
    * **Fila de Processamento:** Receber o evento -> Jogar na Fila (Redis/Celery) -> Responder `200 OK` imediatamente para evitar timeout da API.
3.  **Abordagem "Human-in-the-Loop" (Copilot):**
    * A IA sugere o rascunho da resposta, o humano aprova/edita.
    * **Zero Alucinação Clínica:** System Prompt rígido proibindo diagnósticos médicos ou prescrições.
4.  **Esteira CI/CD (DevOps):**
    * Pipeline automatizado: Linting (Ruff) -> Unit Tests (Pytest) -> Build Docker -> Deploy.
    * Ambientes segregados: `Staging` (Homologação) vs `Production`.

## 4. Design System & Identidade Visual

Estética **"Pediatric Soft-Tech"**: acolhedora, eficiente e profissional.

### Identidade
* **Tipografia UI:** *Nunito* (Legibilidade amigável).
* **Tipografia Dados:** *Roboto Mono* (IDs, Financeiro, Datas).

### Paleta de Cores Oficial

| Nome da Cor | HEX | Uso Obrigatório | Contexto |
| :--- | :--- | :--- | :--- |
| **Bem-Querer Blue** | `#00A3E0` | Header, Destaques | Confiança, Marca principal. |
| **Soft Lilac** | `#E0D7F5` | Fundos de Chat | Tecnologia suave, Materno. |
| **Sales Purple** | `#8B5CF6` | Tags "Venda" | Sucesso comercial. |
| **Urgent Coral** | `#FF6B6B` | Tags "Emergência" | Alerta visual imediato. |
| **WhatsApp Green**| `#25D366` | Ícone UazAPI/Status | Conexão ativa. |
| **Canvas White** | `#F9FAFB` | Fundo Geral | Limpeza visual. |
| **Text Slate** | `#334155` | Textos principais | Contraste suave. |

## 5. Padrões de Resposta da IA (Prompt Engineering)

Ao interagir com o Gemini:

* **Persona:** "Você é a Carol, assistente virtual da Bem-Querer Odontologia. Seu tom é empático, acolhedor e eficiente. Você fala com mães preocupadas ou pacientes ocupados."
* **Estrutura de Saída (Tools):** Retornar JSON para ações do Frontend. Ex: `{"action": "show_calendar", "intent": "booking"}`.
* **Contexto UazAPI:** A IA deve entender que áudios são transcritos e deve responder em texto curto, simulando naturalidade.

### 👥 Nossos Especialistas (Agents.md)

Estes são os perfis de agente especializados para invocar durante o desenvolvimento:

#### **@ProductManager (PM)**
* **Foco:** Métricas de Funil, Integração Clinicorp, UX da Recepção.
* **Missão:** Validar se os status de mensagem da UazAPI (Sent, Delivered, Read) estão atualizando corretamente o Kanban.

#### **@TechLead (Arch)**
* **Foco:** FastAPI, Webhooks UazAPI, Segurança de Dados (LGPD).
* **Missão:** Garantir rotação de tokens, segurança da API e tratamento de erros de desconexão (QR Code caiu).

#### **@FrontendLead (UX)**
* **Foco:** React, Interface de Chat (Clone WhatsApp Web otimizado), Mobile-First.
* **Missão:** Criar alertas visuais claros quando a UazAPI estiver desconectada ou quando houver erro de sincronia com Clinicorp.

#### **@AIEngineer (Gemini)**
* **Foco:** Prompt Tuning, RAG (Busca em convênios), Tratamento de Alucinações.
* **Missão:** Garantir que a IA não entre em loops de conversa e saiba transbordar para humano em casos complexos.

#### **@QA_Specialist**
* **Foco:** Testes E2E, Testes de Carga em Webhooks.
* **Missão:** Simular picos de mensagens (Black Friday) para garantir que a fila de processamento não trave o atendimento.