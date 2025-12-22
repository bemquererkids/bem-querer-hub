import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Loader2, UserPlus, ArrowLeft, Sparkles } from 'lucide-react';
import { supabase } from '../../services/supabase';
import { fadeInUp, scaleIn, staggerContainer, staggerItem } from '../../utils/animations';

export const SignUpPage: React.FC<{ onBack: () => void, onSuccess: () => void }> = ({ onBack, onSuccess }) => {
    const [clinicName, setClinicName] = useState('');
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSignUp = async (e: React.FormEvent) => {
        e.preventDefault();
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
                    slug: clinicName.toLowerCase().replace(/ /g, '-'),
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
            onSuccess();

        } catch (err: any) {
            console.error(err);

            // Friendly error messages
            let friendlyMessage = "Erro ao criar conta. Tente novamente.";

            if (err.message?.includes("User already registered")) {
                friendlyMessage = "⚠️ Este email já está cadastrado. Por favor, faça login ou use outro email.";
            } else if (err.message?.includes("Invalid email")) {
                friendlyMessage = "❌ Email inválido. Verifique e tente novamente.";
            } else if (err.message?.includes("Password")) {
                friendlyMessage = "❌ A senha deve ter no mínimo 6 caracteres.";
            } else if (err.message?.includes("violates")) {
                friendlyMessage = "⚠️ Erro ao criar perfil. Entre em contato com o suporte.";
            }

            setError(friendlyMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-emerald-50/30 to-slate-50 p-4">
            <motion.div
                {...scaleIn}
                className="w-full max-w-md"
            >
                <Card className="shadow-xl border-slate-200/60 backdrop-blur-sm bg-white/80">
                    <CardHeader className="space-y-1 text-center pb-6">
                        <motion.div
                            className="flex justify-center mb-4"
                            initial={{ scale: 0, rotate: -180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            transition={{ type: "spring", duration: 0.6, delay: 0.1 }}
                        >
                            <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl flex items-center justify-center text-white text-2xl shadow-lg shadow-emerald-500/30">
                                <Sparkles className="w-8 h-8" />
                            </div>
                        </motion.div>
                        <CardTitle className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-emerald-500 bg-clip-text text-transparent">
                            Nova Clínica
                        </CardTitle>
                        <CardDescription className="text-slate-600">
                            Cadastre-se para acessar o Bem-Querer Hub
                        </CardDescription>
                    </CardHeader>

                    <form onSubmit={handleSignUp}>
                        <motion.div
                            variants={staggerContainer}
                            initial="initial"
                            animate="animate"
                        >
                            <CardContent className="space-y-4">
                                {error && (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="bg-red-50 text-red-600 text-sm p-3 rounded-lg border border-red-200"
                                    >
                                        {error}
                                    </motion.div>
                                )}

                                <motion.div variants={staggerItem} className="space-y-2">
                                    <Label htmlFor="clinic" className="text-slate-700">Nome da Clínica</Label>
                                    <Input
                                        id="clinic"
                                        placeholder="Ex: OdontoSmile"
                                        className="border-slate-200 focus:border-emerald-500 focus:ring-emerald-500/20"
                                        value={clinicName}
                                        onChange={(e) => setClinicName(e.target.value)}
                                        required
                                    />
                                </motion.div>

                                <motion.div variants={staggerItem} className="space-y-2">
                                    <Label htmlFor="name" className="text-slate-700">Seu Nome Completo</Label>
                                    <Input
                                        id="name"
                                        placeholder="Dra. Ana Silva"
                                        className="border-slate-200 focus:border-emerald-500 focus:ring-emerald-500/20"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                        required
                                    />
                                </motion.div>

                                <motion.div variants={staggerItem} className="space-y-2">
                                    <Label htmlFor="email" className="text-slate-700">Email Corporativo</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="contato@clinica.com"
                                        className="border-slate-200 focus:border-emerald-500 focus:ring-emerald-500/20"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                </motion.div>

                                <motion.div variants={staggerItem} className="space-y-2">
                                    <Label htmlFor="password" className="text-slate-700">Senha</Label>
                                    <Input
                                        id="password"
                                        type="password"
                                        placeholder="Crie uma senha forte"
                                        className="border-slate-200 focus:border-emerald-500 focus:ring-emerald-500/20"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        minLength={6}
                                    />
                                </motion.div>
                            </CardContent>
                        </motion.div>

                        <CardFooter className="flex-col gap-3 pt-2">
                            <motion.div className="w-full" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                                <Button
                                    className="w-full bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-700 hover:to-emerald-600 text-white shadow-lg shadow-emerald-500/30 transition-all"
                                    disabled={loading}
                                >
                                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <UserPlus className="mr-2 h-4 w-4" />}
                                    Criar Minha Conta
                                </Button>
                            </motion.div>

                            <Button variant="ghost" className="w-full text-slate-600 hover:text-emerald-600 hover:bg-emerald-50" onClick={onBack} type="button">
                                <ArrowLeft className="mr-2 h-4 w-4" /> Voltar para Login
                            </Button>
                        </CardFooter>
                    </form>
                </Card>
            </motion.div>
        </div>
    );
};
