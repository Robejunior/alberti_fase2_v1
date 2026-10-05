# 🏛️ Arquitetura do Sistema - TIA Fase 2

## 📐 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         CAMADA DE APRESENTAÇÃO                  │
│              (Client: Browser, Mobile, Desktop App)              │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAMADA DE API REST                          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               Flask Web Framework (app.py)               │   │
│  │  ┌─────────────┬──────────────┬──────────────────────┐  │   │
│  │  │   Routes    │  Controllers │   Middleware/CORS   │  │   │
│  │  └─────────────┴──────────────┴──────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Endpoints:                                                       │
│  • GET  /api/v1/saude              (Health Check)              │
│  • GET  /api/v1/info               (Info da API)               │
│  • POST /api/v1/validar-entrada    (Validação)                 │
│  • POST /api/v1/classificar        (Classificação)             │
│  • GET  /api/v1/classificacoes     (Listar)                    │
│  • GET  /api/v1/estatisticas       (Estatísticas)              │
│  • POST /api/v1/explicar/{id}      (Explicação LLM)            │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐        ┌──────────┐      ┌──────────┐
    │ Database │        │ Modelo IA│      │Config &  │
    │Manager   │        │(modelo.py)      │Logs      │
    │(db.py)   │        └──────────┘      └──────────┘
    └──────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE DADOS                               │
│                   MySQL 8.0 Database                             │
│                     (tia_fase2)                                  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │          TABELAS PRINCIPAIS                             │   │
│  │  • lote_importacao      • modelo                        │   │
│  │  • diagnostico          • classificacao                 │   │
│  │  • paciente             • explicacao                    │   │
│  │  • internacao           • usuario                       │   │
│  │  • registro_sih         • revisao                       │   │
│  │  • coorte_treino        • vw_marco_funcional (View)     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Requisição - Classificação

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CLIENT REQUEST                                               │
│    POST /api/v1/classificar                                     │
│    {                                                             │
│      "idade": 75,                                               │
│      "diagnostico_principal": "I50.0",                          │
│      "internacoes_anteriores_12_meses": 3                       │
│    }                                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. VALIDAÇÃO (app.py)                                           │
│    ├─ Verificar JSON válido                                    │
│    ├─ Validar campos obrigatórios                              │
│    ├─ Chamar validadores (modelo.py)                           │
│    └─ Se inválido → ERRO 400                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ ✓ Válido
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. OBTER MODELO ATIVO (database.py)                             │
│    SELECT * FROM modelo ORDER BY treinado_em DESC LIMIT 1      │
│    ↓                                                             │
│    Retorna: modelo_id, versao, limites                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. CLASSIFICAÇÃO (modelo.py)                                   │
│    ┌─ Calcular probabilidade                                  │
│    │  peso_idade = (75 - 60) * 0.002                          │
│    │  peso_internacoes = 3 * 0.15                             │
│    │  peso_diagnostico = 0.40 (I50.0)                         │
│    │  probabilidade = 0.79                                    │
│    │                                                            │
│    └─ Mapear para faixa                                       │
│       (0.79 >= 0.667) → ALTO                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. INSERIR CLASSIFICAÇÃO (database.py)                          │
│    INSERT INTO classificacao (                                  │
│      modelo_id, entrada_json, idade, diagnostico,              │
│      internacoes_anteriores, status, risco, probabilidade      │
│    ) VALUES (...)                                               │
│    ↓                                                             │
│    Retorna: classificacao_id = 42                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. CALCULAR FATORES (modelo.py)                                │
│    ├─ Internações: 3 (importância 71%)                         │
│    ├─ Idade: 75 anos (importância 24%)                         │
│    └─ Diagnóstico: I50.0 (importância 4%)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. RESPOSTA SUCESSO                                             │
│    {                                                             │
│      "classificacao_id": 42,                                    │
│      "risco_readmissao": "ALTO",                               │
│      "probabilidade_estimada": 0.79,                            │
│      "fatores_relevantes": [...]                               │
│    }                                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Estrutura de Pastas e Módulos

