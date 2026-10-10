# Entrega E2 — Baseline e Arquitetura Mínima Viável
Entrega 15/10/2026 • PI I • Tecnólogo de IA em Saúde • 30h planejadas.
Pacote independente: arquivos anteriores e Fase 3 permanecem na pasta superior.
## Execução PowerShell
Entre nesta pasta entrega_e2. Use Python 3.12 ou superior compatível com as dependências.
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m src.main --validar-dados
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m src.main
```
Copie .env.example apenas na primeira configuração; não sobrescreva um .env preenchido.
GEMINI_MODEL deve ser um modelo habilitado no seu AI Studio. Preencha chaves somente localmente.
A execução faz três chamadas ao Gemini e pode consumir a cota da conta.
## Preparar MySQL
No cliente mysql>, com administrador, crie um banco novo para a baseline:
```sql
CREATE DATABASE IF NOT EXISTS tia_e2 CHARACTER SET utf8mb4;
CREATE USER 'tia_e2'@'localhost' IDENTIFIED BY 'SUBSTITUA_POR_SENHA_LOCAL';
GRANT SELECT, INSERT, CREATE ON tia_e2.* TO 'tia_e2'@'localhost';
```
Não execute CREATE USER novamente se ele já existir. Configure host/permissão adequado
se Python e MySQL estiverem em contêineres diferentes. Não interrompa o MySQL local.
O driver cria baseline_execucao automaticamente; também há src/schema.sql.
## Critério de sucesso
Código de saída zero, três itens PERSISTIDO_E_RELIDO no relatório e SELECT correspondente
no banco. O JSON retornado e texto bruto são os recebidos do Gemini, sem números inventados.
A execução não calcula probabilidade clínica; demonstra integração acadêmica.
## Painel web (formulário de avaliação + revisão humana)
Além do pipeline de linha de comando (`src.main`), esta pasta inclui um painel
web em `src/painel.py` (servido em `http://127.0.0.1:8503`), com três partes:
- **Resultados da baseline**: lê o banco `tia_e2` (tabela `baseline_execucao`)
  e os relatórios em `docs/evidencias/*.json` — mesma baseline acima.
- **Nova avaliação**: formulário (ID do paciente, idade, CID-10, internações)
  que avalia risco de readmissão (Árvore de Decisão + explicação do Gemini),
  com gráfico de risco e cores por faixa (verde=BAIXO, laranja=MEDIO, vermelho=ALTO).
- **Revisão humana**: cadastro de revisores e fila de classificações pendentes
  de parecer (Concorda/Discorda/Inconclusivo).

As duas últimas partes **não usam** o banco `tia_e2` nem o Gemini desta pasta —
elas chamam uma API de classificação separada (Árvore de Decisão treinada sobre
coorte sintética), incluída em `api_fase3/` com seu próprio banco MySQL e seu
próprio `.env`. São dois servidores independentes, que precisam estar rodando
ao mesmo tempo:

```powershell
# Terminal 1 — API de classificação (ver api_fase3/README.md para o setup inicial)
.\iniciar_api_fase3.ps1

# Terminal 2 — Painel web (usa o ambiente .venv-colab já citado acima)
.\iniciar_painel.ps1
```

Depois, abra `http://127.0.0.1:8503` no navegador.

## Entrega
Esta pasta deve ser a raiz dos arquivos da E2 no repositório oficial.
Não inclua .env, .venv, credenciais ou dados reais. Não há commit/push automático.
Depois de validar o ambiente, registre versões:
```powershell
.\.venv\Scripts\python.exe -m pip freeze > requirements.lock.txt
```
Leia docs/PLANO_ENTREGA_E2.md. ABNT e execução externa permanecem pendentes.
SDK: https://ai.google.dev/gemini-api/docs/libraries
