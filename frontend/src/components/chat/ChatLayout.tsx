import React, { useState, useEffect } from 'react';
import { ChatSidebar } from './ChatSidebar';
import { ChatWindow } from './ChatWindow';
import { WhatsAppEmptyState } from './WhatsAppEmptyState';
import { chatService } from '../../services/api';
import { supabase } from '../../services/supabase';
import { ChatContact, ChatMessage } from '../../types/chat';
import { Card } from '../ui/card';
import { RefreshCw } from 'lucide-react';
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { formatTime } from '../../utils/formatDate';

export const ChatLayout: React.FC<{ onNavigateToDeal?: (dealId: string) => void }> = ({ onNavigateToDeal }) => {
    const [chats, setChats] = useState<ChatContact[]>([]);
    const [activeChatId, setActiveChatId] = useState<string | undefined>(undefined);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingMessages, setLoadingMessages] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Fetch Chat List with timeout
    useEffect(() => {
        const fetchChats = async () => {
            try {
                const data = await chatService.getChats();

                // Transform data using our strict date formatter
                const formattedData = (data || []).map((chat: any) => ({
                    ...chat,
                    lastMessageTime: formatTime(chat.lastMessageTime)
                }));

                setChats(formattedData);
                setError(null);
            } catch (err) {
                console.error("Failed to fetch chats", err);
                setError(err instanceof Error ? err.message : 'Unknown error');
                setChats([]);
            } finally {
                setLoading(false);
            }
        };

        fetchChats();

        // REALTIME SUBSCRIPTION FOR CHAT LIST
        const subscription = supabase
            .channel('public:whatsapp_conversations')
            .on('postgres_changes', {
                event: '*',
                schema: 'public',
                table: 'whatsapp_conversations'
            }, async (payload) => {
                // Simplest strategy: Refetch list on any change to ensure correct sorting/counts
                // Optimally we would merge payload, but refetch is safer for consistency
                await fetchChats();
            })
            .subscribe();

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    // Fetch Messages & Mark as Read when Active Chat changes
    useEffect(() => {
        if (!activeChatId) return;

        const handleChatSelection = async () => {
            // 0. Clear previous messages to avoid visual mix
            setMessages([]);
            setLoadingMessages(true);

            // 1. Optimistic Update locally
            setChats(prev => prev.map(c =>
                c.id === activeChatId ? { ...c, unreadCount: 0 } : c
            ));

            try {
                // 2. Mark as read on backend
                await chatService.markAsRead(activeChatId);

                // 3. Fetch messages
                const rawData = await chatService.getMessages(activeChatId);
                // Transform API data to Frontend Model
                const formattedMessages: ChatMessage[] = rawData.map((msg: any) => ({
                    id: msg.id,
                    content: msg.content,
                    // Map is_from_me to sender: true = agent (me), false = user
                    sender: msg.is_from_me ? 'agent' : 'user',
                    timestamp: msg.created_at,
                    type: msg.message_type || 'text',
                    status: 'read'
                }));
                setMessages(formattedMessages);
            } catch (error) {
                console.error("Failed to fetch messages or mark read", error);
            } finally {
                setLoadingMessages(false);
            }
        };

        handleChatSelection();
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

    // Always show chat interface, even if empty
    // WhatsAppEmptyState is only shown from settings page

    return (
        <div className="h-full w-full flex flex-col md:flex-row overflow-hidden bg-white dark:bg-card border-x border-zinc-200 dark:border-border shadow-sm">
            {/* SIDEBAR AREA */}
            <div className={`
                flex-none w-full md:w-80 lg:w-96 border-r border-zinc-200 dark:border-zinc-800 bg-white dark:bg-[#111b21] z-10
                ${activeChatId ? 'hidden md:flex' : 'flex'}
                flex-col h-full
            `}>
                <ChatSidebar
                    chats={chats}
                    activeChatId={activeChatId}
                    onSelectChat={setActiveChatId}
                    className="h-full w-full"
                />
            </div>

            {/* CHAT WINDOW AREA */}
            <div className={`
                flex-1 min-w-0 h-full bg-[#efeae2] dark:bg-[#0b141a] relative
                ${activeChatId ? 'flex' : 'hidden md:flex'}
                flex-col
            `}>
                {loadingMessages ? (
                    <div className="flex-1 flex items-center justify-center">
                        <div className="flex flex-col items-center gap-2">
                            <RefreshCw className="animate-spin text-cyan-600 w-8 h-8" />
                            <p className="text-sm text-slate-500">Carregando mensagens...</p>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 flex items-center justify-center bg-[#efeae2]">
                        <div className="text-center p-8 bg-white/80 rounded-xl shadow-sm backdrop-blur-sm max-w-md">
                            <div className="flex justify-center mb-4">
                                <ChatBubbleLeftRightIcon className="w-12 h-12 text-cyan-200" />
                            </div>
                            <h3 className="text-xl font-bold text-slate-800 mb-2">Selecione uma conversa</h3>
                            <p className="text-slate-500">Escolha um contato para gerenciar o atendimento em tempo real.</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
