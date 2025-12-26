import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { ChatContact } from '../types/chat';

export const useWhatsAppChats = () => {
    const [chats, setChats] = useState<ChatContact[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Load initial chats
        loadChats();

        // Subscribe to realtime updates
        const subscription = supabase
            .channel('whatsapp_updates')
            .on('postgres_changes', {
                event: '*',
                schema: 'public',
                table: 'whatsapp_conversations'
            }, () => {
                loadChats(); // Reload when conversations change
            })
            .subscribe();

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    const loadChats = async () => {
        try {
            const { data, error: fetchError } = await supabase
                .from('whatsapp_conversations')
                .select('*')
                .order('last_message_at', { ascending: false });

            if (fetchError) throw fetchError;

            // Transform to ChatContact format
            const transformed: ChatContact[] = (data || []).map(conv => ({
                id: conv.id,
                name: conv.contact_name || conv.phone_number,
                lastMessage: conv.last_message || '',
                lastMessageTime: formatTime(conv.last_message_at),
                unreadCount: conv.unread_count || 0,
                tags: conv.tags || [],
                avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(conv.contact_name || conv.phone_number)}&background=random&size=128`
            }));

            setChats(transformed);
            setError(null);
        } catch (err) {
            console.error('Error loading WhatsApp chats:', err);
            setError(err instanceof Error ? err.message : 'Failed to load chats');
        } finally {
            setLoading(false);
        }
    };

    const markAsRead = async (conversationId: string) => {
        try {
            await supabase
                .from('whatsapp_conversations')
                .update({ unread_count: 0 })
                .eq('id', conversationId);

            // Reload to update UI
            loadChats();
        } catch (err) {
            console.error('Error marking as read:', err);
        }
    };

    return {
        chats,
        loading,
        error,
        refresh: loadChats,
        markAsRead
    };
};

function formatTime(timestamp: string | null): string {
    if (!timestamp) return '';

    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    // Less than 24 hours - show time
    if (diff < 86400000) {
        return date.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Less than 7 days - show day of week
    if (diff < 604800000) {
        return date.toLocaleDateString('pt-BR', {
            weekday: 'short'
        });
    }

    // Older - show date
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit'
    });
}
