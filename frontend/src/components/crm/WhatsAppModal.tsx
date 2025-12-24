
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'; // Correct import

interface WhatsAppModalProps {
    isOpen: boolean;
    onClose: () => void;
    recipientName: string;
    recipientPhone: string;
    onSend: (message: string) => void;
}

export const WhatsAppModal: React.FC<WhatsAppModalProps> = ({ isOpen, onClose, recipientName, recipientPhone, onSend }) => {
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = () => {
        setLoading(true);
        // Simulate API call delay
        setTimeout(() => {
            onSend(message);
            setLoading(false);
            setMessage('');
            onClose();
        }, 1000);
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md bg-white dark:bg-card border-zinc-200 dark:border-border">
                <DialogHeader>
                    <DialogTitle className="text-zinc-900 dark:text-foreground">Nova Mensagem WhatsApp</DialogTitle>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="name" className="text-right text-zinc-700 dark:text-muted-foreground">
                            Para
                        </Label>
                        <Input id="name" value={recipientName} disabled className="col-span-3 bg-zinc-100 dark:bg-secondary/50 border-zinc-200 dark:border-border text-zinc-500 dark:text-muted-foreground" />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="phone" className="text-right text-zinc-700 dark:text-muted-foreground">
                            WhatsApp
                        </Label>
                        <Input id="phone" value={recipientPhone} disabled className="col-span-3 bg-zinc-100 dark:bg-secondary/50 border-zinc-200 dark:border-border text-zinc-500 dark:text-muted-foreground" />
                    </div>
                    <div className="grid gap-2">
                        <Label htmlFor="message" className="text-zinc-700 dark:text-foreground">
                            Mensagem
                        </Label>
                        <Textarea
                            id="message"
                            placeholder="Olá, gostaria de confirmar..."
                            className="bg-zinc-50 dark:bg-zinc-950/50 border-zinc-200 dark:border-border focus:ring-green-500"
                            rows={5}
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={onClose} className="border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800">Cancelar</Button>
                    <Button onClick={handleSend} disabled={!message || loading} className="bg-green-600 hover:bg-green-700 text-white shadow-sm">
                        {loading ? 'Enviando...' : (
                            <>
                                <PaperAirplaneIcon className="w-4 h-4 mr-2" />
                                Enviar
                            </>
                        )}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};
