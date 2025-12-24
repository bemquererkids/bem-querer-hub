# 🌐 Guia de Sincronização em Tempo Real (Localhost)

Para que as mensagens do WhatsApp apareçam no sistema enquanto você está desenvolvendo no seu computador (localhost), a **UazAPI** precisa de um caminho para "falar" com o seu backend. Como o seu computador não tem um endereço público na internet, precisamos usar o **Ngrok**.

## 1. Instalar o Ngrok
Se ainda não tem, baixe em: [ngrok.com/download](https://ngrok.com/download)

## 2. Criar o Túnel
Abra um terminal e digite:
```bash
ngrok http 8000
```
*Isso vai gerar um endereço como: `https://abcd-123.ngrok-free.app`*

## 3. Configurar o Backend
No seu arquivo `backend/.env`, atualize a variável `PUBLIC_URL` com esse novo endereço:
```env
PUBLIC_URL=https://abcd-123.ngrok-free.app
```
**Reinicie o backend** após salvar.

## 4. Sincronizar
1. No sistema, vá em **Configurações > Clínica**.
2. Clique em **Conectar WhatsApp** (ou verifique se já está online).
3. O sistema agora vai configurar automaticamente a UazAPI para enviar as mensagens para o seu túnel Ngrok.
4. **Pronto!** Agora, qualquer mensagem que você receber no WhatsApp vai aparecer instantaneamente no Chat.

---

### 💡 Dúvidas Frequentes:

**Preciso escanear no site da UazAPI e no App?**
Não! O seu App (Bem-Querer) já gerencia a instância. Ao escanear o QR Code no nosso sistema, você está linkando o seu celular diretamente à instância configurada. O site da UazAPI serve apenas para você gerenciar o plano ou pegar o Token, mas a operação diária é 100% pelo nosso sistema.

**Por que as mensagens antigas não aparecem?**
Assim que a conexão é estabelecida via Ngrok, a UazAPI envia um "pacote" com o histórico. O nosso backend já está preparado para processar esse pacote e criar os chats automaticamente.

**E se eu desligar o Ngrok?**
As mensagens enviadas enquanto o Ngrok estiver desligado serão processadas assim que você ligar o túnel e a UazAPI tentar reenviar os webhooks pendentes (ou quando houver uma nova interação).
