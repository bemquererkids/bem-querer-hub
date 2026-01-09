"""
Embedded Knowledge Base - Fallback

Esta é uma versão simplificada da base de conhecimento embutida no código,
para garantir que funcione mesmo se a pasta knowledge_base/ não for incluída no deploy.
"""

EMBEDDED_KNOWLEDGE = {
    "especialidades_valores": """
# Especialidades e Valores - Bem Querer Kids

## Consultas Médicas

### Pediatria Geral
- Valor: R$ 250,00
- Duração: 30-40 minutos
- Profissionais: Dr. João Silva, Dra. Maria Santos
- Convênios: Unimed, Bradesco Saúde, SulAmérica, Amil

### Neuropediatria
- Valor: R$ 350,00
- Duração: 45-60 minutos
- Descrição: Avaliação neurológica, TDAH, autismo, epilepsia
- Profissionais: Dra. Ana Paula Oliveira
- Convênios: Unimed, Bradesco Saúde, SulAmérica

### Cardiologia Pediátrica
- Valor: R$ 380,00
- Duração: 45 minutos
- Profissionais: Dr. Carlos Mendes
- Convênios: Unimed, Bradesco Saúde

## Terapias

### Fonoaudiologia
- Valor: R$ 180,00 (sessão individual)
- Duração: 45 minutos
- Profissionais: Fga. Juliana Costa, Fga. Patrícia Lima
- Pacotes: 4 sessões R$ 680 (5% desconto), 8 sessões R$ 1.296 (10% desconto)

### Psicologia Infantil
- Valor: R$ 200,00 (sessão individual)
- Duração: 50 minutos
- Profissionais: Psic. Fernanda Alves, Psic. Roberto Souza

### Terapia Ocupacional
- Valor: R$ 190,00
- Duração: 45 minutos
- Profissionais: TO. Mariana Ribeiro

### Fisioterapia Pediátrica
- Valor: R$ 170,00
- Duração: 45 minutos
- Profissionais: Ft. Lucas Martins

## Formas de Pagamento
- Dinheiro: 5% desconto à vista
- PIX: 3% desconto à vista
- Cartão de Débito: À vista
- Cartão de Crédito: Até 3x sem juros
- Convênios: Conforme tabela
""",
    
    "preparos_exames": """
# Preparos para Exames

## Ultrassom Abdominal
- Jejum: 6 horas (crianças acima de 5 anos)
- Jejum: 4 horas (crianças de 2 a 5 anos)
- Jejum: 3 horas (bebês até 2 anos)
- Não urinar 2 horas antes
- Beber 4 copos de água 1 hora antes

## Exame de Sangue
- Jejum: 8-12 horas (crianças acima de 5 anos)
- Jejum: 6-8 horas (crianças de 2 a 5 anos)
- Jejum: 3-4 horas (bebês até 2 anos)
- Pode beber água à vontade
""",
    
    "politicas": """
# Políticas da Clínica

## Horário de Atendimento
- Segunda a Sexta: 7h às 19h
- Sábado: 8h às 12h
- Domingo e Feriados: Fechado

## Cancelamento
- Mais de 24 horas: Sem custo
- Entre 12h e 24h: Cobrança de 50%
- Menos de 12 horas: Cobrança de 100%

## Convênios Aceitos
- Unimed
- Bradesco Saúde
- SulAmérica
- Amil
- Porto Seguro
""",
    
    "faq": """
# Perguntas Frequentes

## Como agendar?
- WhatsApp: (48) 99999-9999
- Telefone: (48) 3333-3333
- Site: www.bemquerer.com.br

## Quais convênios aceitam?
Unimed, Bradesco Saúde, SulAmérica, Amil, Porto Seguro

## Qual o horário de funcionamento?
Segunda a Sexta: 7h às 19h
Sábado: 8h às 12h

## Como cancelar consulta?
Cancele com 24h de antecedência sem custo.
WhatsApp, telefone ou site.
"""
}


def search_embedded_knowledge(query: str) -> str:
    """
    Busca na base de conhecimento embutida
    
    Args:
        query: Texto da pergunta
        
    Returns:
        Contexto relevante encontrado
    """
    query_lower = query.lower()
    context_parts = []
    
    # Palavras-chave para cada categoria
    keywords = {
        "especialidades_valores": [
            "quanto", "custa", "valor", "preço", "pediatria", "neuropediatria",
            "cardiologia", "fonoaudiologia", "psicologia", "terapia", "fisioterapia",
            "especialidade", "profissional", "médico", "doutor", "doutora"
        ],
        "preparos_exames": [
            "jejum", "preparo", "exame", "ultrassom", "sangue", "urina",
            "preparar", "fazer", "preciso"
        ],
        "politicas": [
            "horário", "funciona", "abre", "fecha", "cancelar", "cancelamento",
            "convênio", "aceita", "atende"
        ],
        "faq": [
            "como", "agendar", "marcar", "telefone", "whatsapp", "contato"
        ]
    }
    
    # Encontrar categorias relevantes
    relevant_categories = []
    for category, words in keywords.items():
        if any(word in query_lower for word in words):
            relevant_categories.append(category)
    
    # Se não encontrou nada específico, usar todas
    if not relevant_categories:
        relevant_categories = list(EMBEDDED_KNOWLEDGE.keys())
    
    # Montar contexto
    context_parts.append("=== INFORMAÇÕES DA BEM QUERER KIDS ===\n")
    
    for category in relevant_categories[:2]:  # Máximo 2 categorias
        content = EMBEDDED_KNOWLEDGE.get(category, "")
        if content:
            context_parts.append(content)
            context_parts.append("\n---\n")
    
    return '\n'.join(context_parts)
