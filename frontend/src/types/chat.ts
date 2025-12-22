export type MessageType = 'text' | 'audio' | 'image' | 'document';
export type MessageSender = 'user' | 'agent' | 'system';

export interface Message {
    id: string;
    content: string;
    type: MessageType;
    sender: MessageSender;
    timestamp: string; // ISO string
    status: 'sent' | 'delivered' | 'read';
}

export interface ChatContact {
    id: string;
    name: string;
    avatarUrl?: string;
    lastMessage: string;
    lastMessageTime: string;
    unreadCount: number;
    status: 'open' | 'waiting' | 'closed';
    tags: ('emergency' | 'schedule' | 'financial' | 'question')[];
}

export interface PatientContext {
    id: string;
    name: string;
    age: number;
    guardianName?: string; // Nome da mãe/responsável
    nextAppointment?: string;
    lastVisit?: string;
}