```
tia_api/
│
├── 📄 app.py (500+ linhas)
│   └─ Responsabilidades:
│      ├─ Inicializar Flask app
│      ├─ Definir routes (8 endpoints)
│      ├─ Middleware (CORS, erro handling)
│      ├─ Integração com database.py
│      └─ Integração com modelo.py
│
├── 📄 config.py (60+ linhas)
│   └─ Responsabilidades:
│      ├─ Configurações (Development, Testing, Production)
│      ├─ Variáveis de ambiente
│      ├─ Constantes da API
│      └─ Limites e timeouts
│
├── 📄 database.py (150+ linhas)
│   └─ Responsabilidades:
│      ├─ Conexão com MySQL
│      ├─ Operações CRUD
│      ├─ Consultas otimizadas
│      ├─ Tratamento de erros
│      └─ Pool de conexões (singleton)
│
├── 📄 modelo.py (140+ linhas)
│   └─ Responsabilidades:
│      ├─ Algoritmo Decision Tree
│      ├─ Cálculo de probabilidades
│      ├─ Mapeamento de faixas
│      ├─ Validação de entrada
│      └─ Extração de fatores
│
├── 📄 testar_api.py (280+ linhas)
│   └─ Responsabilidades:
│      ├─ 8 testes automatizados
│      ├─ Validação de endpoints
│      ├─ Relatório de sucesso
│      └─ Integração com requests
│
├── 📁 venv/
│   └─ Ambiente virtual Python
│
├── 📁 __pycache__/
│   └─ Cache de Python
│
└── 📄 Configuração
    ├─ requirements.txt
    ├─ .env
    ├─ .env.example
    └─ README.md
```

---

## 🔌 Integração de Componentes

### Database.py ↔️ App.py

```
app.py (route handler)
    │
    ├─ Recebe JSON do client
    ├─ Valida com modelo.validar_entrada()
    │
    └─ Chama:
        │
        ├─ db.obter_modelo_ativo()
        │   ↓ Query: SELECT FROM modelo
        │   ↓ Retorna: modelo_id, versao, limites
        │
        └─ db.inserir_classificacao()
            ↓ Query: INSERT INTO classificacao
            ↓ Retorna: classificacao_id
```

### Modelo.py ↔️ App.py

```
app.py (route /classificar)
    │
    └─ Chama:
        │
        ├─ modelo.classificar_risco()
        │   ├─ Valida entrada
        │   ├─ Calcula probabilidade
        │   ├─ Mapeia para faixa
        │   └─ Retorna: {"status", "risco", "probabilidade"}
        │
        └─ modelo.obter_fatores_relevantes()
            └─ Retorna: lista de fatores com importância
```

---

## 📊 Padrões de Projeto

### 1. **Singleton Pattern** (database.py)
```python
_db_instance = None

def get_db(config=None):
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(config)
    return _db_instance
```
✅ Garante uma única conexão com BD

### 2. **Factory Pattern** (app.py)
```python
def resposta_sucesso(dados, mensagem, status_code):
    return jsonify({...}), status_code

def resposta_erro(erro, status_code):
    return jsonify({...}), status_code
```
✅ Padroniza respostas JSON

### 3. **MVC Pattern**
```
Models:   modelo.py, database.py (lógica de negócio)
Views:    app.py (JSON responses)
Control:  app.py (routes, validação)
```

---

## 🔐 Segurança - Camadas

```
┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 1: INPUT VALIDATION                                      │
│ • Validar tipo de dados                                         │
│ • Validar range (idade >= 60)                                   │
│ • Sanitizar strings                                             │
│ • Verificar campos obrigatórios                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 2: SQL INJECTION PREVENTION                              │
│ • Usar parameterized queries ✅ (já implementado)               │
│ • Nunca concatenar SQL                                          │
│ • Usar prepared statements                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 3: ERROR HANDLING                                        │
│ • Try-except em todos os endpoints ✅                           │
│ • Não expor stack traces                                        │
│ • Log de erros internos                                         │
│ • Retornar mensagens genéricas                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 4: AUTENTICAÇÃO (TODO)                                   │
│ • JWT tokens                                                    │
│ • Refresh tokens                                                │
│ • Token expiration                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CAMADA 5: AUTORIZAÇÃO (TODO)                                    │
│ • Role-based access control                                     │
│ • Resource-level permissions                                    │
│ • Audit logging                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Performance

### Query Optimization

```sql
-- ❌ LENTO (N+1 problem)
SELECT * FROM classificacao;  -- 1000 registros
-- Para cada um, SELECT FROM modelo  -- 1000 queries

