# 🚀 Guia Fase 3 - Frontend Streamlit

## 📋 Resumo

Fase 3 introduz a interface Streamlit para interação com o sistema de prognóstico de readmissão hospitalar. O frontend conecta-se à API existente (Fase 2) e fornece uma experiência visual intuitiva.

---

## ✨ Novo na Fase 3

| Item | Descrição |
|------|-----------|
| `frontend.py` | Interface Streamlit completa (450+ linhas) |
| `frontend_config.py` | Configurações centralizadas |
| `run_app.ps1` | Script para iniciar API + Frontend |
| `docs/GUIA_FRONTEND_STREAMLIT.md` | Documentação detalhada |
| Streamlit em `requirements.txt` | Dependências frontend |

---

## 🚀 Início Rápido

### Opção 1: Iniciar Tudo Automaticamente

```powershell
cd C:\Users\ralbertijuni\Desktop\tia_api
.\run_app.ps1
```

Isso inicia:
- ✅ API Flask em `http://localhost:5000`
- ✅ Frontend Streamlit em `http://localhost:8501`

### Opção 2: Iniciar Manualmente

**Terminal 1 - API:**
```powershell
cd C:\Users\ralbertijuni\Desktop\tia_api
.\venv\Scripts\Activate.ps1
python src/app.py
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\ralbertijuni\Desktop\tia_api
.\venv\Scripts\Activate.ps1
streamlit run frontend.py
```

---

## 📊 Páginas do Frontend

### 1️⃣ Avaliação (🎯 Avaliação)

**Entrada:**
- ID do Paciente
- Idade (60-120 anos)
- Diagnóstico (código CID-10)
- Internações anteriores (12 meses)

**Funções:**
- ✓ Validar Entrada: verifica se dados estão corretos
- 🚀 Avaliar Risco: chama API e exibe resultado

**Saída:**
- Nível de Risco (BAIXO/MÉDIO/ALTO) com cor
- Probabilidade de Readmissão (%)
- Gauge chart visual
- Fatores relevantes
- Histórico em sessão

### 2️⃣ Dashboard (📊 Dashboard)

**Análise:**
- Total de análises realizadas
- Contagem de riscos altos
- Probabilidade média

**Visualizações:**
- Gráfico de barras (distribuição de risco)
- Tabela com histórico completo

### 3️⃣ Sobre (📚 Sobre)

Informações gerais sobre:
- O sistema e seus objetivos
- Tecnologias utilizadas
- Fases de desenvolvimento
- Contato da equipe

### 4️⃣ Configurações (⚙️ Configurações)

Ajustes:
- URL da API (padrão: localhost:5000)
- Seleção de tema
- Teste de conexão

---

## 🔌 Fluxo de Dados

```
┌─────────────────────────┐
│  ENTRADA (Streamlit)    │
│ - Form inputs           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  VALIDAÇÃO              │
│ - Idade: 60-120         │
│ - Diagnóstico: 2-50 chr │
│ - Internações: 0-50     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  API CALL               │
│ POST /api/v1/classificar│
│ JSON payload            │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  RESULTADO (Flask API)  │
│ - risco_readmissao      │
│ - probabilidade_estimada│
│ - fatores_relevantes    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  EXIBIÇÃO (Streamlit)   │
│ - Gauge chart           │
│ - Cards de métrica      │
│ - Histórico em session  │
└─────────────────────────┘
```

---

## 🎨 Customização

### Alterar Cores

Arquivo: `frontend_config.py`, linha 11-20

```python
COLORS = {
    'BAIXO': '#28a745',      # Verde
    'MEDIO': '#ffc107',      # Amarelo
    'ALTO': '#dc3545',       # Vermelho
}
```

### Alterar URL da API

Arquivo: `frontend_config.py`, linha 27

```python
API_CONFIG = {
    'BASE_URL': 'http://localhost:5000',  # ← Modificar aqui
}
```

### Alterar Regras de Validação

Arquivo: `frontend_config.py`, linha 33-39

