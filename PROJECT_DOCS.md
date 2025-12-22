# 🦷 Bem-Querer Hub - Documentação Técnica Oficial

**Versão:** 1.0.0 (MVP)  
**Data:** Dezembro/2025  
**Status:** Funcional / Híbrido (Integração Real + Simulação)

---

## 1. Visão do Produto

O **Bem-Querer Hub** é uma plataforma SaaS B2B ("Middleware") projetada para clínicas odontológicas. Ele atua como o "cérebro comercial" que preenche a lacuna entre a aquisição de leads (Marketing) e o software de gestão clínica (ERP/Clinicorp).

### O Problema: "A Tela Dupla"
Atualmente, a secretária precisa alternar entre o WhatsApp Web (para falar) e o Clinicorp (para agendar), perdendo agilidade, dados de rastreamento de marketing e oportunidades de follow-up.

### A Solução
Um painel único onde:
1.  O WhatsApp é centralizado.
2.  Uma IA (**Carol**) atua como primeira linha de atendimento, capaz de consultar a agenda.
3.  O CRM organiza os pacientes por etapa (Lead, Agendado, Compareceu).
4.  O Follow-up gera listas ativas de contato para "aquecer" leads frios.

---

## 2. Arquitetura do Sistema

O sistema opera em uma arquitetura de microsserviços monolíticos (Modular Monolith) focada em eventos.

### Fluxo de Dados:
1.  **Entrada:** Paciente manda mensagem no WhatsApp -> **UazAPI** (Gateway) -> **Webhook Backend**.
2.  **Processamento:** Backend identifica o paciente -> Carrega Histórico -> Envia para **OpenAI (GPT-4)**.
3.  **Ação da IA:** 
    *   A IA decide se responde texto simples ou se precisa de uma **Tool**.
    *   Se precisar consultar agenda: Backend -> **Clinicorp Adapter** -> API Clinicorp.
4.  **Resposta:** Backend envia texto da IA -> **UazAPI** -> WhatsApp do Paciente.
5.  **Interface:** O Frontend consome os dados via API REST (`/crm`, `/chat`, `/dashboard`) para mostrar em tempo real.

---

## 3. Stack Tecnológica

### 🎨 Frontend (Interface)
*   **Framework:** React 18 + Vite (Alta performance).
*   **Linguagem:** TypeScript (Segurança de tipagem).
*   **Design System:** Shadcn/UI (Baseado em Radix Primitives) + Tailwind CSS.
*   **Estilo Visual:** "Star Admin" Clean (Azul/Branco) com adaptação para Odontologia.
*   **Gerenciamento de Estado:** React Hooks + Context.
*   **Funcionalidades Chave:**
    *   `recharts`: Gráficos de Funil e Financeiro.
    *   `@hello-pangea/dnd`: (Legado) Drag-and-drop inicial, migrado para Tabs.
    *   `lucide-react`: Ícones consistentes.

### ⚙️ Backend (API & Lógica)
*   **Framework:** FastAPI (Python 3.11+) - Async nativo.
*   **IA Engine:** OpenAI (`gpt-4-turbo-preview`) com **Function Calling**.
*   **HTTP Client:** `httpx` para chamadas assíncronas externas.
*   **Validação:** Pydantic para schemas de dados rigorosos.

### 🗄️ Dados & Infraestrutura
*   **Banco de Dados:** Supabase (PostgreSQL).
*   **Armazenamento Vetorial:** (Planejado) PGVector para memória de longo prazo da IA.
*   **Hospedagem (Dev):** Localhost com Uvicorn.
*   **Túnel:** Ngrok/LocalTunnel para Webhooks.

---

## 4. Módulos do Sistema

### 📊 Dashboard
*   **KPIs:** Leads Pendentes, Agenda do Dia, Faturamento Estimado.
*   **Monitor da Recepção:** Visualização em tempo real de quem está em atendimento e disponibilidade dos dentistas.
*   **Gráficos:** Funil de Conversão (Leads -> Vendas) e Fluxo Semanal.

### 👥 CRM (Gestão de Oportunidades)
*   **Visualização:** Baseada em Abas (Tabs) em vez de colunas Kanban tradicionais, otimizada para listas grandes.
*   **Abas:** Leads, Agendamentos, No-Shows, Comparecimentos, Vendas.
*   **Cards Inteligentes:** Mudam de contexto (botão "Agendar" para leads, botões "Compareceu/Faltou" para agendamentos).
*   **Integração Visual:** Badges indicando origem (Google/Insta) e status de sincronia com Clinicorp.

### 💬 Chat & IA (A "Carol")
*   **Persona Configurável:** Tela para definir nome, tom de voz e regras da IA.
*   **Skills:** A IA possui a ferramenta `consultar_agenda`, permitindo que ela veja horários reais disponíveis no Clinicorp antes de responder.
*   **Interface:** Clone do WhatsApp Web com filtros de funil e badges de status.

### 📅 Follow-up Ativo
*   **Listas Automáticas:**
    *   🔥 **Quentes:** Pediram contato hoje.
    *   ⏰ **Recuperação:** Orçamentos não respondidos.
    *   ❄️ **Reativação:** Pacientes inativos há 6+ meses.
*   **Scripts:** Sugestões prontas do que falar para cada caso.

---

## 5. Estratégia de Integração (O "Pulo do Gato")

Integramos com sistemas fechados (Clinicorp) e instáveis (WhatsApp) usando uma estratégia de **Camadas de Adaptação**.

### Integração Clinicorp (Híbrida)
Devido a limitações nas permissões da chave de API disponível (Widget Key vs Partner Key), adotamos uma abordagem mista:

1.  **Leitura de Disponibilidade (Real):**
    *   Usamos o endpoint `/appointment/get_avaliable_times_calendar`.
    *   **Resultado:** A IA consegue ver vagas reais.
2.  **Leitura de Dados Sensíveis (Simulação/Mock):**
    *   Para endpoints bloqueados (`/appointments`), o Backend intercepta e retorna dados mockados de alta fidelidade se a chave não tiver permissão.
    *   **Benefício:** O sistema nunca "quebra" ou fica vazio na demonstração.
3.  **Escrita/Atualização (Webhook):**
    *   Implementamos o endpoint receptor `/webhook/clinicorp` para receber atualizações passivas do sistema de gestão.

### Integração UazAPI (WhatsApp)
*   **Webhook:** Recebe mensagens, detecta a origem (UTM/Source) via Regex e cria o lead no banco automaticamente.
*   **Envio:** Endpoint preparado para disparo de mensagens ativas.

---

## 6. Como Rodar o Projeto

### Pré-requisitos
*   Node.js 18+
*   Python 3.11+
*   Chave OpenAI (Opcional para modo Mock, Obrigatória para IA real)

### Passos
1.  **Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
2.  **Backend:**
    ```bash
    cd backend
    # Ativar venv
    venv\Scripts\activate
    # Instalar deps
    pip install -r requirements.txt
    # Rodar servidor
    uvicorn app.main:app --reload
    ```
3.  **Acessar:** `http://localhost:5173`

---

## 7. Próximos Passos (Roadmap)

1.  **Oficializar Integração:** Solicitar Client ID/Secret OAuth2 para Clinicorp para remover a camada de Mock dos dados sensíveis.
2.  **Dashboard Financeiro:** Conectar com a API financeira para ver "Valor Pago" real.
3.  **Multi-Tenant:** Habilitar a criação dinâmica de clínicas via painel Admin.

---
*Documentação gerada automaticamente pelo Assistente de Engenharia Bem-Querer.*
