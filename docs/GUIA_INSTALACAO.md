# 🚀 Guia Completo de Instalação - API TIA Fase 2

## 📋 Pré-requisitos

✅ Python 3.12+  
✅ MySQL 8.0+ (já configurado)  
✅ Banco de dados `tia_fase2` criado  
✅ pip (gerenciador de pacotes Python)  

---

## ⚙️ Passo 1: Preparar o Ambiente

### 1.1 Abra o PowerShell

```powershell
# Navegue até a pasta do projeto
cd C:\Users\ralbertijuni\Desktop\tia_api
```

### 1.2 Verifique se Python está instalado

```powershell
python --version
# Esperado: Python 3.12.x ou superior
```

Se não tiver Python, [baixe aqui](https://www.python.org/downloads/).

---

## 🏗️ Passo 2: Criar Ambiente Virtual

O ambiente virtual isola as dependências do projeto.

```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1
```

Você verá `(venv)` aparecer no prompt PowerShell.

**Se der erro de permissão:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📦 Passo 3: Instalar Dependências

```powershell
# Atualizar pip (opcional)
python -m pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt
```

**Pacotes que serão instalados:**
- Flask 3.0.0 (framework web)
- mysql-connector-python 8.2.0 (conexão MySQL)
- scikit-learn 1.8.0 (machine learning)
- pandas 3.0.2 (análise de dados)
- numpy 2.4.4 (computação numérica)

---

## 🔧 Passo 4: Configurar Variáveis de Ambiente

### 4.1 Copie o arquivo de exemplo

```powershell
copy .env.example .env
```

### 4.2 Edite o arquivo `.env`

Abra `C:\Users\ralbertijuni\Desktop\tia_api\.env` em um editor de texto (Notepad, VSCode, etc.)

**Altere estas linhas com suas credenciais MySQL:**

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=SUA_SENHA_AQUI
MYSQL_DATABASE=tia_fase2
MYSQL_PORT=3306
```

**Exemplo completo:**
```env
DEBUG=True
FLASK_ENV=development
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=minha_senha_123
MYSQL_DATABASE=tia_fase2
MYSQL_PORT=3306
SECRET_KEY=dev-secret-key-mudar-em-producao
```

---

## 🧪 Passo 5: Testar Conexão MySQL

Antes de rodar a API, verifique se consegue conectar ao MySQL:

```powershell
# No PowerShell, fora do ambiente da API
mysql -u root -p

# Digite sua senha
# Se conectou, veja as tabelas:
USE tia_fase2;
SHOW TABLES;

# Saia
exit
```

---

## 🚀 Passo 6: Executar a API

```powershell
# Certifique-se que está no diretório correto
cd C:\Users\ralbertijuni\Desktop\tia_api

# Ative o ambiente virtual
.\venv\Scripts\Activate.ps1

# Execute a API
python app.py
```

**Você verá:**
```
============================================================
TIA - Projeto 10 - Fase 2
API REST - Sistema de Prognóstico de Readmissão
============================================================
Versão: 1.0.0
Debug: True
Iniciando servidor em http://localhost:5000
============================================================
 * Running on http://127.0.0.1:5000
```

A API está **pronta para usar**! ✅

---

## 🧪 Passo 7: Testar a API

### Opção A: Usar o Script de Teste

**Em OUTRO PowerShell/Terminal:**

```powershell
cd C:\Users\ralbertijuni\Desktop\tia_api
.\venv\Scripts\Activate.ps1
python testar_api.py
```

Você verá:
```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          TIA - Projeto 10 - Fase 2                      ║
║          Suite de Testes da API REST                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

TESTE 1: Health Check
✅ Health Check: OK
...
```

### Opção B: Usar cURL

```powershell
# Health Check
curl -X GET http://localhost:5000/api/v1/saude

# Informações
curl -X GET http://localhost:5000/api/v1/info

# Classificar um paciente
curl -X POST http://localhost:5000/api/v1/classificar `
  -H "Content-Type: application/json" `
  -d '{
    "paciente_id": "PAC_001",
    "internacao_id": "INT_001",
    "idade": 75,
    "diagnostico_principal": "I50.0",
    "internacoes_anteriores_12_meses": 3
  }'
```

### Opção C: Usar Postman

1. Abra o [Postman](https://www.postman.com/downloads/)
2. Crie uma nova requisição
3. URL: `http://localhost:5000/api/v1/saude`
4. Método: `GET`
5. Clique em "Send"

---

## 📊 Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/saude` | Health check |
| GET | `/api/v1/info` | Informações da API |
| GET | `/api/v1/estatisticas` | Estatísticas |
| POST | `/api/v1/classificar` | Classificar risco |
| GET | `/api/v1/classificacoes` | Listar classificações |
| GET | `/api/v1/classificacoes/{id}` | Obter classificação |
| POST | `/api/v1/validar-entrada` | Validar dados |
| POST | `/api/v1/explicar/{id}` | Gerar explicação |

---

## 🛠️ Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"

**Solução:**
```powershell
# Certifique-se que o ambiente virtual está ativado
.\venv\Scripts\Activate.ps1

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: "Can't connect to MySQL server"

**Solução:**
```powershell
# Verifique se MySQL está rodando
mysql -u root -p

# Verifique credenciais no .env
cat .env

# Teste conexão diretamente
mysql -h localhost -u root -p tia_fase2
```

### Erro: "Port 5000 already in use"

**Solução:**
```powershell
# Encontre o processo usando a porta 5000
netstat -ano | findstr :5000

# Ou execute em uma porta diferente
# Edite app.py e mude: app.run(port=5001)
```

### Erro: "Database doesn't exist"

**Solução:**
```powershell
# Verifique se o banco foi criado
mysql -u root -p
SHOW DATABASES;
USE tia_fase2;
SHOW TABLES;
```

---

## 📁 Estrutura de Pastas

```
C:\Users\ralbertijuni\Desktop\tia_api\
├── app.py                 # API principal
├── config.py              # Configurações
├── database.py            # Banco de dados
├── modelo.py              # Modelo de IA
├── testar_api.py          # Script de testes
├── requirements.txt       # Dependências
├── .env                   # Variáveis de ambiente
├── .env.example           # Exemplo de .env
├── README.md              # Documentação
├── GUIA_INSTALACAO.md    # Este arquivo
└── venv/                  # Ambiente virtual (criado)
```

---

## 🎯 Próximos Passos

Depois de instalar com sucesso:

1. ✅ **Testar a API** - Execute `testar_api.py`
2. 📚 **Ler Documentação** - Veja `README.md`
3. 🔐 **Implementar Segurança** - Adicionar JWT
4. 📊 **Criar Dashboard** - Frontend com resultados
5. 🚀 **Deploy** - Colocar em produção

---

## 📞 Suporte Rápido

**Problema?** Verifique nesta ordem:

1. ✅ Python 3.12+ instalado?
2. ✅ Ambiente virtual ativado (`(venv)` aparece no prompt)?
3. ✅ Dependências instaladas (`pip list` mostra Flask)?
4. ✅ MySQL está rodando?
5. ✅ `.env` tem credenciais corretas?
6. ✅ Banco `tia_fase2` existe?

---

## 🎉 Conclusão

Parabéns! Você tem uma **API REST profissional** rodando! 🚀

**URLs úteis:**
- 🌐 API: http://localhost:5000
- 📊 Health: http://localhost:5000/api/v1/saude
- 📋 Docs: http://localhost:5000/api/v1/info

**Próxima fase:** Documentação Técnica Completa ✅

---

**Última atualização:** 2026-10-03
