import React, { useState, useEffect } from 'react';
import { ChatSidebar } from './ChatSidebar';
import { ChatWindow } from './ChatWindow';
import { WhatsAppEmptyState } from './WhatsAppEmptyState';
import { chatService } from '../../services/api';
import { ChatContact, ChatMessage } from '../../types/chat';
import { Card } from '../ui/card';
import { RefreshCw } from 'lucide-react';

export const ChatLayout: React.FC = () => {
    const [chats, setChats] = useState<ChatContact[]>([]);
    const [activeChatId, setActiveChatId] = useState<string | undefined>(undefined);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [loading, setLoading] = useState(true);

    // Fetch Chat List with timeout
    useEffect(() => {
        const fetchChats = async () => {
            try {
                const data = await chatService.getChats();
                setChats(data);
            } catch (error) {
                console.error("Failed to fetch chats", error);
                setChats([]);
            } finally {
                setLoading(false);
            }
        };

        // Reduced timeout from 5s to 3s
        const timeout = setTimeout(() => {
            setLoading(false);
            setChats([]);
        }, 3000);

        fetchChats().then(() => clearTimeout(timeout));

        return () => clearTimeout(timeout);
    }, []);

    // Fetch Messages when Active Chat changes
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
        // Optimistic update logic handled in ChatWindow
    };

    const activeChat = chats.find(c => c.id === activeChatId);

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center bg-white dark:bg-card rounded-lg">
                <div className="flex flex-col items-center gap-2">
                    <RefreshCw className="animate-spin text-indigo-600 dark:text-primary w-8 h-8" />
                    <p className="text-sm text-zinc-500 dark:text-muted-foreground">Carregando conversas...</p>
                </div>
            </div>
        );
    }

    // Show empty state if no chats available (WhatsApp not connected)
    if (chats.length === 0) {
        return <WhatsAppEmptyState />;
    }

    return (
        <div className="h-full animate-in fade-in slide-in-from-bottom-4 duration-300">
            <Card className="h-full flex overflow-hidden border-zinc-200 dark:border-border shadow-sm rounded-lg bg-white dark:bg-card">
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
        </div>
    );
};
