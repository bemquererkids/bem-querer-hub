import { Deal } from "../types/crm";

export const MOCK_DEALS: Deal[] = [
    {
        id: 'd1',
        patientName: 'Pedro Silva',
        status: 'new',
        lastContact: '10 min atrás',
        source: 'instagram',
        probability: 'medium'
    },
    {
        id: 'd2',
        patientName: 'Julia Costa',
        status: 'qualifying',
        lastContact: 'Ontem',
        source: 'google',
        treatmentType: 'Invisalign',
        value: 12000,
        probability: 'high'
    },
    {
        id: 'd3',
        patientName: 'Marcos Santos',
        status: 'scheduled',
        lastContact: '2 dias atrás',
        source: 'indication',
        treatmentType: 'Canal',
        value: 800,
        probability: 'high'
    },
    {
        id: 'd4',
        patientName: 'Ana Clara',
        status: 'noshow',
        lastContact: '5 dias atrás',
        source: 'google',
        probability: 'low'
    },
    {
        id: 'd5',
        patientName: 'Lucas Ferreira',
        status: 'won',
        lastContact: '1 semana atrás',
        source: 'instagram',
        treatmentType: 'Odontopediatria Geral',
        value: 500,
        probability: 'high'
    }
];