-- ✅ RÁPIDO (Join único)
SELECT c.*, m.versao 
FROM classificacao c
JOIN modelo m ON c.modelo_id = m.modelo_id
ORDER BY c.criado_em DESC
LIMIT 10;
```

### Índices do Banco

```sql
CREATE INDEX idx_modelo_versao ON modelo(versao);
CREATE INDEX idx_classificacao_modelo ON classificacao(modelo_id);
CREATE INDEX idx_classificacao_criado ON classificacao(criado_em);
CREATE INDEX idx_lote_hash ON lote_importacao(hash_sha256);
```

### Cache Strategy

```
Implementar:
├─ Redis para cache de modelos
├─ Cache de diagnósticos
└─ Cache de estatísticas
```

---

## 📈 Escalabilidade

### Horizontal Scaling

```
Load Balancer (Nginx)
    ├─ API Instance 1 (Port 5000)
    ├─ API Instance 2 (Port 5001)
    ├─ API Instance 3 (Port 5002)
    └─ API Instance N (Port 500N)
        └─ MySQL (Replication)
            ├─ Master (Write)
            └─ Slave (Read)
```

### Vertical Scaling

```
Otimizar:
├─ Aumentar CPU
├─ Aumentar RAM
├─ Usar SSD para MySQL
└─ Aumentar banda de rede
```

---

## 🔄 Deployment Pipeline

```
┌────────────┐
│   Git      │ (Branch: feature/api)
│  Commit    │
└─────┬──────┘
      │
      ▼
┌────────────┐
│  GitHub    │ (Trigger CI/CD)
│  Actions   │
└─────┬──────┘
      │
      ▼
┌────────────────────┐
│   Test Stage       │
│ • pytest           │
│ • coverage         │
│ • linting          │
└─────┬──────────────┘
      │ ✓ Pass
      ▼
┌────────────────────┐
│   Build Stage      │
│ • Docker image     │
│ • Push to registry │
└─────┬──────────────┘
      │
      ▼
┌────────────────────┐
│   Deploy Stage     │
│ • Dev environment  │
│ • Staging env      │
│ • Production env   │
└────────────────────┘
```

---

## 📊 Diagrama de Estado - Classificação

```
┌──────────┐
│  INICIO  │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│  VALIDANDO INPUT │
└────┬─────────────┘
     │
     ├─ ❌ Inválido
     │   ▼
     │  ┌──────────────────┐
     │  │  ERRO_VALIDACAO  │
     │  └──────────────────┘
     │
     └─ ✓ Válido
        ▼
     ┌──────────────────────┐
     │ CLASSIFICANDO RISCO  │
     └────┬─────────────────┘
          │
          ├─ Dados insuficientes
          │   ▼
          │  ┌────────────────────────┐
          │  │ DADOS_INSUFICIENTES    │
          │  └────────────────────────┘
          │
          └─ ✓ Sucesso
             ▼
          ┌────────────┐
          │     OK     │
          │ Risco: ✅  │
          │ Prob: ✅   │
          └────────────┘
```

---

## 🎯 Conclusão

Esta arquitetura garante:
- ✅ **Modularidade** - Componentes desacoplados
- ✅ **Escalabilidade** - Fácil de escalar horizontalmente
- ✅ **Manutenibilidade** - Código limpo e organizado
- ✅ **Segurança** - Múltiplas camadas de proteção
- ✅ **Performance** - Queries otimizadas
- ✅ **Testabilidade** - Fácil de testar cada componente

---

**Próximo documento:** Diagrama ER e Schema do Banco
