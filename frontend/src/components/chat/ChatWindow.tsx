import React, { useState, useEffect, useRef } from 'react';
import { ChatContact, ChatMessage } from '../../types/chat';
import { supabase } from '../../services/supabase';
import { Send, Paperclip, Mic, MoreVertical, Phone, Video, ChevronLeft, ChevronDown, CheckCircle2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { chatService, crmService } from '../../services/api';
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
}

const formatPhoneNumber = (phone: string) => {
    if (!phone) return '';
    // Remove non-digits
    const cleaned = phone.replace(/\D/g, '');

    // Check for Brazilian format: 55 + DDD + Number
    // Landline: 55 (2) + DDD (2) + 8 digits = 12 chars
    // Mobile: 55 (2) + DDD (2) + 9 digits = 13 chars

    if (cleaned.length === 13) { // Mobile: +55 (11) 99999-9999
        return `+${cleaned.slice(0, 2)} (${cleaned.slice(2, 4)}) ${cleaned.slice(4, 9)}-${cleaned.slice(9)}`;
    }

    if (cleaned.length === 12) { // Landline: +55 (11) 4444-4444
        return `+${cleaned.slice(0, 2)} (${cleaned.slice(2, 4)}) ${cleaned.slice(4, 8)}-${cleaned.slice(8)}`;
    }

    // Fallback for other formats, just return as is or basic formatting
    return phone;
};

