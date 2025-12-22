import React, { useState, useEffect, useRef } from 'react';
import { ChatContact, ChatMessage } from '../../types/chat';
import { Send, Paperclip, Mic, MoreVertical, Phone, Video } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { chatService } from '../../services/api';

interface ChatWindowProps {
    chat?: ChatContact;
    messages: ChatMessage[];
    onSendMessage: (text: string) => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ chat, messages: initialMessages, onSendMessage }) => {
    const [newMessage, setNewMessage] = useState('');
    const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        setMessages(initialMessages);
    }, [initialMessages]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isTyping]);

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
                id: (Date.now() + 1).toString(),
                content: response.response,
                sender: 'user', // Represents the 'other side' (AI acting as the contact)
                timestamp: new Date().toISOString(),
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
            <div className="h-16 bg-white border-b border-border flex items-center justify-between px-4 shadow-sm z-10">
                <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10 border border-slate-100 cursor-pointer">
                        <AvatarImage src={`https://ui-avatars.com/api/?name=${chat.name.replace(' ', '+')}&background=random`} />
                        <AvatarFallback>{chat.name.substring(0, 2).toUpperCase()}</AvatarFallback>
                    </Avatar>
                    <div>
                        <h3 className="font-bold text-slate-800 text-sm">{chat.name}</h3>
                        <p className="text-xs text-green-600 font-medium">Carol (IA) Ativa</p>
                    </div>
                </div>
                <div className="flex items-center gap-1 text-slate-400">
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
                                className={`max-w-[70%] px-4 py-2 shadow-sm relative text-sm ${isMe
                                        ? 'bg-gradient-to-r from-cyan-500 to-teal-500 text-white rounded-2xl rounded-tr-sm'
                                        : 'bg-white border border-slate-100 text-slate-700 rounded-2xl rounded-tl-sm'
                                    }`}
                            >
                                <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                                <span className="text-[10px] text-slate-200 block text-right mt-1 opacity-70">
                                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    {isMe && <span className="ml-1 text-blue-200">✓✓</span>}
                                </span>
                            </div>
                        </div>
                    );
                })}
                {isTyping && (
                    <div className="flex justify-start animate-pulse">
                        <div className="bg-white rounded-lg p-3 rounded-tl-none shadow-sm flex gap-1 items-center">
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100"></span>
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200"></span>
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-slate-100 flex items-center gap-2">
                <Button variant="ghost" size="icon" className="text-slate-400 hover:text-cyan-600 hover:bg-cyan-50 transition-colors">
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
                        className="absolute right-1 top-1 h-8 w-8 text-slate-400 hover:text-cyan-600"
                    >
                        <Mic className="w-4 h-4" />
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