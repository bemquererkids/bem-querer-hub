export type CRMStatus = 'new' | 'qualifying' | 'scheduled' | 'noshow' | 'won' | 'attended';

export interface Deal {
    id: string;
    patientName: string;
    patientAvatar?: string;
    phone?: string;
    value?: number;
    status: CRMStatus;
    lastContact: string;
    source: 'instagram' | 'google' | 'indication';
    treatmentType?: string; // ex: "Ortodontia", "Limpeza"
    probability: 'low' | 'medium' | 'high';
}
