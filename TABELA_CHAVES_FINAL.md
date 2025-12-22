# 📋 Guia Definitivo: Variáveis na Vercel

Para organizar a confusão, aqui está a lista exata do que você precisa colocar no painel da Vercel. 

### 💡 Dica de Ouro:
Várias chaves se repetem (umas com `VITE_` e outras sem). **Isso é normal**. O Frontend (Vite) exige o prefixo, o Backend (Python) exige o nome limpo.

---

## 🏗️ Grupo 1: Banco de Dados (Supabase)
*São 5 variáveis no total para este grupo.*

| Nome da Variável | Valor | Destinado a |
| :--- | :--- | :--- |
| **`SUPABASE_URL`** | URL do Projeto | Backend |
| **`SUPABASE_KEY`** | Anon Key | Backend |
| **`VITE_SUPABASE_URL`** | **MESMA URL** acima | Frontend (Vite) |
| **`VITE_SUPABASE_KEY`** | **MESMA Anon Key** acima | Frontend (Vite) |
| **`SUPABASE_SERVICE_KEY`**| Service Role Key | Backend (Poderosa) |

## 🧠 Grupo 2: Inteligência Artificial & Segurança
| Nome da Variável | Valor | Destinado a |
| :--- | :--- | :--- |
| **`OPENAI_API_KEY`** | Sua chave `sk-...` | Backend (Carol) |
| **`SECRET_KEY`** | Uma senha aleatória | Backend (JWT) |

## 💬 Grupo 3: WhatsApp (UazAPI)
| Nome da Variável | Valor | Destinado a |
| :--- | :--- | :--- |
| **`UAZAPI_BASE_URL`** | URL da instância | Backend |
| **`UAZAPI_TOKEN`** | Token Global | Backend |

## 🔗 Grupo 4: Links Internos
| Nome da Variável | Valor | Destinado a |
| :--- | :--- | :--- |
| **`VITE_API_URL`** | `/api` | Frontend |

---

### ✅ Checklist Final após inserir as chaves:
1. [ ] Clicou em **Save** em todas?
2. [ ] Foi na aba **Deployments**?
3. [ ] Clicou nos `...` do último build e selecionou **Redeploy**? (Isso é obrigatório para as chaves `VITE_` funcionarem).
