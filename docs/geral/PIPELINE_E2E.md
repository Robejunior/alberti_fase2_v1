# 🔄 Pipeline End-to-End (Fase 2)

## Visão Geral

Este documento descreve o pipeline completo implementado conforme os requisitos da Fase 2 do Projeto Integrador.

```
ENTRADA DE DADOS → PROCESSAMENTO IA (Gemini) → PERSISTÊNCIA (MySQL)
```

---

## 1️⃣ Entrada de Dados

### Fonte: `src/main.py`

O pipeline inicia lendo dados estruturados do paciente:

```python
dados_teste = {
    'paciente_id': 'PAC_001',
    'internacao_id': 'INT_001',
    'idade': 75,
    'diagnostico_principal': 'I50.0',
    'internacoes_anteriores_12_meses': 2
}
```

### Origem dos Dados:
- **API REST**: `/api/v1/classificar` endpoint
- **Arquivo JSON**: `data/pacientes_teste.json`
- **Google Colab**: Leitura do Google Drive

---

## 2️⃣ Processamento IA (Gemini)

### Módulo: `src/ai_engine.py`

```python
ai_engine = AIEngine(config)
resultado = ai_engine.processar_classificacao(dados_paciente)
```

### Fluxo:

1. **Construir Prompt**: Estruturado com contexto clínico
2. **Chamar Gemini API**: `model.generate_content(prompt)`
3. **Receber Resposta**: JSON estruturado
4. **Validar Resposta**: Verificar estrutura e dados

### Exemplo de Prompt:
```
Analise os dados do paciente e forneça:
- Classificação de risco (BAIXO, MÉDIO, ALTO)
- Probabilidade de readmissão (0-100%)
- Fatores de risco identificados
- Recomendações clínicas

Responda em JSON...
```

### Resposta Esperada:
```json
{
  "risco": "ALTO",
  "probabilidade": 78,
  "fatores_risco": ["idade_avançada", "multiplas_internacoes"],
  "recomendacoes": ["acompanhamento_clinico", "monitoramento_sintomas"],
  "justificativa": "Paciente com múltiplas internações em 12 meses..."
}
```

---

## 3️⃣ Persistência (MySQL)

### Banco de Dados: `tia_fase2`

Dados salvos na tabela `classificacao`:

```sql
INSERT INTO classificacao (
  modelo_id, 
  entrada_json, 
  idade, 
  diagnostico_principal,
  internacoes_anteriores_12_meses,
  status,
  motivos,
  risco_readmissao,
  probabilidade_estimada
) VALUES (...)
```

### Campos Persistidos:
- `entrada_json`: Dados originais do paciente
- `idade`: Idade do paciente
- `diagnostico_principal`: Código CID-10
- `internacoes_anteriores_12_meses`: Histórico
- `status`: OK / ERRO_VALIDACAO / DADOS_INSUFICIENTES
- `risco_readmissao`: BAIXO / MÉDIO / ALTO
- `probabilidade_estimada`: 0.0-1.0

---

## 🚀 Como Executar

### Pré-requisitos:
```bash
# 1. Configurar .env
GEMINI_API_KEY=sua-chave-aqui
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=...
```

### Executar Pipeline:
```bash
cd C:\Users\ralbertijuni\Desktop\tia_api

# Ativar venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Rodar pipeline
python src/main.py
```

### Saída Esperada:
```
======================================================================
TIA - FASE 2 - PIPELINE END-TO-END
======================================================================

1️⃣  Inicializando componentes...
   ✅ Componentes inicializados com sucesso

2️⃣  ENTRADA DE DADOS
   Processando 5 registros de teste...

3️⃣  PROCESSAMENTO IA (Gemini)
   Paciente 1/5: PAC_001
      ✅ Resposta Gemini recebida
      💾 Salvando no MySQL...
      ✅ Salvo no MySQL com sucesso

...

📊 RESUMO DO PIPELINE
======================================================================
✅ Sucessos: 5/5
❌ Erros: 0/5
📈 Taxa de sucesso: 100.0%

🎉 PIPELINE CONCLUÍDO COM SUCESSO!
======================================================================
```

---

## 📊 Estrutura de Arquivos

```
meu-projeto-ia-saude/
├── src/
│   ├── config.py          ← Configurações
│   ├── database.py        ← Driver MySQL
│   ├── ai_engine.py       ← Integração Gemini
│   ├── auth.py            ← Autenticação JWT
│   ├── modelo.py          ← Algoritmo IA local
│   ├── app.py             ← API REST Flask
│   └── main.py            ← Pipeline E2E
│
├── docs/
│   ├── README.md
│   ├── PIPELINE_E2E.md    ← Este arquivo
│   └── ...
│
├── data/
│   └── pacientes_teste.json ← Dados de teste
│
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

---

## ✅ Checklist da Entrega (E2)

| Item | Status | Descrição |
|------|--------|-----------|
| ✅ Script Python | ✅ Done | `main.py` rodando pipeline completo |
| ✅ Schemas MySQL | ✅ Done | 12 tabelas com constraints |
| ✅ Integração Gemini | ✅ Done | `ai_engine.py` com SDK genai |
| ✅ Dados de Teste | ✅ Done | `data/pacientes_teste.json` |
| ✅ Versionamento | ✅ Done | Git com histórico de commits |

---

## 📈 Próximos Passos (Fase 3)

- [ ] Engenharia de Prompts (Structured Outputs)
- [ ] Mecanismo de Fallback
- [ ] Interface Streamlit/Gradio
- [ ] Validação mais rigorosa

---

**Data de Criação**: 2026-10-03  
**Versão**: 1.0.0  
**Status**: ✅ Pronto para Entrega
