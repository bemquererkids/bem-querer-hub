/// <reference types="vite/client" />
import axios from 'axios';
import { Deal } from '../types/crm';

// Get API URL from Environment (Vite) or fallback to local/relative
const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000/api' : '/api');

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
  }
};

export const chatService = {
  getChats: async () => {
    const response = await api.get('/chat/list'); // Assuming this endpoint exists or mock handles it
    return response.data;
  },
  getMessages: async (chatId: string) => {
    const response = await api.get(`/chat/${chatId}/messages`);
    return response.data;
  },
  sendMessage: async (chatId: string, message: string) => {
    const response = await api.post('/chat/message', { chat_id: chatId, message });
    return response.data;
  }
};

export const integrationService = {
  connectClinicorp: async (clientId: string, clientSecret: string) => {
    const response = await api.post('/integrations/clinicorp/configure', {
      client_id: clientId,
      client_secret: clientSecret
    });
    return response.data;
  }
};