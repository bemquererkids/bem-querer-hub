# 🚀 Configuração de Variáveis de Ambiente - Vercel

## 📋 Variáveis Obrigatórias para WhatsApp

Acesse o painel da Vercel: **Settings → Environment Variables**

### UazAPI (WhatsApp)

```
UAZAPI_BASE_URL=https://bemquerer.uazapi.com
UAZAPI_TOKEN=093b971c-f10f-4af1-b0aa-a13c6ad15909
UAZAPI_INSTANCE=bemquerer
```

### Supabase (Já configuradas)

```
SUPABASE_URL=sua-url-supabase
SUPABASE_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key
VITE_SUPABASE_URL=mesma-url-supabase
VITE_SUPABASE_KEY=mesma-anon-key
```

### OpenAI (Já configurada)

```
OPENAI_API_KEY=sua-chave-openai
```

### Secret Key (Já configurada)

```
SECRET_KEY=sua-secret-key
```

---

## ⚙️ Como Adicionar na Vercel

### Passo a Passo:

1. **Acessar Vercel Dashboard**
   - Ir para https://vercel.com/dashboard
   - Selecionar seu projeto

2. **Abrir Configurações**
   - Clicar em **Settings**
   - No menu lateral, clicar em **Environment Variables**

3. **Adicionar Variáveis**
   - Clicar em **Add New**
   - **Name**: `UAZAPI_BASE_URL`
   - **Value**: `https://bemquerer.uazapi.com`
   - **Environment**: Selecionar **Production**, **Preview** e **Development**
   - Clicar em **Save**

4. **Repetir para cada variável**:
   - `UAZAPI_TOKEN` = `093b971c-f10f-4af1-b0aa-a13c6ad15909`
   - `UAZAPI_INSTANCE` = `bemquerer`

5. **Redeploy**
   - Após adicionar todas as variáveis
   - Ir em **Deployments**
   - Clicar nos 3 pontinhos do último deploy
   - Clicar em **Redeploy**

---

## ✅ Checklist de Variáveis

### WhatsApp (UazAPI) - NOVO
- [ ] `UAZAPI_BASE_URL` = `https://bemquerer.uazapi.com`
- [ ] `UAZAPI_TOKEN` = `093b971c-f10f-4af1-b0aa-a13c6ad15909`
- [ ] `UAZAPI_INSTANCE` = `bemquerer`

### Supabase (Já deve estar configurado)
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `SUPABASE_SERVICE_KEY`
- [ ] `VITE_SUPABASE_URL`
- [ ] `VITE_SUPABASE_KEY`

### OpenAI (Já deve estar configurado)
- [ ] `OPENAI_API_KEY`

### Segurança (Já deve estar configurado)
- [ ] `SECRET_KEY`

---

## 🧪 Testar Após Deploy

### 1. Verificar Status
```bash
curl https://seu-app.vercel.app/api/integrations/whatsapp/status
```

**Resposta Esperada:**
```json
{
  "connected": true,
  "instance": {
    "name": "bemquerer",
    "phone": "5511991026844"
  }
}
```

### 2. Enviar Mensagem de Teste
```bash
curl -X POST https://seu-app.vercel.app/api/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5511999999999",
    "message": "Teste de mensagem do sistema NEXUS"
  }'
```

---

## ⚠️ Notas Importantes

1. **Não usar aspas** nos valores das variáveis
   - ✅ Correto: `https://bemquerer.uazapi.com`
   - ❌ Errado: `"https://bemquerer.uazapi.com"`

2. **Aplicar em todos os ambientes**
   - Marcar: Production, Preview e Development

3. **Redeploy obrigatório**
   - Variáveis só são aplicadas após novo deploy

4. **Segurança**
   - Nunca compartilhar o `UAZAPI_TOKEN` publicamente
   - Não commitar no Git

---

## 🔍 Troubleshooting

### Erro: "Token inválido"
**Solução:** Verificar se `UAZAPI_TOKEN` está correto

### Erro: "Cannot connect to instance"
**Solução:** Verificar se `UAZAPI_BASE_URL` está correto (sem `/` no final)

### WhatsApp não conecta
**Solução:** 
1. Verificar se variáveis foram salvas
2. Fazer redeploy
3. Aguardar 2-3 minutos para deploy completar
4. Testar novamente

---

## 📊 Status Atual

**Número WhatsApp:** 5511991026844  
**Status:** Conectado  
**Instância:** bemquerer  
**URL:** https://bemquerer.uazapi.com

Após configurar as variáveis na Vercel, o sistema estará pronto para enviar mensagens via WhatsApp! 🎉
