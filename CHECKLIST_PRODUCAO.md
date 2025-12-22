# 🏁 Checklist de Produção (Bem-Querer Hub)

Para transformar este protótipo em um sistema de produção real, siga este checklist técnico:

## 1. 🛠️ Mudanças no Código (Escalabilidade)
- [ ] **Desmontar Hardcodes**: Em `clinicorp_service.py`, os campos `subscriber_id` e `code_link` estão fixos como 'bemquerer'. Eles precisam ser movidos para o banco de dados (tabela de configurações da clínica).
- [ ] **Multi-tenancy Real**: O `clinic_id` no webhook está fixo como `000...001`. Em produção, ele deve vir da configuração da instância no Banco de Dados.
- [ ] **RAG (Pesquisa em PDF/Docs)**: A Carol responde bem, mas para ela saber os preços e detalhes dos seus procedimentos, precisamos terminar a implementação da busca semântica (embeddings).

## 2. 🚀 Infraestrutura (Vercel)
- [ ] **Variáveis de Ambiente**: Preencher todas as chaves no painel da Vercel (conforme o guia criado).
- [ ] **Atenção Frontend**: Garantiu que as chaves do Supabase foram duplicadas com o prefixo `VITE_`? (Ex: `VITE_SUPABASE_URL`). Sem isso, o cadastro não funciona.
- [ ] **Build Check**: Mover o `requirements.txt` para a raiz para a Vercel instalar as dependências corretamente.
- [ ] **OpenAI Plan**: Garantir que a conta na OpenAI tenha créditos, pois o modelo `gpt-4-turbo` é pago por uso.

## 3. 💬 Integrações Externas
- [ ] **UazAPI (Live)**: No painel da UazAPI, configure o Webhook URL para o endereço da sua Vercel (Ex: `https://seu-app.vercel.app/webhooks/whatsapp`).
- [ ] **Clinicorp (API Real)**: Verificar com o suporte da Clinicorp se sua chave tem permissão para os endpoints de `/appointment` e `/patients`.

## 4. 🔒 Segurança
- [ ] **Service Role Key**: Na Vercel, a `SUPABASE_SERVICE_KEY` é poderosa. Nunca a exponha no Frontend.
- [ ] **CORS**: Atualmente o backend aceita `*` (qualquer site). Em produção, mude para apenas o seu domínio da Vercel.

---

> [!TIP]
> **Estado Atual**: O sistema está pronto para ser **testado em produção (Fase Beta)**. Você pode fazer o commit, dar o push e as funções básicas de Chat e CRM devem funcionar imediatamente se as chaves forem configuradas.
