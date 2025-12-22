import { ChatContact, ChatMessage } from '../types/chat';

export const MOCK_CHATS: ChatContact[] = [
    {
        id: '1',
        name: 'Maria Silva (Mãe do Pedro)',
        lastMessage: 'Meu filho está com muita dor de dente, é urgente!',
        lastMessageTime: '10:45',
        unreadCount: 2,
        status: 'online',
        tags: ['emergency']
    },
    {
        id: '2',
        name: 'João Souza',
        lastMessage: 'Gostaria de saber o preço do aparelho invisível.',
        lastMessageTime: '09:30',
        unreadCount: 0,
        status: 'online',
        tags: ['financial', 'question']
    },
    {
        id: '3',
        name: 'Ana Paula (Mãe da Julia)',
        lastMessage: 'Confirmado para amanhã às 14h.',
        lastMessageTime: 'Ontem',
        unreadCount: 0,
        status: 'offline',
        tags: ['schedule']
    }
];

export const MOCK_MESSAGES: ChatMessage[] = [
    {
        id: 'm1',
        content: 'Olá, bom dia! Gostaria de marcar uma consulta.',
        type: 'text',
        sender: 'user',
        timestamp: '2023-12-21T10:40:00',
        status: 'read'
    },
    {
        id: 'm2',
        content: 'Olá Maria! Claro, sou a Carol, assistente virtual. É para você ou para seu filho?',
        type: 'text',
        sender: 'system', // AI
        timestamp: '2023-12-21T10:40:05',
        status: 'read'
    },
    {
        id: 'm3',
        content: 'Para o Pedro, ele tem 5 anos.',
        type: 'text',
        sender: 'user',
        timestamp: '2023-12-21T10:41:00',
        status: 'read'
    },
    {
        id: 'm4',
        content: 'Entendi. Ele está sentindo alguma dor ou é apenas rotina?',
        type: 'text',
        sender: 'agent', // Human took over
        timestamp: '2023-12-21T10:42:00',
        status: 'read'
    },
    {
        id: 'm5',
        content: 'Meu filho está com muita dor de dente, é urgente!',
        type: 'text',
        sender: 'user',
        timestamp: '2023-12-21T10:45:00',
        status: 'delivered'
    }
];
