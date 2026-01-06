import React, { useState, useEffect, useRef } from 'react';
import { ChatContact, ChatMessage } from '../../types/chat';
import { supabase } from '../../services/supabase';
import { Send, Paperclip, Mic, MoreVertical, Phone, Video, ChevronLeft, ChevronDown, CheckCircle2, StickyNote, Bell, Tag, Trash2, Plus, Calendar as CalendarIcon, Clock, X } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { chatService, crmService, productivityService } from '../../services/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { Badge } from '../ui/badge';

interface ChatWindowProps {
    chat?: ChatContact;
    messages: ChatMessage[];
    onSendMessage: (text: string) => void;
    onBack?: () => void;
    onNavigateToDeal?: (dealId: string) => void;
}

const formatPhoneNumber = (phone: string) => {
    if (!phone) return '';
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 13) return `+${cleaned.slice(0, 2)} (${cleaned.slice(2, 4)}) ${cleaned.slice(4, 9)}-${cleaned.slice(9)}`;
    if (cleaned.length === 12) return `+${cleaned.slice(0, 2)} (${cleaned.slice(2, 4)}) ${cleaned.slice(4, 8)}-${cleaned.slice(8)}`;
    return phone;
};

// Types for Productivity Features
interface Note {
    id: string;
    content: string;
    created_at: string;
}

