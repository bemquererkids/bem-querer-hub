# 🗝️ Guia de Variáveis de Ambiente para Vercel

Para que o **Bem-Querer Hub** funcione corretamente em produção, você deve configurar as seguintes variáveis no painel da Vercel (**Settings > Environment Variables**).

## 🚀 Obrigatórias (Core)
| Variável | Descrição | Onde conseguir |
| :--- | :--- | :--- |
| `SUPABASE_URL` | URL do seu projeto Supabase (Backend) | Dashboard Supabase > Settings > API |
| `SUPABASE_KEY` | Anon Key (Public) (Backend) | Dashboard Supabase > Settings > API |
| `VITE_SUPABASE_URL` | IGUAL ao SUPABASE_URL (Front) | Necessário para o Vite ver a variável |
| `VITE_SUPABASE_KEY` | IGUAL ao SUPABASE_KEY (Front) | Necessário para o Vite ver a variável |
| `SUPABASE_SERVICE_KEY`| Service Role Key (Bypass RLS) | Dashboard Supabase > Settings > API |
| `SECRET_KEY` | Chave para tokens JWT | Use o `backend\generate_secret.bat` |

## 🧠 Inteligência Artificial (Carol)
| Variável | Descrição | Onde conseguir |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | Chave da OpenAI para o GPT-4 | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `GEMINI_API_KEY` | Chave para o Google Gemini (Legacy) | [Google AI Studio](https://aistudio.google.com/app/apikey) |

## 💬 WhatsApp (UazAPI)
| Variável | Descrição | Onde conseguir |
| :--- | :--- | :--- |
| `UAZAPI_BASE_URL` | URL da sua instância UazAPI | Fornecido pela UazAPI |
| `UAZAPI_TOKEN` | Token de autorização | Fornecido pela UazAPI em 'Global Token' |

## 🦷 Integração Clinicorp
| Variável | Descrição | Onde conseguir |
| :--- | :--- | :--- |
| `CLINICORP_API_URL` | URL da API do Clinicorp | [Clinicorp Docs](https://clinicorp.com) |
| `CLINICORP_API_KEY` | Chave de Integração | Painel Clinicorp |

---

> [!IMPORTANT]
> **Atenção**: Não use aspas nos valores dentro do painel da Vercel. 
> Exemplo: `https://xyz.supabase.co` (CORRETO) e não `"https://xyz.supabase.co"` (ERRADO).

> [!TIP]
> O backend foi configurado para entrar em **Mock Mode** automaticamente se alguma dessas chaves estiver faltando, permitindo que o sistema "suba" mesmo sem as chaves, mas as funções de IA e WhatsApp real só funcionarão após a configuração.
