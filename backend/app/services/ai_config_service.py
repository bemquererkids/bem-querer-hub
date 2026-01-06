"""
AI Configuration Service
Manages dynamic AI assistant configuration for multi-tenant clinics
"""
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

class AIConfigService:
    """
    Service to generate dynamic AI prompts based on clinic configuration
    Replaces hardcoded prompts with database-driven configuration
    """
    
    @staticmethod
    def generate_system_prompt(config: Dict[str, Any]) -> str:
        """
        Generate complete system prompt from configuration
        
        Args:
            config: Dictionary with clinic AI configuration
            
        Returns:
            Complete system prompt string
        """
        
        # Extract configuration sections
        persona = config.get('persona', {})
        team = config.get('team', [])
        admin_info = config.get('admin_info', {})
        protocols = config.get('protocols', {})
        
        # Build prompt dynamically
        prompt = f"""
# {persona.get('name', 'ASSISTENTE VIRTUAL')} - {persona.get('clinic_name', 'CLÍNICA')}

Você é {persona.get('name', 'a assistente virtual')}, {persona.get('role', 'secretária virtual')} da {persona.get('clinic_name', 'clínica')}.

## 🎯 SUA PERSONA
- **Tom:** {persona.get('tone', 'Profissional e acolhedor')}
- **Público-Alvo:** {persona.get('target_audience', 'Pacientes em geral')}
- **Objetivo:** {persona.get('objective', 'Ajudar com agendamentos e tirar dúvidas')}

---

## 👥 EQUIPE MÉDICA

{AIConfigService._generate_team_section(team)}

---

## 📋 INFORMAÇÕES ADMINISTRATIVAS

{AIConfigService._generate_admin_section(admin_info)}

---

## 🔧 PROTOCOLOS DE ATENDIMENTO

{AIConfigService._generate_protocols_section(protocols)}

---

## 🛡️ REGRAS CRÍTICAS

### ✅ FAZER:
{AIConfigService._generate_rules_list(protocols.get('do_rules', []))}

### ❌ NÃO FAZER:
{AIConfigService._generate_rules_list(protocols.get('dont_rules', []))}

---

## 💬 TOM DE VOZ
{persona.get('voice_examples', 'Seja empático, acolhedor e eficiente.')}

---

**Data Atual:** {{current_date}}
"""
        
        return prompt
    
    @staticmethod
    def _generate_team_section(team: List[Dict]) -> str:
        """Generate team section from configuration"""
        if not team:
            return "Equipe não configurada."
        
        sections = {}
        
        # Group by specialty
        for member in team:
            specialty = member.get('specialty', 'Geral')
            if specialty not in sections:
                sections[specialty] = []
            sections[specialty].append(member)
        
        output = []
        for specialty, members in sections.items():
            output.append(f"### {specialty}")
            for member in members:
                output.append(f"{member.get('position', '')}. **{member.get('name', 'Profissional')}**")
                if member.get('clinicorp_id'):
                    output.append(f"   - ID Clinicorp: {member['clinicorp_id']}")
                if member.get('focus'):
                    output.append(f"   - Foco: {member['focus']}")
                if member.get('schedule'):
                    output.append(f"   - Atende: {member['schedule']}")
                output.append("")
        
        return "\n".join(output)
    
    @staticmethod
    def _generate_admin_section(admin: Dict) -> str:
        """Generate administrative info section"""
        sections = []
        
        # Location
        if admin.get('location'):
            loc = admin['location']
            sections.append("### 📍 Localização")
            sections.append(f"- **Endereço:** {loc.get('address', '')}")
            if loc.get('reference'):
                sections.append(f"- **Referência:** {loc.get('reference')}")
            if loc.get('parking'):
                sections.append(f"- **Estacionamento:** {loc.get('parking')}")
            sections.append("")
        
        # Schedule
        if admin.get('schedule'):
            sch = admin['schedule']
            sections.append("### ⏰ Horários")
            sections.append(f"- **Segunda a Sexta:** {sch.get('weekdays', '')}")
            sections.append(f"- **Sábado:** {sch.get('saturday', 'Fechado')}")
            sections.append(f"- **Domingo/Feriados:** {sch.get('sunday', 'Fechado')}")
            sections.append("")
        
        # Pricing
        if admin.get('pricing'):
            price = admin['pricing']
            sections.append("### 💰 Valores e Pagamento")
            sections.append(f"- **Consulta:** {price.get('consultation', 'Consultar')}")
            if price.get('consultation_note'):
                sections.append(f"  - *{price['consultation_note']}*")
            if price.get('insurance'):
                sections.append(f"- **Convênios:** {price['insurance']}")
            if price.get('payment_methods'):
                sections.append(f"- **Formas de Pagamento:** {price['payment_methods']}")
            sections.append("")
        
        # Contact
        if admin.get('contact'):
            cont = admin['contact']
            sections.append("### 📞 Contatos")
            if cont.get('phone'):
                sections.append(f"- **WhatsApp:** {cont['phone']}")
            if cont.get('website'):
                sections.append(f"- **Site:** {cont['website']}")
            if cont.get('instagram'):
                sections.append(f"- **Instagram:** {cont['instagram']}")
            sections.append("")
        
        return "\n".join(sections)
    
    @staticmethod
    def _generate_protocols_section(protocols: Dict) -> str:
        """Generate protocols section"""
        sections = []
        
        # Emergency
        if protocols.get('emergency'):
            emerg = protocols['emergency']
            sections.append("### 🚨 EMERGÊNCIA")
            sections.append(f"**Gatilhos:** {emerg.get('triggers', '')}")
            sections.append("")
            sections.append("**Ação:**")
            for step in emerg.get('steps', []):
                sections.append(f"- {step}")
            sections.append("")
        
        # Scheduling
        if protocols.get('scheduling'):
            sched = protocols['scheduling']
            sections.append("### 📅 AGENDAMENTO")
            for step in sched.get('steps', []):
                sections.append(f"- {step}")
            sections.append("")
        
        return "\n".join(sections)
    
    @staticmethod
    def _generate_rules_list(rules: List[str]) -> str:
        """Generate rules list"""
        if not rules:
            return "- Nenhuma regra configurada"
        return "\n".join([f"- {rule}" for rule in rules])


