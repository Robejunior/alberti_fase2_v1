# api_fase3/ — API de classificação (Árvore de Decisão + Gemini)

Cópia autocontida da API Flask que normalmente vive em `tia_api\src` (fora
desta pasta). Ela foi trazida para cá para que este pacote (`entrega_e2_pacote_completo`)
funcione sozinho, sem depender de outra pasta no computador.

O painel web deste pacote (`../src/painel.py`, servido em `http://127.0.0.1:8503`)
chama esta API em `http://127.0.0.1:5000/api/v1/...` para:
- avaliar risco de readmissão (`/classificar`) — decisão da Árvore de Decisão,
  com explicação complementar do Gemini (nunca decide o risco, só explica);
- revisão humana (`/usuarios`, `/revisao/pendentes`, `/revisao`).

Isso é **separado** do banco `tia_e2` usado pelo restante de `entrega_e2`
(a baseline de resumos Gemini). Esta API usa seu próprio banco MySQL
(`MYSQL_DATABASE`, padrão `tia_fase2` — ver `config.py`), com as tabelas
`modelo`, `classificacao`, `explicacao`, `usuario`, `revisao` definidas em
`database/schema.sql`.

## Como rodar

```powershell
cd api_fase3
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env   # preencha GEMINI_API_KEY (opcional) e as credenciais MySQL
python app.py
```

A API sobe em `http://localhost:5000` mesmo sem o Gemini configurado (cai em
texto de reserva) e mesmo sem o MySQL no ar (só os endpoints que dependem do
banco ficam indisponíveis, com erro explícito — a API não quebra).

Para criar o banco e as tabelas, rode o schema em `database/schema.sql` no
seu servidor MySQL antes de usar `/classificar`.
