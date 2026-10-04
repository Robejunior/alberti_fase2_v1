# -*- coding: utf-8 -*-
"""
TIA - Frontend Streamlit Simplificado (Fase 3)
Sem gráficos Plotly - Apenas interface de teste
"""

import streamlit as st
import requests
from datetime import datetime

# Configuração de página
st.set_page_config(
    page_title="🏥 TIA - Readmissão Hospitalar",
    page_icon="🏥",
    layout="wide"
)

# =====================================================================
# FUNÇÕES
# =====================================================================

def conectar_api(endpoint, metodo='GET', dados=None):
    """Conectar com a API REST"""
    try:
        url = f'http://localhost:5000/api/v1{endpoint}'

        if metodo == 'POST':
            response = requests.post(url, json=dados, timeout=5)
        else:
            response = requests.get(url, timeout=5)

        if response.status_code == 200:
            return response.json().get('dados'), None
        else:
            return None, f"Erro {response.status_code}"

    except Exception as e:
        return None, f"Erro: {str(e)}"

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

# =====================================================================
# HEADER
# =====================================================================

st.markdown("<h1 style='text-align: center; color: #0066cc;'>🏥 Sistema de Prognóstico de Readmissão</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Avaliação de Risco para Pacientes 60+</p>", unsafe_allow_html=True)

# =====================================================================
# SIDEBAR
# =====================================================================

st.sidebar.markdown("## 📋 Menu")

pagina = st.sidebar.radio(
    "Selecione a página:",
    ["🎯 Avaliação", "📚 Sobre", "⚙️ Configurações"]
)

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

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Dados do Paciente")

        paciente_id = st.text_input("ID do Paciente:", value="PAC_001")
        idade = st.number_input("Idade:", min_value=18, max_value=120, value=75)
        diagnostico = st.text_input("Diagnóstico (CID-10):", value="I50.0")
        internacoes = st.number_input("Internações nos últimos 12 meses:", min_value=0, max_value=50, value=2)

        validar_btn = st.button("✓ Validar Entrada", use_container_width=True)
        avaliar_btn = st.button("🚀 Avaliar Risco", use_container_width=True, type="primary")

    with col2:
        st.markdown("### 📊 Resultado")

        if validar_btn:
            erros = validar_entrada(idade, diagnostico, internacoes)
            if erros:
                st.error("❌ Erros na validação:")
                for erro in erros:
                    st.write(f"  • {erro}")
            else:
                st.success("✅ Dados validados com sucesso!")

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
                        st.error(f"❌ {erro}")
                    else:
                        risco = resultado.get('risco_readmissao', 'DESCONHECIDO')
                        probabilidade = resultado.get('probabilidade_estimada', 0)

                        # Cores por risco
                        cores = {
                            'BAIXO': '#28a745',
                            'MEDIO': '#ffc107',
                            'ALTO': '#dc3545'
                        }
                        cor = cores.get(risco, '#6c757d')

                        # Exibir resultados
                        st.markdown(f"<h2 style='color: {cor};'>Nível de Risco: {risco}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<h3>Probabilidade: {probabilidade*100:.1f}%</h3>", unsafe_allow_html=True)

                        # Fatores relevantes
                        st.markdown("### 📌 Fatores Relevantes")
                        fatores = resultado.get('fatores_relevantes', [])
                        for fator in fatores:
                            st.info(f"• {fator}")

                        # Salvar em session state
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
# PÁGINA 2: SOBRE
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
    - **Frontend**: Streamlit
    - **Segurança**: Rate Limiting

    ### 📊 Fases de Desenvolvimento

    **Fase 1** ✅ Discovery & Requisitos
    **Fase 2** ✅ Baseline & Arquitetura
    **Fase 3** 🔄 Frontend & Interface (atual)
    **Fase 4** ⏳ Validação & Pitch
    """)

# =====================================================================
# PÁGINA 3: CONFIGURAÇÕES
# =====================================================================

elif pagina == "⚙️ Configurações":
    st.markdown("## Configurações")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔌 Configuração de API")

        api_url = st.text_input(
            "URL da API:",
            value="http://localhost:5000"
        )

        if st.button("🧪 Testar Conexão"):
            saude, erro = conectar_api('/saude')
            if saude:
                st.success("✅ Conexão bem-sucedida!")
            else:
                st.error(f"❌ Erro: {erro}")

# =====================================================================
# FOOTER
# =====================================================================

st.markdown("---")
st.markdown("<div style='text-align: center; color: #999; font-size: 0.9rem;'><p>TIA - Projeto Integrador IA | Fase 3</p></div>", unsafe_allow_html=True)
