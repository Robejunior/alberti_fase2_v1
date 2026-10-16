# Histórico de Hospedagem, Correções e Segurança — Painel TIA (Fase 2)

> Registro técnico das decisões e mudanças feitas para colocar o Projeto Integrador de IA (TIA — Projeto 10) no ar em um servidor próprio, corrigir o Explorador de Resultados e proteger o acesso com usuário e senha. Mantido como histórico para consulta futura — não substitui os demais documentos da pasta `docs/`.

## 1. Objetivo

Disponibilizar o painel do projeto (Fase 2/3) em um endereço público, acessível por qualquer pessoa — incluindo a banca avaliadora — de qualquer rede, sem depender do notebook do autor ligado ou conectado.

## 2. Hospedagem

- **Provedor:** Hetzner Cloud.
- **Endereço público:** `http://204.168.165.21:8503`
- **Componentes rodando no servidor:**
  - API REST (Flask, `api_fase3/app.py`) na porta **5000**, só acessível internamente (`127.0.0.1`).
  - Painel web (`src/painel.py`, servidor HTTP próprio em Python) na porta **8503**, exposta publicamente.
  - MySQL 8.4 (banco `tia_fase2`), também interno.
- Firewall configurado para liberar apenas a porta necessária ao público; MySQL e a API não ficam expostos diretamente.
- Teste ponta a ponta validado com sucesso a partir de uma rede externa (SINT_001 → classificação de risco ALTO → explicação do Gemini), confirmando que o acesso público funciona de qualquer máquina.

## 3. Problemas identificados pelo autor e correções aplicadas

O autor reportou três problemas no painel já hospedado, através de capturas de tela:

1. Os cartões "Registros exibidos" e "Casos distintos" ficavam permanentemente em "—".
2. O "Explorador de Resultados" sempre mostrava "Nenhum registro encontrado" / "0 resultados", tornando a funcionalidade inútil.
3. Pergunta central: **depois de registrar um parecer na Revisão Humana, onde ficam os dados para consulta futura (auditoria ou mudança de opinião)?**

Diante da pergunta 3, foi avaliado se bastava uma solução paliativa ou uma correção definitiva — o autor optou por **implementar a correção completa imediatamente**.

### 3.1 Causa raiz

O painel (`src/painel.py`) consultava uma base antiga (`tia_e2`), desconectada da base real onde a API grava tudo (`tia_fase2`). Além disso, a consulta de classificações não trazia a explicação do Gemini nem o parecer humano — cada informação ficava isolada em tabelas diferentes (`classificacao`, `explicacao`, `revisao`, `usuario`), sem nenhum JOIN que as reunisse para exibição.

### 3.2 Arquivos alterados

| Arquivo | Mudança |
|---|---|
| `api_fase3/database.py` | `listar_classificacoes()` passou a fazer `LEFT JOIN` de `classificacao` com `explicacao` e com o **parecer de revisão mais recente** (via subquery correlacionada em `revisao` + `usuario`), trazendo tudo em uma única consulta. |
| `api_fase3/app.py` | Limite máximo de registros por página elevado de 100 para 200. |
| `src/painel.py` | Deixou de conectar diretamente ao MySQL; passou a consultar a própria API (`/api/v1/classificacoes`) — fonte única de verdade, evitando dessincronia entre painel e API. |
| `web/index.html` | Textos atualizados para refletir a nova arquitetura (explicação do Gemini + parecer humano no mesmo lugar); filtro de busca trocado de "Modelo" para "Risco". |
| `web/app.js` | Funções `filtered()`, `detail()`, `render()` e `load()` reescritas para consumir o novo formato de dados (idade, diagnóstico, internações, risco, probabilidade, explicação do Gemini, parecer/revisor/observação/data da revisão). Também corrigido: o formulário de revisão não limpava os campos "Parecer" e "Observação" depois de registrar — corrigido para resetar após o envio. |

### 3.3 Resultado

Confirmado em produção: ao abrir o "Explorador de Resultados" e selecionar um caso já revisado, a tela de detalhe mostra idade, diagnóstico, internações, risco, probabilidade, a explicação do Gemini **e**, quando houver, a seção "Revisão humana" com parecer, revisor, observação e data/hora — respondendo à pergunta original sobre auditoria.

> Nota: por um momento a tabela do Explorador pareceu vazia ao buscar "PAC_001" — não era bug, apenas um identificador de teste que nunca chegou a ser cadastrado (os casos reais usados foram `SINT_001`, `SINT_004`, etc.). Limpando o campo de busca, a lista aparece normalmente.

## 4. Deploy das correções

Os 5 arquivos alterados foram enviados ao servidor via `scp`, a partir do terminal local do Windows (nunca de dentro de uma sessão SSH). Durante o processo houve confusão entre a aba local (PowerShell comum) e as abas SSH (conectadas ao servidor) — resolvida consolidando o fluxo em duas janelas SSH dedicadas (uma para a API, outra para o painel) mais uma janela local só para `scp`.

