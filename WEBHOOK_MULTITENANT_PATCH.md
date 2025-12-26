# Mudanças Necessárias no webhooks.py

## 1. Atualizar webhook handler (linha ~110-145)

Substituir a função `receive_whatsapp_message` por:

```python
@router.post("/whatsapp")
async def receive_whatsapp_message(payload: dict, background_tasks: BackgroundTasks):
    """
    Receives notification from UazAPI (messages, history, connection, etc).
    Multi-tenant: Maps instance to clinic_id for data isolation.
    """
    try:
        event = payload.get('event', 'messages.upsert')
        instance_id = payload.get('instance', 'main')
        data = payload.get('data', {})
        
        # Get clinic_id from instance (multi-tenant mapping)
        try:
            clinic_id = await get_clinic_id_from_instance(instance_id)
        except HTTPException as e:
            logger.warning(f"Unknown instance '{instance_id}': {e.detail}")
            return {"status": "error", "message": f"Instance '{instance_id}' not registered"}

        # 1. Handle Historical Sync
        if event == 'messaging-history.set':
            messages = data.get('messages', [])
            print(f"📦 Recebendo histórico: {len(messages)} mensagens (clinic: {clinic_id}).")
            for msg in messages:
                background_tasks.add_task(process_single_message_data, msg, instance_id, clinic_id)
            return {"status": "sync_started", "count": len(messages), "clinic_id": clinic_id}

        # 2. Handle Real-time Messages
        if event == 'messages.upsert':
            messages = data.get('messages', []) if isinstance(data.get('messages'), list) else [data]
            for message_data in messages:
                if message_data.get('key', {}).get('fromMe'):
                    continue
                
                background_tasks.add_task(process_single_message_data, message_data, instance_id, clinic_id)
            
            return {"status": "upsert_processed", "clinic_id": clinic_id}

        return {"status": "event_unhandled", "event": event}

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return {"status": "error", "detail": str(e)}
```

## 2. Atualizar process_single_message_data (linha ~147)

Substituir a função por:

```python
async def process_single_message_data(data: dict, instance_id: str, clinic_id: str):
    """
    Helper to extract details and queue the lead processor.
    Also saves message to WhatsApp tables for chat integration.
    Multi-tenant: uses clinic_id for data isolation.
    """
    try:
        remote_jid = data.get('key', {}).get('remoteJid')
        if not remote_jid or '@s.whatsapp.net' not in remote_jid:
            return

        push_name = data.get('pushName', 'Desconhecido')
        message_info = data.get('message', {})
        message_id = data.get('key', {}).get('id', str(uuid.uuid4()))
        timestamp = data.get('messageTimestamp')
        is_from_me = data.get('key', {}).get('fromMe', False)
        
        # Tentar extrair texto
        text_content = ""
        message_type = "text"
        media_url = None
        
        if 'conversation' in message_info:
            text_content = message_info['conversation']
        elif 'extendedTextMessage' in message_info:
            text_content = message_info['extendedTextMessage'].get('text', '')
        elif 'imageMessage' in message_info:
            text_content = message_info['imageMessage'].get('caption', '[Imagem]')
            message_type = "image"
            media_url = message_info['imageMessage'].get('url')
        elif 'videoMessage' in message_info:
            text_content = message_info['videoMessage'].get('caption', '[Vídeo]')
            message_type = "video"
            media_url = message_info['videoMessage'].get('url')
            
        if not text_content:
            return

        # Save to WhatsApp tables for chat integration
        await save_whatsapp_message(
            clinic_id=clinic_id,
            phone=remote_jid.split('@')[0],
            contact_name=push_name,
            message_id=message_id,
            content=text_content,
            message_type=message_type,
            media_url=media_url,
            timestamp=datetime.fromtimestamp(int(timestamp)).isoformat() if timestamp else None,
            is_from_me=is_from_me
        )

        # Process lead (existing functionality)
        if not is_from_me:
            await process_new_lead(remote_jid, push_name, text_content, instance_id)
    except Exception as e:
        logger.error(f"Error processing single message: {e}")
```

## Resumo das Mudanças

1. ✅ `get_clinic_id_from_instance` - JÁ ADICIONADA
2. ✅ `save_whatsapp_message` - JÁ ATUALIZADA com clinic_id
3. ⚠️ `receive_whatsapp_message` - PRECISA ATUALIZAR (adicionar clinic_id mapping)
4. ⚠️ `process_single_message_data` - PRECISA ATUALIZAR (adicionar clinic_id parameter e WhatsApp saving)

## Como Aplicar

Abra `backend/app/api/webhooks.py` e faça as substituições manualmente nas funções indicadas.
