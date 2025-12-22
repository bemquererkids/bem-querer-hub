import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea'; // Assuming we have this, or use standard
import { Button } from '../ui/button';
import { Bot, Save, Sparkles, MessageSquare } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';

export const ConfigPromptPage: React.FC = () => {
    const [personaName, setPersonaName] = useState("Carol");
    const [tone, setTone] = useState("Empático, acolhedor e eficiente. Use emojis moderadamente.");
    const [instructions, setInstructions] = useState("Não forneça diagnósticos médicos. Para valores, peça para agendar avaliação.");
    const [loading, setLoading] = useState(false);

    const handleSave = () => {
        setLoading(true);
        // Simulate API call
        setTimeout(() => {
            setLoading(false);
            alert("Configurações da IA salvas com sucesso!");
        }, 1000);
    };

    return (
        <div className="max-w-4xl mx-auto py-8 px-4 space-y-8 animate-in fade-in duration-500">
            
            <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-purple-100 rounded-xl">
                    <Sparkles className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Personalidade da IA</h1>
                    <p className="text-slate-500">Defina como sua assistente virtual interage com os pacientes.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                
                {/* Left Column: Settings Form */}
                <div className="md:col-span-2 space-y-6">
                    <Card className="border-slate-200 shadow-sm">
                        <CardHeader>
                            <CardTitle className="text-lg">Identidade</CardTitle>
                            <CardDescription>Quem é a sua assistente?</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">Nome da Persona</Label>
                                <div className="relative">
                                    <Bot className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                    <Input 
                                        id="name" 
                                        value={personaName} 
                                        onChange={(e) => setPersonaName(e.target.value)}
                                        className="pl-9 bg-slate-50"
                                        placeholder="Ex: Carol, Ana, Recepcionista"
                                    />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="border-slate-200 shadow-sm">
                        <CardHeader>
                            <CardTitle className="text-lg">Comportamento</CardTitle>
                            <CardDescription>Como ela deve falar e agir?</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="tone">Tom de Voz</Label>
                                <Input 
                                    id="tone" 
                                    value={tone}
                                    onChange={(e) => setTone(e.target.value)}
                                    className="bg-slate-50"
                                />
                                <p className="text-[11px] text-slate-400">Ex: Formal, Descontraído, Maternal.</p>
                            </div>
                            
                            <div className="space-y-2">
                                <Label htmlFor="instructions">Instruções e Regras</Label>
                                <textarea 
                                    id="instructions"
                                    value={instructions}
                                    onChange={(e) => setInstructions(e.target.value)}
                                    className="flex min-h-[120px] w-full rounded-md border border-input bg-slate-50 px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    placeholder="Regras específicas da clínica..."
                                />
                            </div>
                        </CardContent>
                        <CardFooter className="bg-slate-50/50 border-t border-slate-100 flex justify-end p-4">
                            <Button onClick={handleSave} disabled={loading} className="bg-purple-600 hover:bg-purple-700 text-white gap-2">
                                {loading ? <span className="animate-spin">⏳</span> : <Save className="w-4 h-4" />}
                                Salvar Alterações
                            </Button>
                        </CardFooter>
                    </Card>
                </div>

                {/* Right Column: Live Preview */}
                <div className="space-y-6">
                    <div className="sticky top-6">
                        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">Pré-visualização</h3>
                        
                        {/* WhatsApp Bubble Preview */}
                        <div className="bg-[#e5ddd5] p-4 rounded-xl shadow-inner min-h-[300px] border border-slate-200 flex flex-col gap-4 relative overflow-hidden">
                            {/* Background Pattern Mock */}
                            <div className="absolute inset-0 opacity-10" style={{backgroundImage: "url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png')"}}></div>
                            
                            <div className="relative z-10 flex flex-col gap-3">
                                {/* System Message */}
                                <div className="self-center bg-[#fffae6] text-slate-600 text-[10px] px-2 py-1 rounded shadow-sm">
                                    As mensagens são protegidas com criptografia de ponta-a-ponta.
                                </div>

                                {/* User Message */}
                                <div className="self-end bg-[#dcf8c6] p-2 rounded-lg rounded-tr-none shadow-sm max-w-[85%]">
                                    <p className="text-sm text-slate-800">Olá, gostaria de saber sobre implantes.</p>
                                    <span className="text-[10px] text-slate-500 block text-right mt-1">10:42</span>
                                </div>

                                {/* AI Response Preview */}
                                <div className="self-start bg-white p-2 rounded-lg rounded-tl-none shadow-sm max-w-[85%] flex gap-2">
                                    <div>
                                        <p className="text-[10px] font-bold text-purple-600 mb-0.5">{personaName} (IA)</p>
                                        <p className="text-sm text-slate-800">
                                            Olá! Tudo bem? Sou a <strong>{personaName}</strong> da Bem-Querer. 🦷✨
                                            <br/><br/>
                                            {tone.includes("Empático") ? "Fico feliz pelo seu interesse! " : ""}
                                            Para implantes, precisamos agendar uma avaliação inicial. Qual o melhor horário para você?
                                        </p>
                                        <span className="text-[10px] text-slate-500 block text-right mt-1">10:42</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-4 p-4 bg-blue-50 border border-blue-100 rounded-lg text-xs text-blue-700">
                            <strong>Dica:</strong> A IA usará o nome <em>{personaName}</em> e seguirá o tom <em>{tone.split(' ')[0]}</em> em todas as conversas.
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};
