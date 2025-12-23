# Guia: Recebendo Conversas no Sistema (Webhooks)

Para que as conversas do WhatsApp apareçam no sistema em tempo real, você precisa configurar os **Webhooks** no painel da UazAPI.

## 📡 O que é um Webhook?

É a forma como a UazAPI avisa o nosso backend que chegou uma nova mensagem. Sem isso, o sistema fica "cego" para o que os clientes enviam.

---

## 🔧 Como configurar agora:

### 1. Se o sistema estiver rodando na nuvem (Vercel/DigitalOcean):
1. Acesse o painel da UazAPI.
2. Vá em **Instâncias** → **Configurações da Instância**.
3. No campo **URL do Webhook**, cole o seu endereço do backend:
   ```
   https://seu-dominio.com/api/webhooks/whatsapp
   ```
4. Salve as alterações.

### 2. Se você estiver testando no computador (Localhost):
O WhatsApp não consegue "falar" com o seu `localhost` diretamente. Você precisa de um túnel (como o **ngrok**):

1. **Baixe o ngrok**: [ngrok.com](https://ngrok.com)
2. **Abra o terminal e rode**:
   ```bash
   ngrok http 8000
   ```
3. O ngrok vai te dar um link parecido com: `https://abcd-123.ngrok-free.app`
4. Na UazAPI, use este link como Webhook:
   ```
   https://abcd-123.ngrok-free.app/api/webhooks/whatsapp
   ```

---

## ✅ O que acontece depois de configurar:

1. Quando um cliente enviar uma mensagem, a UazAPI vai chamar o nosso backend.
2. O sistema vai:
   - Identificar o paciente (ou criar um novo automaticamente no **CRM**).
   - Salvar a mensagem no **Supabase**.
   - Chamar a **Carol (IA)** para gerar uma resposta inteligente.
   - Enviar a resposta de volta ao cliente via WhatsApp.
3. **Você verá tudo isso** na aba de **Chat** do Bem-Querer Hub! 🦷✨

---

## 🛠️ Verificação Técnica (Backend)

Já implementei os endpoints necessários para que o frontend mostre os dados:
- `GET /api/chat/list`: Traz a lista de todas as conversas ativas.
- `GET /api/chat/{id}/messages`: Traz o histórico completo daquela conversa.

**Tudo pronto para rodar!** Assim que as primeiras mensagens chegarem via Webhook, seu Chat ganhará vida. 🚀