```python
VALIDATION = {
    'IDADE_MIN': 60,          # ← Modificar
    'IDADE_MAX': 120,         # ← Modificar
    'INTERNACOES_MIN': 0,     # ← Modificar
    'INTERNACOES_MAX': 50,    # ← Modificar
}
```

---

## 🧪 Testes Manuais

### Teste 1: Validação de Entrada

```
1. Abrir "Avaliação"
2. Deixar Idade = 50
3. Clicar "Validar Entrada"
4. Esperado: ❌ "Idade deve ser >= 60 anos"
```

### Teste 2: Avaliação Completa

```
1. Abrir "Avaliação"
2. Preencher:
   - ID: PAC_002
   - Idade: 78
   - Diagnóstico: I10
   - Internações: 3
3. Clicar "Avaliar Risco"
4. Esperado: ✅ Resultado com gauge e fatores
```

### Teste 3: Dashboard

```
1. Fazer 3+ avaliações
2. Abrir "Dashboard"
3. Esperado: ✅ Gráfico e tabela com histórico
```

### Teste 4: Health Check

```
1. Sidebar → "Status da API"
2. Se API rodando: ✅ "API Online"
3. Se API parada: ❌ "API Offline"
```

---

## 🔍 Troubleshooting

### "API Offline" aparece

**Causa:** API não está rodando  
**Solução:**
```powershell
python src/app.py
```

### "Connection refused"

**Causa:** Porta 5000 já em uso  
**Solução:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Streamlit não abre

**Causa:** Porta 8501 em uso  
**Solução:**
```powershell
streamlit run frontend.py --server.port 8502
```

### Erro "ModuleNotFoundError"

**Causa:** Dependências não instaladas  
**Solução:**
```powershell
pip install -r requirements.txt
```

---

## 📈 Estrutura de Arquivos - Fase 3

```
tia_api/
├── 📁 src/
│   ├── app.py              (API Flask existente)
│   ├── database.py         (Banco de dados)
│   ├── ai_engine.py        (Gemini integration)
│   └── ...
│
├── 📁 docs/
│   ├── GUIA_FRONTEND_STREAMLIT.md    ✨ [NOVO]
│   └── ...
│
├── frontend.py             ✨ [NOVO] - Interface principal
├── frontend_config.py      ✨ [NOVO] - Configurações
├── run_app.ps1             ✨ [NOVO] - Script automático
├── requirements.txt        ✅ (Atualizado com Streamlit)
└── GUIA_FASE3_FRONTEND.md  ✨ [NOVO] - Este arquivo
```

---

## 🎯 Próximas Melhorias (Futuro)

- [ ] Autenticação JWT no Streamlit
- [ ] Persistência de histórico em banco
- [ ] Upload de arquivo CSV
- [ ] Exportar resultados em PDF
- [ ] Notificações de risco alto
- [ ] Dark mode
- [ ] Deploy em Streamlit Cloud
- [ ] Integração com Google Sheets

---

## 📊 Exemplo de Uso Completo

```
1. Terminal 1:
   $ .\run_app.ps1
   
2. Terminal 2 (automático):
   ✅ API online em http://localhost:5000
   ✅ Frontend online em http://localhost:8501

3. Abrir navegador:
   http://localhost:8501

4. Preencher e avaliar:
   - ID: PAC_TEST
   - Idade: 72
   - Diagnóstico: E11
   - Internações: 1

5. Ver resultado com gauge chart

6. Ir para Dashboard ver histórico

7. Verificar Status da API na sidebar
```

---

## 🔐 Segurança

- ✅ Validação de entrada no frontend
- ✅ Validação novamente no backend
- ✅ Sem dados sensíveis armazenados localmente
- ✅ Histórico em memória de sessão (perdido ao recarregar)

---

## 📞 Suporte

**Problemas com a API?**  
Consulte: `docs/GUIA_INSTALACAO.md`

**Detalhes técnicos do frontend?**  
Consulte: `docs/GUIA_FRONTEND_STREAMLIT.md`

**Dúvidas gerais?**  
Consulte: `README.md`

---

**Data**: 2026-10-03  
**Versão**: 1.0.0  
**Status**: ✅ Pronto para Uso  
**Fase**: 3 - Frontend Streamlit
