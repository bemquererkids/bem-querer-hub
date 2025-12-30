/// <reference types="vite/client" />
import axios from 'axios';
import { Deal } from '../types/crm';

// Get API URL from Environment (Vite) or fallback to local/relative
const envApiUrl = import.meta.env.VITE_API_URL;
// Always use relative path to leverage Vite Proxy in dev and relative path in prod
const API_URL = envApiUrl || '/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Simple interceptor to inject token (Mock for now or if we had auth)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const crmService = {
  getDeals: async (): Promise<Deal[]> => {
    const response = await api.get<Deal[]>('/crm/deals');
    return response.data;
  },
  updateDealStatus: async (dealId: string, status: string) => {
    const response = await api.put(`/crm/deals/${dealId}/status`, { status });
    return response.data;
  },
  updateDealValue: async (dealId: string, value: number) => {
    const response = await api.put(`/crm/deals/${dealId}/value`, { value });
    return response.data;
  },
  getMetrics: async () => {
    const response = await api.get('/crm/metrics');
    return response.data;
  }
};

export const chatService = {
  getChats: async () => {
    const response = await api.get('/chat/conversations');
    return response.data;
  },
  getMessages: async (chatId: string) => {
    const response = await api.get(`/chat/messages/${chatId}`);
    return response.data;
  },
  sendMessage: async (conversationId: string, message: string) => {
    const response = await api.post('/chat/send', {
      conversation_id: conversationId,
      message
    });
    return response.data;
  },
  markAsRead: async (conversationId: string) => {
    const response = await api.post(`/chat/read/${conversationId}`);
    return response.data;
  },
  sendMedia: async (conversationId: string, mediaUrl: string, mediaType: 'image' | 'audio' | 'document', caption?: string, filename?: string) => {
    const response = await api.post('/chat/send-media', {
      conversation_id: conversationId,
      media_url: mediaUrl,
      media_type: mediaType,
      caption,
      filename
    });
    return response.data;
  }
};

export const integrationService = {
  connectClinicorp: async (clientId: string, clientSecret: string) => {
    const response = await api.post('/integrations/clinicorp/connect', {
      client_id: clientId,
      client_secret: clientSecret
    });
    return response.data;
  },
  connectWhatsApp: async () => {
    const response = await api.post('/integrations/whatsapp/connect');
    return response.data;
  },
  getWhatsAppStatus: async () => {
    const response = await api.get('/integrations/whatsapp/status');
    return response.data;
  },
  getClinicorpStatus: async () => {
    const response = await api.get('/integrations/clinicorp/status');
    return response.data;
  },
  connectOpenAI: async (apiKey: string) => {
    const response = await api.post('/integrations/openai/connect', { api_key: apiKey });
    return response.data;
  },
  getOpenAIStatus: async () => {
    const response = await api.get('/integrations/openai/status');
    return response.data;
  },
  connectGemini: async (apiKey: string) => {
    const response = await api.post('/integrations/gemini/connect', { api_key: apiKey });
    return response.data;
  },
  getGeminiStatus: async () => {
    const response = await api.get('/integrations/gemini/status');
    return response.data;
  }
};

export const productivityService = {
  // Notes
  getNotes: async (conversationId: string) => {
    const response = await api.get(`/notes/${conversationId}`);
    return response.data;
  },
  createNote: async (conversationId: string, content: string) => {
    const response = await api.post('/notes', { conversation_id: conversationId, content });
    return response.data;
  },
  deleteNote: async (noteId: string) => {
    const response = await api.delete(`/notes/${noteId}`);
    return response.data;
  },

  // Reminders
  getReminders: async (conversationId: string) => {
    const response = await api.get(`/reminders/${conversationId}`);
    return response.data;
  },
  createReminder: async (conversationId: string, title: string, dueAt: string) => {
    const response = await api.post('/reminders', { conversation_id: conversationId, title, due_at: dueAt });
    return response.data;
  },
  updateReminderStatus: async (reminderId: string, status: string) => {
    const response = await api.put(`/reminders/${reminderId}/status`, { status });
    return response.data;
  },

  // Tags
  addTag: async (conversationId: string, tag: string) => {
    const response = await api.post(`/tags/${conversationId}`, { tag });
    return response.data;
  },
  removeTag: async (conversationId: string, tag: string) => {
    const response = await api.delete(`/tags/${conversationId}`, { data: { tag } });
    return response.data;
  }
};