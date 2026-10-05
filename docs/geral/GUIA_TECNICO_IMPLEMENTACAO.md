# 🔧 Guia Técnico de Implementação - TIA Fase 2

## 📚 Índice

1. [Arquitetura Geral](#arquitetura-geral)
2. [Instalação & Setup](#instalação--setup)
3. [Estrutura de Código](#estrutura-de-código)
4. [APIs Disponíveis](#apis-disponíveis)
5. [Fluxo de Desenvolvimento](#fluxo-de-desenvolvimento)
6. [Troubleshooting](#troubleshooting)

---

## 🏛️ Arquitetura Geral

### Stack Tecnológico

```
Frontend (Consumidor)
    ↓ HTTP REST JSON
API Gateway (Flask)
    ├─ Routes & Middleware
    ├─ Validação
    └─ Response Handling
    ↓
Business Logic (Python)
    ├─ Modelo de IA (clasificação)
    ├─ Processamento de dados
    └─ Cálculos
    ↓
Data Layer (MySQL)
    ├─ CRUD Operations
    ├─ Queries Otimizadas
    └─ Índices
```

### Camadas da Aplicação

```
┌─────────────────────────────┐
│   Presentation Layer        │ (JSON responses)
├─────────────────────────────┤
│   API Layer (app.py)        │ (Routes, endpoints)
├─────────────────────────────┤
│   Business Logic (modelo.py)│ (Core algorithms)
├─────────────────────────────┤
│   Data Access (database.py) │ (SQL queries)
├─────────────────────────────┤
│   Database Layer (MySQL)    │ (Data persistence)
└─────────────────────────────┘
```

---

## 🔨 Instalação & Setup

### Pré-requisitos

```bash
✅ Python 3.12+
✅ MySQL 8.0+ (com banco tia_fase2)
✅ pip (Python package manager)
✅ Git (versionamento)
```

### Passo 1: Clonar Repositório

```bash
cd C:\Users\ralbertijuni\Desktop\tia_api
git init
git add .
git commit -m "Initial commit: API REST v1.0.0"
```

### Passo 2: Setup de Ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list
```

### Passo 3: Configurar `.env`

```bash
# Copiar template
copy .env.example .env

# Editar com credenciais reais
# MYSQL_PASSWORD=sua_senha_aqui
```

### Passo 4: Inicializar Banco

```bash
mysql -u root -p tia_fase2 < script_criacao_banco.sql
# ou executar manualmente o arquivo SQL
```

### Passo 5: Executar API

```bash
python app.py

# Output esperado:
# ============================================================
# TIA - Projeto 10 - Fase 2
# Iniciando servidor em http://localhost:5000
# ============================================================
```

---

## 🏗️ Estrutura de Código

### app.py (500+ linhas)

**Responsabilidades:**
- Inicializar Flask application
- Definir todas as rotas (8 endpoints)
- Middleware (CORS, error handling)
- Integração com outros módulos

**Estrutura:**

```python
# Imports
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
from modelo import ModeloIA
from config import get_config

# Inicialização
app = Flask(__name__)
config = get_config('development')
app.config.from_object(config)
CORS(app)

# Middleware
app.before_request(conectar_db)
app.after_request(lambda r: desconectar_db(None))

# Helpers
def resposta_sucesso(dados, mensagem, status_code):
    return jsonify({...}), status_code

def resposta_erro(erro, status_code):
    return jsonify({...}), status_code

# Routes
@app.route('/api/v1/saude', methods=['GET'])
def saude():
    return resposta_sucesso({'status': 'ok'})

@app.route('/api/v1/classificar', methods=['POST'])
def classificar():
    # Lógica principal
    ...

# Error Handlers
@app.errorhandler(404)
def nao_encontrado(erro):
    return resposta_erro('Endpoint não encontrado', 404)

# Main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

### config.py (60+ linhas)

**Responsabilidades:**
- Centralizar todas as configurações
- Suportar múltiplos ambientes (dev, test, prod)
- Carregar variáveis de ambiente

**Exemplo:**

```python
class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    
    # Database
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'tia_fase2')
    
    # API
    API_VERSION = '1.0.0'
    API_TITLE = 'TIA - Sistema de Prognóstico'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
```

---

### database.py (150+ linhas)

**Responsabilidades:**
- Gerenciar conexão MySQL
- Executar queries (CRUD)
- Retornar dados em formato consistente

**Métodos Principais:**

```python
class Database:
    def conectar(self):
        """Conectar ao MySQL"""
        
    def desconectar(self):
        """Fechar conexão"""
        
    def executar_query(self, query, params):
        """INSERT, UPDATE, DELETE"""
        return sucesso, erro
        
    def obter_dados(self, query, params):
        """SELECT - retorna lista"""
        return dados, erro
        
    def obter_um(self, query, params):
        """SELECT - retorna um registro"""
        return dados, erro
        
    def obter_modelo_ativo(self):
        """Obter modelo mais recente"""
        
    def inserir_classificacao(self, ...):
        """Inserir resultado de classificação"""
        
    def obter_estatisticas(self):
        """Estatísticas do sistema"""
```

**Padrão de Uso:**

```python
# Conectar
db = Database(config)
db.conectar()

try:
    # Obter dados
    dados, erro = db.obter_dados("SELECT * FROM modelo")
    if erro:
        print(f"Erro: {erro}")
    
    # Inserir
    sucesso, erro = db.executar_query(
        "INSERT INTO classificacao (...) VALUES (...)",
        params
    )
finally:
    db.desconectar()
```

---

### modelo.py (140+ linhas)

**Responsabilidades:**
- Implementar algoritmo de classificação
- Validar dados de entrada
- Calcular probabilidades
- Extrair fatores relevantes

**Métodos Principais:**

```python
class ModeloIA:
    def classificar_risco(self, idade, diagnostico, internacoes):
        """Principal - classifica risco"""
        # Valida entrada
        # Calcula probabilidade
        # Mapeia para faixa
        # Retorna resultado
        
        return {
            'status': 'OK' ou 'ERRO_VALIDACAO',
            'risco': 'BAIXO' ou 'MEDIO' ou 'ALTO',
            'probabilidade': 0.00000 a 1.00000,
            'motivos': [...] ou None
        }
    
    def _validar_entrada(self, idade, diagnostico, internacoes):
        """Validar tipos e ranges"""
        
    def _calcular_probabilidade(self, idade, diagnostico, internacoes):
        """Heurística de cálculo"""
        # peso_idade = (idade - 60) * 0.002
        # peso_internacoes = internacoes * 0.15
        # peso_diagnostico = self._obter_peso_diagnostico(diagnostico)
        # return sum(pesos) limitado a [0.05, 0.95]
        
    def _mapear_para_faixa(self, probabilidade):
        """Converter probabilidade em faixa"""
        # < 0.333 → BAIXO
        # 0.333-0.667 → MEDIO
        # >= 0.667 → ALTO
        
    def obter_fatores_relevantes(self, ...):
        """Explicability - quais fatores influenciaram"""
```

**Algoritmo de Classificação:**

```
Entrada:
  - idade: 75
  - diagnostico: I50.0
  - internacoes: 3

Processamento:
  1. Validar:
     ✓ idade >= 60
     ✓ diagnostico não vazio
     ✓ internacoes >= 0
     
  2. Calcular pesos:
     peso_idade = (75-60) * 0.002 = 0.03
     peso_internacoes = 3 * 0.15 = 0.45
     peso_diagnostico = 0.40 (I50.0)
     
  3. Somar:
     probabilidade = min(0.95, max(0.05, 0.03 + 0.45 + 0.40))
                  = min(0.95, max(0.05, 0.88))
                  = 0.88
     
  4. Mapear:
     0.88 >= 0.667 → ALTO
     
Saída:
  {
    "status": "OK",
    "risco": "ALTO",
    "probabilidade": 0.88,
    "fatores": [
      {"fator": "internacoes", "importancia": 0.71},
      {"fator": "idade", "importancia": 0.24},
      {"fator": "diagnostico", "importancia": 0.04}
    ]
  }
```

---

## 🌐 APIs Disponíveis

### Endpoint 1: Health Check

```
GET /api/v1/saude
```

**Request:**
```bash
curl http://localhost:5000/api/v1/saude
```

**Response (200):**
```json
{
  "sucesso": true,
  "mensagem": "Sucesso",
  "dados": {
    "status": "ok"
  }
}
```

---

### Endpoint 2: Informações da API

```
GET /api/v1/info
```

**Response (200):**
```json
{
  "sucesso": true,
  "dados": {
    "titulo": "TIA - Sistema de Prognóstico...",
    "descricao": "...",
    "versao": "1.0.0",
    "modelo": {
      "versao": "v1.0.0",
      "algoritmo": "DecisionTree"
    }
  }
}
```

---

### Endpoint 3: Classificar Risco ⭐

```
POST /api/v1/classificar
Content-Type: application/json
```

**Request:**
```json
{
  "paciente_id": "PAC_001",
  "internacao_id": "INT_001",
  "idade": 75,
  "diagnostico_principal": "I50.0",
  "internacoes_anteriores_12_meses": 3
}
```

**Response (201):**
```json
{
  "sucesso": true,
  "mensagem": "Classificação realizada com sucesso",
  "dados": {
    "classificacao_id": 1,
    "modelo_versao": "v1.0.0",
    "status": "OK",
    "risco_readmissao": "ALTO",
    "probabilidade_estimada": 0.79,
    "fatores_relevantes": [
      {
        "fator": "internacoes_anteriores",
        "valor": 3,
        "importancia": 0.71,
        "descricao": "3 internações..."
      }
    ],
    "timestamp": "2026-10-03T15:30:45..."
  }
}
```

**Status Codes:**
- `201` - Sucesso
- `400` - Erro de validação
- `500` - Erro interno

---

### Endpoint 4: Validar Entrada

```
POST /api/v1/validar-entrada
```

**Request:**
```json
{
  "idade": 75,
  "diagnostico_principal": "I50.0",
  "internacoes_anteriores_12_meses": 3
}
```

**Response (200):**
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

### Endpoint 5: Listar Classificações

```
GET /api/v1/classificacoes?pagina=0&limite=10
```

**Response (200):**
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

---

### Endpoints 6-8

```
GET /api/v1/classificacoes/{id}      - Obter específica
POST /api/v1/explicar/{id}           - Gerar explicação
GET /api/v1/estatisticas             - Estatísticas
```

---

## 🔄 Fluxo de Desenvolvimento

### 1. Feature Development

```
1. Criar branch
   git checkout -b feature/nova-funcionalidade
   
2. Implementar em:
   - app.py (novo endpoint)
   - modelo.py (lógica)
   - database.py (queries)
   - config.py (configurações)
   
3. Adicionar testes em:
   - testar_api.py
   
4. Commit
   git add .
   git commit -m "feature: adicionar nova funcionalidade"
   
5. Push
   git push origin feature/nova-funcionalidade
```

### 2. Testing

```bash
# Rodar suite de testes
python testar_api.py

# Esperado: 8/8 testes passando ✅
```

### 3. Code Review

```
Checklist:
 ☐ Código segue PEP 8
 ☐ Não há SQL injection
 ☐ Erros são tratados
 ☐ Testes passam
 ☐ Documentação atualizada
```

### 4. Deployment

```bash
# Dev
python app.py --env development

# Staging
python app.py --env testing

# Production
gunicorn -w 4 -b 0.0.0.0:5000 app:app --env production
```

---

## 🐛 Troubleshooting

### Erro: "Can't connect to MySQL"

**Diagnóstico:**
```bash
# Verificar se MySQL está rodando
mysql -u root -p

# Verificar credenciais em .env
cat .env | grep MYSQL

# Verificar banco existe
mysql -u root -p -e "USE tia_fase2; SHOW TABLES;"
```

**Solução:**
```bash
# Reiniciar MySQL (Windows)
net start MySQL80

# Ou via Services
services.msc → MySQL80 → Start
```

---

### Erro: "Port 5000 already in use"

**Solução:**
```bash
# Encontrar processo na porta 5000
netstat -ano | findstr :5000

# Matar processo
taskkill /PID <PID> /F

# Ou usar porta diferente
# Editar app.py, mude:
app.run(host='0.0.0.0', port=5001)
```

---

### Erro: "ModuleNotFoundError"

**Solução:**
```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Reinstalar dependências
pip install -r requirements.txt

# Verificar pacotes instalados
pip list | grep -i flask
```

---

### Erro: "ValidationError"

**Solução:**
```bash
# Adicionar print debug
@app.route('/api/v1/classificar', methods=['POST'])
def classificar():
    dados = request.get_json()
    print(f"DEBUG: Dados recebidos: {dados}")  # ← Adicionar
    
    # Verificar campos obrigatórios
    if 'idade' not in dados:
        return resposta_erro('Campo obrigatório: idade', 400)
```

---

## 📊 Performance Tuning

### Database Queries

```sql
-- ✅ RÁPIDO (com índice)
SELECT * FROM classificacao 
WHERE modelo_id = 1 
ORDER BY criado_em DESC 
LIMIT 10;

-- ❌ LENTO (sem índice)
SELECT * FROM classificacao 
WHERE status = 'OK' 
ORDER BY criado_em DESC;
-- Solução: CREATE INDEX idx_class_status ON classificacao(status);
```

### Connection Pooling

```python
# Usar singleton
db = get_db(config)  # Sempre mesma instância
db.conectar()
# ... usar
db.desconectar()
```

### Caching

```python
# TODO: Implementar Redis
from functools import lru_cache

@lru_cache(maxsize=128)
def get_modelo_ativo():
    return db.obter_modelo_ativo()
```

---

## 🎓 Boas Práticas

### 1. Segurança

✅ Usar prepared statements (já implementado)
✅ Validar entrada (já implementado)
✅ Tratar erros (já implementado)
☐ TODO: Adicionar autenticação JWT
☐ TODO: Implementar rate limiting

### 2. Código

✅ Seguir PEP 8
✅ Documentar funções (docstrings)
✅ DRY (Don't Repeat Yourself)
✅ SOLID principles
☐ TODO: Adicionar type hints

### 3. Testes

✅ 8 testes automatizados
✅ Cobertura de endpoints
☐ TODO: Unit tests
☐ TODO: Integration tests

---

## 📋 Checklist de Deployment

```
Pre-deployment:
 ☐ Todos os testes passam
 ☐ Código review aprovado
 ☐ Não há warnings/errors
 ☐ Documentação atualizada
 ☐ .env configurado corretamente

Deployment:
 ☐ Backup do banco feito
 ☐ Migrations aplicadas
 ☐ Variáveis de ambiente setadas
 ☐ SSL/TLS configurado
 ☐ Logs habilitados

Post-deployment:
 ☐ Health check OK
 ☐ Testes de smoke feitos
 ☐ Monitoring ativo
 ☐ Alertas configurados
 ☐ Documentação de rollback
```

---

**Próximo documento:** Performance & Scalability Guide
