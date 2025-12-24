import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { ArrowPathIcon, UserPlusIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import { supabase } from '../../services/supabase';
import { staggerContainer, staggerItem } from '../../utils/animations';

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
        <div className="min-h-screen w-full grid grid-cols-1 lg:grid-cols-2">
            {/* Left Column: Form */}
            <div className="flex flex-col justify-center px-4 py-12 sm:px-6 lg:flex-none lg:px-20 xl:px-24 bg-white dark:bg-card">
                <div className="mx-auto w-full max-w-sm lg:w-96">
                    <motion.div
                        variants={staggerContainer}
                        initial="initial"
                        animate="animate"
                    >
                        <motion.div variants={staggerItem} className="mb-8">
                            <h2 className="mt-8 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">
                                Criar nova conta clínica
                            </h2>
                            <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
                                Comece a usar o <span className="font-semibold text-indigo-600 dark:text-primary">NEXUS</span> hoje mesmo.
                            </p>
                        </motion.div>

                        <form onSubmit={handleSignUp} className="space-y-5">
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="bg-red-50 text-red-600 text-sm p-3 rounded-md border border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-900/30"
                                >
                                    {error}
                                </motion.div>
                            )}

                            <motion.div variants={staggerItem} className="space-y-2">
                                <Label htmlFor="clinic" className="text-zinc-700 dark:text-zinc-300 font-medium">Nome da Clínica</Label>
                                <Input
                                    id="clinic"
                                    placeholder="Ex: OdondoSmile"
                                    value={clinicName}
                                    onChange={(e) => setClinicName(e.target.value)}
                                    required
                                    className="bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800"
                                />
                            </motion.div>

                            <motion.div variants={staggerItem} className="space-y-2">
                                <Label htmlFor="name" className="text-zinc-700 dark:text-zinc-300 font-medium">Seu Nome Completo</Label>
                                <Input
                                    id="name"
                                    placeholder="Ex: Dra. Ana Silva"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    required
                                    className="bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800"
                                />
                            </motion.div>

                            <motion.div variants={staggerItem} className="space-y-2">
                                <Label htmlFor="email" className="text-zinc-700 dark:text-zinc-300 font-medium">Email Corporativo</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="admin@clinica.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800"
                                />
                            </motion.div>

                            <motion.div variants={staggerItem} className="space-y-2">
                                <Label htmlFor="password" className="text-zinc-700 dark:text-zinc-300 font-medium">Senha</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="Mínimo 6 caracteres"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    minLength={6}
                                    className="bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800"
                                />
                            </motion.div>

                            <motion.div variants={staggerItem} className="pt-2">
                                <Button
                                    type="submit"
                                    className="w-full bg-indigo-600 hover:bg-indigo-700 dark:bg-primary dark:hover:bg-primary/90 text-white shadow-md group"
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <ArrowPathIcon className="mr-2 h-4 w-4 animate-spin" />
                                    ) : (
                                        <span className="flex items-center">
                                            <UserPlusIcon className="mr-2 h-4 w-4" />
                                            Criar Conta
                                        </span>
                                    )}
                                </Button>
                            </motion.div>

                            <motion.div variants={staggerItem}>
                                <Button
                                    type="button"
                                    variant="ghost"
                                    onClick={onBack}
                                    className="w-full text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-800"
                                >
                                    <ArrowLeftIcon className="mr-2 h-4 w-4" />
                                    Voltar para Login
                                </Button>
                            </motion.div>
                        </form>
                    </motion.div>
                </div>
            </div>

            {/* Right Column: Branding */}
            <div className="hidden lg:block relative flex-1 bg-slate-950">
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1551076805-e1869033e561?q=80&w=2532&auto=format&fit=crop')] bg-cover bg-center opacity-20 mix-blend-overlay"></div>
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-indigo-900/10"></div>

                <div className="relative z-10 h-full flex flex-col justify-between p-12 text-white">
                    <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <span className="text-xl font-bold tracking-wider text-white">NEXUS</span>
                    </div>

                    <div className="max-w-md">
                        <h1 className="text-4xl font-bold tracking-tight mb-4 text-white">
                            Junte-se à revolução.
                        </h1>
                        <p className="text-slate-400 text-lg">
                            Milhares de clínicas já estão automatizando seus atendimentos e multiplicando resultados com o Nexus.
                        </p>
                    </div>

                    <div className="flex gap-4 opacity-50 text-sm text-slate-400">
                        <span>© 2025 Nexus Inc.</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
