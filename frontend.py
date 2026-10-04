# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 3
Frontend - Interface Streamlit
Sistema de Prognóstico de Readmissão Hospitalar
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# =====================================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================================

st.set_page_config(
    page_title="TIA - Readmissão Hospitalar",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# CONFIGURAÇÃO DE TEMA
# =====================================================================

COLORS = {
    'BAIXO': '#28a745',      # Verde
    'MEDIO': '#ffc107',      # Amarelo
    'ALTO': '#dc3545',       # Vermelho
    'primary': '#0066cc',
    'secondary': '#6c757d',
    'background': '#f8f9fa'
}

# =====================================================================
# FUNÇÕES AUXILIARES
# =====================================================================

def conectar_api(endpoint, metodo='GET', dados=None):
    """Conectar com a API REST"""
    try:
        url = f'http://localhost:5000/api/v1{endpoint}'

        if metodo == 'POST':
            response = requests.post(url, json=dados)
        else:
            response = requests.get(url)

        if response.status_code == 200:
            return response.json()['dados'], None
        else:
            return None, f"Erro {response.status_code}: {response.text}"

    except Exception as e:
        return None, f"Erro de conexão: {str(e)}"

def validar_entrada(idade, diagnostico, internacoes):
    """Validar dados de entrada"""
    erros = []

    if idade < 60:
        erros.append("Idade deve ser >= 60 anos")
    if idade > 120:
        erros.append("Idade parece inválida (> 120)")
    if not diagnostico or len(diagnostico) == 0:
        erros.append("Diagnóstico é obrigatório")
    if internacoes < 0:
        erros.append("Internações não pode ser negativo")

    return erros

def get_cor_risco(risco):
    """Retornar cor baseada no nível de risco"""
    return COLORS.get(risco, '#6c757d')

# =====================================================================
# HEADER
# =====================================================================

st.markdown("""
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
</style>

<div class="header-title">🏥 Sistema de Prognóstico de Readmissão</div>
<div class="header-subtitle">Avaliação de Risco para Pacientes 60+</div>
""", unsafe_allow_html=True)

# =====================================================================
# SIDEBAR - NAVEGAÇÃO
# =====================================================================

st.sidebar.markdown("## 📋 Menu")

pagina = st.sidebar.radio(
    "Selecione a página:",
    ["🎯 Avaliação", "📊 Dashboard", "📚 Sobre", "⚙️ Configurações"]
)

# Health check da API
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔧 Status da API")

    saude, erro = conectar_api('/saude')
    if saude and saude.get('status') == 'ok':
        st.success("✅ API Online")
    else:
        st.error("❌ API Offline")

# =====================================================================
# PÁGINA 1: AVALIAÇÃO
# =====================================================================

if pagina == "🎯 Avaliação":
    st.markdown("## Avaliar Risco de Readmissão")

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown("### 📋 Dados do Paciente")

        # Inputs
        paciente_id = st.text_input(
            "ID do Paciente:",
            value="PAC_001",
            help="Identificador único do paciente"
        )

        idade = st.number_input(
            "Idade:",
            min_value=18,
            max_value=120,
            value=75,
            help="Idade do paciente em anos"
        )

        diagnostico = st.text_input(
            "Diagnóstico (CID-10):",
            value="I50.0",
            help="Código CID-10 do diagnóstico principal"
        )

        internacoes = st.number_input(
            "Internações nos últimos 12 meses:",
            min_value=0,
            max_value=50,
            value=2,
            help="Número de internações anteriores"
        )

        # Botão de validação
        validar_btn = st.button(
            "✓ Validar Entrada",
            use_container_width=True,
            key="btn_validar"
        )

        # Botão de avaliação
        avaliar_btn = st.button(
            "🚀 Avaliar Risco",
            use_container_width=True,
            key="btn_avaliar",
            type="primary"
        )

    with col2:
        st.markdown("### 📊 Resultado")

        # Validação
        if validar_btn:
            erros = validar_entrada(idade, diagnostico, internacoes)

            if erros:
                st.error("❌ Erros na validação:")
                for erro in erros:
                    st.write(f"  • {erro}")
            else:
                st.success("✅ Dados validados com sucesso!")

        # Avaliação
        if avaliar_btn:
            erros = validar_entrada(idade, diagnostico, internacoes)

            if erros:
                st.error("❌ Corrija os erros antes de avaliar")
            else:
                with st.spinner("🔄 Avaliando risco..."):
                    resultado, erro = conectar_api(
                        '/classificar',
                        metodo='POST',
                        dados={
                            'paciente_id': paciente_id,
                            'idade': idade,
                            'diagnostico_principal': diagnostico,
                            'internacoes_anteriores_12_meses': internacoes
                        }
                    )

                    if erro:
                        st.error(f"❌ Erro: {erro}")
                    else:
                        # Exibir resultados
                        risco = resultado.get('risco_readmissao', 'DESCONHECIDO')
                        probabilidade = resultado.get('probabilidade_estimada', 0)

                        # Métrica principal
                        col_risco, col_prob = st.columns(2)

                        with col_risco:
                            cor = get_cor_risco(risco)
                            st.markdown(f"""
                            <div class="metric-card">
                                <p style="color: #666; margin: 0;">Nível de Risco</p>
                                <h2 style="margin: 0.5rem 0; color: {cor};">{risco}</h2>
                            </div>
                            """, unsafe_allow_html=True)

                        with col_prob:
                            st.markdown(f"""
                            <div class="metric-card">
                                <p style="color: #666; margin: 0;">Probabilidade</p>
                                <h2 style="margin: 0.5rem 0; color: #0066cc;">{probabilidade*100:.1f}%</h2>
                            </div>
                            """, unsafe_allow_html=True)

                        # Gauge chart
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=probabilidade * 100,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Probabilidade de Readmissão (%)"},
                            delta={'reference': 50, 'suffix': " vs. baseline"},
                            gauge={
                                'axis': {'range': [0, 100]},
                                'bar': {'color': cor},
                                'steps': [
                                    {'range': [0, 33], 'color': "#dfe6e9"},
                                    {'range': [33, 67], 'color': "#fff5e1"},
                                    {'range': [67, 100], 'color': "#fadbd8"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))

                        fig.update_layout(
                            height=300,
                            margin=dict(l=20, r=20, t=70, b=20)
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        # Fatores relevantes
                        st.markdown("### 📌 Fatores Relevantes")

                        fatores = resultado.get('fatores_relevantes', [])
                        if fatores:
                            for fator in fatores:
                                st.info(f"• {fator}")
                        else:
                            st.write("Nenhum fator específico identificado")

                        # Salvar no histórico (sessão)
                        if 'historico' not in st.session_state:
                            st.session_state.historico = []

                        st.session_state.historico.append({
                            'timestamp': datetime.now(),
                            'paciente_id': paciente_id,
                            'idade': idade,
                            'diagnostico': diagnostico,
                            'risco': risco,
                            'probabilidade': probabilidade
                        })

# =====================================================================
# PÁGINA 2: DASHBOARD
# =====================================================================

elif pagina == "📊 Dashboard":
    st.markdown("## Dashboard de Análises")

    if 'historico' not in st.session_state or len(st.session_state.historico) == 0:
        st.info("📊 Nenhuma análise realizada ainda. Vá para 'Avaliação' para começar.")
    else:
        # Converter histórico em DataFrame
        df = pd.DataFrame(st.session_state.historico)

        # Estatísticas gerais
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Análises", len(df))

        with col2:
            riscos_altos = len(df[df['risco'] == 'ALTO'])
            st.metric("Riscos Altos", riscos_altos)

        with col3:
            prob_media = df['probabilidade'].mean() * 100
            st.metric("Probabilidade Média", f"{prob_media:.1f}%")

        # Gráfico de distribuição de risco
        st.markdown("### 📈 Distribuição de Risco")

        risco_dist = df['risco'].value_counts()
        fig = go.Figure(data=[
            go.Bar(
                x=risco_dist.index,
                y=risco_dist.values,
                marker_color=[get_cor_risco(r) for r in risco_dist.index]
            )
        ])

        fig.update_layout(
            title="Contagem de Pacientes por Nível de Risco",
            xaxis_title="Nível de Risco",
            yaxis_title="Quantidade",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabela de histórico
        st.markdown("### 📋 Histórico de Análises")

        df_display = df.copy()
        df_display['timestamp'] = df_display['timestamp'].dt.strftime('%d/%m/%Y %H:%M:%S')
        df_display['probabilidade'] = (df_display['probabilidade'] * 100).round(1).astype(str) + '%'
        df_display = df_display[['timestamp', 'paciente_id', 'idade', 'diagnostico', 'risco', 'probabilidade']]
        df_display.columns = ['Data/Hora', 'ID Paciente', 'Idade', 'Diagnóstico', 'Risco', 'Probabilidade']

        st.dataframe(df_display, use_container_width=True)

# =====================================================================
# PÁGINA 3: SOBRE
# =====================================================================

elif pagina == "📚 Sobre":
    st.markdown("""
    ## Sobre o Sistema

    ### 🏥 O que é?
    Sistema de Prognóstico de Readmissão Hospitalar é uma ferramenta de IA
    que avalia o risco de readmissão para pacientes com idade 60+.

    ### 🎯 Objetivo
    Identificar pacientes com alto risco de readmissão para implementar
    estratégias de prevenção e melhorar resultados clínicos.

    ### 🤖 Tecnologia
    - **Backend**: Python Flask
    - **IA**: Google Gemini API
    - **Banco de Dados**: MySQL
    - **Frontend**: Streamlit
    - **Segurança**: JWT Authentication

    ### 📊 Fases de Desenvolvimento

    **Fase 1** ✅ Discovery & Requisitos
    **Fase 2** ✅ Baseline & Arquitetura
    **Fase 3** 🔄 Aprimoramento & Interface (atual)
    **Fase 4** ⏳ Validação & Pitch

    ### 👥 Equipe
    Projeto Integrador - Aplicações Práticas de IA em Saúde

    ### 📞 Contato
    Para dúvidas ou sugestões, entre em contato com a equipe de projeto.
    """)

# =====================================================================
# PÁGINA 4: CONFIGURAÇÕES
# =====================================================================

elif pagina == "⚙️ Configurações":
    st.markdown("## Configurações")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔌 Configuração de API")

        api_url = st.text_input(
            "URL da API:",
            value="http://localhost:5000",
            help="Endereço base da API REST"
        )

        if st.button("🧪 Testar Conexão"):
            saude, erro = conectar_api('/saude')
            if saude:
                st.success("✅ Conexão bem-sucedida!")
            else:
                st.error(f"❌ Erro: {erro}")

    with col2:
        st.markdown("### 🎨 Tema")

        tema = st.selectbox(
            "Selecione o tema:",
            ["Automático", "Claro", "Escuro"]
        )

        st.info(f"Tema selecionado: {tema}")

# =====================================================================
# FOOTER
# =====================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.9rem;">
    <p>TIA - Projeto Integrador IA | Fase 3 - Frontend</p>
    <p>© 2026 - Aplicações Práticas de IA em Saúde</p>
</div>
""", unsafe_allow_html=True)
