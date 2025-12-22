# API Reference - Bem-Querer Hub

## Endpoints

### Health & Status

#### `GET /`
Health check básico.

**Response:**
```json
{
  "status": "online",
  "service": "Bem-Querer Hub API",
  "version": "1.0.0"
}
```

#### `GET /health`
Status detalhado dos serviços.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "services": {
    "uazapi": "pending",
    "gemini": "pending",
    "clinicorp": "pending"
  }
}
```

---

### Webhooks

#### `POST /webhook/whatsapp`
Recebe eventos do WhatsApp via UazAPI.

**Headers:**
- `Content-Type: application/json`

**Request Body:**
```json
{
  "event": "messages.upsert",
  "instance": "instance-name",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "message-id"
    },
    "message": {
      "conversation": "Olá, gostaria de agendar"
    }
  }
}
```

**Response:**
```json
{
  "status": "received",
  "event": "messages.upsert"
}
```

**Eventos Suportados:**
- `messages.upsert` - Nova mensagem recebida
- `messages.update` - Atualização de status (enviado, lido)
- `connection.update` - Mudança no status de conexão

---

## Services (Uso Interno)

### Gemini AI Service

```python
from app.services.gemini_service import get_gemini_service

gemini = get_gemini_service()

# Processar mensagem
result = await gemini.process_message(
    message="Quero agendar consulta",
    chat_history=[...],
    context={...}
)

# Classificar intenção
intent = await gemini.classify_intent("Meu filho está com dor")

# Gerar embedding
embedding = await gemini.generate_embedding("texto para vetorizar")
```

### Message Processor

```python
from app.services.message_processor import get_message_processor

processor = get_message_processor()

result = await processor.process_incoming_message(
    clinic_id="clinic-uuid",
    whatsapp_number="5511999999999",
    message_content="Olá",
    message_type="text"
)
```

### UazAPI Service

```python
from app.services.uazapi_service import get_uazapi_service

uazapi = get_uazapi_service()

# Enviar mensagem
await uazapi.send_message(
    instance="instance-name",
    phone="5511999999999",
    message="Olá! Como posso ajudar?"
)

# Verificar status
status = await uazapi.get_instance_status("instance-name")
```

---

## Database Schema

### Tables

#### `clinics`
Tenants (clínicas).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Nome da clínica |
| cnpj | VARCHAR(18) | CNPJ (unique) |
| plan | VARCHAR(50) | trial, basic, premium |
| status | VARCHAR(20) | active, suspended, cancelled |

#### `chats`
Conversas do WhatsApp.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Primary key |
| clinic_id | UUID | Foreign key → clinics |
| patient_id | UUID | Foreign key → patients (nullable) |
| whatsapp_number | VARCHAR(20) | Número do WhatsApp |
| status | VARCHAR(50) | open, waiting_human, closed |
| intent | VARCHAR(50) | booking, emergency, question, complaint |
| urgency | VARCHAR(20) | low, normal, high, urgent |

#### `messages`
Mensagens individuais.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Primary key |
| clinic_id | UUID | Foreign key → clinics |
| chat_id | UUID | Foreign key → chats |
| content | TEXT | Conteúdo da mensagem |
| message_type | VARCHAR(20) | text, audio, image, document |
| sender_type | VARCHAR(20) | user, ai, human_agent |
| embedding | vector(768) | Vetor para busca semântica |
| ai_confidence | FLOAT | Confiança da IA (0-1) |

---

## Environment Variables

```env
# Application
APP_NAME=Bem-Querer Hub
DEBUG=True

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Google Gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash-exp

# UazAPI
UAZAPI_BASE_URL=https://api.uazapi.com
UAZAPI_TOKEN=token...

# Security
SECRET_KEY=generated-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Error Handling

Todos os serviços implementam tratamento de erros:

```python
try:
    result = await service.method()
except Exception as e:
    logger.error(f"Error: {str(e)}")
    return {
        "success": False,
        "error": str(e)
    }
```

---

## Testing

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar testes específicos
pytest tests/test_gemini_service.py -v

# Com cobertura
pytest tests/ --cov=app --cov-report=html
```
