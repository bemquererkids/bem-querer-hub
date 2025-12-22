import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Loader2, UserPlus, ArrowLeft } from 'lucide-react';
import { supabase } from '../../services/supabase';

export const SignUpPage: React.FC<{ onBack: () => void, onSuccess: () => void }> = ({ onBack, onSuccess }) => {
    const [clinicName, setClinicName] = useState('');
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSignUp = async (e: React.FormEvent) => {
        e.preventDefault();

        // Check if keys are present (Vercel Build Check)
        if (!supabaseUrl || !supabaseKey) {
            setError("⚠️ ERRO CRÍTICO: Chaves do Supabase não encontradas no Frontend! Você fez o 'Redeploy' na Vercel?");
            setLoading(false);
            return;
        }

        setLoading(true);
        setError('');

        try {
            // 1. Create Auth User
            const { data: authData, error: authError } = await supabase.auth.signUp({
                email,
                password,
            });

            if (authError) throw authError;
            if (!authData.user) throw new Error("Erro ao criar usuário");

            const userId = authData.user.id;

            // 2. Create Clinic (Tenant)
            const { data: clinicData, error: clinicError } = await supabase
                .from('clinicas')
                .insert({
                    nome_fantasia: clinicName,
                    slug: clinicName.toLowerCase().replace(/ /g, '-'), // Simple slug
                    status: 'ativo'
                })
                .select()
                .single();

            if (clinicError) throw clinicError;

            // 3. Create Profile (Link User -> Clinic)
            const { error: profileError } = await supabase
                .from('perfis')
                .insert({
                    id: userId,
                    clinica_id: clinicData.id,
                    nome_completo: fullName,
                    cargo: 'admin',
                    avatar_url: `https://ui-avatars.com/api/?name=${fullName.replace(' ', '+')}&background=random`
                });

            if (profileError) throw profileError;

            alert("Conta criada com sucesso! Faça login.");
            onSuccess(); // Switch to Login

        } catch (err: any) {
            console.error(err);
            setError(err.message || "Erro ao criar conta. Tente novamente.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#f2f8f9] p-4">
            <Card className="w-full max-w-md shadow-xl border-slate-200 animate-in fade-in zoom-in duration-300">
                <CardHeader className="space-y-1 text-center">
                    <div className="flex justify-center mb-4">
                        <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center text-white text-2xl shadow-lg">
                            ✨
                        </div>
                    </div>
                    <CardTitle className="text-2xl font-bold text-slate-800">Nova Clínica</CardTitle>
                    <CardDescription>Cadastre-se para acessar o Bem-Querer Hub</CardDescription>
                </CardHeader>
                <form onSubmit={handleSignUp}>
                    <CardContent className="space-y-4">
                        {error && (
                            <div className="bg-red-50 text-red-600 text-xs p-3 rounded-md border border-red-200">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <Label htmlFor="clinic">Nome da Clínica</Label>
                            <Input
                                id="clinic"
                                placeholder="Ex: OdontoSmile"
                                value={clinicName}
                                onChange={(e) => setClinicName(e.target.value)}
                                required
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="name">Seu Nome Completo</Label>
                            <Input
                                id="name"
                                placeholder="Dra. Ana Silva"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                required
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="email">Email Corporativo</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="contato@clinica.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Senha</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="Crie uma senha forte"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                minLength={6}
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="flex-col gap-2">
                        <Button className="w-full bg-green-600 hover:bg-green-700" disabled={loading}>
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <UserPlus className="mr-2 h-4 w-4" />}
                            Criar Minha Conta
                        </Button>
                        <Button variant="ghost" className="w-full" onClick={onBack} type="button">
                            <ArrowLeft className="mr-2 h-4 w-4" /> Voltar para Login
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
};
