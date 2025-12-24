import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { motion } from 'framer-motion';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { ArrowPathIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import { staggerContainer, staggerItem } from '../../utils/animations';

export const LoginPage: React.FC<{ onLogin: () => void, onSignUp: () => void }> = ({ onLogin, onSignUp }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();

        // Use the auth context login
        await login(email, password);
        // onLogin prop might be deprecated but keeping it safe
        onLogin();
    };

    return (
        <div className="min-h-screen w-full grid grid-cols-1 lg:grid-cols-2">
            {/* Left Column: Form */}
            <div className="flex flex-col justify-center px-4 py-12 sm:px-6 lg:flex-none lg:px-20 xl:px-24 bg-white">
                <div className="mx-auto w-full max-w-sm lg:w-96">
                    <motion.div
                        variants={staggerContainer}
                        initial="initial"
                        animate="animate"
                    >
                        <motion.div variants={staggerItem} className="mb-10">
                            <h2 className="mt-8 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-white">
                                Acessar conta
                            </h2>
                            <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
                                Entre com suas credenciais para gerenciar sua clínica pelo <span className="font-semibold text-indigo-600 dark:text-primary">NEXUS</span>.
                            </p>
                        </motion.div>

                        <form onSubmit={handleLogin} className="space-y-6">
                            <motion.div variants={staggerItem} className="space-y-2">
                                <Label htmlFor="email" className="text-zinc-700 dark:text-zinc-300 font-medium">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="admin@clinica.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    autoComplete="email"
                                    className="bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800"
                                />
                            </motion.div>

                            <motion.div variants={staggerItem} className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <Label htmlFor="password" className="text-zinc-700 dark:text-zinc-300 font-medium">Senha</Label>
                                    <a href="#" className="text-xs text-zinc-600 dark:text-zinc-400 hover:text-indigo-600 dark:hover:text-primary hover:underline">
                                        Esqueceu?
                                    </a>
                                </div>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
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
                                            Entrar
                                            <ArrowRightIcon className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                                        </span>
                                    )}
                                </Button>
                            </motion.div>
                        </form>

                        <motion.div variants={staggerItem} className="mt-8 relative">
                            <div className="absolute inset-0 flex items-center" aria-hidden="true">
                                <div className="w-full border-t border-zinc-200 dark:border-zinc-800" />
                            </div>
                            <div className="relative flex justify-center text-sm">
                                <span className="bg-white dark:bg-card px-2 text-zinc-500 dark:text-zinc-400">Novo na plataforma?</span>
                            </div>
                        </motion.div>

                        <motion.div variants={staggerItem} className="mt-6">
                            <Button variant="outline" onClick={onSignUp} className="w-full font-semibold text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-900 border-zinc-200 dark:border-zinc-800">
                                Criar conta clínica
                            </Button>
                        </motion.div>
                    </motion.div>
                </div>
            </div>

            {/* Right Column: Branding */}
            <div className="hidden lg:block relative flex-1 bg-slate-950">
                <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1628177142898-93e36e4e3bd7?q=80&w=2515&auto=format&fit=crop')] bg-cover bg-center opacity-20 mix-blend-overlay"></div>
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
                            A evolução da gestão odontológica.
                        </h1>
                        <p className="text-slate-400 text-lg">
                            Integração total entre WhatsApp, IA e seus sistemas clínicos em um único hyper-loop operacional.
                        </p>
                    </div>

                    <div className="flex gap-4 opacity-50 text-sm text-slate-400">
                        <span>© 2025 Nexus Inc.</span>
                        <span>Termos</span>
                        <span>Privacidade</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
