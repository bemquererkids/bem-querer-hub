import axios from 'axios';
import { Deal } from '../types/crm';

// TODO: Get from env var
const API_URL = 'http://localhost:8000'; 

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
    sendMessage: async (message: string) => {
        const response = await api.post('/chat/message', { message });
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