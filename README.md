# TIA - Projeto 10 - Fase 2
## API REST - Sistema de Prognóstico de Readmissão Hospitalar

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Flask](https://img.shields.io/badge/flask-3.0+-green)
![MySQL](https://img.shields.io/badge/mysql-8.0+-blue)

---

## 📋 Descrição

API REST para prognóstico de risco de readmissão hospitalar em pacientes com 60 anos ou mais, utilizando dados do SUS/SIH.

**Funcionalidades:**
- ✅ Classificação de risco (BAIXO, MÉDIO, ALTO)
- ✅ Cálculo de probabilidade de readmissão
- ✅ Explicações automáticas via LLM
- ✅ Integração com banco de dados MySQL
- ✅ Auditoria completa de classificações
- ✅ Estatísticas em tempo real

---

## 🚀 Início Rápido

### 1. **Clonar/Baixar Projeto**

```bash
cd C:\Users\ralbertijuni\Desktop\tia_api
```

### 2. **Criar Ambiente Virtual**

```bash
python -m venv venv
```

### 3. **Ativar Ambiente Virtual**

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
venv\Scripts\activate.bat
```

### 4. **Instalar Dependências**

```bash
pip install -r requirements.txt
```

### 5. **Configurar Variáveis de Ambiente**

Copie `.env.example` para `.env`:
```bash
copy .env.example .env
```

Edite `.env` com suas credenciais MySQL:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=tia_fase2
```

### 6. **Executar API**

```bash
python app.py
```

Você verá:
```
============================================================
TIA - Projeto 10 - Fase 2
API REST - Sistema de Prognóstico de Readmissão
============================================================
Versão: 1.0.0
Debug: True
Iniciando servidor em http://localhost:5000
============================================================
```

---

## 📡 Endpoints da API

### **Base URL:** `http://localhost:5000/api/v1`

### 1️⃣ **Informações Gerais**

#### GET `/info`
Obter informações da API

**Resposta:**
```json
{
  "sucesso": true,
  "mensagem": "Sucesso",
  "dados": {
    "titulo": "TIA - Sistema de Prognóstico de Readmissão Hospitalar",
    "versao": "1.0.0",
    "modelo": {
      "versao": "v1.0.0",
      "algoritmo": "DecisionTree"
    }
  }
}
```

#### GET `/saude`
Health check

**Resposta:**
```json
{
  "sucesso": true,
  "dados": {"status": "ok"}
}
```

#### GET `/estatisticas`
Obter estatísticas do sistema

**Resposta:**
```json
{
  "sucesso": true,
  "dados": {
    "total_classificacoes": 50,
    "classificacoes_ok": 48,
    "classificacoes_erro": 2,
    "risco_baixo": 15,
    "risco_medio": 25,
    "risco_alto": 10,
    "modelo_ativo": "v1.0.0"
  }
}
```

---

### 2️⃣ **Classificação de Risco**

#### POST `/classificar`
Classificar risco de readmissão

**Payload:**
```json
{
  "paciente_id": "PAC_001",
  "internacao_id": "INT_001",
  "idade": 75,
  "diagnostico_principal": "I50.0",
  "internacoes_anteriores_12_meses": 3
}
```

**Resposta (Sucesso):**
```json
{
  "sucesso": true,
  "mensagem": "Classificação realizada com sucesso",
  "dados": {
    "classificacao_id": 1,
    "modelo_versao": "v1.0.0",
    "status": "OK",
    "risco_readmissao": "ALTO",
    "probabilidade_estimada": 0.75234,
    "fatores_relevantes": [
      {
        "fator": "internacoes_anteriores",
        "valor": 3,
        "importancia": 0.71,
        "descricao": "3 internações nos últimos 12 meses"
      },
      {
        "fator": "idade_avancada",
        "valor": 75,
        "importancia": 0.24,
        "descricao": "Idade de 75 anos"
      }
    ],
    "timestamp": "2026-10-03T15:30:45.123456"
  }
}
```

#### GET `/classificacoes?pagina=0&limite=10`
Listar classificações com paginação

**Resposta:**
```json
{
  "sucesso": true,
  "dados": {
    "total": 50,
    "pagina": 0,
    "limite": 10,
    "classificacoes": [...]
  }
}
```

#### GET `/classificacoes/{id}`
Obter uma classificação específica

---

### 3️⃣ **Explicações (LLM)**

#### POST `/explicar/{classificacao_id}`
Gerar explicação para uma classificação

**Resposta:**
```json
{
  "sucesso": true,
  "dados": {
    "classificacao_id": 1,
    "explicacao": "Relatório de classificação...",
    "origem": "RESERVA"
  }
}
```

---

### 4️⃣ **Validação**

#### POST `/validar-entrada`
Validar dados antes de classificar

**Payload:**
```json
{
  "idade": 75,
  "diagnostico_principal": "I50.0",
  "internacoes_anteriores_12_meses": 3
}
```

**Resposta:**
```json
{
  "sucesso": true,
  "dados": {
    "valido": true,
    "validacoes": {
      "idade": {"valido": true},
      "diagnostico_principal": {"valido": true},
      "internacoes_anteriores_12_meses": {"valido": true}
    }
  }
}
```

---

## 🧪 Exemplos de Uso (cURL)

### Verificar Saúde da API
```bash
curl -X GET http://localhost:5000/api/v1/saude
```

### Classificar um Paciente
```bash
curl -X POST http://localhost:5000/api/v1/classificar \
  -H "Content-Type: application/json" \
  -d '{
    "paciente_id": "PAC_001",
    "internacao_id": "INT_001",
    "idade": 75,
    "diagnostico_principal": "I50.0",
    "internacoes_anteriores_12_meses": 3
  }'
```

### Listar Classificações
```bash
curl -X GET "http://localhost:5000/api/v1/classificacoes?pagina=0&limite=10"
```

### Gerar Explicação
```bash
curl -X POST http://localhost:5000/api/v1/explicar/1
```

---

## 📊 Diagnósticos Suportados

| Código CID-10 | Descrição | Peso de Risco |
|---|---|---|
| I50.0 | Insuficiência cardíaca | 0.40 |
| I10 | Hipertensão essencial | 0.20 |
| E11 | Diabetes mellitus tipo 2 | 0.25 |
| J18 | Pneumonia | 0.30 |
| R51 | Cefaleia | 0.10 |

---

## 🔐 Segurança

- [ ] Adicionar autenticação JWT
- [ ] Adicionar rate limiting
- [ ] Validar HTTPS em produção
- [ ] Implementar CORS seguro
- [ ] Logs de auditoria
- [ ] Criptografia de dados sensíveis

---

## 📁 Estrutura do Projeto

```
tia_api/
├── app.py                 # API principal
├── config.py              # Configurações
├── database.py            # Gerenciador de BD
├── modelo.py              # Modelo de IA
├── requirements.txt       # Dependências
├── .env.example           # Exemplo de .env
├── README.md              # Este arquivo
└── tests/                 # (Será adicionado)
    └── test_api.py
```

---

## 🛠️ Desenvolvimento

### Executar em Modo Debug
```bash
DEBUG=True python app.py
```

### Executar Testes
```bash
pytest tests/
```

### Gerar Documentação
```bash
pydoc -w tia_api
```

---

## 📝 Próximos Passos

1. ✅ Implementar API REST
2. 🟡 Adicionar testes automatizados
3. 🟡 Implementar autenticação JWT
4. 🟡 Integrar com Gemini LLM
5. 🟡 Criar documentação Swagger
6. 🟡 Deploy em produção

---

## 📞 Suporte

Para dúvidas ou problemas, verifique:
- Logs de erro na console
- Verificar conectividade MySQL: `mysql -u root -p`
- Validar arquivo `.env`

---

## 📄 Licença

Projeto TIA - Fase 2 (2026)

---

**Última atualização:** 2026-10-03