interface Reminder {
    id: string;
    title: string;
    due_at: string;
    status: 'pending' | 'completed' | 'cancelled';
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ chat, messages: initialMessages, onSendMessage, onBack, onNavigateToDeal }) => {
    const [newMessage, setNewMessage] = useState('');
    const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
    const [isTyping, setIsTyping] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [isRecording, setIsRecording] = useState(false);

    // Productivity State
    const [showProductivity, setShowProductivity] = useState(false);
    const [notes, setNotes] = useState<Note[]>([]);
    const [reminders, setReminders] = useState<Reminder[]>([]);
    const [newNote, setNewNote] = useState('');
    const [newReminderTitle, setNewReminderTitle] = useState('');
    const [newReminderDate, setNewReminderDate] = useState('');
    const [newReminderTime, setNewReminderTime] = useState('');
    const [activeTab, setActiveTab] = useState('notes');

    const scrollRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    useEffect(() => {
        setMessages(initialMessages);
    }, [initialMessages]);

    useEffect(() => {
        if (!chat?.id) return;

        // Fetch productivity data
        fetchProductivityData();

        const subscription = supabase
            .channel(`chat:${chat.id}`)
            .on('postgres_changes', {
                event: 'INSERT',
                schema: 'public',
                table: 'whatsapp_messages',
                filter: `conversation_id=eq.${chat.id}`
            }, (payload) => {
                console.log('[Realtime] Nova mensagem recebida:', payload);
                console.log('[Realtime] Payload.new completo:', JSON.stringify(payload.new, null, 2));
                const newMsg = payload.new;

                // Log all fields for debugging
                console.log('[Realtime] Campos da mensagem:', {
                    id: newMsg.id,
                    message_id: newMsg.message_id,
                    content: newMsg.content,
                    is_from_me: newMsg.is_from_me,
                    created_at: newMsg.created_at,
                    message_type: newMsg.message_type,
                    conversation_id: newMsg.conversation_id
                });

                // Use message_id from database as the unique identifier
                const messageId = newMsg.message_id || newMsg.id;
                console.log('[Realtime] messageId final:', messageId);

                setMessages(prev => {
                    console.log('[Realtime] Estado atual de mensagens:', prev.length, 'mensagens');
                    console.log('[Realtime] IDs existentes:', prev.map(m => m.id));

                    // Check if message already exists using message_id
                    const alreadyExists = prev.some(m => m.id === messageId);

                    if (alreadyExists) {
                        console.log('[Realtime] Mensagem duplicada, ignorando. ID:', messageId);
                        return prev;
                    }

                    // IMPORTANT: Only ignore is_from_me messages if they already exist
                    // This allows AI responses (is_from_me: true from backend) to appear
                    // while preventing duplicates from optimistic updates
                    console.log('[Realtime] Mensagem nova detectada!', {
                        is_from_me: newMsg.is_from_me,
                        content: newMsg.content?.substring(0, 50)
                    });

                    const novaMensagem: ChatMessage = {
                        id: messageId,
                        content: newMsg.content,
                        sender: (newMsg.is_from_me ? 'agent' : 'user') as 'agent' | 'user',
                        timestamp: newMsg.created_at,
                        type: newMsg.message_type,
                        status: 'read'
                    };

                    console.log('[Realtime] Adicionando mensagem ao chat:', novaMensagem);
                    const novoEstado = [...prev, novaMensagem];
                    console.log('[Realtime] Novo estado terá:', novoEstado.length, 'mensagens');

                    return novoEstado;
                });
            })
            .subscribe((status) => {
                console.log('[Realtime] Subscription status:', status);
            });

        return () => {
            console.log('[Realtime] Unsubscribing from chat:', chat.id);
            subscription.unsubscribe();
        };
    }, [chat?.id]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isTyping]);

    const fetchProductivityData = async () => {
        if (!chat?.id) return;
        try {
            const [notesData, remindersData] = await Promise.all([
                productivityService.getNotes(chat.id),
                productivityService.getReminders(chat.id)
            ]);
            setNotes(notesData);
            setReminders(remindersData);
        } catch (error) {
            console.error("Failed to load productivity data", error);
        }
    };

    const handleCreateNote = async () => {
        if (!chat?.id || !newNote.trim()) return;
        try {
            const created = await productivityService.createNote(chat.id, newNote);
            setNotes(prev => [created, ...prev]);
            setNewNote('');
        } catch (error) {
            console.error("Failed to create note", error);
        }
    };

    const handleDeleteNote = async (id: string) => {
        try {
            await productivityService.deleteNote(id);
            setNotes(prev => prev.filter(n => n.id !== id));
        } catch (error) {
            console.error("Failed to delete note", error);
        }
    };

    const handleCreateReminder = async () => {
        if (!chat?.id || !newReminderTitle.trim() || !newReminderDate || !newReminderTime) return;
        try {
            const dueAt = new Date(`${newReminderDate}T${newReminderTime}`).toISOString();
            const created = await productivityService.createReminder(chat.id, newReminderTitle, dueAt);
            setReminders(prev => [...prev, created]); // Pending reminders usually at bottom or sorted by date
            setNewReminderTitle('');
            setNewReminderDate('');
            setNewReminderTime('');
        } catch (error) {
            console.error("Failed to create reminder", error);
        }
    };

    const handleToggleReminderStatus = async (id: string, currentStatus: string) => {
        try {
            const newStatus = currentStatus === 'pending' ? 'completed' : 'pending';
            await productivityService.updateReminderStatus(id, newStatus);
            setReminders(prev => prev.map(r => r.id === id ? { ...r, status: newStatus } : r));
        } catch (error) {
            console.error("Failed to update reminder", error);
        }
    };

    const handleMicClick = async () => {
        if (isRecording) {
            mediaRecorderRef.current?.stop();
            setIsRecording(false);
        } else {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const mediaRecorder = new MediaRecorder(stream);
                mediaRecorderRef.current = mediaRecorder;
                audioChunksRef.current = [];

                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) audioChunksRef.current.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                    const audioFile = new File([audioBlob], `voice_${Date.now()}.webm`, { type: 'audio/webm' });
                    setIsUploading(true);
                    try {
                        const fileName = `${chat?.id || 'temp'}/${Date.now()}_voice.webm`;
                        const { error: uploadError } = await supabase.storage.from('chat-media').upload(fileName, audioFile);
                        if (uploadError) throw uploadError;
                        const { data: { publicUrl } } = supabase.storage.from('chat-media').getPublicUrl(fileName);
                        if (chat?.id) {
                            await chatService.sendMedia(chat.id, publicUrl, 'audio');
                            setMessages(prev => [...prev, {
                                id: Date.now().toString(),
                                content: publicUrl,
                                sender: 'agent',
                                timestamp: new Date().toISOString(),
                                type: 'audio',
                                status: 'sent'
                            }]);
                        }
                    } catch (e) {
                        console.error("Audio upload failed", e);
                        alert("Erro ao enviar áudio");
                    } finally {
                        setIsUploading(false);
                        stream.getTracks().forEach(track => track.stop());
                    }
                };

                mediaRecorder.start();
                setIsRecording(true);
            } catch (err) {
                console.error("Mic permission denied", err);
                alert("Permissão de microfone negada.");
            }
        }
    };

    const handleSend = async () => {
        if (!newMessage.trim() || !chat?.id) return;
        const text = newMessage;
        setNewMessage('');

        // Optimistic update - add message immediately to UI
        const userMsg: ChatMessage = {
            id: `temp-${Date.now()}`,
            content: text,
            sender: 'agent',
            timestamp: new Date().toISOString(),
            type: 'text',
            status: 'sending'
        };
        setMessages(prev => [...prev, userMsg]);

        try {
            // Send message to backend
            const response = await chatService.sendMessage(chat.id, text);

            // Update message status to sent AND update ID to real DB ID
            // This is CRITICAL to avoid duplicates since Realtime will use this same ID
            setMessages(prev => prev.map(m =>
                m.id === userMsg.id ? { ...m, id: response.message_id || m.id, status: 'sent' } : m
            ));

            // AI response will come via Supabase realtime subscription
            // No need to wait for it here
        } catch (error) {
            console.error("Chat Error", error);
            // Mark message as failed
            setMessages(prev => prev.map(m =>
                m.id === userMsg.id ? { ...m, status: 'failed' } : m
            ));
        }
    };

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files || e.target.files.length === 0 || !chat) return;
        const file = e.target.files[0];
        setIsUploading(true);
        try {
            const fileExt = file.name.split('.').pop();
            const fileName = `${chat.id}/${Date.now()}.${fileExt}`;
            const { error: uploadError } = await supabase.storage.from('chat-media').upload(fileName, file);
            if (uploadError) throw uploadError;
            const { data: { publicUrl } } = supabase.storage.from('chat-media').getPublicUrl(fileName);
            let mediaType: 'image' | 'audio' | 'document' = 'document';
            if (file.type.startsWith('image/')) mediaType = 'image';
            else if (file.type.startsWith('audio/')) mediaType = 'audio';
            await chatService.sendMedia(chat.id, publicUrl, mediaType, undefined, file.name);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                content: publicUrl,
                sender: 'agent',
                timestamp: new Date().toISOString(),
                type: mediaType,
                status: 'sent'
            }]);
        } catch (error) {
            console.error("Upload failed", error);
            alert("Falha no envio do arquivo.");
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleStatusChange = async (newStatus: string) => {
        if (!chat) return;
        try {
            await crmService.updateDealStatus(chat.id, newStatus);
            if (onNavigateToDeal && typeof onNavigateToDeal === 'function') {
                onNavigateToDeal(chat.id);
            }
        } catch (e) {
            console.error("Failed to update status", e);
            alert("Erro ao atualizar status.");
        }
    };

    if (!chat) {
        return (
            <div className="flex-1 flex items-center justify-center bg-[#efeae2] h-full">
                <div className="text-center p-8 bg-white/80 rounded-xl shadow-sm backdrop-blur-sm max-w-md">
                    <h3 className="text-xl font-bold text-slate-800 mb-2">Bem-vindo ao Bem-Querer Chat</h3>
                    <p className="text-slate-500">Selecione uma conversa para iniciar o atendimento ou deixe a Carol trabalhar por você.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 flex h-full overflow-hidden bg-[#efeae2]">
            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col h-full min-w-0">
                {/* Header */}
                <div className="h-16 bg-white border-b border-border flex items-center justify-between px-4 shadow-sm z-10 shrink-0">
                    <div className="flex items-center gap-3">
                        {onBack && (
                            <Button variant="ghost" size="icon" className="md:hidden text-slate-500 -ml-2" onClick={onBack}>
                                <ChevronLeft className="w-6 h-6" />
                            </Button>
                        )}
                        <Avatar className="h-10 w-10 border border-slate-100 cursor-pointer">
                            <AvatarImage src={chat.avatar || `https://ui-avatars.com/api/?name=${(chat.name || 'Desconhecido').replace(' ', '+')}&background=random`} />
                            <AvatarFallback>{(chat.name || 'U').substring(0, 2).toUpperCase()}</AvatarFallback>
                        </Avatar>
                        <div className="cursor-pointer" title={`Nome: ${chat.name}\nTelefone: ${chat.phoneNumber || 'Não informado'}\nClique para ver detalhes`}>
                            <h3 className="font-bold text-slate-800 text-sm">{chat.name}</h3>
                            <p className="text-xs text-slate-500 font-medium">
                                {chat.phoneNumber ? formatPhoneNumber(chat.phoneNumber) : 'Carol (IA) Ativa'}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-1 text-slate-400">
                        <Button
                            variant="ghost"
                            size="sm"
                            className={`hidden md:flex gap-2 ${showProductivity ? 'text-cyan-600 bg-cyan-50' : 'text-slate-600'}`}
                            onClick={() => setShowProductivity(!showProductivity)}
                        >
                            <StickyNote className="w-4 h-4" />
                            <span className="text-xs font-medium">Notas e Lembretes</span>
                        </Button>
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="outline" size="sm" className="mr-2 gap-2 text-slate-600 border-slate-200">
                                    <span className="hidden md:inline">Funil</span>
                                    <ChevronDown className="w-4 h-4" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                {['Lead', 'Em Negociação', 'Agendado', 'Compareceu', 'Faltou', 'Venda Realizada'].map(status => (
                                    <DropdownMenuItem key={status} onClick={() => handleStatusChange(status)}>
                                        {status}
                                    </DropdownMenuItem>
                                ))}
                            </DropdownMenuContent>
                        </DropdownMenu>
                        <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setShowProductivity(!showProductivity)}>
                            <MoreVertical className="w-5 h-5" />
                        </Button>
                    </div>
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                    {messages.map((msg) => {
                        const isMe = msg.sender === 'agent';
                        return (
                            <div key={msg.id} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[70%] px-3 py-1.5 shadow-sm relative text-[14.2px] leading-relaxed ${isMe ? 'bg-[#d9fdd3] text-[#111b21] rounded-lg rounded-tr-none' : 'bg-white text-[#111b21] rounded-lg rounded-tl-none'}`}>
                                    <p className="whitespace-pre-wrap">{msg.content}</p>
                                    <div className="flex justify-end items-center gap-1 mt-1 select-none">
                                        <span className="text-[11px] text-[#667781] min-w-fit">
                                            {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                                        </span>
                                        {isMe && <span className={`text-[11px] ${msg.status === 'read' ? 'text-[#53bdeb]' : 'text-[#667781]'}`}>✓✓</span>}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                    {isTyping && (
                        <div className="flex justify-start animate-pulse">
                            <div className="bg-white rounded-lg p-2 rounded-tl-none shadow-sm flex gap-1 items-center">
                                <span className="w-1.5 h-1.5 bg-[#667781] rounded-full animate-bounce"></span>
                                <span className="w-1.5 h-1.5 bg-[#667781] rounded-full animate-bounce delay-100"></span>
                                <span className="w-1.5 h-1.5 bg-[#667781] rounded-full animate-bounce delay-200"></span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Area */}
                <div className="p-4 bg-white border-t border-slate-100 flex items-center gap-2">
                    <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileSelect} />
                    <Button variant="ghost" size="icon" className="text-slate-400 hover:text-cyan-600 hover:bg-cyan-50 transition-colors" onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
                        <Paperclip className="w-5 h-5" />
                    </Button>
                    <div className="flex-1 relative">
                        <Input value={newMessage} onChange={(e) => setNewMessage(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()} placeholder="Digite sua mensagem..." className="pr-10 bg-slate-50 border-slate-200 focus:border-cyan-500 focus:ring-cyan-500/20" />
                        <Button variant="ghost" size="icon" className={`absolute right-1 top-1 h-8 w-8 transition-colors ${isRecording ? 'text-red-500 hover:text-red-600 bg-red-50' : 'text-slate-400 hover:text-cyan-600'}`} onClick={handleMicClick} disabled={isUploading}>
                            {isRecording ? <div className="w-3 h-3 rounded-sm bgCurrent" style={{ backgroundColor: 'currentColor' }} /> : <Mic className="w-4 h-4" />}
                        </Button>
                    </div>
                    <Button onClick={handleSend} className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white shadow-lg shadow-cyan-500/30 rounded-full w-10 h-10 p-0 flex items-center justify-center transition-all hover:scale-105">
                        <Send className="w-4 h-4 ml-0.5" />
                    </Button>
                </div>
            </div>

            {/* Productivity Panel (Right Side) */}
            {showProductivity && (
                <div className="w-80 bg-white border-l border-border h-full flex flex-col shadow-xl animate-in slide-in-from-right duration-300">
                    <div className="p-4 border-b flex items-center justify-between bg-slate-50">
                        <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                            <Tag className="w-4 h-4" /> Produtividade
                        </h3>
                        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setShowProductivity(false)}>
                            <X className="w-4 h-4" />
                        </Button>
                    </div>
                    <div className="flex-1 overflow-hidden p-4">
                        <Tabs defaultValue="notes" className="h-full flex flex-col" value={activeTab} onValueChange={setActiveTab}>
                            <TabsList className="grid w-full grid-cols-2 mb-4">
                                <TabsTrigger value="notes" className="text-xs">Notas</TabsTrigger>
                                <TabsTrigger value="reminders" className="text-xs">Lembretes</TabsTrigger>
                            </TabsList>

                            {/* Notes Tab */}
                            <TabsContent value="notes" className="flex-1 flex flex-col min-h-0">
                                <div className="space-y-3 mb-4">
                                    <Textarea
                                        placeholder="Adicionar nota..."
                                        value={newNote}
                                        onChange={(e) => setNewNote(e.target.value)}
                                        className="text-sm min-h-[80px] resize-none"
                                    />
                                    <Button size="sm" className="w-full h-8" onClick={handleCreateNote}>
                                        <Plus className="w-3 h-3 mr-1" /> Adicionar Nota
                                    </Button>
                                </div>
                                <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                                    {notes.length === 0 ? (
                                        <div className="text-center text-slate-400 text-xs py-8">Nenhuma nota ainda.</div>
                                    ) : (
                                        notes.map(note => (
                                            <div key={note.id} className="bg-yellow-50 border border-yellow-100 p-3 rounded-lg relative group">
                                                <p className="text-sm text-slate-700 whitespace-pre-wrap">{note.content}</p>
                                                <div className="mt-2 flex justify-between items-center">
                                                    <span className="text-[10px] text-slate-400">
                                                        {new Date(note.created_at).toLocaleDateString()}
                                                    </span>
                                                    <Button variant="ghost" size="icon" className="h-5 w-5 opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-500" onClick={() => handleDeleteNote(note.id)}>
                                                        <Trash2 className="w-3 h-3" />
                                                    </Button>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </TabsContent>

                            {/* Reminders Tab */}
                            <TabsContent value="reminders" className="flex-1 flex flex-col min-h-0">
                                <div className="space-y-3 mb-4 border-b pb-4">
                                    <Input
                                        placeholder="Título do lembrete"
                                        value={newReminderTitle}
                                        onChange={(e) => setNewReminderTitle(e.target.value)}
                                        className="h-8 text-sm"
                                    />
                                    <div className="flex gap-2">
                                        <div className="flex-1">
                                            <Input type="date" className="h-8 text-xs" value={newReminderDate} onChange={(e) => setNewReminderDate(e.target.value)} />
                                        </div>
                                        <div className="w-24">
                                            <Input type="time" className="h-8 text-xs" value={newReminderTime} onChange={(e) => setNewReminderTime(e.target.value)} />
                                        </div>
                                    </div>
                                    <Button size="sm" className="w-full h-8" onClick={handleCreateReminder}>
                                        <Bell className="w-3 h-3 mr-1" /> Criar Lembrete
                                    </Button>
                                </div>
                                <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                                    {reminders.length === 0 ? (
                                        <div className="text-center text-slate-400 text-xs py-8">Nenhum lembrete pendente.</div>
                                    ) : (
                                        reminders.map(reminder => (
                                            <div key={reminder.id} className={`p-3 rounded-lg border flex items-start gap-2 ${reminder.status === 'completed' ? 'bg-slate-50 border-slate-100' : 'bg-white border-slate-200 shadow-sm'}`}>
                                                <button
                                                    className={`mt-0.5 w-4 h-4 rounded border flex items-center justify-center transition-colors ${reminder.status === 'completed' ? 'bg-green-500 border-green-500 text-white' : 'border-slate-300 hover:border-green-500'}`}
                                                    onClick={() => handleToggleReminderStatus(reminder.id, reminder.status)}
                                                >
                                                    {reminder.status === 'completed' && <CheckCircle2 className="w-3 h-3" />}
                                                </button>
                                                <div className="flex-1 min-w-0">
                                                    <p className={`text-sm font-medium leading-none ${reminder.status === 'completed' ? 'text-slate-400 line-through' : 'text-slate-800'}`}>
                                                        {reminder.title}
                                                    </p>
                                                    <div className="flex items-center gap-1 mt-1.5 text-xs text-slate-500">
                                                        <CalendarIcon className="w-3 h-3" />
                                                        <span>{new Date(reminder.due_at).toLocaleDateString()}</span>
                                                        <Clock className="w-3 h-3 ml-1" />
                                                        <span>{new Date(reminder.due_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </TabsContent>
                        </Tabs>
                    </div>
                </div>
            )}
        </div>
    );
};