# Bem-Querer Hub - Supabase Database

## Aplicar Schema

1. **Acessar o Supabase Dashboard:**
   - Vá para [https://app.supabase.com](https://app.supabase.com)
   - Selecione seu projeto

2. **Executar SQL:**
   - Navegue até `SQL Editor`
   - Crie uma nova query
   - Cole o conteúdo de `schema.sql`
   - Execute (Run)

3. **Verificar:**
   - Vá para `Table Editor` e confirme que as tabelas foram criadas
   - Verifique em `Database` > `Extensions` se `pgvector` está habilitado

## Estrutura do Schema

### Tabelas Principais

- **clinics**: Tenants (clínicas)
- **profiles**: Perfis de usuário (vinculados ao Supabase Auth)
- **patients**: Pacientes
- **appointments**: Agendamentos
- **chats**: Conversas do WhatsApp
- **messages**: Mensagens individuais (com embeddings para IA)
- **webhook_logs**: Log de eventos da UazAPI

### Segurança (RLS)

Todas as tabelas possuem políticas de Row Level Security que garantem:
- Usuários só acessam dados da própria clínica (`clinic_id`)
- Isolamento total entre tenants

### Vector Search (AI)

A tabela `messages` possui:
- Coluna `embedding vector(768)` para armazenar embeddings do Gemini
- Índice `ivfflat` para busca por similaridade (RAG)

## Seed Data

O schema inclui uma clínica demo:
- ID: `00000000-0000-0000-0000-000000000001`
- Nome: "Clínica Bem-Querer Demo"

## Próximos Passos

1. Configurar Supabase Auth (Email/Password ou OAuth)
2. Criar usuários de teste via Dashboard
3. Vincular usuários à clínica demo na tabela `profiles`