export const ChatWindow: React.FC<ChatWindowProps> = ({ chat, messages: initialMessages, onSendMessage, onBack }) => {
    const [newMessage, setNewMessage] = useState('');
    const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
    const [isTyping, setIsTyping] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [isRecording, setIsRecording] = useState(false);

    const scrollRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    useEffect(() => {
        setMessages(initialMessages);
    }, [initialMessages]);

    useEffect(() => {
        if (!chat?.id) return;

        // Subscribe to new messages for this conversation
        const subscription = supabase
            .channel(`chat:${chat.id}`)
            .on('postgres_changes', {
                event: 'INSERT',
                schema: 'public',
                table: 'whatsapp_messages',
                filter: `conversation_id=eq.${chat.id}`
            }, (payload) => {
                const newMsg = payload.new;

                // Avoid duplicating distinct messages (check ID)
                setMessages(prev => {
                    if (prev.some(m => m.id === newMsg.message_id)) return prev;

                    return [...prev, {
                        id: newMsg.message_id,
                        content: newMsg.content,
                        sender: newMsg.is_from_me ? 'agent' : 'user',
                        timestamp: newMsg.created_at,
                        type: newMsg.message_type,
                        status: 'read'
                    }];
                });
            })
            .subscribe();

        return () => {
            subscription.unsubscribe();
        };
    }, [chat?.id]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isTyping]);

    const handleMicClick = async () => {
        if (isRecording) {
            // Stop Recording
            mediaRecorderRef.current?.stop();
            setIsRecording(false);
        } else {
            // Start Recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const mediaRecorder = new MediaRecorder(stream);
                mediaRecorderRef.current = mediaRecorder;
                audioChunksRef.current = [];

                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunksRef.current.push(event.data);
                    }
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                    const audioFile = new File([audioBlob], `voice_${Date.now()}.webm`, { type: 'audio/webm' });

                    // Upload
                    setIsUploading(true);
                    try {
                        const fileName = `${chat?.id || 'temp'}/${Date.now()}_voice.webm`;
                        const { error: uploadError } = await supabase.storage
                            .from('chat-media')
                            .upload(fileName, audioFile);

                        if (uploadError) throw uploadError;

                        const { data: { publicUrl } } = supabase.storage
                            .from('chat-media')
                            .getPublicUrl(fileName);

                        // Send
                        if (chat?.id) {
                            await chatService.sendMedia(chat.id, publicUrl, 'audio');

                            // Optimistic
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
        if (!newMessage.trim()) return;

        const text = newMessage;
        setNewMessage('');

        // 1. Optimistic Update (User Message)
        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            content: text,
            sender: 'agent', // Representing 'me'/operator/user in this UI context
            timestamp: new Date().toISOString(),
            type: 'text',
            status: 'sent'
        };

        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            // 2. Call AI Backend
            const response = await chatService.sendMessage(chat.id, text);

            // 3. Add AI Response
            const aiMsg: ChatMessage = {
                id: response.ai_message.id,
                content: response.ai_message.content,
                sender: 'user',
                timestamp: response.ai_message.timestamp,
                type: 'text',
                status: 'read'
            };
            setMessages(prev => [...prev, aiMsg]);
        } catch (error) {
            console.error("Chat Error", error);
            // Error handling (optional: add error message bubble)
        } finally {
            setIsTyping(false);
        }
    };

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files || e.target.files.length === 0 || !chat) return;

        const file = e.target.files[0];
        setIsUploading(true);

        try {
            // 1. Upload to Supabase
            const fileExt = file.name.split('.').pop();
            const fileName = `${chat.id}/${Date.now()}.${fileExt}`;
            const { error: uploadError, data } = await supabase.storage
                .from('chat-media')
                .upload(fileName, file);

            if (uploadError) throw uploadError;

            // 2. Get Public URL
            const { data: { publicUrl } } = supabase.storage
                .from('chat-media')
                .getPublicUrl(fileName);

            // 3. Determine Type
            let mediaType: 'image' | 'audio' | 'document' = 'document';
            if (file.type.startsWith('image/')) mediaType = 'image';
            else if (file.type.startsWith('audio/')) mediaType = 'audio';

            // 4. Send via Backend
            await chatService.sendMedia(chat.id, publicUrl, mediaType, undefined, file.name);

            // 5. Optimistic Update
            const newMsg: ChatMessage = {
                id: Date.now().toString(),
                content: publicUrl, // For now, content is URL
                sender: 'agent',
                timestamp: new Date().toISOString(),
                type: mediaType,
                status: 'sent'
            };
            setMessages(prev => [...prev, newMsg]);

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
        } catch (e) {
            console.error("Failed to update status", e);
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
        <div className="flex-1 flex flex-col h-full bg-[#efeae2]">
            {/* Header */}
            <div className="h-16 bg-white border-b border-border flex items-center justify-between px-4 shadow-sm z-10 shrink-0">
                <div className="flex items-center gap-3">
                    {/* Back Button (Mobile Only) */}
                    {onBack && (
                        <Button variant="ghost" size="icon" className="md:hidden text-slate-500 -ml-2" onClick={onBack}>
                            <ChevronLeft className="w-6 h-6" />
                        </Button>
                    )}

                    <Avatar className="h-10 w-10 border border-slate-100 cursor-pointer">
                        <AvatarImage src={`https://ui-avatars.com/api/?name=${(chat.name || 'Desconhecido').replace(' ', '+')}&background=random`} />
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
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" size="sm" className="mr-2 gap-2 text-slate-600 border-slate-200">
                                <span className="hidden md:inline">Funil de Vendas</span>
                                <ChevronDown className="w-4 h-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleStatusChange('Lead')}>
                                <div className="w-2 h-2 rounded-full bg-indigo-500 mr-2" />
                                Lead
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleStatusChange('Em Negociação')}>
                                <div className="w-2 h-2 rounded-full bg-indigo-500 mr-2" />
                                Em Negociação
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleStatusChange('Agendado')}>
                                <div className="w-2 h-2 rounded-full bg-purple-500 mr-2" />
                                Agendado
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleStatusChange('Compareceu')}>
                                <div className="w-2 h-2 rounded-full bg-emerald-500 mr-2" />
                                Compareceu
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleStatusChange('Faltou')}>
                                <div className="w-2 h-2 rounded-full bg-red-500 mr-2" />
                                Faltou
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleStatusChange('Venda Realizada')}>
                                <div className="w-2 h-2 rounded-full bg-amber-500 mr-2" />
                                Venda Realizada
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>

                    <Button variant="ghost" size="icon"><Video className="w-5 h-5" /></Button>
                    <Button variant="ghost" size="icon"><Phone className="w-5 h-5" /></Button>
                    <Button variant="ghost" size="icon"><MoreVertical className="w-5 h-5" /></Button>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {messages.map((msg) => {
                    const isMe = msg.sender === 'agent';
                    return (
                        <div key={msg.id} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                            <div
                                className={`max-w-[70%] px-3 py-1.5 shadow-sm relative text-[14.2px] leading-relaxed ${isMe
                                    ? 'bg-[#d9fdd3] text-[#111b21] rounded-lg rounded-tr-none'
                                    : 'bg-white text-[#111b21] rounded-lg rounded-tl-none'
                                    }`}
                            >
                                <p className="whitespace-pre-wrap">{msg.content}</p>
                                <div className="flex justify-end items-center gap-1 mt-1 select-none">
                                    <span className="text-[11px] text-[#667781] min-w-fit">
                                        {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                                    </span>
                                    {isMe && (
                                        <span className={`text-[11px] ${msg.status === 'read' ? 'text-[#53bdeb]' : 'text-[#667781]'}`}>
                                            ✓✓
                                        </span>
                                    )}
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
                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    onChange={handleFileSelect}
                />
                <Button
                    variant="ghost"
                    size="icon"
                    className="text-slate-400 hover:text-cyan-600 hover:bg-cyan-50 transition-colors"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                >
                    <Paperclip className="w-5 h-5" />
                </Button>
                <div className="flex-1 relative">
                    <Input
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Digite sua mensagem..."
                        className="pr-10 bg-slate-50 border-slate-200 focus:border-cyan-500 focus:ring-cyan-500/20"
                    />
                    <Button
                        variant="ghost"
                        size="icon"
                        className={`absolute right-1 top-1 h-8 w-8 transition-colors ${isRecording ? 'text-red-500 hover:text-red-600 bg-red-50' : 'text-slate-400 hover:text-cyan-600'
                            }`}
                        onClick={handleMicClick}
                        disabled={isUploading}
                    >
                        {isRecording ? <div className="w-3 h-3 rounded-sm bgCurrent" style={{ backgroundColor: 'currentColor' }} /> : <Mic className="w-4 h-4" />}
                    </Button>
                </div>
                <Button
                    onClick={handleSend}
                    className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white shadow-lg shadow-cyan-500/30 rounded-full w-10 h-10 p-0 flex items-center justify-center transition-all hover:scale-105"
                >
                    <Send className="w-4 h-4 ml-0.5" />
                </Button>
            </div>
        </div>
    );
};