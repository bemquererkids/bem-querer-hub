export type CRMStatus = 'new' | 'qualifying' | 'scheduled' | 'noshow' | 'won' | 'attended' | 'lost';

export interface Deal {
    id: string;
    patientName: string;
    patientAvatar?: string;
    phone?: string;
    value?: number;
    status: CRMStatus;
    lastContact: string;
    source: 'instagram' | 'google' | 'facebook' | 'indication';
    campaignId?: string; // ID da campanha de origem
    treatmentType?: string; // ex: "Ortodontia", "Limpeza"
    probability: 'low' | 'medium' | 'high';
}
