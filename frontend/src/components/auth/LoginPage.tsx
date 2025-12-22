import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Loader2, Lock, Sparkles } from 'lucide-react';
import { scaleIn, staggerContainer, staggerItem } from '../../utils/animations';

export const LoginPage: React.FC<{ onLogin: () => void, onSignUp: () => void }> = ({ onLogin, onSignUp }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setTimeout(() => {
            setLoading(false);
            onLogin();
        }, 1500);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-white via-cyan-50/20 to-white p-4">
            <motion.div
                {...scaleIn}
                className="w-full max-w-md"
            >
                <Card className="shadow-2xl border-slate-100 backdrop-blur-sm bg-white">
                    <CardHeader className="space-y-1 text-center pb-6">
                        <motion.div
                            className="flex justify-center mb-4"
                            initial={{ scale: 0, rotate: -180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            transition={{ type: "spring", duration: 0.6, delay: 0.1 }}
                        >
                            <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-teal-500 rounded-2xl flex items-center justify-center text-white text-2xl shadow-lg shadow-cyan-500/30">
                                <Sparkles className="w-8 h-8" />
                            </div>
                        </motion.div>
                        <CardTitle className="text-3xl font-bold bg-gradient-to-r from-cyan-600 to-teal-500 bg-clip-text text-transparent">
                            Bem-vindo de Volta
                        </CardTitle>
                        <CardDescription className="text-slate-600">
                            Acesse sua central de inteligência odontológica
                        </CardDescription>
                    </CardHeader>

                    <form onSubmit={handleLogin}>
                        <motion.div
                            variants={staggerContainer}
                            initial="initial"
                            animate="animate"
                        >
                            <CardContent className="space-y-4">
                                <motion.div variants={staggerItem} className="space-y-2">
                                    <Label htmlFor="email" className="text-slate-700">Email Corporativo</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="dra.ana@bemquerer.com.br"
                                        className="border-slate-200 focus:border-cyan-500 focus:ring-cyan-500/20"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                </motion.div>

                                <motion.div variants={staggerItem} className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <Label htmlFor="password" className="text-slate-700">Senha</Label>
                                        <a href="#" className="text-xs text-cyan-600 hover:text-cyan-700 hover:underline">Esqueceu?</a>
                                    </div>
                                    <Input
                                        id="password"
                                        type="password"
                                        placeholder="••••••••"
                                        className="border-slate-200 focus:border-cyan-500 focus:ring-cyan-500/20"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </motion.div>
                            </CardContent>
                        </motion.div>

                        <CardFooter className="flex-col gap-3 pt-2">
                            <motion.div className="w-full" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                                <Button
                                    className="w-full bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 text-white shadow-lg shadow-cyan-500/30 transition-all"
                                    disabled={loading}
                                >
                                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Lock className="mr-2 h-4 w-4" />}
                                    Entrar no Sistema
                                </Button>
                            </motion.div>

                            <div className="text-center text-sm text-slate-600">
                                Não tem uma conta? <button type="button" onClick={onSignUp} className="text-cyan-600 font-semibold hover:text-cyan-700 hover:underline">Cadastre sua clínica</button>
                            </div>
                        </CardFooter>
                    </form>
                </Card>
            </motion.div>
        </div>
    );
};
