# 🔐 Configuração de Variáveis de Ambiente na Vercel

Para que as integrações Clinicorp e OpenAI permaneçam conectadas permanentemente, você precisa configurar as variáveis de ambiente no painel da Vercel.

## 📋 Passo a Passo

### 1. Acesse o Painel da Vercel
1. Vá para [vercel.com](https://vercel.com)
2. Faça login
3. Selecione o projeto **bem-querer-hub**

### 2. Configure as Variáveis de Ambiente

1. Clique em **Settings** (Configurações)
2. No menu lateral, clique em **Environment Variables**
3. Adicione as seguintes variáveis:

#### Clinicorp
```
Nome: CLINICORP_CLIENT_ID
Valor: bemquerer (ou seu client_id)
```

```
Nome: CLINICORP_CLIENT_SECRET
Valor: [seu client_secret do Clinicorp]
```

#### OpenAI (ChatGPT)
```
Nome: OPENAI_API_KEY
Valor: sk-... (sua chave da OpenAI)
```

### 3. Selecione os Ambientes

Para cada variável, marque:
- ✅ Production
- ✅ Preview  
- ✅ Development

### 4. Salve e Redeploy

1. Clique em **Save** para cada variável
2. Após adicionar todas, vá em **Deployments**
3. Clique nos 3 pontinhos (...) do último deploy
4. Selecione **Redeploy**
5. Aguarde o deploy completar

## ✅ Verificação

Após o redeploy:
1. Acesse https://bem-querer-hub.vercel.app
2. Vá em **Configurações → Integrações**
3. Clinicorp e ChatGPT devem aparecer como **Conectado** automaticamente
4. O status persiste em todos os dispositivos!

## 📝 Notas Importantes

- As variáveis de ambiente são **privadas** e **seguras**
- Não são expostas no frontend
- Funcionam em qualquer dispositivo que acessar o app
- Não precisam ser reconectadas após configuradas
- Para desconectar, basta remover as variáveis e fazer redeploy
