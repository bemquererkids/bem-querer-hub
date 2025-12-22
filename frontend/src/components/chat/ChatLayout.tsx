import React, { useState } from 'react';
import { ChatSidebar } from './ChatSidebar';
import { ChatWindow } from './ChatWindow';
import { MOCK_CHATS, MOCK_MESSAGES } from '../../services/mockData';
import { Card } from '../ui/card';

export const ChatLayout: React.FC = () => {
    const [activeChatId, setActiveChatId] = useState<string | undefined>(undefined);
    const [messages, setMessages] = useState(MOCK_MESSAGES);

    const handleSendMessage = (text: string) => {
        const newMessage = {
            id: Date.now().toString(),
            content: text,
            type: 'text' as const,
            sender: 'agent' as const,
            timestamp: new Date().toISOString(),
            status: 'sent' as const
        };
        setMessages([...messages, newMessage]);
    };

    const activeChat = MOCK_CHATS.find(c => c.id === activeChatId);

    return (
        <Card className="h-full flex overflow-hidden border-border shadow-sm rounded-xl">
            <ChatSidebar 
                chats={MOCK_CHATS} 
                activeChatId={activeChatId}
                onSelectChat={setActiveChatId}
            />
            <ChatWindow 
                chat={activeChat}
                messages={activeChatId ? messages : []} 
                onSendMessage={handleSendMessage}
            />
        </Card>
    );
};