Um envio do `api_fase3/app.py` falhou uma vez por queda momentânea de conexão SSH ("Connection closed") — sem impacto, pois a lógica principal estava em `database.py`, que havia sido enviado com sucesso. Foi reenviado manualmente depois.

## 5. Persistência: serviços systemd

**Problema:** a API e o painel rodavam em primeiro plano dentro de janelas SSH abertas manualmente. Fechar essas janelas (ou perder a conexão) derrubava os processos — mesmo com o servidor ligado.

**Solução:** os dois processos foram convertidos em serviços do sistema operacional (`systemd`), soltos de qualquer terminal:

- `/etc/systemd/system/tia-api.service` — roda `api_fase3/app.py` na porta 5000.
- `/etc/systemd/system/tia-painel.service` — roda `python -m src.painel` na porta 8503.

Ambos configurados com `Restart=always` (reinicia sozinho se cair) e `enable` (sobe automaticamente após qualquer reinício do servidor). Comandos de operação:

```bash
systemctl status tia-api tia-painel --no-pager   # ver se estão rodando
systemctl restart tia-api                         # reiniciar a API após atualizar código
systemctl restart tia-painel                       # reiniciar o painel após atualizar código
journalctl -u tia-api -f                           # acompanhar logs em tempo real
journalctl -u tia-painel -f
```

Testado e confirmado: com todas as janelas SSH fechadas e o notebook do autor desligado, o painel continuou acessível normalmente em `http://204.168.165.21:8503` a partir de uma aba anônima em outra máquina.

## 6. Segurança: autenticação por usuário e senha

Para demonstrar controle de acesso à banca, foi adicionada **autenticação HTTP Basic** diretamente no `src/painel.py`:

- Toda requisição (`GET` e `POST`) passa a exigir usuário e senha antes de qualquer resposta.
- Usuário e senha são lidos de variáveis de ambiente (`PAINEL_USUARIO`, `PAINEL_SENHA`) definidas apenas no arquivo de serviço do systemd no servidor — **nunca gravados no código-fonte nem versionados no Git**, evitando vazar a senha caso o repositório seja público.
- O navegador exibe o diálogo nativo de login do próprio sistema operacional/navegador (não é uma tela customizada da aplicação).

> As credenciais reais ficam apenas na configuração do serviço no servidor (`/etc/systemd/system/tia-painel.service`). Por segurança, não estão registradas neste documento — devem ser repassadas à banca separadamente (verbalmente ou por canal próprio), nunca dentro do repositório.

## 7. Troubleshooting da autenticação

Depois de configurada, a autenticação pareceu não funcionar em dois momentos distintos — ambos elucidados por diagnóstico passo a passo:

1. **Primeira tentativa:** a página carregava normalmente, sem pedir senha. Causa: o serviço havia sido recriado com as variáveis de ambiente, mas o arquivo `src/painel.py` atualizado (com o código de autenticação) ainda não tinha sido reenviado ao servidor — ou seja, o processo rodando era o código antigo, que nunca lia aquelas variáveis. Resolvido reenviando o arquivo via `scp` e reiniciando o serviço; confirmado via `grep -n "_autenticado" src/painel.py` no servidor.

2. **Segunda tentativa:** o navegador (Chrome e Edge, inclusive em modo anônimo) mostrava o texto "Acesso restrito..." como se fosse uma página comum, sem abrir a caixa de login. Diagnóstico feito com `curl -i http://127.0.0.1:8503/` **direto no servidor**, que confirmou a resposta `401 Unauthorized` com o cabeçalho `WWW-Authenticate` corretos — ou seja, o servidor estava 100% certo. O teste decisivo foi acessar a mesma URL pelo celular usando dados móveis (sem Wi-Fi corporativo): o popup de login apareceu normalmente. **Conclusão:** a rede corporativa (proxy/antivírus da DXC) filtra esse cabeçalho de autenticação em conexões HTTP sem criptografia — uma limitação da rede do notebook de testes, não do projeto. Confirmado que qualquer pessoa fora dessa rede (a banca, por exemplo) vê o login normalmente.

## 8. Pendências e recomendações

- **GitHub:** os 5 arquivos corrigidos (`api_fase3/database.py`, `api_fase3/app.py`, `src/painel.py`, `web/index.html`, `web/app.js`) foram commitados localmente (`git commit`). Falta rodar `git push` para sincronizar com o repositório remoto, caso o professor vá avaliar o código diretamente pelo GitHub.
- **HTTPS:** a autenticação atual roda sobre HTTP simples (sem certificado). Suficiente para fins acadêmicos, mas, se quiser evoluir o projeto futuramente, o próximo passo de segurança seria configurar HTTPS (exige domínio próprio) — fora do escopo avaliado por esta entrega.
- **Lembrete prático:** passar à banca o endereço (`http://204.168.165.21:8503`) junto com o usuário e a senha configurados — sem essas credenciais, ninguém consegue nem abrir a tela inicial.
