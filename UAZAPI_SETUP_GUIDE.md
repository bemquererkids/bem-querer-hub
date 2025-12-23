# Guia de Configuração: WhatsApp via UazAPI

## 📋 Pré-requisitos

1. **Conta UazAPI**: Crie uma conta em [uazapi.com](https://uazapi.com)
2. **Instância WhatsApp**: Configure uma instância no painel UazAPI
3. **Token de API**: Obtenha seu token de autenticação

---

## 🔧 Configuração Passo a Passo

### 1. Obter Credenciais UazAPI

1. Acesse o painel UazAPI
2. Vá em **Configurações** → **API**
3. Copie:
   - **Base URL**: geralmente `https://api.uazapi.com` ou `https://{seu-subdominio}.uazapi.com`
   - **Token**: seu token de autenticação
   - **Nome da Instância**: o nome que você deu para sua instância WhatsApp

### 2. Configurar Variáveis de Ambiente

Edite o arquivo `backend/.env` e adicione:

```env
# UazAPI WhatsApp Gateway
UAZAPI_BASE_URL=https://api.uazapi.com
UAZAPI_TOKEN=seu_token_aqui
```

**⚠️ IMPORTANTE**: 
- Nunca commite o arquivo `.env` no Git
- O token é sensível, mantenha em segredo

### 3. Conectar Instância WhatsApp

No painel UazAPI:
1. Vá em **Instâncias**
2. Clique em **Conectar** na sua instância
3. Escaneie o QR Code com seu WhatsApp Business
4. Aguarde o status mudar para **Conectado** ✅

---

## 🧪 Testar a Integração

### Opção 1: Script de Teste Rápido

1. Edite o arquivo `test_whatsapp_integration.py`:
   ```python
   PHONE_NUMBER = "5585999887766"  # Seu número com DDD
   INSTANCE_NAME = "bemquerer"     # Nome da sua instância
   ```

2. Execute:
   ```bash
   python test_whatsapp_integration.py
   ```

### Opção 2: Via API Backend

Com o backend rodando (`uvicorn app.main:app --reload`):

```bash
curl -X POST http://localhost:8000/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "instance": "bemquerer",
    "phone": "5585999887766",
    "message": "Teste do Bem-Querer Hub! 🦷"
  }'
```

---

## 📡 Endpoints Disponíveis

### 1. Enviar Mensagem de Texto
```
POST /message/sendText/{instance}
Authorization: Bearer {token}

Body:
{
  "number": "5585999887766",
  "text": "Sua mensagem aqui"
}
```

### 2. Enviar Imagem
```
POST /message/sendImage/{instance}
Authorization: Bearer {token}

Body:
{
  "number": "5585999887766",
  "image": "https://url-da-imagem.com/foto.jpg",
  "caption": "Legenda opcional"
}
```

### 3. Verificar Status da Instância
```
GET /instance/connectionState/{instance}
Authorization: Bearer {token}
```

---

## 🔍 Troubleshooting

### ❌ Erro: "Unauthorized" ou 401
- Verifique se o token está correto no `.env`
- Confirme que o token não expirou

### ❌ Erro: "Instance not found"
- Verifique o nome da instância (case-sensitive)
- Confirme que a instância existe no painel UazAPI

### ❌ Erro: "Instance not connected"
- Vá no painel UazAPI e reconecte a instância
- Escaneie o QR Code novamente se necessário

### ❌ Mensagem não chega
- Verifique o formato do número: `{código_país}{DDD}{número}` (sem +, espaços ou hífens)
- Exemplo correto: `5585999887766`
- Exemplo incorreto: `+55 (85) 99988-7766`

---

## 🚀 Próximos Passos

Após confirmar que o teste funciona:

1. **Webhook**: Configure o webhook no UazAPI para receber mensagens
2. **Automação**: Implemente respostas automáticas via IA
3. **CRM**: Integre com o sistema de leads e agendamentos

---

## 📞 Suporte

- **Documentação UazAPI**: [docs.uazapi.com](https://docs.uazapi.com)
- **Suporte Bem-Querer Hub**: Abra uma issue no repositório
