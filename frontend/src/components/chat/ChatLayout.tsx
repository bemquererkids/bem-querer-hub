import React, { useState } from 'react';
import { ChatSidebar } from './ChatSidebar';
import { ChatWindow } from './ChatWindow';
import { chatService } from '../../services/api';
import { ChatContact, ChatMessage } from '../../types/chat';
import { Card } from '../ui/card';
import { Loader2 } from 'lucide-react';

export const ChatLayout: React.FC = () => {
    const [chats, setChats] = useState<ChatContact[]>([]);
    const [activeChatId, setActiveChatId] = useState<string | undefined>(undefined);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [loading, setLoading] = useState(true);

    // 1. Fetch Chat List
    useEffect(() => {
        const fetchChats = async () => {
            try {
                const data = await chatService.getChats();
                setChats(data);
                if (data.length > 0 && !activeChatId) {
                    // Do not auto-select to avoid noise, or select first
                }
            } catch (error) {
                console.error("Failed to fetch chats", error);
            } finally {
                setLoading(false);
            }
        };
        fetchChats();
    }, []);

    // 2. Fetch Messages when Active Chat changes
    useEffect(() => {
        if (!activeChatId) return;

        const fetchMessages = async () => {
            try {
                const data = await chatService.getMessages(activeChatId);
                setMessages(data);
            } catch (error) {
                console.error("Failed to fetch messages", error);
            }
        };
        fetchMessages();
    }, [activeChatId]);

    const handleSendMessage = (text: string) => {
        // Optimistic update logic is now handled inside ChatWindow for better UX
        // but we keep the state sync here if needed for global context
    };

    const activeChat = chats.find(c => c.id === activeChatId);

    if (loading) {
        return <div className="h-full flex items-center justify-center bg-white rounded-xl shadow-sm"><Loader2 className="animate-spin text-blue-500 w-8 h-8" /></div>;
    }

    return (
        <Card className="h-full flex overflow-hidden border-border shadow-sm rounded-xl bg-white">
            <ChatSidebar
                chats={chats}
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
