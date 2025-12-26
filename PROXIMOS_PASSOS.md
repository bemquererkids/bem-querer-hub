# Guia Rápido - Próximos Passos

## 1️⃣ Executar Migration SQL

### Opção A: Via Supabase Dashboard (Recomendado)
1. Acesse: https://supabase.com/dashboard
2. Selecione seu projeto
3. Vá em: **SQL Editor**
4. Clique em **New Query**
5. Cole o conteúdo de: `supabase/migrations/v2_meta_migration.sql`
6. Clique em **Run** (ou pressione Ctrl+Enter)
7. Aguarde mensagem de sucesso

### Opção B: Via psql (Linha de Comando)
```bash
# Se você tem a connection string do Supabase
psql "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres" -f supabase/migrations/v2_meta_migration.sql
```

### Opção C: Via Script Python
```bash
cd c:\projetos\sistemabemquerer-v2\backend
python run_migration.py
```

---

## 2️⃣ Verificar Migration

Execute no SQL Editor do Supabase:

```sql
-- Verificar estrutura da tabela
\d clinic_integrations

-- Verificar colunas Meta (deve retornar 4 linhas)
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'clinic_integrations' 
AND column_name IN ('phone_number_id', 'waba_id', 'access_token', 'verify_token');

-- Verificar colunas UazAPI removidas (deve retornar 0 linhas)
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'clinic_integrations' 
AND column_name IN ('instance_name', 'token', 'qr_code_base64');
```

---

## 3️⃣ Obter Credenciais Meta

### A. Criar WhatsApp Business App
1. Acesse: https://developers.facebook.com/apps
2. Clique em **Create App**
3. Selecione **Business** como tipo
4. Preencha nome do app
5. Adicione produto **WhatsApp**

### B. Obter Phone Number ID
1. No app, vá em **WhatsApp** → **API Setup**
2. Copie o **Phone Number ID** (ex: `123456789012345`)

### C. Obter WABA ID
1. No mesmo painel, procure **WhatsApp Business Account ID**
2. Copie o **WABA ID**

### D. Gerar Access Token Permanente
1. Vá em **Business Settings** (ícone de engrenagem)
2. **System Users** → **Add**
3. Nome: "Sistema Bem-Querer"
4. Role: Admin
5. Clique no System User criado
6. **Generate New Token**
7. Selecione o app WhatsApp
8. Permissões:
   - ✅ `whatsapp_business_management`
   - ✅ `whatsapp_business_messaging`
9. **Generate Token**
10. **COPIE E SALVE** o token (começa com `EAA...`)

---

## 4️⃣ Configurar no Sistema

### Via Interface Web
1. Iniciar backend:
   ```bash
   cd c:\projetos\sistemabemquerer-v2\backend
   uvicorn app.main:app --reload
   ```

2. Iniciar frontend:
   ```bash
   cd c:\projetos\sistemabemquerer-v2\frontend
   npm run dev
   ```

3. Acessar: http://localhost:5173

4. Ir em: **Configurações** → **Integrações** → **WhatsApp**

5. Preencher:
   - **Phone Number ID**: `[colar]`
   - **WABA ID**: `[colar]`
   - **Access Token**: `[colar]`

6. Clicar em **Conectar WhatsApp**

7. **COPIAR** os valores exibidos:
   - Webhook URL
   - Verify Token

---

## 5️⃣ Configurar Webhook na Meta

1. No Meta Developer Console
2. **WhatsApp** → **Configuration**
3. Seção **Webhook**
4. Clicar em **Edit**
5. Preencher:
   - **Callback URL**: `[Webhook URL copiada]`
   - **Verify Token**: `[Verify Token copiado]`
6. Clicar em **Verify and Save**
7. Aguardar ✅ **Verified**
8. Subscrever campos:
   - ✅ `messages`
   - ✅ `message_status` (opcional)

---

## 6️⃣ Testar

### Teste 1: Enviar Mensagem (Meta → Você)
1. No Meta Developer Console
2. **WhatsApp** → **API Setup**
3. Usar ferramenta **Send and receive messages**
4. Enviar mensagem de teste para seu número

### Teste 2: Receber Mensagem (Você → Sistema)
1. Do seu WhatsApp pessoal
2. Enviar mensagem para o número comercial
3. Verificar:
   - Logs do backend (deve receber POST)
   - IA Carol deve responder
   - Mensagem deve aparecer no CRM

---

## ✅ Checklist

- [ ] Migration SQL executada
- [ ] Schema verificado (4 colunas Meta, 0 colunas UazAPI)
- [ ] Credenciais Meta obtidas
- [ ] Credenciais configuradas no sistema
- [ ] Webhook URL e Verify Token copiados
- [ ] Webhook configurado na Meta
- [ ] Webhook verificado (✅ Verified)
- [ ] Teste de envio realizado
- [ ] Teste de recebimento realizado
- [ ] IA Carol respondendo

---

## 🆘 Problemas?

Consulte:
- [GUIA_INTEGRACAO_META.md](file:///c:/projetos/sistemabemquerer-v2/GUIA_INTEGRACAO_META.md) - Guia completo
- [RESUMO_MIGRACAO.md](file:///C:/Users/luiz.bezerra_santodi/.gemini/antigravity/brain/b01c19be-6842-4b04-9542-196849a89449/RESUMO_MIGRACAO.md) - Troubleshooting
- Documentação Meta: https://developers.facebook.com/docs/whatsapp/cloud-api
