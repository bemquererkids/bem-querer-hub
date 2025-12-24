import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Button } from '../ui/button';
import { Bot, Save, Sparkles, MessageSquare, Info, ArrowRight, ArrowLeft, Check } from 'lucide-react';

export const ConfigPromptPage: React.FC = () => {
    const [currentStep, setCurrentStep] = useState(1);
    const [personaName, setPersonaName] = useState("Carol");
    const [tone, setTone] = useState("Empático, acolhedor e eficiente. Use emojis moderadamente.");
    const [instructions, setInstructions] = useState("Não forneça diagnósticos médicos. Para valores, peça para agendar avaliação.");
    const [loading, setLoading] = useState(false);

    const handleSave = () => {
        setLoading(true);
        setTimeout(() => {
            setLoading(false);
            alert("Configurações da IA salvas com sucesso!");
            setCurrentStep(1);
        }, 1000);
    };

    const steps = [
        { number: 1, title: "Identidade", icon: Bot },
        { number: 2, title: "Comportamento", icon: MessageSquare },
        { number: 3, title: "Revisão", icon: Check },
    ];

    return (
        <div className="p-5 h-full flex flex-col max-w-5xl mx-auto animate-in fade-in duration-500">

            {/* Header - Compacted */}
            <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                    <Sparkles className="w-5 h-5 text-indigo-600 dark:text-primary" />
                </div>
                <div>
                    <h1 className="text-lg font-bold text-zinc-900 dark:text-foreground tracking-tight">Personalidade da IA</h1>
                    <p className="text-xs text-zinc-500 dark:text-muted-foreground">Configure sua assistente virtual em 3 etapas.</p>
                </div>
            </div>

            {/* Stepper - Compacted */}
            <div className="flex items-center justify-center gap-3 mb-5">
                {steps.map((step, index) => {
                    const Icon = step.icon;
                    const isActive = currentStep === step.number;
                    const isCompleted = currentStep > step.number;

                    return (
                        <React.Fragment key={step.number}>
                            <div className="flex flex-col items-center gap-1">
                                <div className={`
                                    w-9 h-9 rounded-full flex items-center justify-center border-2 transition-all
                                    ${isActive ? 'bg-indigo-600 dark:bg-primary border-indigo-600 dark:border-primary text-white' : ''}
                                    ${isCompleted ? 'bg-indigo-100 dark:bg-indigo-900/30 border-indigo-600 dark:border-primary text-indigo-600 dark:text-primary' : ''}
                                    ${!isActive && !isCompleted ? 'bg-zinc-100 dark:bg-zinc-800 border-zinc-300 dark:border-zinc-700 text-zinc-400 dark:text-zinc-500' : ''}
                                `}>
                                    {isCompleted ? <Check className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                                </div>
                                <span className={`text-[10px] font-medium ${isActive ? 'text-indigo-600 dark:text-primary' : 'text-zinc-500 dark:text-zinc-400'}`}>
                                    {step.title}
                                </span>
                            </div>
                            {index < steps.length - 1 && (
                                <div className={`h-0.5 w-14 ${currentStep > step.number ? 'bg-indigo-600 dark:bg-primary' : 'bg-zinc-200 dark:bg-zinc-700'}`} />
                            )}
                        </React.Fragment>
                    );
                })}
            </div>

            {/* Step Content */}
            <div className="flex-1 flex flex-col min-h-0">

                {/* Step 1: Identity */}
                {currentStep === 1 && (
                    <Card className="bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-700 shadow-sm flex-1 flex flex-col">
                        <CardHeader className="border-b border-zinc-100 dark:border-zinc-700 bg-zinc-50/50 dark:bg-zinc-800 py-3">
                            <div className="flex items-center gap-2">
                                <Bot className="w-4 h-4 text-indigo-600 dark:text-primary" />
                                <CardTitle className="text-base text-zinc-900 dark:text-foreground">Identidade da IA</CardTitle>
                            </div>
                            <CardDescription className="text-xs text-zinc-500 dark:text-muted-foreground">Escolha um nome para sua assistente virtual.</CardDescription>
                        </CardHeader>
                        <CardContent className="pt-6 pb-4 flex-1 flex flex-col justify-center">
                            <div className="space-y-3 max-w-md mx-auto w-full">
                                <div className="space-y-2">
                                    <Label htmlFor="name" className="text-zinc-700 dark:text-zinc-200 font-medium text-sm">Nome da Persona</Label>
                                    <div className="relative">
                                        <Bot className="absolute left-3 top-2.5 h-4 w-4 text-zinc-400 dark:text-zinc-500" />
                                        <Input
                                            id="name"
                                            value={personaName}
                                            onChange={(e) => setPersonaName(e.target.value)}
                                            className="pl-10 h-10 bg-zinc-50 dark:bg-zinc-800 border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 focus:ring-indigo-500/20 dark:focus:ring-primary/20 focus:border-indigo-600 dark:focus:border-primary"
                                            placeholder="Ex: Carol, Ana, Recepcionista"
                                        />
                                    </div>
                                    <p className="text-xs text-zinc-500 dark:text-zinc-400">Este nome aparecerá nas mensagens automáticas.</p>
                                </div>

                                <div className="p-3 bg-indigo-50 dark:bg-indigo-900/30 border border-indigo-100 dark:border-indigo-700 rounded-lg">
                                    <div className="flex gap-2">
                                        <Info className="w-4 h-4 text-indigo-600 dark:text-primary shrink-0 mt-0.5" />
                                        <p className="text-xs text-indigo-700 dark:text-indigo-300">
                                            <strong>Dica:</strong> Escolha um nome amigável e fácil de lembrar.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter className="bg-zinc-50/50 dark:bg-zinc-800 border-t border-zinc-100 dark:border-zinc-700 flex justify-end p-3">
                            <Button
                                onClick={() => setCurrentStep(2)}
                                disabled={!personaName.trim()}
                                className="bg-indigo-600 dark:bg-primary hover:bg-indigo-700 dark:hover:bg-primary/90 text-white dark:text-primary-foreground gap-2 h-9"
                            >
                                Próximo
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </CardFooter>
                    </Card>
                )}

                {/* Step 2: Behavior */}
                {currentStep === 2 && (
                    <Card className="bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-700 shadow-sm flex-1 flex flex-col">
                        <CardHeader className="border-b border-zinc-100 dark:border-zinc-700 bg-zinc-50/50 dark:bg-zinc-800 py-3">
                            <div className="flex items-center gap-2">
                                <MessageSquare className="w-4 h-4 text-indigo-600 dark:text-primary" />
                                <CardTitle className="text-base text-zinc-900 dark:text-foreground">Comportamento</CardTitle>
                            </div>
                            <CardDescription className="text-xs text-zinc-500 dark:text-muted-foreground">Defina como a IA deve se comunicar.</CardDescription>
                        </CardHeader>
                        <CardContent className="pt-6 pb-4 flex-1 flex flex-col justify-center">
                            <div className="space-y-4 max-w-2xl mx-auto w-full">
                                <div className="space-y-2">
                                    <Label htmlFor="tone" className="text-zinc-700 dark:text-zinc-200 font-medium text-sm">Tom de Voz</Label>
                                    <Input
                                        id="tone"
                                        value={tone}
                                        onChange={(e) => setTone(e.target.value)}
                                        className="h-9 bg-zinc-50 dark:bg-zinc-800 border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 focus:ring-indigo-500/20 dark:focus:ring-primary/20 focus:border-indigo-600 dark:focus:border-primary"
                                        placeholder="Ex: Formal, Descontraído, Maternal"
                                    />
                                    <p className="text-xs text-zinc-500 dark:text-zinc-400">Descreva a personalidade desejada.</p>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="instructions" className="text-zinc-700 dark:text-zinc-200 font-medium text-sm">Instruções e Regras</Label>
                                    <Textarea
                                        id="instructions"
                                        value={instructions}
                                        onChange={(e) => setInstructions(e.target.value)}
                                        className="min-h-[90px] bg-zinc-50 dark:bg-zinc-800 border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 focus:ring-indigo-500/20 dark:focus:ring-primary/20 focus:border-indigo-600 dark:focus:border-primary resize-none text-sm"
                                        placeholder="Regras específicas da clínica, limitações, diretrizes..."
                                    />
                                    <p className="text-xs text-zinc-500 dark:text-zinc-400">Defina limites e comportamentos específicos.</p>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter className="bg-zinc-50/50 dark:bg-zinc-800 border-t border-zinc-100 dark:border-zinc-700 flex justify-between p-3">
                            <Button
                                variant="outline"
                                onClick={() => setCurrentStep(1)}
                                className="border-zinc-200 dark:border-border text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 gap-2 h-9"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Voltar
                            </Button>
                            <Button
                                onClick={() => setCurrentStep(3)}
                                disabled={!tone.trim() || !instructions.trim()}
                                className="bg-indigo-600 dark:bg-primary hover:bg-indigo-700 dark:hover:bg-primary/90 text-white dark:text-primary-foreground gap-2 h-9"
                            >
                                Próximo
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </CardFooter>
                    </Card>
                )}

                {/* Step 3: Review & Preview */}
                {currentStep === 3 && (
                    <Card className="bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-700 shadow-sm flex-1 flex flex-col">
                        <CardHeader className="border-b border-zinc-100 dark:border-zinc-700 bg-zinc-50/50 dark:bg-zinc-800 py-3">
                            <div className="flex items-center gap-2">
                                <Check className="w-4 h-4 text-indigo-600 dark:text-primary" />
                                <CardTitle className="text-base text-zinc-900 dark:text-foreground">Revisão e Pré-visualização</CardTitle>
                            </div>
                            <CardDescription className="text-xs text-zinc-500 dark:text-muted-foreground">Confira as configurações antes de salvar.</CardDescription>
                        </CardHeader>
                        <CardContent className="pt-4 pb-3 flex-1 overflow-auto">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">

                                {/* Summary */}
                                <div className="space-y-3">
                                    <h3 className="text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">Configurações</h3>

                                    <div className="space-y-2">
                                        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-700">
                                            <p className="text-[10px] text-zinc-500 dark:text-zinc-400 mb-0.5">Nome da Persona</p>
                                            <p className="text-sm font-semibold text-zinc-900 dark:text-foreground">{personaName}</p>
                                        </div>

                                        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-border">
                                            <p className="text-[10px] text-zinc-500 dark:text-zinc-400 mb-0.5">Tom de Voz</p>
                                            <p className="text-xs text-zinc-700 dark:text-zinc-300">{tone}</p>
                                        </div>

                                        <div className="p-2.5 bg-zinc-50 dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-border">
                                            <p className="text-[10px] text-zinc-500 dark:text-zinc-400 mb-0.5">Instruções</p>
                                            <p className="text-xs text-zinc-700 dark:text-zinc-300 line-clamp-2">{instructions}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Preview */}
                                <div className="space-y-3">
                                    <h3 className="text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">Pré-visualização</h3>

                                    <div className="bg-[#e5ddd5] dark:bg-zinc-800 p-3 rounded-lg min-h-[220px] relative border border-zinc-200 dark:border-zinc-700">
                                        <div className="absolute inset-0 opacity-10 dark:opacity-5" style={{ backgroundImage: "url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png')" }}></div>

                                        <div className="relative z-10 flex flex-col gap-2">
                                            <div className="self-center bg-[#fffae6] dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 text-[9px] px-2 py-1 rounded-md shadow-sm">
                                                Mensagens criptografadas
                                            </div>

                                            <div className="self-end bg-[#dcf8c6] dark:bg-indigo-600 p-2 rounded-lg rounded-tr-none shadow-md max-w-[85%]">
                                                <p className="text-xs text-zinc-800 dark:text-white">Olá, gostaria de saber sobre implantes.</p>
                                                <span className="text-[9px] text-zinc-500 dark:text-indigo-200 block text-right mt-0.5">10:42</span>
                                            </div>

                                            <div className="self-start bg-white dark:bg-zinc-800 p-2 rounded-lg rounded-tl-none shadow-md max-w-[85%]">
                                                <p className="text-[9px] font-bold text-indigo-600 dark:text-primary mb-0.5">{personaName} (IA)</p>
                                                <p className="text-xs text-zinc-800 dark:text-zinc-200 leading-snug">
                                                    Olá! Sou a <strong>{personaName}</strong> da Bem-Querer. 🦷✨
                                                    <br /><br />
                                                    {tone.includes("Empático") ? "Fico feliz! " : ""}
                                                    Para implantes, precisamos agendar avaliação. Qual o melhor horário?
                                                </p>
                                                <span className="text-[9px] text-zinc-500 dark:text-zinc-400 block text-right mt-1">10:42</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter className="bg-zinc-50/50 dark:bg-zinc-900/50 border-t border-zinc-100 dark:border-border flex justify-between p-3">
                            <Button
                                variant="outline"
                                onClick={() => setCurrentStep(2)}
                                className="border-zinc-200 dark:border-border text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 gap-2 h-9"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Voltar
                            </Button>
                            <Button
                                onClick={handleSave}
                                disabled={loading}
                                className="bg-indigo-600 dark:bg-primary hover:bg-indigo-700 dark:hover:bg-primary/90 text-white dark:text-primary-foreground gap-2 shadow-sm h-9"
                            >
                                {loading ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Salvando...
                                    </>
                                ) : (
                                    <>
                                        <Save className="w-4 h-4" />
                                        Salvar
                                    </>
                                )}
                            </Button>
                        </CardFooter>
                    </Card>
                )}
            </div>
        </div>
    );
};
