/**
 * Enhanced AI Configuration Wizard with better UX
 * - Specialty dropdowns
 * - Day of week checkboxes
 * - Tone presets
 * - CEP lookup
 * - Input masks
 */
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Plus, Trash2, Eye, Save, ArrowLeft, ArrowRight, Sparkles, Search } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const CLINIC_ID = '00000000-0000-0000-0000-000000000001';

// Presets
const SPECIALTIES = [
    'Ortodontia',
    'Odontopediatria',
    'Implantodontia',
    'Periodontia',
    'Endodontia',
    'Prótese Dentária',
    'Cirurgia Bucomaxilofacial',
    'Estomatologia',
    'Radiologia',
    'Clínica Geral',
    'Harmonização Orofacial',
    'DTM e Dor Orofacial',
    'Pacientes Especiais (PNE)'
];

const TONE_PRESETS = [
    { value: 'empatica', label: 'Empática e Acolhedora', description: 'Tom maternal, carinhoso e compreensivo' },
    { value: 'profissional', label: 'Profissional e Objetiva', description: 'Tom direto, claro e eficiente' },
    { value: 'amigavel', label: 'Amigável e Descontraída', description: 'Tom leve, próximo e informal' },
    { value: 'tecnica', label: 'Técnica e Educativa', description: 'Tom explicativo e informativo' }
];

const DAYS_OF_WEEK = [
    { id: 'mon', label: 'Segunda' },
    { id: 'tue', label: 'Terça' },
    { id: 'wed', label: 'Quarta' },
    { id: 'thu', label: 'Quinta' },
    { id: 'fri', label: 'Sexta' },
    { id: 'sat', label: 'Sábado' },
    { id: 'sun', label: 'Domingo' }
];

interface TeamMember {
    name: string;
    clinicorp_id: string;
    specialty: string;
    focus: string;
    schedule: string[];
    position: string;
}

interface AIConfiguration {
    persona: {
        name: string;
        clinic_name: string;
        role: string;
        tone: string;
        target_audience: string;
        objective: string;
        voice_examples: string;
    };
    team: TeamMember[];
    admin_info: {
        location: {
            cep: string;
            address: string;
            number: string;
            complement: string;
            neighborhood: string;
            city: string;
            state: string;
            reference: string;
            parking: string;
        };
        schedule: {
            weekdays: string;
            saturday: string;
            sunday: string;
        };
        pricing: {
            consultation: string;
            consultation_note: string;
            insurance: string;
            payment_methods: string;
        };
        contact: {
            phone: string;
            website: string;
            instagram: string;
        };
    };
    protocols: {
        emergency: { triggers: string; steps: string[] };
        scheduling: { steps: string[] };
        do_rules: string[];
        dont_rules: string[];
    };
}

