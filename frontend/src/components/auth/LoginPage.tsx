import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Loader2, Lock } from 'lucide-react';

export const LoginPage: React.FC<{ onLogin: () => void }> = ({ onLogin }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        
        // Simulação de Login
        setTimeout(() => {
            setLoading(false);
            // Aqui chamaríamos supabase.auth.signInWithPassword({ email, password })
            onLogin(); 
        }, 1500);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#f2f8f9] p-4">
            <Card className="w-full max-w-md shadow-xl border-slate-200">
                <CardHeader className="space-y-1 text-center">
                    <div className="flex justify-center mb-4">
                        <div className="w-12 h-12 bg-[#1a97d4] rounded-full flex items-center justify-center text-white text-2xl shadow-lg">
                            🦷
                        </div>
                    </div>
                    <CardTitle className="text-2xl font-bold text-slate-800">Bem-Querer Hub</CardTitle>
                    <CardDescription>Acesse sua central de inteligência odontológica</CardDescription>
                </CardHeader>
                <form onSubmit={handleLogin}>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="email">Email Corporativo</Label>
                            <Input 
                                id="email" 
                                type="email" 
                                placeholder="dra.ana@bemquerer.com.br"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password">Senha</Label>
                                <a href="#" className="text-xs text-[#1a97d4] hover:underline">Esqueceu?</a>
                            </div>
                            <Input 
                                id="password" 
                                type="password" 
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button className="w-full bg-[#1a97d4] hover:bg-[#1585bc]" disabled={loading}>
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Lock className="mr-2 h-4 w-4" />}
                            Entrar no Sistema
                        </Button>
                    </CardFooter>
                </form>
                <div className="p-4 text-center text-xs text-slate-400 bg-slate-50 rounded-b-xl border-t border-slate-100">
                    Protegido por criptografia de ponta-a-ponta.
                </div>
            </Card>
        </div>
    );
};
