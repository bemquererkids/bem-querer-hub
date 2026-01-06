/**
 * AI Configuration Wizard - Multi-step form for configuring AI assistant
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
import { Plus, Trash2, Eye, Save, ArrowLeft, ArrowRight, Sparkles, Search, Check, X, User, Users, Building, Settings, FileText } from 'lucide-react';
import axios from 'axios';

// Custom notification helper
const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500'
    };

    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-in slide-in-from-top`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('animate-out', 'fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
};

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const CLINIC_ID = '00000000-0000-0000-0000-000000000001';

// UX Presets
const SPECIALTIES = [
    'Ortodontia',
    'Ortopedia Funcional dos Maxilares',
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
    'Pacientes Especiais (PNE)',
    'Dentística Restauradora'
];

const TONE_PRESETS = [
    { value: 'Empática, acolhedora e eficiente', label: 'Empática e Acolhedora' },
    { value: 'Profissional, objetiva e clara', label: 'Profissional e Objetiva' },
    { value: 'Amigável, descontraída e próxima', label: 'Amigável e Descontraída' },
    { value: 'Técnica, educativa e informativa', label: 'Técnica e Educativa' }
];

const DAYS_OF_WEEK = [
    { id: 'seg', label: 'Seg' },
    { id: 'ter', label: 'Ter' },
    { id: 'qua', label: 'Qua' },
    { id: 'qui', label: 'Qui' },
    { id: 'sex', label: 'Sex' },
    { id: 'sab', label: 'Sáb' },
    { id: 'dom', label: 'Dom' }
];

interface PersonaConfig {
    name: string;
    clinic_name: string;
    role: string;
    tone: string;
    target_audience: string;
    objective: string;
    voice_examples: string;
}

interface TeamMember {
    name: string;
    clinicorp_id: string;
    specialty: string[];  // Array for multiple specialties
    focus: string;
    schedule: string;
    position: string;
}

interface LocationInfo {
    address: string;
    reference: string;
    parking: string;
}

interface ScheduleInfo {
    weekdays: string;
    saturday: string;
    sunday: string;
}

interface PricingInfo {
    consultation: string;
    consultation_note: string;
    insurance: string;
    payment_methods: string;
}

interface ContactInfo {
    phone: string;
    website: string;
    instagram: string;
}

interface AdminInfo {
    location: LocationInfo;
    schedule: ScheduleInfo;
    pricing: PricingInfo;
    contact: ContactInfo;
}

interface EmergencyProtocol {
    triggers: string;
    steps: string[];
}

interface SchedulingProtocol {
    steps: string[];
}

interface Protocols {
    emergency: EmergencyProtocol;
    scheduling: SchedulingProtocol;
    do_rules: string[];
    dont_rules: string[];
}

interface AIConfiguration {
    persona: PersonaConfig;
    team: TeamMember[];
    admin_info: AdminInfo;
    protocols: Protocols;
}

export default function AIConfigWizard() {
    const [currentStep, setCurrentStep] = useState(0);
    const [loading, setLoading] = useState(false);
    const [preview, setPreview] = useState('');
    const [showPreview, setShowPreview] = useState(false);

    const [config, setConfig] = useState<AIConfiguration>({
        persona: {
            name: 'Carol',
            clinic_name: '',
            role: 'secretária virtual',
            tone: 'Empática, acolhedora e eficiente',
            target_audience: 'Mães preocupadas e pacientes ocupados',
            objective: 'Conduzir conversas naturalmente e direcionar para agendamento',
            voice_examples: 'Use "pequeno(a)", "mamãe", "papai" quando apropriado. Seja empática e objetiva.'
        },
        team: [],
        admin_info: {
            location: { address: '', reference: '', parking: '' },
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

    // Load existing configuration
    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/ai-config/${CLINIC_ID}`);
            if (response.data.config) {
                // Deep merge to ensure all nested objects exist
                const loadedConfig = response.data.config;
                setConfig({
                    persona: { ...config.persona, ...loadedConfig.persona },
                    team: loadedConfig.team || [],
                    admin_info: {
                        location: { ...config.admin_info.location, ...(loadedConfig.admin_info?.location || {}) },
                        schedule: { ...config.admin_info.schedule, ...(loadedConfig.admin_info?.schedule || {}) },
                        pricing: { ...config.admin_info.pricing, ...(loadedConfig.admin_info?.pricing || {}) },
                        contact: { ...config.admin_info.contact, ...(loadedConfig.admin_info?.contact || {}) }
                    },
                    protocols: {
                        emergency: { ...config.protocols.emergency, ...(loadedConfig.protocols?.emergency || {}) },
                        scheduling: { ...config.protocols.scheduling, ...(loadedConfig.protocols?.scheduling || {}) },
                        do_rules: loadedConfig.protocols?.do_rules || [],
                        dont_rules: loadedConfig.protocols?.dont_rules || []
                    }
                });
            }
        } catch (error) {
            console.log('No existing config found, using defaults');
        }
    };

    const saveConfig = async () => {
        setLoading(true);
        try {
            await axios.post(`${API_URL}/api/ai-config/${CLINIC_ID}`, config);
            alert('Configuração salva com sucesso!');
        } catch (error) {
            console.error('Error saving config:', error);
            alert('Erro ao salvar configuração');
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
            showNotification('✨ Preview gerado com sucesso!', 'success');
        } catch (error) {
            console.error('Error loading preview:', error);
            showNotification('❌ Erro ao gerar preview', 'error');
        } finally {
            setLoading(false);
        }
    };

    const steps = [
        { title: 'Persona', icon: User },
        { title: 'Equipe', icon: Users },
        { title: 'Administrativo', icon: Building },
        { title: 'Protocolos', icon: Settings },
        { title: 'Preview', icon: Eye }
    ];

    return (
        <div className="container mx-auto p-4 max-w-6xl">
            <Card className="shadow-lg border-0 bg-white dark:bg-card dark:border dark:border-border">
                <CardHeader className="pb-4 border-b border-zinc-100 dark:border-zinc-800 space-y-1">
                    <CardTitle className="flex items-center gap-2 text-xl text-zinc-900 dark:text-zinc-50 tracking-tight">
                        <div className="p-2 bg-purple-100 dark:bg-purple-500/20 rounded-lg">
                            <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                        </div>
                        Configuração da Assistente Virtual
                    </CardTitle>
                    <CardDescription className="text-sm dark:text-gray-400">
                        Configure a personalidade e comportamento da sua assistente de IA
                    </CardDescription>
                </CardHeader>
                <CardContent className="pt-6">
                    {/* Progress Steps */}
                    <div className="flex justify-between mb-6">
                        {steps.map((step, index) => (
                            <div
                                key={index}
                                className={`flex flex-col items-center cursor-pointer transition-all ${index === currentStep ? 'text-purple-600 dark:text-purple-400 scale-105' : 'text-gray-400 dark:text-gray-500'
                                    }`}
                                onClick={() => setCurrentStep(index)}
                            >
                                <div
                                    className={`w-10 h-10 rounded-full flex items-center justify-center text-lg mb-2 transition-all duration-300 ${index === currentStep
                                        ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/30 scale-110 ring-2 ring-purple-600 ring-offset-2 dark:ring-offset-gray-900'
                                        : 'bg-zinc-100 text-zinc-400 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-500 dark:hover:bg-zinc-700'
                                        }`}
                                >
                                    <step.icon className="w-5 h-5" />
                                </div>
                                <span className="text-xs font-medium">{step.title}</span>
                            </div>
                        ))}
                    </div>

                    {/* Step Content */}
                    <div className="min-h-[400px] max-h-[500px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-zinc-200 dark:scrollbar-thumb-zinc-800 scrollbar-track-transparent">
                        {currentStep === 0 && <PersonaStep config={config} setConfig={setConfig} />}
                        {currentStep === 1 && <TeamStep config={config} setConfig={setConfig} />}
                        {currentStep === 2 && <AdminStep config={config} setConfig={setConfig} />}
                        {currentStep === 3 && <ProtocolsStep config={config} setConfig={setConfig} />}
                        {currentStep === 4 && (
                            <PreviewStep
                                config={config}
                                preview={preview}
                                showPreview={showPreview}
                                loadPreview={loadPreview}
                                loading={loading}
                            />
                        )}
                    </div>

                    {/* Navigation */}
                    <div className="flex justify-between mt-6 pt-4 border-t dark:border-gray-700">
                        <Button
                            variant="outline"
                            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                            disabled={currentStep === 0}
                            className="text-zinc-600 dark:text-zinc-400 border-zinc-200 dark:border-zinc-700 hover:bg-zinc-100 dark:hover:bg-zinc-800 dark:hover:text-zinc-200 transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Anterior
                        </Button>

                        <div className="flex gap-2">
                            {currentStep === steps.length - 1 ? (
                                <Button onClick={saveConfig} disabled={loading} className="bg-purple-600">
                                    <Save className="w-4 h-4 mr-2" />
                                    Salvar Configuração
                                </Button>
                            ) : (
                                <Button
                                    onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
                                    className="bg-purple-600"
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

// Step 1: Persona Configuration
function PersonaStep({ config, setConfig }: any) {
    const updatePersona = (field: string, value: string) => {
        setConfig({
            ...config,
            persona: { ...config.persona, [field]: value }
        });
    };

    return (
        <div className="space-y-3">
            <h3 className="text-base font-semibold mb-3 dark:text-white">Defina a Persona da Assistente</h3>

            <div className="grid grid-cols-2 gap-3">
                <div>
                    <Label htmlFor="name" className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Nome da Assistente</Label>
                    <Input
                        id="name"
                        value={config.persona.name}
                        onChange={(e) => updatePersona('name', e.target.value)}
                        placeholder="Ex: Carol, Ana..."
                        className="h-10 mt-1.5 dark:bg-zinc-900/50 dark:border-zinc-700 focus:ring-purple-500/20"
                    />
                </div>

                <div>
                    <Label htmlFor="clinic_name" className="text-sm">Nome da Clínica</Label>
                    <Input
                        id="clinic_name"
                        value={config.persona.clinic_name}
                        onChange={(e) => updatePersona('clinic_name', e.target.value)}
                        placeholder="Ex: Bem-Querer Odontokids"
                        className="h-9 text-sm"
                    />
                </div>

                <div>
                    <Label htmlFor="role" className="text-sm">Função/Papel</Label>
                    <Input
                        id="role"
                        value={config.persona.role}
                        onChange={(e) => updatePersona('role', e.target.value)}
                        placeholder="Ex: secretária virtual"
                        className="h-9 text-sm"
                    />
                </div>

                <div>
                    <Label htmlFor="tone" className="text-sm">Tom de Voz</Label>
                    <Select value={config.persona.tone} onValueChange={(value) => updatePersona('tone', value)}>
                        <SelectTrigger id="tone" className="h-9 text-sm">
                            <SelectValue placeholder="Selecione o tom" />
                        </SelectTrigger>
                        <SelectContent>
                            {TONE_PRESETS.map((tone) => (
                                <SelectItem key={tone.value} value={tone.value} className="text-sm">
                                    {tone.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <div>
                <Label htmlFor="target_audience" className="text-sm">Público-Alvo</Label>
                <Input
                    id="target_audience"
                    value={config.persona.target_audience}
                    onChange={(e) => updatePersona('target_audience', e.target.value)}
                    placeholder="Ex: Mães preocupadas, pacientes ocupados"
                    className="h-9 text-sm"
                />
            </div>

            <div>
                <Label htmlFor="objective" className="text-sm">Objetivo Principal</Label>
                <Textarea
                    id="objective"
                    value={config.persona.objective}
                    onChange={(e) => updatePersona('objective', e.target.value)}
                    placeholder="Ex: Conduzir conversas naturalmente..."
                    rows={2}
                    className="text-sm resize-none"
                />
            </div>
        </div>
    );
}

// Step 2: Team Configuration
function TeamStep({ config, setConfig }: any) {
    const addTeamMember = () => {
        setConfig({
            ...config,
            team: [
                ...config.team,
                {
                    name: '',
                    clinicorp_id: '',
                    specialty: [],
                    focus: '',
                    schedule: '',
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

    const removeTeamMember = (index: number) => {
        setConfig({
            ...config,
            team: config.team.filter((_: any, i: number) => i !== index)
        });
    };

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold dark:text-white">Equipe Médica</h3>
                <Button onClick={addTeamMember} size="sm" className="bg-purple-600">
                    <Plus className="w-4 h-4 mr-2" />
                    Adicionar Profissional
                </Button>
            </div>

            {config.team.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                    Nenhum profissional adicionado. Clique em "Adicionar Profissional" para começar.
                </div>
            ) : (
                <div className="space-y-4">
                    {config.team.map((member: TeamMember, index: number) => (
                        <Card key={index} className="bg-white dark:bg-zinc-900/30 border border-zinc-200 dark:border-zinc-800 shadow-sm transition-all hover:border-zinc-300 dark:hover:border-zinc-700">
                            <CardContent className="pt-6">
                                <div className="flex justify-between items-center mb-4 pb-3 border-b border-dashed border-zinc-200 dark:border-zinc-800">
                                    <div className="flex items-center gap-2">
                                        <div className="w-6 h-6 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-xs font-bold text-purple-700 dark:text-purple-400">
                                            {index + 1}
                                        </div>
                                        <h4 className="font-medium text-sm text-zinc-900 dark:text-zinc-100">Profissional</h4>
                                    </div>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => removeTeamMember(index)}
                                        className="text-red-500"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>

                                <div className="grid grid-cols-12 gap-3">
                                    <div className="col-span-4">
                                        <Label className="text-xs dark:text-gray-300">Nome</Label>
                                        <Input
                                            value={member.name}
                                            onChange={(e) => updateTeamMember(index, 'name', e.target.value)}
                                            placeholder="Dra. Fernanda"
                                            className="h-9 text-xs mt-1 dark:bg-zinc-950/50 dark:border-zinc-800 dark:text-zinc-100 focus:border-purple-500 focus:ring-purple-500/20"
                                        />
                                    </div>

                                    <div className="col-span-4">
                                        <Label className="text-xs dark:text-gray-300">ID Clinicorp</Label>
                                        <Input
                                            value={member.clinicorp_id}
                                            onChange={(e) => updateTeamMember(index, 'clinicorp_id', e.target.value)}
                                            placeholder="611370666..."
                                            className="h-9 text-xs mt-1 dark:bg-zinc-950/50 dark:border-zinc-800 dark:text-zinc-100 focus:border-purple-500 focus:ring-purple-500/20"
                                        />
                                    </div>

                                    <div className="col-span-4">
                                        <Label className="text-xs dark:text-gray-300">Foco/Área</Label>
                                        <Input
                                            value={member.focus}
                                            onChange={(e) => updateTeamMember(index, 'focus', e.target.value)}
                                            placeholder="Aparelhos fixos"
                                            className="h-9 text-xs mt-1 dark:bg-zinc-950/50 dark:border-zinc-800 dark:text-zinc-100 focus:border-purple-500 focus:ring-purple-500/20"
                                        />
                                    </div>


                                    <div className="col-span-12">
                                        <Label className="text-xs dark:text-gray-300">Especialidades</Label>
                                        <Select
                                            onValueChange={(value) => {
                                                const currentSpecs = member.specialty || [];
                                                if (!currentSpecs.includes(value)) {
                                                    updateTeamMember(index, 'specialty', [...currentSpecs, value]);
                                                }
                                            }}
                                        >
                                            <SelectTrigger className="h-9 text-xs mt-1 dark:bg-zinc-950/50 dark:border-zinc-800 dark:text-zinc-100">
                                                <SelectValue placeholder="Adicionar especialidade..." />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {SPECIALTIES.filter(spec => !member.specialty?.includes(spec)).map((spec) => (
                                                    <SelectItem key={spec} value={spec} className="text-sm">
                                                        {spec}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        {Array.isArray(member.specialty) && member.specialty.length > 0 && (
                                            <div className="flex flex-wrap gap-2 mt-2">
                                                {member.specialty.map((spec, specIndex) => (
                                                    <span
                                                        key={specIndex}
                                                        className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-purple-50 text-purple-700 dark:bg-purple-500/10 dark:text-purple-300 border border-purple-100 dark:border-purple-500/20 rounded-md text-xs font-medium transition-colors"
                                                    >
                                                        {spec}
                                                        <X
                                                            className="w-3 h-3 cursor-pointer hover:text-purple-900"
                                                            onClick={() => {
                                                                const newSpecs = member.specialty.filter((_, i) => i !== specIndex);
                                                                updateTeamMember(index, 'specialty', newSpecs);
                                                            }}
                                                        />
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                    </div>



                                    <div className="col-span-12">
                                        <Label className="text-xs dark:text-gray-300">Dias de Atendimento</Label>
                                        <div className="flex gap-2 mt-1 flex-wrap">
                                            {DAYS_OF_WEEK.map((day) => {
                                                // Normalize schedule string for display check
                                                let safeSchedule = member.schedule || '';
                                                safeSchedule = safeSchedule
                                                    .replace(/Segunda/g, 'Seg')
                                                    .replace(/Terça/g, 'Ter')
                                                    .replace(/Quarta/g, 'Qua')
                                                    .replace(/Quinta/g, 'Qui')
                                                    .replace(/Sexta/g, 'Sex')
                                                    .replace(/Sábado/g, 'Sáb')
                                                    .replace(/Domingo/g, 'Dom');
                                                const scheduleArray = safeSchedule.split(',').map((s: string) => s.trim());
                                                const isChecked = scheduleArray.includes(day.label);

                                                return (
                                                    <div key={day.id} className="flex items-center space-x-2">
                                                        <Checkbox
                                                            id={`${index}-${day.id}`}
                                                            checked={isChecked}
                                                            onCheckedChange={(checked) => {
                                                                const dayLabel = day.label;
                                                                // Filter out the current day AND any legacy long names
                                                                let currentDays = scheduleArray.filter((d: string) =>
                                                                    d !== dayLabel &&
                                                                    d !== 'Segunda' && d !== 'Terça' && d !== 'Quarta' &&
                                                                    d !== 'Quinta' && d !== 'Sexta' && d !== 'Sábado' && d !== 'Domingo'
                                                                );

                                                                if (checked) {
                                                                    currentDays.push(dayLabel);
                                                                }

                                                                // Sort days correctly: Seg -> Ter -> Qua ...
                                                                const dayOrder = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
                                                                currentDays.sort((a, b) => dayOrder.indexOf(a) - dayOrder.indexOf(b));

                                                                // Deduplicate just in case
                                                                currentDays = [...new Set(currentDays)];

                                                                updateTeamMember(index, 'schedule', currentDays.join(', '));
                                                            }}
                                                        />
                                                        <Label htmlFor={`${index}-${day.id}`} className="text-sm cursor-pointer font-normal dark:text-gray-300">
                                                            {day.label}
                                                        </Label>
                                                    </div>
                                                );
                                            })}
                                        </div>

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

// Step 3: Administrative Info
function AdminStep({ config, setConfig }: any) {
    const [loadingCep, setLoadingCep] = useState(false);

    const searchCep = async () => {
        const cep = config.admin_info.location.address.replace(/\D/g, '');
        if (cep.length !== 8) {
            alert('CEP deve ter 8 dígitos');
            return;
        }

        setLoadingCep(true);
        try {
            const response = await axios.get(`https://viacep.com.br/ws/${cep}/json/`);
            if (response.data.erro) {
                alert('CEP não encontrado');
                return;
            }

            const fullAddress = `${response.data.logradouro}, ${response.data.bairro} - ${response.data.localidade}/${response.data.uf}`;
            updateLocation('address', fullAddress);
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

    const updateSchedule = (field: string, value: string) => {
        setConfig({
            ...config,
            admin_info: {
                ...config.admin_info,
                schedule: { ...config.admin_info.schedule, [field]: value }
            }
        });
    };

    const updatePricing = (field: string, value: string) => {
        setConfig({
            ...config,
            admin_info: {
                ...config.admin_info,
                pricing: { ...config.admin_info.pricing, [field]: value }
            }
        });
    };

    const updateContact = (field: string, value: string) => {
        setConfig({
            ...config,
            admin_info: {
                ...config.admin_info,
                contact: { ...config.admin_info.contact, [field]: value }
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
        <div className="space-y-4">
            <Tabs defaultValue="location">
                <TabsList className="grid w-full grid-cols-4 dark:bg-gray-800 dark:text-gray-400">
                    <TabsTrigger value="location" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white dark:data-[state=active]:bg-purple-700">📍 Localização</TabsTrigger>
                    <TabsTrigger value="schedule" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white dark:data-[state=active]:bg-purple-700">⏰ Horários</TabsTrigger>
                    <TabsTrigger value="pricing" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white dark:data-[state=active]:bg-purple-700">💰 Valores</TabsTrigger>
                    <TabsTrigger value="contact" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white dark:data-[state=active]:bg-purple-700">📞 Contatos</TabsTrigger>
                </TabsList>

                <TabsContent value="location" className="space-y-3 mt-3">
                    <div className="grid grid-cols-4 gap-4">
                        <div className="col-span-3">
                            <Label className="dark:text-gray-300">CEP</Label>
                            <Input
                                value={config.admin_info.location.address.replace(/\D/g, '').slice(0, 8)}
                                onChange={(e) => {
                                    const cep = e.target.value.replace(/\D/g, '');
                                    updateLocation('address', cep);
                                }}
                                placeholder="00000-000"
                                maxLength={8}
                                className="dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
                            />
                        </div>
                        <div className="flex items-end">
                            <Button
                                onClick={searchCep}
                                disabled={loadingCep}
                                type="button"
                                variant="outline"
                                className="w-full bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-white dark:border-gray-600"
                            >
                                <Search className="w-4 h-4 mr-2" />
                                {loadingCep ? 'Buscando...' : 'Buscar'}
                            </Button>
                        </div>
                    </div>

                    <div>
                        <Label className="dark:text-gray-300">Endereço Completo</Label>
                        <Input
                            value={config.admin_info.location.address}
                            onChange={(e) => updateLocation('address', e.target.value)}
                            placeholder="Ex: Rua Siqueira Campos, 1068 – Centro – Santo André"
                            className="dark:bg-gray-900 dark:border-gray-700 dark:text-gray-100"
                        />
                    </div>
                    <div>
                        <Label>Ponto de Referência</Label>
                        <Input
                            value={config.admin_info.location.reference}
                            onChange={(e) => updateLocation('reference', e.target.value)}
                            placeholder="Ex: Próximo à Padaria Brasileira"
                        />
                    </div>
                    <div>
                        <Label>Estacionamento</Label>
                        <Input
                            value={config.admin_info.location.parking}
                            onChange={(e) => updateLocation('parking', e.target.value)}
                            placeholder="Ex: RB Quality Parking (Rua Santo André, 100)"
                        />
                    </div>
                </TabsContent>

                <TabsContent value="schedule" className="space-y-3 mt-3">
                    <div>
                        <Label>Segunda a Sexta</Label>
                        <Input
                            value={config.admin_info.schedule.weekdays}
                            onChange={(e) => updateSchedule('weekdays', e.target.value)}
                            placeholder="Ex: 08h às 19h"
                        />
                    </div>
                    <div>
                        <Label>Sábado</Label>
                        <Input
                            value={config.admin_info.schedule.saturday}
                            onChange={(e) => updateSchedule('saturday', e.target.value)}
                            placeholder="Ex: 09h às 16h"
                        />
                    </div>
                    <div>
                        <Label>Domingo/Feriados</Label>
                        <Input
                            value={config.admin_info.schedule.sunday}
                            onChange={(e) => updateSchedule('sunday', e.target.value)}
                            placeholder="Ex: Fechado"
                        />
                    </div>
                </TabsContent>

                <TabsContent value="pricing" className="space-y-3 mt-3">
                    <div>
                        <Label>Valor da Consulta</Label>
                        <Input
                            value={config.admin_info.pricing.consultation}
                            onChange={(e) => updatePricing('consultation', e.target.value)}
                            placeholder="Ex: R$ 250,00"
                        />
                    </div>
                    <div>
                        <Label>Observação sobre Consulta</Label>
                        <Input
                            value={config.admin_info.pricing.consultation_note}
                            onChange={(e) => updatePricing('consultation_note', e.target.value)}
                            placeholder="Ex: Se o tratamento for realizado no mesmo dia, o valor é abatido"
                        />
                    </div>
                    <div>
                        <Label>Política de Convênios</Label>
                        <Input
                            value={config.admin_info.pricing.insurance}
                            onChange={(e) => updatePricing('insurance', e.target.value)}
                            placeholder="Ex: NÃO atendemos diretamente. Emitimos NF para reembolso"
                        />
                    </div>
                    <div>
                        <Label>Formas de Pagamento</Label>
                        <Input
                            value={config.admin_info.pricing.payment_methods}
                            onChange={(e) => updatePricing('payment_methods', e.target.value)}
                            placeholder="Ex: À vista (PIX, Dinheiro, Débito) ou Parcelado (Cartão)"
                        />
                    </div>
                </TabsContent>

                <TabsContent value="contact" className="space-y-3 mt-3">
                    <div>
                        <Label>WhatsApp/Telefone</Label>
                        <Input
                            value={config.admin_info.contact.phone}
                            onChange={(e) => {
                                const formatted = formatPhone(e.target.value);
                                updateContact('phone', formatted);
                            }}
                            placeholder="Ex: (11) 98765-4321"
                            maxLength={15}
                        />
                    </div>
                    <div>
                        <Label>Website</Label>
                        <Input
                            value={config.admin_info.contact.website}
                            onChange={(e) => updateContact('website', e.target.value)}
                            placeholder="Ex: bemquererodontokids.com.br"
                        />
                    </div>
                    <div>
                        <Label>Instagram</Label>
                        <Input
                            value={config.admin_info.contact.instagram}
                            onChange={(e) => updateContact('instagram', e.target.value)}
                            placeholder="Ex: @bemquererodontokids"
                        />
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}

// Step 4: Protocols
function ProtocolsStep({ config, setConfig }: any) {
    const addStep = (type: 'emergency' | 'scheduling', step: string) => {
        if (!step.trim()) return;

        if (type === 'emergency') {
            setConfig({
                ...config,
                protocols: {
                    ...config.protocols,
                    emergency: {
                        ...config.protocols.emergency,
                        steps: [...config.protocols.emergency.steps, step]
                    }
                }
            });
        } else {
            setConfig({
                ...config,
                protocols: {
                    ...config.protocols,
                    scheduling: {
                        ...config.protocols.scheduling,
                        steps: [...config.protocols.scheduling.steps, step]
                    }
                }
            });
        }
    };

    const removeStep = (type: 'emergency' | 'scheduling', index: number) => {
        if (type === 'emergency') {
            setConfig({
                ...config,
                protocols: {
                    ...config.protocols,
                    emergency: {
                        ...config.protocols.emergency,
                        steps: config.protocols.emergency.steps.filter((_: any, i: number) => i !== index)
                    }
                }
            });
        } else {
            setConfig({
                ...config,
                protocols: {
                    ...config.protocols,
                    scheduling: {
                        ...config.protocols.scheduling,
                        steps: config.protocols.scheduling.steps.filter((_: any, i: number) => i !== index)
                    }
                }
            });
        }
    };

    const addRule = (type: 'do' | 'dont', rule: string) => {
        if (!rule.trim()) return;

        const field = type === 'do' ? 'do_rules' : 'dont_rules';
        setConfig({
            ...config,
            protocols: {
                ...config.protocols,
                [field]: [...config.protocols[field], rule]
            }
        });
    };

    const removeRule = (type: 'do' | 'dont', index: number) => {
        const field = type === 'do' ? 'do_rules' : 'dont_rules';
        setConfig({
            ...config,
            protocols: {
                ...config.protocols,
                [field]: config.protocols[field].filter((_: any, i: number) => i !== index)
            }
        });
    };

    const [newEmergencyStep, setNewEmergencyStep] = useState('');
    const [newSchedulingStep, setNewSchedulingStep] = useState('');
    const [newDoRule, setNewDoRule] = useState('');
    const [newDontRule, setNewDontRule] = useState('');

    return (
        <div className="space-y-4">
            <Tabs defaultValue="emergency">
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="emergency">🚨 Emergência</TabsTrigger>
                    <TabsTrigger value="scheduling">📅 Agendamento</TabsTrigger>
                    <TabsTrigger value="rules">✅ Regras</TabsTrigger>
                </TabsList>

                <TabsContent value="emergency" className="space-y-4 mt-4">
                    <div>
                        <Label>Gatilhos de Emergência</Label>
                        <Textarea
                            value={config.protocols.emergency.triggers}
                            onChange={(e) =>
                                setConfig({
                                    ...config,
                                    protocols: {
                                        ...config.protocols,
                                        emergency: { ...config.protocols.emergency, triggers: e.target.value }
                                    }
                                })
                            }
                            placeholder="Ex: Trauma, dor aguda, inchaço, sangramento"
                            rows={2}
                        />
                    </div>

                    <div>
                        <Label>Passos do Protocolo</Label>
                        <div className="flex gap-2 mb-2">
                            <Input
                                value={newEmergencyStep}
                                onChange={(e) => setNewEmergencyStep(e.target.value)}
                                placeholder="Ex: Acolher imediatamente"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        addStep('emergency', newEmergencyStep);
                                        setNewEmergencyStep('');
                                    }
                                }}
                            />
                            <Button
                                onClick={() => {
                                    addStep('emergency', newEmergencyStep);
                                    setNewEmergencyStep('');
                                }}
                                size="sm"
                            >
                                <Plus className="w-4 h-4" />
                            </Button>
                        </div>
                        <div className="space-y-2">
                            {config.protocols.emergency.steps.map((step: string, index: number) => (
                                <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                                    <span className="flex-1">{index + 1}. {step}</span>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => removeStep('emergency', index)}
                                        className="text-red-500"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    </div>
                </TabsContent>

                <TabsContent value="scheduling" className="space-y-4 mt-4">
                    <div>
                        <Label>Passos do Agendamento</Label>
                        <div className="flex gap-2 mb-2">
                            <Input
                                value={newSchedulingStep}
                                onChange={(e) => setNewSchedulingStep(e.target.value)}
                                placeholder="Ex: Coletar nome e idade da criança"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        addStep('scheduling', newSchedulingStep);
                                        setNewSchedulingStep('');
                                    }
                                }}
                            />
                            <Button
                                onClick={() => {
                                    addStep('scheduling', newSchedulingStep);
                                    setNewSchedulingStep('');
                                }}
                                size="sm"
                            >
                                <Plus className="w-4 h-4" />
                            </Button>
                        </div>
                        <div className="space-y-2">
                            {config.protocols.scheduling.steps.map((step: string, index: number) => (
                                <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded">
                                    <span className="flex-1">{index + 1}. {step}</span>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => removeStep('scheduling', index)}
                                        className="text-red-500"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    </div>
                </TabsContent>

                <TabsContent value="rules" className="space-y-4 mt-4">
                    <div>
                        <Label className="text-green-600">✅ O que FAZER</Label>
                        <div className="flex gap-2 mb-2">
                            <Input
                                value={newDoRule}
                                onChange={(e) => setNewDoRule(e.target.value)}
                                placeholder="Ex: Sempre coletar telefone para contato"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        addRule('do', newDoRule);
                                        setNewDoRule('');
                                    }
                                }}
                            />
                            <Button
                                onClick={() => {
                                    addRule('do', newDoRule);
                                    setNewDoRule('');
                                }}
                                size="sm"
                            >
                                <Plus className="w-4 h-4" />
                            </Button>
                        </div>
                        <div className="space-y-2">
                            {config.protocols.do_rules.map((rule: string, index: number) => (
                                <div key={index} className="flex items-center gap-2 p-2 bg-green-50 rounded">
                                    <span className="flex-1">✅ {rule}</span>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => removeRule('do', index)}
                                        className="text-red-500"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div>
                        <Label className="text-red-600">❌ O que NÃO FAZER</Label>
                        <div className="flex gap-2 mb-2">
                            <Input
                                value={newDontRule}
                                onChange={(e) => setNewDontRule(e.target.value)}
                                placeholder="Ex: NUNCA inventar horários ou nomes"
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                        addRule('dont', newDontRule);
                                        setNewDontRule('');
                                    }
                                }}
                            />
                            <Button
                                onClick={() => {
                                    addRule('dont', newDontRule);
                                    setNewDontRule('');
                                }}
                                size="sm"
                            >
                                <Plus className="w-4 h-4" />
                            </Button>
                        </div>
                        <div className="space-y-2">
                            {config.protocols.dont_rules.map((rule: string, index: number) => (
                                <div key={index} className="flex items-center gap-2 p-2 bg-red-50 rounded">
                                    <span className="flex-1">❌ {rule}</span>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => removeRule('dont', index)}
                                        className="text-red-500"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}

// Step 5: Preview
function PreviewStep({ config, preview, showPreview, loadPreview, loading }: any) {
    return (
        <div className="space-y-4">
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
                <div className="mt-6">
                    <Card>
                        <CardContent className="pt-6">
                            <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded max-h-96 overflow-y-auto">
                                {preview}
                            </pre>
                        </CardContent>
                    </Card>
                </div>
            )}

            {!showPreview && (
                <div className="text-center py-12 text-gray-400">
                    Clique em "Gerar Preview" para visualizar o prompt completo
                </div>
            )}
        </div>
    );
}
