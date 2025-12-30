export interface ChatContact {
    id: string;
    name: string;
    lastMessage: string;
    lastMessageTime: string;
    unreadCount: number;
    tags: string[];
    avatar?: string;
    phoneNumber?: string;
    status?: 'online' | 'offline';
}

export interface ChatMessage {
    id: string;
    content: string;
    sender: 'user' | 'agent' | 'system';
    timestamp: string;
    type: 'text' | 'image' | 'audio' | 'document';
    status?: 'sent' | 'delivered' | 'read';
}