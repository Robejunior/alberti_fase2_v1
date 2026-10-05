# 🔐 Guia de Segurança - TIA Fase 2

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação JWT](#autenticação-jwt)
3. [Rate Limiting](#rate-limiting)
4. [Validação de Entrada](#validação-de-entrada)
5. [CORS e Origem](#cors-e-origem)
6. [Variáveis de Ambiente](#variáveis-de-ambiente)
7. [Boas Práticas](#boas-práticas)
8. [Deployment Seguro](#deployment-seguro)
9. [Checklist de Segurança](#checklist-de-segurança)

---

## 🎯 Visão Geral

A API TIA implementa múltiplas camadas de segurança:

```
┌─────────────────────────────────────────────────────────┐
│              Cliente / Aplicação                         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
    HTTPS/TLS              Rate Limiting
        │                         │
        └────────────┬────────────┘
                     │
              JWT Authentication
                     │
           Input Validation & Sanitização
                     │
              CORS & Origem Verificada
                     │
         Acesso ao Banco de Dados Seguro
                     │
         Parameterized Queries (SQL Injection Prevention)
```

---

## 🔑 Autenticação JWT

### O que é JWT?

JWT (JSON Web Token) é um método seguro de autenticação que:
- ✅ Não requer sessão no servidor
- ✅ Pode ser usado em APIs REST
- ✅ É stateless (escalável)
- ✅ Contém informações criptografadas

### Fluxo de Autenticação

```
1. Cliente faz POST /api/v1/login
   {
     "usuario_id": "alberti",
     "senha": "sua-senha"
   }

2. Servidor valida credenciais e gera token
   {
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "tipo": "Bearer",
     "expira_em": "24 horas"
   }

3. Cliente armazena o token

4. Para cada requisição, enviar:
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

5. Servidor valida o token antes de processar
```

### Exemplo: Login e Uso

**1. Fazer Login:**

```bash
curl -X POST http://localhost:5000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "alberti",
    "senha": "minha-senha"
  }'
```

**Resposta:**

```json
{
  "sucesso": true,
  "mensagem": "Login bem-sucedido",
  "dados": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvX2lkIjoiYWxiZXJ0aSIsInBhcGVsIjoidXN1YXJpbyIsImlhdCI6MTcyNzk5MzkyOCwiZXhwIjoxNzI4MDgwMzI4fQ.abc123...",
    "tipo": "Bearer",
    "expira_em": "24 horas"
  }
}
```

**2. Usar o Token:**

```bash
curl -X GET http://localhost:5000/api/v1/classificacoes \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvX2lkIjoiYWxiZXJ0aSIsInBhcGVsIjoidXN1YXJpbyIsImlhdCI6MTcyNzk5MzkyOCwiZXhwIjoxNzI4MDgwMzI4fQ.abc123..."
```

**Se token expirar:**

```json
{
  "sucesso": false,
  "erro": "Erro ao validar token: Token expirado"
}
```

### Propriedades do Token

Cada token contém:

| Campo | Valor | Descrição |
|-------|-------|-----------|
| `usuario_id` | string | ID do usuário autenticado |
| `papel` | string | Papel do usuário (usuario, admin) |
| `iat` | timestamp | Quando o token foi emitido |
| `exp` | timestamp | Quando o token expira (24h depois) |

---

## 🚦 Rate Limiting

### Proteção contra Abuso

O Rate Limiting protege contra:
- 🔴 Força bruta (tentativas de login)
- 🔴 Flood de requisições
- 🔴 DDoS (Distributed Denial of Service)
- 🔴 Abuso de API

### Limites Configurados

| Endpoint | Limite | Janela |
|----------|--------|--------|
| `POST /login` | 5 por minuto | 1 minuto |
| `POST /classificar` | 30 por minuto | 1 minuto |
| `GET /classificacoes/*` | 60 por minuto | 1 minuto |
| `GET /estatisticas` | 60 por minuto | 1 minuto |
| **Global** | **50 por hora** | **1 hora** |

### Resposta Quando Limite Excedido

```json
{
  "sucesso": false,
  "erro": "429 Too Many Requests - Rate limit exceeded"
}
```

**Status HTTP:** 429 (Too Many Requests)

---

## ✔️ Validação de Entrada

### Princípios

1. ✅ **Whitelist** - Aceitar apenas dados conhecidos
2. ✅ **Type Checking** - Validar tipos de dados
3. ✅ **Length Limits** - Limitar tamanho de entrada
4. ✅ **Sanitização** - Remover caracteres perigosos
5. ✅ **Parametrized Queries** - Usar prepared statements

### Exemplo: Validação de Classificação

```python
# ANTES (❌ Inseguro)
query = f"SELECT * FROM modelo WHERE modelo_id = {modelo_id}"
cursor.execute(query)  # SQL Injection possível!

# DEPOIS (✅ Seguro)
query = "SELECT * FROM modelo WHERE modelo_id = %s"
cursor.execute(query, (modelo_id,))  # Parametrizado
```

### Campos Obrigatórios

```
POST /api/v1/classificar:
- idade (inteiro, 60-120)
- diagnostico_principal (string, 8 chars)
- internacoes_anteriores_12_meses (inteiro, >= 0)

POST /api/v1/login:
- usuario_id (string, obrigatório)
- senha (string, obrigatório)
```

---

## 🌐 CORS e Origem

### Configuração CORS

CORS (Cross-Origin Resource Sharing) controla quem pode acessar a API:

```python
# ANTES: Permitir todas as origens (❌ Inseguro)
CORS(app)  # Permite http://malicioso.com

# DEPOIS: Permitir apenas origens conhecidas (✅ Seguro)
CORS(app, origins=[
    "http://localhost:3000",
    "https://app.example.com",
    "https://portal.example.com"
])
```

### Headers de Segurança

Adicione headers CORS ao `.env`:

```env
ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com
ALLOWED_METHODS=GET,POST,OPTIONS
ALLOWED_HEADERS=Content-Type,Authorization
```

---

## 🔐 Variáveis de Ambiente

### Arquivo .env (Nunca Commitar!)

```env
# Flask
DEBUG=False  # SEMPRE False em produção!
FLASK_ENV=production

# MySQL
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=senha-forte-123!@#
MYSQL_DATABASE=tia_fase2
MYSQL_PORT=3306

# API - SEGURANÇA
SECRET_KEY=sua-chave-secreta-aleatória-muito-longa-32-caracteres-minimo
HASH_ALGORITHM=HS256

# LLM (Gemini)
GEMINI_API_KEY=sua-chave-api-segura

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com
```

### Boas Práticas para SECRET_KEY

```python
# Gerar uma SECRET_KEY segura
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)  # Copiar para .env
```

---

## 🛡️ Boas Práticas

### 1. **Senha Forte**

❌ **Fraco:**
```
senha123
qwerty
admin
```

✅ **Forte:**
```
P@ssw0rd!xY#2024Secure$Key
aB3$xM9!qL2@nP8&vK5#
```

**Requisitos:**
- Mínimo 12 caracteres
- Maiúsculas, minúsculas, números, símbolos
- Sem informações pessoais

### 2. **HTTPS em Produção**

```bash
# ❌ Desenvolvimento (OK)
http://localhost:5000

# ✅ Produção (OBRIGATÓRIO)
https://api.example.com  # Com certificado SSL/TLS
```

### 3. **Logging de Acesso**

Registrar todas as tentativas:

```python
# Implementado em auth.py:registrar_acesso()
[2026-10-03 21:34:04] /api/v1/classificacoes | Usuario: alberti | IP: 192.168.1.100 | Status: 200
[2026-10-03 21:34:05] /api/v1/login | Usuario: hacker | IP: 203.0.113.45 | Status: 401
```

### 4. **Proteção contra SQL Injection**

```python
# ✅ Sempre usar queries parametrizadas
cursor.execute("SELECT * FROM modelo WHERE modelo_id = %s", (id,))

# ❌ NUNCA usar f-strings com SQL
cursor.execute(f"SELECT * FROM modelo WHERE modelo_id = {id}")
```

### 5. **Proteção contra XSS**

```python
# ✅ Validar e sanitizar entrada
dados = request.get_json()
entrada_limpa = sanitizar_entrada(dados, ['campo1', 'campo2'])

# ❌ NUNCA usar input diretamente
html = f"<div>{dados['campo']}</div>"  # Risco de XSS!
```

### 6. **Timeout de Sessão**

- Token JWT expira em **24 horas**
- Requisições expiram em **30 segundos**
- Conexão inativa fecha em **5 minutos**

---

## 🚀 Deployment Seguro

### Checklist de Deployment

```
Segurança:
 ☐ DEBUG=False no .env
 ☐ SECRET_KEY único e forte (32+ caracteres)
 ☐ HTTPS com certificado SSL válido
 ☐ Firewall configurado (bloquear portas desnecessárias)
 ☐ Rate limiting ativo
 ☐ CORS configurado (apenas origens conhecidas)
 ☐ JWT enabled em todos endpoints
 ☐ Logging centralizado ativo
 ☐ Backup automático do banco
 ☐ Monitoramento de falhas
```

### Variáveis em Produção

```env
# production.env
DEBUG=False
FLASK_ENV=production

MYSQL_HOST=db.exemplo.com  # Host seguro
MYSQL_USER=tia_user
MYSQL_PASSWORD=$(openssl rand -base64 32)  # Gerada aleatoriamente

SECRET_KEY=$(openssl rand -base64 32)  # Gerada aleatoriamente

ALLOWED_ORIGINS=https://app.exemplo.com,https://api.exemplo.com
```

### Docker (Seguro)

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Não rodar como root
RUN useradd -m appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Mudar para usuário não-root
USER appuser

# Porta deve estar declarada
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/v1/saude || exit 1

CMD ["python", "app.py"]
```

---

## ✅ Checklist de Segurança

### Antes de Cada Deployment

```
Código:
 ☐ Sem credenciais hardcoded
 ☐ Sem tokens em comentários
 ☐ Sem informações sensíveis em logs
 ☐ Validação de entrada completa
 ☐ Rate limiting configurado
 ☐ CORS restritivo
 ☐ JWT verificando corretamente
 ☐ Testes de segurança passando

Infra:
 ☐ Firewall ativo
 ☐ HTTPS configurado
 ☐ Senhas fortes no banco
 ☐ Backup automático configurado
 ☐ Logs centralizados
 ☐ Monitoramento ativo
 ☐ Alertas configurados
 ☐ Plano de recuperação documentado

Documentação:
 ☐ Guia de segurança atualizado
 ☐ Plano de resposta a incidentes
 ☐ Procedimento de rollback
 ☐ Contatos de segurança definidos
```

---

## 📞 Suporte e Segurança

### Reportar Vulnerabilidade

Se encontrar uma vulnerabilidade:

1. **NÃO publique** em issues públicas
2. Envie email para: **security@exemplo.com**
3. Inclua:
   - Descrição da vulnerabilidade
   - Passos para reproduzir
   - Impacto potencial
   - Sugestão de correção (opcional)

### Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc7519)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [SQL Injection Prevention](https://owasp.org/www-community/attacks/SQL_Injection)

---

**Última atualização:** 2026-10-03

**Versão:** 1.0.0

**Status:** ✅ Implementado e Testado
