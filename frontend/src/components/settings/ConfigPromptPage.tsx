import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Button } from '../ui/button';
import { Bot, Save, Sparkles, MessageSquare, Info, ArrowRight, ArrowLeft, Check, BookOpen, Plus, Trash2, Search } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { aiService } from '../../services/api';

export const ConfigPromptPage: React.FC = () => {
    const [personaName, setPersonaName] = useState("Carol");
    const [tone, setTone] = useState("Empático, acolhedor e eficiente. Use emojis moderadamente.");
    const [targetAudience, setTargetAudience] = useState("Mães preocupadas e pacientes ocupados.");
    const [loading, setLoading] = useState(false);

    // Knowledge Base State
    const [knowledgeItems, setKnowledgeItems] = useState<any[]>([]);
    const [newItemCategory, setNewItemCategory] = useState("Dúvidas Gerais");
    const [newItemQuestion, setNewItemQuestion] = useState("");
    const [newItemAnswer, setNewItemAnswer] = useState("");
    const [isKnowledgeLoading, setIsKnowledgeLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [persona, knowledge] = await Promise.all([
                aiService.getPersona(),
                aiService.getKnowledge()
            ]);

            if (persona) {
                setPersonaName(persona.assistant_name || "Carol");
                setTone(persona.tone || "");
                setTargetAudience(persona.target_audience || "");
            }
            if (knowledge) {
                setKnowledgeItems(knowledge);
            }
        } catch (error) {
            console.error("Failed to load AI config", error);
        } finally {
            setIsKnowledgeLoading(false);
        }
    };

    const handleSavePersona = async () => {
        setLoading(true);
        try {
            await aiService.updatePersona({
                assistant_name: personaName,
                clinic_name: "Bem-Querer Odontologia",
                tone,
                target_audience: targetAudience
            });
            alert("Persona atualizada com sucesso!");
        } catch (e) {
            alert("Erro ao salvar persona.");
        } finally {
            setLoading(false);
        }
    };

    const handleAddKnowledge = async () => {
        if (!newItemQuestion.trim() || !newItemAnswer.trim()) return;

        try {
            const newItem = {
                category: newItemCategory,
                content: newItemAnswer,
                keywords: newItemQuestion.toLowerCase().split(" ") // Simple keyword extraction from question
            };

            // Optimistic Update
            const savedItem = await aiService.saveKnowledge(newItem);
            setKnowledgeItems([...knowledgeItems, savedItem]);

            setNewItemQuestion("");
            setNewItemAnswer("");
        } catch (e) {
            alert("Erro ao adicionar conhecimento.");
        }
    };

    const handleDeleteKnowledge = async (id: string) => {
        if (!confirm("Tem certeza?")) return;
        try {
            await aiService.deleteKnowledge(id);
            setKnowledgeItems(knowledgeItems.filter(i => i.id !== id));
        } catch (e) {
            alert("Erro ao remover item.");
        }
    };

    return (
        <div className="p-6 h-full flex flex-col max-w-6xl mx-auto animate-in fade-in duration-500">

            <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 bg-indigo-100 dark:bg-indigo-900/20 rounded-xl border border-indigo-200 dark:border-indigo-800">
                    <Sparkles className="w-6 h-6 text-indigo-600 dark:text-primary" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-zinc-900 dark:text-foreground tracking-tight">Inteligência Artificial</h1>
                    <p className="text-sm text-zinc-500 dark:text-muted-foreground">Gerencie a personalidade e o conhecimento da sua assistente.</p>
                </div>
            </div>

            <Tabs defaultValue="persona" className="flex-1 flex flex-col min-h-0">
                <TabsList className="w-full max-w-md grid grid-cols-2 mb-6">
                    <TabsTrigger value="persona" className="gap-2">
                        <Bot className="w-4 h-4" />
                        Identidade (Persona)
                    </TabsTrigger>
                    <TabsTrigger value="knowledge" className="gap-2">
                        <BookOpen className="w-4 h-4" />
                        Base de Conhecimento
                    </TabsTrigger>
                </TabsList>

                {/* --- TAB: PERSONA --- */}
                <TabsContent value="persona" className="flex-1 min-h-0 outline-none animate-in slide-in-from-left-4 duration-300">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
                        {/* Editor */}
                        <Card className="bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-700 shadow-sm overflow-hidden flex flex-col">
                            <CardHeader className="border-b border-zinc-100 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-800/50 pb-4">
                                <CardTitle className="text-base font-medium flex items-center gap-2">
                                    <MessageSquare className="w-4 h-4 text-indigo-500" />
                                    Configuração de Comportamento
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="p-6 space-y-5 flex-1 overflow-y-auto">
                                <div className="space-y-2">
                                    <Label>Nome da Assistente</Label>
                                    <div className="relative">
                                        <Bot className="absolute left-3 top-2.5 h-4 w-4 text-zinc-400" />
                                        <Input
                                            value={personaName}
                                            onChange={e => setPersonaName(e.target.value)}
                                            className="pl-9"
                                            placeholder="Ex: Carol"
                                        />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <Label>Tom de Voz</Label>
                                    <Input
                                        value={tone}
                                        onChange={e => setTone(e.target.value)}
                                        placeholder="Ex: Formal, Técnico"
                                    />
                                    <p className="text-xs text-zinc-500">Como ela deve soar nas mensagens?</p>
                                </div>
                                <div className="space-y-2">
                                    <Label>Público Alvo</Label>
                                    <Textarea
                                        value={targetAudience}
                                        onChange={e => setTargetAudience(e.target.value)}
                                        placeholder="Quem são seus clientes?"
                                        className="h-24 resize-none"
                                    />
                                </div>
                            </CardContent>
                            <CardFooter className="border-t border-zinc-100 dark:border-zinc-800 p-4 bg-zinc-50/30 dark:bg-zinc-900/30">
                                <Button onClick={handleSavePersona} disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white">
                                    {loading ? "Salvando..." : "Salvar Alterações"}
                                </Button>
                            </CardFooter>
                        </Card>

                        {/* Preview */}
                        <Card className="bg-zinc-50 dark:bg-zinc-900 border-dashed border-2 border-zinc-200 dark:border-zinc-700 shadow-none flex flex-col justify-center items-center p-8 text-center text-zinc-500">
                            <div className="bg-white dark:bg-zinc-800 p-4 rounded-2xl shadow-lg max-w-sm w-full text-left border border-zinc-100 dark:border-zinc-700">
                                <div className="flex items-center gap-3 mb-3 pb-3 border-b border-zinc-100 dark:border-zinc-700">
                                    <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center">
                                        <Bot className="w-5 h-5 text-indigo-600 dark:text-primary" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold text-zinc-900 dark:text-white">{personaName}</p>
                                        <p className="text-[10px] text-zinc-500">Online agora</p>
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    <div className="bg-indigo-50 dark:bg-indigo-900/20 p-2.5 rounded-lg rounded-tl-none text-xs text-zinc-700 dark:text-zinc-300">
                                        Olá! Sou a <strong>{personaName}</strong>. Como posso ajudar com seu sorriso hoje? ✨
                                    </div>
                                </div>
                            </div>
                            <p className="mt-4 text-xs">Exemplo visual de como o cliente verá o nome.</p>
                        </Card>
                    </div>
                </TabsContent>

                {/* --- TAB: KNOWLEDGE BASE --- */}
                <TabsContent value="knowledge" className="flex-1 min-h-0 outline-none animate-in slide-in-from-right-4 duration-300 flex flex-col gap-4">

                    {/* Add New Item */}
                    <Card className="shrink-0 border-zinc-200 dark:border-zinc-700 shadow-sm">
                        <CardHeader className="py-3 px-4 border-b border-zinc-100 dark:border-zinc-800 bg-zinc-50/50">
                            <CardTitle className="text-sm font-medium flex items-center gap-2">
                                <Plus className="w-4 h-4 text-indigo-500" />
                                Adicionar Novo Conhecimento
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-4 grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
                            <div className="md:col-span-3 space-y-1.5">
                                <Label className="text-xs">Categoria</Label>
                                <Input
                                    value={newItemCategory}
                                    onChange={e => setNewItemCategory(e.target.value)}
                                    placeholder="Ex: Preços"
                                    className="h-9"
                                />
                            </div>
                            <div className="md:col-span-4 space-y-1.5">
                                <Label className="text-xs">Palavras-chave / Pergunta</Label>
                                <Input
                                    value={newItemQuestion}
                                    onChange={e => setNewItemQuestion(e.target.value)}
                                    placeholder="Ex: Quanto custa clareamento?"
                                    className="h-9"
                                />
                            </div>
                            <div className="md:col-span-4 space-y-1.5">
                                <Label className="text-xs">Resposta da IA</Label>
                                <Input
                                    value={newItemAnswer}
                                    onChange={e => setNewItemAnswer(e.target.value)}
                                    placeholder="O valor é R$ 800 sessao completa."
                                    className="h-9"
                                />
                            </div>
                            <div className="md:col-span-1">
                                <Button onClick={handleAddKnowledge} className="w-full h-9 bg-indigo-600 hover:bg-indigo-700 text-white">
                                    <Plus className="w-4 h-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* List Items */}
                    <div className="flex-1 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-lg shadow-sm overflow-hidden flex flex-col">
                        <div className="p-3 border-b border-zinc-100 dark:border-zinc-800 bg-zinc-50/50 flex justify-between items-center">
                            <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
                                <Search className="w-4 h-4 text-zinc-400" />
                                Itens Cadastrados ({knowledgeItems.length})
                            </h3>
                        </div>

                        <div className="flex-1 overflow-y-auto p-0">
                            {knowledgeItems.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center text-zinc-400 gap-2">
                                    <BookOpen className="w-10 h-10 opacity-20" />
                                    <p className="text-sm">Nenhum conhecimento cadastrado ainda.</p>
                                </div>
                            ) : (
                                <table className="w-full text-sm text-left">
                                    <thead className="text-xs text-zinc-500 uppercase bg-zinc-50/50 dark:bg-zinc-800/50 sticky top-0">
                                        <tr>
                                            <th className="px-4 py-3 font-medium">Categoria</th>
                                            <th className="px-4 py-3 font-medium">Palavras-chave</th>
                                            <th className="px-4 py-3 font-medium">Resposta</th>
                                            <th className="px-4 py-3 text-right">Ações</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                                        {knowledgeItems.map((item) => (
                                            <tr key={item.id} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-800/50 transition-colors">
                                                <td className="px-4 py-3 font-medium text-indigo-600 dark:text-indigo-400 whitespace-nowrap">
                                                    {item.category}
                                                </td>
                                                <td className="px-4 py-3 text-zinc-500 max-w-[200px] truncate" title={item.keywords?.join(", ")}>
                                                    {(item.keywords || []).join(", ")}
                                                </td>
                                                <td className="px-4 py-3 text-zinc-700 dark:text-zinc-300 max-w-[400px] truncate" title={item.content}>
                                                    {item.content}
                                                </td>
                                                <td className="px-4 py-3 text-right">
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="h-8 w-8 p-0 text-red-500 hover:text-red-600 hover:bg-red-50"
                                                        onClick={() => handleDeleteKnowledge(item.id)}
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </Button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </div>

                </TabsContent>
            </Tabs>
        </div>
    );
};