# Example configuration structure
EXAMPLE_CONFIG = {
    "persona": {
        "name": "Carol",
        "clinic_name": "Bem-Querer Odontokids",
        "role": "secretária virtual",
        "tone": "Empática, acolhedora e eficiente",
        "target_audience": "Mães preocupadas e pacientes ocupados",
        "objective": "Conduzir conversas naturalmente e direcionar para agendamento",
        "voice_examples": "Use 'pequeno(a)', 'mamãe', 'papai' quando apropriado. Seja empática e objetiva."
    },
    "team": [
        {
            "position": "1",
            "name": "Dra. Fernanda Battistini",
            "clinicorp_id": "6113706666688512",
            "specialty": "🦷 ORTODONTIA",
            "focus": "Ortodontia Fixa (aparelhos metálicos, estéticos)",
            "schedule": "Segunda, Quarta, Sexta e Sábado"
        },
        {
            "position": "2",
            "name": "Dra. Vanessa Battistini",
            "clinicorp_id": "5070281037119488",
            "specialty": "🦷 ORTODONTIA",
            "focus": "Invisalign (alinhadores transparentes), PNE/TEA",
            "schedule": "Segunda a Sábado"
        }
    ],
    "admin_info": {
        "location": {
            "address": "Rua Siqueira Campos, 1068 – Centro – Santo André",
            "reference": "Próximo à Padaria Brasileira",
            "parking": "RB Quality Parking (Rua Santo André, 100)"
        },
        "schedule": {
            "weekdays": "08h às 19h",
            "saturday": "09h às 16h",
            "sunday": "Fechado"
        },
        "pricing": {
            "consultation": "R$ 250,00",
            "consultation_note": "Se o tratamento for realizado no mesmo dia, o valor é abatido",
            "insurance": "NÃO atendemos diretamente. Emitimos NF para reembolso",
            "payment_methods": "À vista (PIX, Dinheiro, Débito) ou Parcelado (Cartão)"
        },
        "contact": {
            "phone": "(11) 4436-1721",
            "website": "bemquererodontokids.com.br",
            "instagram": "@bemquererodontokids"
        }
    },
    "protocols": {
        "emergency": {
            "triggers": "Trauma, dor aguda, inchaço, sangramento",
            "steps": [
                "Acolhimento imediato",
                "Coletar: Nome, idade, telefone",
                "Orientação básica (sem medicar)",
                "Informar que equipe vai ligar"
            ]
        },
        "scheduling": {
            "steps": [
                "Coletar nome e idade da criança",
                "Identificar tipo de consulta",
                "Perguntar período preferido",
                "Oferecer APENAS 2 opções de horário",
                "Confirmar dados e agendar"
            ]
        },
        "do_rules": [
            "Sempre coletar telefone para contato",
            "Ser transparente sobre valores",
            "Usar emojis moderados",
            "Finalizar oferecendo agendamento"
        ],
        "dont_rules": [
            "NUNCA inventar horários ou nomes",
            "NUNCA medique",
            "NUNCA minimize emergências",
            "NUNCA agende sem confirmação"
        ]
    }
}
