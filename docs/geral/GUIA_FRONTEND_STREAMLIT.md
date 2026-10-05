# 🎨 Guia de Frontend - Streamlit Fase 3

## Visão Geral

Frontend Streamlit para o Sistema de Prognóstico de Readmissão Hospitalar. Interface interativa para avaliação de risco de readmissão em pacientes 60+.

---

## ✨ Características

### 📊 4 Páginas Principais

1. **🎯 Avaliação** - Formulário de entrada e resultados
   - Input de dados do paciente
   - Validação de entrada
   - Exibição de resultados com gauge chart
   - Histórico em sessão

2. **📊 Dashboard** - Análise histórica
   - Estatísticas gerais (total, riscos altos, probabilidade média)
   - Gráfico de distribuição de risco
   - Tabela de histórico de análises

3. **📚 Sobre** - Informações do projeto
   - Descrição do sistema
   - Tecnologias utilizadas
   - Fases de desenvolvimento

4. **⚙️ Configurações** - Ajustes da aplicação
   - Configuração de URL da API
   - Seleção de tema
   - Teste de conexão

### 🔌 Integração com API

Conexão com REST API Flask existente:
- Endpoint: `GET /api/v1/saude` (health check)
- Endpoint: `POST /api/v1/classificar` (avaliação)
- Tratamento de erro automático

### 🎨 Tema Responsivo

- Layout Wide (padrão Streamlit)
- Cores personalizadas
  - Verde: BAIXO
  - Amarelo: MÉDIO
  - Vermelho: ALTO
- CSS customizado inline
- Compatível com temas claro/escuro

---

## 🚀 Como Executar

### Pré-requisitos

1. **API rodando** em `http://localhost:5000`
   ```bash
   cd C:\Users\ralbertijuni\Desktop\tia_api
   python src/app.py
   ```

2. **Dependências instaladas**
   ```bash
   pip install streamlit plotly pandas requests
   ```

### Iniciar Frontend

```bash
cd C:\Users\ralbertijuni\Desktop\tia_api

# Ativar venv
.\venv\Scripts\Activate.ps1

# Rodar Streamlit
streamlit run frontend.py
```

### Acesso

Abra em: `http://localhost:8501`

---

## 📁 Estrutura do Arquivo

```
frontend.py
├── Imports
├── Configuração de página
├── Configuração de tema (COLORS)
├── Funções auxiliares
│   ├── conectar_api() - Requisições HTTP
│   ├── validar_entrada() - Validação de dados
│   └── get_cor_risco() - Mapeamento de cor
├── Header
├── Sidebar (navegação)
├── Página 1: Avaliação
├── Página 2: Dashboard
├── Página 3: Sobre
├── Página 4: Configurações
└── Footer
```

---

## 🔗 API Endpoints Utilizados

### Health Check
```python
GET /api/v1/saude
Response: {
  "status": "ok",
  "timestamp": "2026-10-03T12:00:00"
}
```

### Avaliação
```python
POST /api/v1/classificar
Request: {
  "paciente_id": "PAC_001",
  "idade": 75,
  "diagnostico_principal": "I50.0",
  "internacoes_anteriores_12_meses": 2
}
Response: {
  "dados": {
    "risco_readmissao": "ALTO",
    "probabilidade_estimada": 0.78,
    "fatores_relevantes": [
      "Múltiplas internações em 12 meses",
      "Idade avançada"
    ]
  }
}
```

---

## 🧪 Testes Manuais

### Teste 1: Validação de Entrada
1. Ir para "Avaliação"
2. Deixar Idade em 50 (menor que 60)
3. Clicar "Validar Entrada"
4. Esperado: Erro "Idade deve ser >= 60 anos"

### Teste 2: Avaliação Completa
1. Ir para "Avaliação"
2. Preencher:
   - ID: PAC_001
   - Idade: 75
   - Diagnóstico: I50.0
   - Internações: 2
3. Clicar "Avaliar Risco"
4. Esperado: Gauge chart e resultado do Gemini

### Teste 3: Dashboard
1. Fazer 3+ avaliações (na página "Avaliação")
2. Ir para "Dashboard"
3. Esperado: Gráfico e histórico de análises

### Teste 4: Health Check
1. Qualquer página
2. Ver "Status da API" na sidebar
3. Se API online: ✅ Sucesso
4. Se API offline: ❌ Offline

---

## 🎯 Validação de Entrada

Campo | Min | Max | Regra
------|-----|-----|-------
Idade | 60 | 120 | Obrigatório
Diagnóstico | - | - | Obrigatório, não vazio
Internações | 0 | 50 | Não-negativo

---

## 📊 Estrutura de Dados (Session State)

```python
st.session_state.historico = [
  {
    'timestamp': datetime,
    'paciente_id': str,
    'idade': int,
    'diagnostico': str,
    'risco': str,
    'probabilidade': float
  },
  ...
]
```

---

## 🎨 Personalização

### Alterar Cores

Em `frontend.py`, linha 30:
```python
COLORS = {
    'BAIXO': '#28a745',      # Verde
    'MEDIO': '#ffc107',      # Amarelo
    'ALTO': '#dc3545',       # Vermelho
}
```

### Alterar URL da API

Em `conectar_api()`, linha 46:
```python
url = f'http://localhost:5000/api/v1{endpoint}'
```

### Alterar Porta Streamlit

```bash
streamlit run frontend.py --server.port 8502
```

---

## 🔍 Troubleshooting

### "API Offline" na Sidebar

**Problema**: API não está rodando  
**Solução**:
```bash
cd C:\Users\ralbertijuni\Desktop\tia_api
python src/app.py
```

### "Connection refused" ao avaliar

**Problema**: Porta 5000 incorreta  
**Solução**: Verificar se API rodando em localhost:5000

### Streamlit não abre

**Problema**: Porta 8501 em uso  
**Solução**:
```bash
streamlit run frontend.py --server.port 8502
```

### Gráfico não renderiza

**Problema**: Plotly não instalado  
**Solução**:
```bash
pip install plotly
```

---

## 📈 Próximos Passos (Fase 3+)

- [ ] Autenticação JWT no Streamlit
- [ ] Integração com banco de dados (persistência)
- [ ] Upload de arquivo CSV
- [ ] Exportar resultados em PDF
- [ ] Notificações de risco alto
- [ ] Integração com Google Sheets
- [ ] Deploy em Streamlit Cloud

---

## 📝 Notas

- Histórico é perdido ao recarregar (persiste em sessão)
- API deve estar rodando em paralelo
- Requer Python 3.12+
- Compatível com Windows/Mac/Linux

---

**Data**: 2026-10-03  
**Versão**: 1.0.0  
**Status**: ✅ Pronto para Fase 3