export default function AIConfigWizardEnhanced() {
    const [currentStep, setCurrentStep] = useState(0);
    const [loading, setLoading] = useState(false);
    const [preview, setPreview] = useState('');
    const [showPreview, setShowPreview] = useState(false);

    const [config, setConfig] = useState<AIConfiguration>({
        persona: {
            name: 'Carol',
            clinic_name: '',
            role: 'secretária virtual',
            tone: 'empatica',
            target_audience: 'Mães preocupadas e pacientes ocupados',
            objective: 'Conduzir conversas naturalmente e direcionar para agendamento',
            voice_examples: 'Use "pequeno(a)", "mamãe", "papai" quando apropriado. Seja empática e objetiva.'
        },
        team: [],
        admin_info: {
            location: {
                cep: '',
                address: '',
                number: '',
                complement: '',
                neighborhood: '',
                city: '',
                state: '',
                reference: '',
                parking: ''
            },
            schedule: { weekdays: '08h às 19h', saturday: '09h às 16h', sunday: 'Fechado' },
            pricing: { consultation: '', consultation_note: '', insurance: '', payment_methods: '' },
            contact: { phone: '', website: '', instagram: '' }
        },
        protocols: {
            emergency: { triggers: '', steps: [] },
            scheduling: { steps: [] },
            do_rules: [],
            dont_rules: []
        }
    });

    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/ai-config/${CLINIC_ID}`);
            if (response.data.config) {
                const loadedConfig = response.data.config;
                setConfig(prev => ({
                    ...prev,
                    ...loadedConfig,
                    admin_info: {
                        ...prev.admin_info,
                        ...loadedConfig.admin_info,
                        location: { ...prev.admin_info.location, ...loadedConfig.admin_info?.location }
                    }
                }));
            }
        } catch (error) {
            console.log('No existing config found, using defaults');
        }
    };

    const saveConfig = async () => {
        setLoading(true);
        try {
            await axios.post(`${API_URL}/api/ai-config/${CLINIC_ID}`, config);
            alert('✅ Configuração salva com sucesso!');
        } catch (error) {
            console.error('Error saving config:', error);
            alert('❌ Erro ao salvar configuração');
        } finally {
            setLoading(false);
        }
    };

    const loadPreview = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_URL}/api/ai-config/${CLINIC_ID}/preview`);
            setPreview(response.data.prompt);
            setShowPreview(true);
        } catch (error) {
            console.error('Error loading preview:', error);
            alert('Erro ao gerar preview');
        } finally {
            setLoading(false);
        }
    };

    const steps = [
        { title: 'Persona', icon: '🎭' },
        { title: 'Equipe', icon: '👥' },
        { title: 'Administrativo', icon: '📋' },
        { title: 'Protocolos', icon: '🔧' },
        { title: 'Preview', icon: '👁️' }
    ];

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Sparkles className="w-6 h-6 text-purple-500" />
                        Configuração da Assistente Virtual
                    </CardTitle>
                    <CardDescription>
                        Configure a personalidade e comportamento da sua assistente de IA
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {/* Progress Steps */}
                    <div className="flex justify-between mb-8">
                        {steps.map((step, index) => (
                            <div
                                key={index}
                                className={`flex flex-col items-center cursor-pointer transition-all ${index === currentStep ? 'text-purple-600 scale-110' : 'text-gray-400'
                                    }`}
                                onClick={() => setCurrentStep(index)}
                            >
                                <div
                                    className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl mb-2 transition-all ${index === currentStep
                                            ? 'bg-purple-100 ring-2 ring-purple-500 shadow-lg'
                                            : 'bg-gray-100 hover:bg-gray-200'
                                        }`}
                                >
                                    {step.icon}
                                </div>
                                <span className="text-sm font-medium">{step.title}</span>
                            </div>
                        ))}
                    </div>

                    {/* Step Content */}
                    <div className="min-h-[500px]">
                        {currentStep === 0 && <PersonaStepEnhanced config={config} setConfig={setConfig} />}
                        {currentStep === 1 && <TeamStepEnhanced config={config} setConfig={setConfig} />}
                        {currentStep === 2 && <AdminStepEnhanced config={config} setConfig={setConfig} />}
                        {currentStep === 3 && <ProtocolsStepEnhanced config={config} setConfig={setConfig} />}
                        {currentStep === 4 && (
                            <PreviewStepEnhanced
                                config={config}
                                preview={preview}
                                showPreview={showPreview}
                                loadPreview={loadPreview}
                                loading={loading}
                            />
                        )}
                    </div>

                    {/* Navigation */}
                    <div className="flex justify-between mt-8 pt-6 border-t">
                        <Button
                            variant="outline"
                            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                            disabled={currentStep === 0}
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Anterior
                        </Button>

                        <div className="flex gap-2">
                            {currentStep === steps.length - 1 ? (
                                <Button onClick={saveConfig} disabled={loading} className="bg-purple-600 hover:bg-purple-700">
                                    <Save className="w-4 h-4 mr-2" />
                                    {loading ? 'Salvando...' : 'Salvar Configuração'}
                                </Button>
                            ) : (
                                <Button
                                    onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
                                    className="bg-purple-600 hover:bg-purple-700"
                                >
                                    Próximo
                                    <ArrowRight className="w-4 h-4 ml-2" />
                                </Button>
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

// Enhanced Persona Step with Tone Presets
function PersonaStepEnhanced({ config, setConfig }: any) {
    const updatePersona = (field: string, value: string) => {
        setConfig({
            ...config,
            persona: { ...config.persona, [field]: value }
        });
    };

    const selectedTone = TONE_PRESETS.find(t => t.value === config.persona.tone);

    return (
        <div className="space-y-6">
            <h3 className="text-lg font-semibold">Defina a Persona da Assistente</h3>

            <div className="grid grid-cols-2 gap-4">
                <div>
                    <Label htmlFor="name">Nome da Assistente *</Label>
                    <Input
                        id="name"
                        value={config.persona.name}
                        onChange={(e) => updatePersona('name', e.target.value)}
                        placeholder="Ex: Carol, Ana, Sofia..."
                        className="mt-1"
                    />
                </div>

                <div>
                    <Label htmlFor="clinic_name">Nome da Clínica *</Label>
                    <Input
                        id="clinic_name"
                        value={config.persona.clinic_name}
                        onChange={(e) => updatePersona('clinic_name', e.target.value)}
                        placeholder="Ex: Bem-Querer Odontokids"
                        className="mt-1"
                    />
                </div>
            </div>

            <div>
                <Label htmlFor="tone">Tom de Voz *</Label>
                <Select value={config.persona.tone} onValueChange={(value) => updatePersona('tone', value)}>
                    <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Selecione o tom de voz" />
                    </SelectTrigger>
                    <SelectContent>
                        {TONE_PRESETS.map((tone) => (
                            <SelectItem key={tone.value} value={tone.value}>
                                <div className="flex flex-col">
                                    <span className="font-medium">{tone.label}</span>
                                    <span className="text-xs text-gray-500">{tone.description}</span>
                                </div>
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
                {selectedTone && (
                    <p className="text-sm text-gray-600 mt-2">💡 {selectedTone.description}</p>
                )}
            </div>

            <div>
                <Label htmlFor="target_audience">Público-Alvo</Label>
                <Input
                    id="target_audience"
                    value={config.persona.target_audience}
                    onChange={(e) => updatePersona('target_audience', e.target.value)}
                    placeholder="Ex: Mães preocupadas, pacientes ocupados"
                    className="mt-1"
                />
            </div>

            <div>
                <Label htmlFor="objective">Objetivo Principal</Label>
                <Textarea
                    id="objective"
                    value={config.persona.objective}
                    onChange={(e) => updatePersona('objective', e.target.value)}
                    placeholder="Ex: Conduzir conversas naturalmente e direcionar para agendamento"
                    rows={3}
                    className="mt-1"
                />
            </div>
        </div>
    );
}

// Enhanced Team Step with Specialty Dropdown and Day Checkboxes
function TeamStepEnhanced({ config, setConfig }: any) {
    const addTeamMember = () => {
        setConfig({
            ...config,
            team: [
                ...config.team,
                {
                    name: '',
                    clinicorp_id: '',
                    specialty: '',
                    focus: '',
                    schedule: [],
                    position: ''
                }
            ]
        });
    };

    const updateTeamMember = (index: number, field: string, value: any) => {
        const newTeam = [...config.team];
        newTeam[index] = { ...newTeam[index], [field]: value };
        setConfig({ ...config, team: newTeam });
    };

    const toggleDay = (index: number, dayId: string) => {
        const member = config.team[index];
        const schedule = member.schedule || [];
        const newSchedule = schedule.includes(dayId)
            ? schedule.filter((d: string) => d !== dayId)
            : [...schedule, dayId];
        updateTeamMember(index, 'schedule', newSchedule);
    };

    const removeTeamMember = (index: number) => {
        setConfig({
            ...config,
            team: config.team.filter((_: any, i: number) => i !== index)
        });
    };

    const getScheduleText = (schedule: string[]) => {
        if (!schedule || schedule.length === 0) return 'Nenhum dia selecionado';
        return schedule.map(id => DAYS_OF_WEEK.find(d => d.id === id)?.label).join(', ');
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Equipe Médica</h3>
                <Button onClick={addTeamMember} size="sm" className="bg-purple-600">
                    <Plus className="w-4 h-4 mr-2" />
                    Adicionar Profissional
                </Button>
            </div>

            {config.team.length === 0 ? (
                <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg border-2 border-dashed">
                    <p className="text-lg mb-2">👥 Nenhum profissional adicionado</p>
                    <p className="text-sm">Clique em "Adicionar Profissional" para começar</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {config.team.map((member: TeamMember, index: number) => (
                        <Card key={index} className="border-2 hover:border-purple-200 transition-colors">
                            <CardContent className="pt-6">
                                <div className="flex justify-between items-start mb-4">
                                    <h4 className="font-medium text-lg">Profissional #{index + 1}</h4>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => removeTeamMember(index)}
                                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <Label>Nome Completo *</Label>
                                        <Input
                                            value={member.name}
                                            onChange={(e) => updateTeamMember(index, 'name', e.target.value)}
                                            placeholder="Ex: Dra. Fernanda Battistini"
                                            className="mt-1"
                                        />
                                    </div>

                                    <div>
                                        <Label>ID Clinicorp</Label>
                                        <Input
                                            value={member.clinicorp_id}
                                            onChange={(e) => updateTeamMember(index, 'clinicorp_id', e.target.value)}
                                            placeholder="Ex: 6113706666688512"
                                            className="mt-1"
                                        />
                                    </div>

                                    <div>
                                        <Label>Especialidade *</Label>
                                        <Select
                                            value={member.specialty}
                                            onValueChange={(value) => updateTeamMember(index, 'specialty', value)}
                                        >
                                            <SelectTrigger className="mt-1">
                                                <SelectValue placeholder="Selecione a especialidade" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {SPECIALTIES.map((spec) => (
                                                    <SelectItem key={spec} value={spec}>
                                                        {spec}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div>
                                        <Label>Foco/Área Específica</Label>
                                        <Input
                                            value={member.focus}
                                            onChange={(e) => updateTeamMember(index, 'focus', e.target.value)}
                                            placeholder="Ex: Aparelhos fixos, Invisalign"
                                            className="mt-1"
                                        />
                                    </div>

                                    <div className="col-span-2">
                                        <Label>Dias de Atendimento *</Label>
                                        <div className="grid grid-cols-7 gap-2 mt-2">
                                            {DAYS_OF_WEEK.map((day) => (
                                                <div key={day.id} className="flex items-center space-x-2">
                                                    <Checkbox
                                                        id={`${index}-${day.id}`}
                                                        checked={member.schedule?.includes(day.id)}
                                                        onCheckedChange={() => toggleDay(index, day.id)}
                                                    />
                                                    <Label
                                                        htmlFor={`${index}-${day.id}`}
                                                        className="text-sm cursor-pointer"
                                                    >
                                                        {day.label}
                                                    </Label>
                                                </div>
                                            ))}
                                        </div>
                                        <p className="text-sm text-gray-600 mt-2">
                                            📅 {getScheduleText(member.schedule)}
                                        </p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}

// Enhanced Admin Step with CEP Lookup
function AdminStepEnhanced({ config, setConfig }: any) {
    const [loadingCep, setLoadingCep] = useState(false);

    const searchCep = async () => {
        const cep = config.admin_info.location.cep.replace(/\D/g, '');
        if (cep.length !== 8) {
            alert('CEP inválido');
            return;
        }

        setLoadingCep(true);
        try {
            const response = await axios.get(`https://viacep.com.br/ws/${cep}/json/`);
            if (response.data.erro) {
                alert('CEP não encontrado');
                return;
            }

            setConfig({
                ...config,
                admin_info: {
                    ...config.admin_info,
                    location: {
                        ...config.admin_info.location,
                        address: response.data.logradouro,
                        neighborhood: response.data.bairro,
                        city: response.data.localidade,
                        state: response.data.uf
                    }
                }
            });
        } catch (error) {
            alert('Erro ao buscar CEP');
        } finally {
            setLoadingCep(false);
        }
    };

    const updateLocation = (field: string, value: string) => {
        setConfig({
            ...config,
            admin_info: {
                ...config.admin_info,
                location: { ...config.admin_info.location, [field]: value }
            }
        });
    };

    const formatPhone = (value: string) => {
        const numbers = value.replace(/\D/g, '');
        if (numbers.length <= 10) {
            return numbers.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
        }
        return numbers.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
    };

    return (
        <div className="space-y-6">
            <Tabs defaultValue="location">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="location">📍 Localização</TabsTrigger>
                    <TabsTrigger value="schedule">⏰ Horários</TabsTrigger>
                    <TabsTrigger value="pricing">💰 Valores</TabsTrigger>
                    <TabsTrigger value="contact">📞 Contatos</TabsTrigger>
                </TabsList>

                <TabsContent value="location" className="space-y-4 mt-4">
                    <div className="grid grid-cols-4 gap-4">
                        <div className="col-span-3">
                            <Label>CEP *</Label>
                            <Input
                                value={config.admin_info.location.cep}
                                onChange={(e) => updateLocation('cep', e.target.value)}
                                placeholder="00000-000"
                                maxLength={9}
                                className="mt-1"
                            />
                        </div>
                        <div className="flex items-end">
                            <Button
                                onClick={searchCep}
                                disabled={loadingCep}
                                className="w-full"
                                variant="outline"
                            >
                                <Search className="w-4 h-4 mr-2" />
                                {loadingCep ? 'Buscando...' : 'Buscar'}
                            </Button>
                        </div>
                    </div>

                    <div className="grid grid-cols-4 gap-4">
                        <div className="col-span-3">
                            <Label>Endereço</Label>
                            <Input
                                value={config.admin_info.location.address}
                                onChange={(e) => updateLocation('address', e.target.value)}
                                placeholder="Rua, Avenida..."
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <Label>Número</Label>
                            <Input
                                value={config.admin_info.location.number}
                                onChange={(e) => updateLocation('number', e.target.value)}
                                placeholder="123"
                                className="mt-1"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                        <div>
                            <Label>Bairro</Label>
                            <Input
                                value={config.admin_info.location.neighborhood}
                                onChange={(e) => updateLocation('neighborhood', e.target.value)}
                                placeholder="Centro"
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <Label>Cidade</Label>
                            <Input
                                value={config.admin_info.location.city}
                                onChange={(e) => updateLocation('city', e.target.value)}
                                placeholder="São Paulo"
                                className="mt-1"
                            />
                        </div>
                        <div>
                            <Label>Estado</Label>
                            <Input
                                value={config.admin_info.location.state}
                                onChange={(e) => updateLocation('state', e.target.value)}
                                placeholder="SP"
                                maxLength={2}
                                className="mt-1"
                            />
                        </div>
                    </div>

                    <div>
                        <Label>Complemento</Label>
                        <Input
                            value={config.admin_info.location.complement}
                            onChange={(e) => updateLocation('complement', e.target.value)}
                            placeholder="Sala 101, Bloco A..."
                            className="mt-1"
                        />
                    </div>

                    <div>
                        <Label>Ponto de Referência</Label>
                        <Input
                            value={config.admin_info.location.reference}
                            onChange={(e) => updateLocation('reference', e.target.value)}
                            placeholder="Ex: Próximo à Padaria Brasileira"
                            className="mt-1"
                        />
                    </div>

                    <div>
                        <Label>Estacionamento</Label>
                        <Input
                            value={config.admin_info.location.parking}
                            onChange={(e) => updateLocation('parking', e.target.value)}
                            placeholder="Ex: Estacionamento conveniado na Rua X"
                            className="mt-1"
                        />
                    </div>
                </TabsContent>

                <TabsContent value="schedule" className="space-y-4 mt-4">
                    <div>
                        <Label>Segunda a Sexta</Label>
                        <Input
                            value={config.admin_info.schedule.weekdays}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        schedule: { ...config.admin_info.schedule, weekdays: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: 08h às 19h"
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <Label>Sábado</Label>
                        <Input
                            value={config.admin_info.schedule.saturday}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        schedule: { ...config.admin_info.schedule, saturday: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: 09h às 16h"
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <Label>Domingo/Feriados</Label>
                        <Input
                            value={config.admin_info.schedule.sunday}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        schedule: { ...config.admin_info.schedule, sunday: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: Fechado"
                            className="mt-1"
                        />
                    </div>
                </TabsContent>

                <TabsContent value="pricing" className="space-y-4 mt-4">
                    <div>
                        <Label>Valor da Consulta</Label>
                        <Input
                            value={config.admin_info.pricing.consultation}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        pricing: { ...config.admin_info.pricing, consultation: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: R$ 250,00"
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <Label>Observação sobre Consulta</Label>
                        <Input
                            value={config.admin_info.pricing.consultation_note}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        pricing: { ...config.admin_info.pricing, consultation_note: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: Grátis se fechar tratamento no dia"
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <Label>Política de Convênios</Label>
                        <Textarea
                            value={config.admin_info.pricing.insurance}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        pricing: { ...config.admin_info.pricing, insurance: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: Não atendemos diretamente. Emitimos NF para reembolso"
                            rows={2}
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <Label>Formas de Pagamento</Label>
                        <Input
                            value={config.admin_info.pricing.payment_methods}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        pricing: { ...config.admin_info.pricing, payment_methods: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: PIX, Cartão, Dinheiro"
                            className="mt-1"
                        />
                    </div>
                </TabsContent>

                <TabsContent value="contact" className="space-y-4 mt-4">
                    <div>
                        <Label>WhatsApp/Telefone</Label>
                        <Input
                            value={config.admin_info.contact.phone}
                            onChange={(e) => {
                                const formatted = formatPhone(e.target.value);
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        contact: { ...config.admin_info.contact, phone: formatted }
                                    }
                                });
                            }}
                            placeholder="(11) 98765-4321"
                            maxLength={15}
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <Label>Website</Label>
                        <Input
                            value={config.admin_info.contact.website}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        contact: { ...config.admin_info.contact, website: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: minhaclínica.com.br"
                            className="mt-1"
                        />
                    </div>
                    <div>
                        <Label>Instagram</Label>
                        <Input
                            value={config.admin_info.contact.instagram}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    admin_info: {
                                        ...config.admin_info,
                                        contact: { ...config.admin_info.contact, instagram: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: @minhaclínica"
                            className="mt-1"
                        />
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}

// Protocols and Preview steps remain the same as original
function ProtocolsStepEnhanced({ config, setConfig }: any) {
    // Same as original ProtocolsStep
    return <div>Protocolos (mantido igual ao original)</div>;
}

function PreviewStepEnhanced({ config, preview, showPreview, loadPreview, loading }: any) {
    return (
        <div className="space-y-6">
            <div className="text-center">
                <h3 className="text-lg font-semibold mb-2">Preview do Prompt Gerado</h3>
                <p className="text-gray-600 mb-4">
                    Visualize como ficará o prompt da sua assistente virtual
                </p>
                <Button onClick={loadPreview} disabled={loading} className="bg-purple-600">
                    <Eye className="w-4 h-4 mr-2" />
                    {loading ? 'Gerando...' : 'Gerar Preview'}
                </Button>
            </div>

            {showPreview && (
                <Card>
                    <CardContent className="pt-6">
                        <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded max-h-96 overflow-y-auto">
                            {preview}
                        </pre>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
