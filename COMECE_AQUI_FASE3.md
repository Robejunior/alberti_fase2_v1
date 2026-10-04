# 🚀 COMECE AQUI - Fase 3

## 📋 O que você precisa fazer?

1. **Instalar dependências** (apenas 1x)
2. **Iniciar a aplicação**
3. **Abrir no navegador**

Pronto!

---

## ⚡ Passo 1: Preparação (uma única vez)

### Abrir PowerShell:
```powershell
cd C:\Users\ralbertijuni\Desktop\tia_api
```

### Criar ambiente virtual (se ainda não existe):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Instalar dependências:
```powershell
pip install -r requirements.txt
```

✅ **Pronto!** Você só precisa fazer isso uma vez.

---

## 🚀 Passo 2: Iniciar a Aplicação

### Opção A: AUTOMÁTICO (recomendado)

```powershell
cd C:\Users\ralbertijuni\Desktop\tia_api
.\run_app.ps1
```

Isso inicia automaticamente:
- ✅ API em `http://localhost:5000`
- ✅ Frontend em `http://localhost:8501`

### Opção B: MANUAL (dois terminais)

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

## 🌐 Passo 3: Abrir no Navegador

Após iniciar, abra em seu navegador:

```
http://localhost:8501
```

🎉 **Pronto!** O frontend está rodando!

---

## 📊 O que fazer agora?

### Na página "Avaliação" (padrão):

1. **Preencha os dados:**
   - ID do Paciente: (ex: PAC_001)
   - Idade: (ex: 75)
   - Diagnóstico: (ex: I50.0)
   - Internações: (ex: 2)

2. **Clique "Avaliar Risco"**

3. **Veja o resultado:** 
   - Nível de risco (BAIXO/MÉDIO/ALTO)
   - Probabilidade em percentual
   - Gráfico visual (gauge)

### Explore as outras páginas:

- **📊 Dashboard:** Veja histórico e estatísticas
- **📚 Sobre:** Saiba mais sobre o projeto
- **⚙️ Configurações:** Ajuste URL da API

---

## ✅ Checklist - Tudo Funcionando?

- [ ] Terminal mostra "✅ API Iniciada"
- [ ] Navegador abre em localhost:8501
- [ ] Sidebar mostra "✅ API Online"
- [ ] Consegue preencher formulário
- [ ] Consegue avaliar e ver resultado

Se tudo acima está OK: **🎉 Perfeito! Tudo funcionando!**

---

## ❌ Algo não funcionou?

### "API Offline" na sidebar

Significa API não está rodando. Abra outro terminal:
```powershell
cd C:\Users\ralbertijuni\Desktop\tia_api
python src/app.py
```

### "Connection refused" ao avaliar

Porta 5000 pode estar em uso. Tente:
```powershell
netstat -ano | findstr :5000
```

### Streamlit não abre

Tente uma porta diferente:
```powershell
streamlit run frontend.py --server.port 8502
```

---

## 📚 Mais Informações

Para guias completos, consulte:

| Documento | Conteúdo |
|-----------|----------|
| `GUIA_FASE3_FRONTEND.md` | Guia detalhado da Fase 3 |
| `docs/GUIA_FRONTEND_STREAMLIT.md` | Documentação técnica completa |
| `README.md` | Overview geral do projeto |
| `docs/GUIA_INSTALACAO.md` | Setup da API |

---

## 🎯 Resumo Rápido

```bash
# 1. Preparação (uma vez)
cd C:\Users\ralbertijuni\Desktop\tia_api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Iniciar
.\run_app.ps1

# 3. Abrir navegador
http://localhost:8501
```

**Fim!** 🎉

---

**Data**: 2026-10-03  
**Versão**: 1.0.0  
**Status**: ✅ Pronto  
**Fase**: 3 - Frontend Streamlit
