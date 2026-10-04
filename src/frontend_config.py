# -*- coding: utf-8 -*-
"""
TIA - Frontend Configuration
Configurações de tema, cores e constantes
"""

# =====================================================================
# CORES DO SISTEMA
# =====================================================================

COLORS = {
    # Níveis de risco
    'BAIXO': '#28a745',          # Verde
    'MEDIO': '#ffc107',          # Amarelo
    'ALTO': '#dc3545',           # Vermelho

    # Cores primárias
    'primary': '#0066cc',        # Azul principal
    'secondary': '#6c757d',      # Cinza
    'success': '#28a745',        # Verde
    'warning': '#ffc107',        # Amarelo
    'danger': '#dc3545',         # Vermelho
    'info': '#17a2b8',           # Ciano

    # Cores de fundo
    'background': '#f8f9fa',     # Cinza claro
    'surface': '#ffffff',        # Branco
    'border': '#dee2e6',         # Cinza claro
}

# =====================================================================
# CONFIGURAÇÕES DE API
# =====================================================================

API_CONFIG = {
    'BASE_URL': 'http://localhost:5000',
    'API_VERSION': 'v1',
    'TIMEOUT': 30,  # segundos
    'ENDPOINTS': {
        'SAUDE': '/saude',
        'INFO': '/info',
        'CLASSIFICAR': '/classificar',
        'GET_CLASSIFICACAO': '/classificacao/{id}',
        'LISTAR_CLASSIFICACOES': '/classificacoes',
        'ESTATISTICAS': '/estatisticas',
    }
}

# =====================================================================
# VALIDAÇÃO DE ENTRADA
# =====================================================================

VALIDATION = {
    'IDADE_MIN': 60,
    'IDADE_MAX': 120,
    'INTERNACOES_MIN': 0,
    'INTERNACOES_MAX': 50,
    'DIAGNOSTICO_MIN_LENGTH': 2,
    'DIAGNOSTICO_MAX_LENGTH': 50,
}

# =====================================================================
# CONFIGURAÇÕES DE STREAMLIT
# =====================================================================

STREAMLIT_CONFIG = {
    'PAGE_TITLE': '🏥 TIA - Readmissão Hospitalar',
    'PAGE_ICON': '🏥',
    'LAYOUT': 'wide',
    'INITIAL_SIDEBAR': 'expanded',
    'THEME': 'light',
}

# =====================================================================
# MENSAGENS
# =====================================================================

MESSAGES = {
    'API_ONLINE': '✅ API Online',
    'API_OFFLINE': '❌ API Offline',
    'VALIDATION_ERROR': '❌ Erros na validação:',
    'VALIDATION_SUCCESS': '✅ Dados validados com sucesso!',
    'EVALUATION_ERROR': '❌ Corrija os erros antes de avaliar',
    'EVALUATION_LOADING': '🔄 Avaliando risco...',
    'EVALUATION_ERROR_MSG': '❌ Erro: ',
    'NO_ANALYSES': '📊 Nenhuma análise realizada ainda. Vá para "Avaliação" para começar.',
    'CONNECTION_SUCCESS': '✅ Conexão bem-sucedida!',
    'CONNECTION_ERROR': '❌ Erro: ',
    'TEST_CONNECTION': '🧪 Testar Conexão',
}

# =====================================================================
# RÓTULOS DE NAVEGAÇÃO
# =====================================================================

PAGES = {
    'EVALUATION': '🎯 Avaliação',
    'DASHBOARD': '📊 Dashboard',
    'ABOUT': '📚 Sobre',
    'SETTINGS': '⚙️ Configurações',
}

# =====================================================================
# MÉTRICAS DE RISCO
# =====================================================================

RISK_LEVELS = {
    'BAIXO': {
        'label': 'BAIXO',
        'color': COLORS['BAIXO'],
        'description': 'Risco baixo de readmissão',
        'recommendations': ['Acompanhamento de rotina', 'Monitoramento periódico']
    },
    'MEDIO': {
        'label': 'MÉDIO',
        'color': COLORS['MEDIO'],
        'description': 'Risco médio de readmissão',
        'recommendations': ['Acompanhamento intensivo', 'Monitoramento semanal']
    },
    'ALTO': {
        'label': 'ALTO',
        'color': COLORS['ALTO'],
        'description': 'Risco alto de readmissão',
        'recommendations': ['Acompanhamento clínico intensivo', 'Monitoramento diário', 'Intervenção preventiva']
    }
}

# =====================================================================
# CSS CUSTOMIZADO
# =====================================================================

CUSTOM_CSS = """
<style>
    .header-title {
        color: #0066cc;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        color: #666;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }
    .risco-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
        color: white;
    }
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.9rem;
    }
</style>
"""

# =====================================================================
# EXEMPLOS DE DADOS
# =====================================================================

EXAMPLE_PATIENT = {
    'paciente_id': 'PAC_001',
    'idade': 75,
    'diagnostico_principal': 'I50.0',
    'internacoes_anteriores_12_meses': 2,
}

# =====================================================================
# FUNÇÕES AUXILIARES
# =====================================================================

def get_risk_color(risk_level):
    """Retorna cor do risco"""
    return COLORS.get(risk_level, COLORS['secondary'])

def get_risk_label(risk_level):
    """Retorna rótulo do risco"""
    if risk_level in RISK_LEVELS:
        return RISK_LEVELS[risk_level]['label']
    return 'DESCONHECIDO'

def get_risk_description(risk_level):
    """Retorna descrição do risco"""
    if risk_level in RISK_LEVELS:
        return RISK_LEVELS[risk_level]['description']
    return 'Nível de risco desconhecido'

def get_risk_recommendations(risk_level):
    """Retorna recomendações baseadas no risco"""
    if risk_level in RISK_LEVELS:
        return RISK_LEVELS[risk_level]['recommendations']
    return []
