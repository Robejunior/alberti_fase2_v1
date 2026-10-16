# Roteiro de Apresentação — TIA · Projeto 10 (Triagem de Risco de Readmissão Hospitalar)

> Dois roteiros de fala prontos para adaptar: um para a Banca avaliadora (formal, foco técnico e de governança) e um para explicar o projeto aos colegas de turma (didático, foco em "como funciona e como testar"). Baseado no tema oficial do Projeto 10 e em tudo o que foi efetivamente implementado e hospedado. Mantido como material de apoio — não substitui os demais documentos da pasta `docs/`.

---

## 1. Speech para a Banca Avaliadora

**Duração sugerida:** 7 a 9 minutos de fala + tempo para perguntas. Os colchetes `[...]` indicam o que fazer na tela enquanto fala (demonstração ao vivo).

### 1.1 Abertura — o problema

> "Bom dia. Meu projeto é o número 10: **Triagem Automatizada do Risco de Readmissão Hospitalar de Pacientes Idosos**.
>
> O problema que ele ataca é concreto e caro para o sistema de saúde: um paciente idoso recebe alta, mas em menos de 30 dias volta a ser internado pela mesma causa — a chamada **reinternação precoce**. Isso acontece porque, no momento da alta, raramente existe uma avaliação objetiva da capacidade do paciente ou da família de manter o tratamento em casa. O resultado são leitos ocupados por readmissões evitáveis, recursos desperdiçados e o próprio idoso exposto outra vez a riscos hospitalares, como infecções.
>
> A proposta do projeto é usar dados públicos do SIH/SUS e um modelo simples e explicável — uma Árvore de Decisão — para classificar, ainda no momento da alta, se aquele paciente tem risco **Baixo, Médio ou Alto** de retornar. A ideia não é substituir o julgamento clínico, e sim dar à equipe um sinal objetivo e rastreável para priorizar atenção."

### 1.2 Dados e metodologia

> "O modelo lê três variáveis simples e disponíveis no momento da alta: **idade**, **número de internações anteriores** e **diagnóstico principal (CID-10)**. Com uma Árvore de Decisão treinada em Python, essas três entradas geram uma classificação de risco. Escolhi uma Árvore de Decisão de propósito: é um classificador iniciante, interpretável — dá para explicar exatamente qual caminho de decisão levou àquele resultado, o que importa muito num contexto de saúde, onde uma 'caixa-preta' teria menos credibilidade com a equipe clínica."

### 1.3 Arquitetura e demonstração ao vivo

> "Para não ficar só no papel, o projeto foi além do notebook: eu montei um pipeline completo, de ponta a ponta, e hospedei ele publicamente para que qualquer pessoa — vocês inclusive — possa validar agora, de qualquer rede, sem depender do meu computador ligado."

**[Abra `http://204.168.165.21:8503` em uma aba anônima para mostrar que não é sessão salva]**

> "O fluxo tem quatro etapas, que aparecem aqui na tela de visão geral:
>
> 1. **Entrada sintética** — dados estruturados e validados no formulário.
> 2. **Processamento** — a Árvore de Decisão calcula o risco, e um modelo de linguagem (Gemini) gera um resumo explicativo em texto, complementar à classificação.
> 3. **Persistência em banco de dados** — tudo é gravado em um MySQL, numa API própria que eu escrevi em Flask (Python).
> 4. **Conferência e auditoria** — todo resultado fica disponível para consulta posterior, com rastreabilidade completa."

**[Vá até "Nova avaliação", preencha um caso sintético e clique em "Avaliar risco e salvar"]**

> "Aqui eu registro um caso: idade, diagnóstico CID-10 e número de internações recentes. Ao enviar, a classificação roda, o resultado aparece com o nível de risco e o percentual estimado, e tudo já fica salvo no banco — não é só uma tela bonita, é persistência real."

**[Vá até "Explorador de Resultados", clique em um registro]**

> "Esse é o ponto que considero mais importante para uma banca avaliadora: o **Explorador de Resultados**. Cada registro salvo pode ser reaberto, e aqui eu mostro não só a classificação, mas também a explicação gerada pela IA e, quando existir, o **parecer de revisão humana** sobre aquele caso. Ou seja, o sistema não entrega uma decisão fechada — ele entrega uma sugestão rastreável, auditável, que pode ser conferida e contestada por um profissional."

**[Vá até "Revisão Humana"]**

> "E esse é o mecanismo de governança: um profissional cadastrado pode abrir uma classificação pendente e registrar se **concorda**, **discorda** ou considera **inconclusiva** aquela triagem, com uma observação. Isso fecha o ciclo: a IA sugere, o humano decide, e tudo fica registrado para auditoria futura — inclusive para estudos posteriores sobre a acurácia do modelo frente ao julgamento humano."

### 1.4 Diferenciais do projeto

> "Três pontos que fui além do mínimo pedido pela atividade:
>
> - **Hospedagem pública real**, em um servidor próprio na nuvem (Hetzner Cloud), com os serviços rodando via `systemd` — ou seja, o sistema continua no ar mesmo se eu desligar meu notebook ou fechar o terminal. Isso garante que a banca pode acessar o projeto a qualquer momento, de qualquer lugar, sem depender da minha presença.
> - **Controle de acesso com autenticação de sessão** — login e senha, com um botão de 'Sair' funcional, cabeçalhos de segurança e uma lista de endereços permitidos, para mostrar cuidado com segurança mesmo em um ambiente acadêmico.
> - **Rastreabilidade de ponta a ponta** — da entrada do dado até o parecer humano, passando pela explicação gerada por IA, tudo com registro em banco relacional e recuperável a qualquer momento."

### 1.5 Limites, honestidade técnica e fechamento

> "É importante ser transparente sobre os limites: os dados usados são **sintéticos**, sem identificação pessoal, e o modelo atual é uma baseline — para uso real em produção clínica, ele precisaria de treinamento e validação estatística rigorosa sobre uma base real do SIH/SUS, com métricas de desempenho, curva ROC, validação cruzada, e aprovação de comitê de ética. O painel deixa isso explícito para quem acessa: não é uma ferramenta de decisão clínica, é uma demonstração acadêmica da arquitetura e do raciocínio.
>
> Com isso, encerro: o projeto entrega não só o classificador pedido, mas um sistema completo, hospedado, seguro e auditável — pronto para evoluir para uma validação clínica real. Fico à disposição para perguntas."

### 1.6 Perguntas prováveis da banca — respostas curtas prontas

- **"Por que Árvore de Decisão e não outro modelo?"** → "Porque é interpretável: dá para explicar o caminho de decisão a uma equipe clínica, o que importa mais, nesta fase, do que ganhar alguns pontos de acurácia com um modelo de caixa-preta."
- **"Os dados são reais?"** → "São sintéticos, inspirados na estrutura do SIH/SUS, sem nenhum dado identificável de paciente real — decisão deliberada para a fase acadêmica."
- **"O que acontece se o modelo errar?"** → "Por isso existe a etapa de Revisão Humana: toda classificação pode ser confirmada, contestada ou marcada como inconclusiva por um profissional, e isso fica registrado — o modelo sugere, não decide sozinho."
- **"Isso está pronto para uso real em um hospital?"** → "Não ainda. Falta validação estatística em base real, aprovação ética e testes de carga/segurança adicionais. O que existe hoje é a arquitetura funcional, hospedada, pronta para essa evolução."
- **"Como vocês garantem que o acesso é seguro?"** → "Autenticação por sessão com login e senha, cookies protegidos, política de segurança de conteúdo no servidor e lista de endereços permitidos — e o acesso roda de forma persistente via systemd no servidor, não dependendo de nenhuma máquina pessoal."

---

## 2. Speech para explicar aos colegas de turma

**Duração sugerida:** 4 a 6 minutos, tom mais solto — é para ensinar, não para ser avaliado.

### 2.1 Gancho inicial

> "Pessoal, deixa eu mostrar rapidinho o que o meu grupo fez no Projeto 10, porque dá pra vocês testarem no celular de vocês agora mesmo, ao vivo. A gente pegou aquele problema de idoso que recebe alta e volta pro hospital em menos de 30 dias — reinternação precoce — e construiu um sisteminha que, com três informações simples (idade, histórico de internações e o diagnóstico), já dá uma pista de risco: Baixo, Médio ou Alto."

### 2.2 Como está por dentro, em linguagem simples

> "Por trás, tem uma Árvore de Decisão em Python — pensem nela como um fluxograma de perguntas tipo 'a idade é maior que X? o número de internações é maior que Y?' até chegar numa resposta. A gente também plugou uma IA generativa (Gemini) pra gerar um textinho explicando o resultado, e guardamos tudo isso num banco MySQL, com uma API que eu escrevi em Flask.
>
> A parte que dei mais atenção foi deixar isso **auditável**: cada caso que a gente classifica fica salvo com a explicação da IA e, se alguém revisar aquilo depois, o parecer da revisão também fica junto. Então não é só 'a IA falou e pronto' — dá pra rastrear tudo."

### 2.3 Como testar agora (passo a passo para os colegas)

> "Quem quiser testar: acessem **`http://204.168.165.21:8503`** de qualquer celular ou computador, não precisa estar na minha rede nem eu estar com o notebook ligado — está hospedado num servidor próprio, 24 horas no ar.
>
> Vai pedir um usuário e senha — é só uma proteção simples pra não ficar totalmente aberto, me perguntem direto que eu passo.
>
> Depois de entrar:
> 1. Cliquem em **'Nova avaliação'**, preencham um caso de exemplo (já vem um preenchido, só clicar em 'Avaliar risco e salvar').
> 2. Olhem o resultado: risco, percentual e o texto explicativo gerado pela IA.
> 3. Desçam até **'Explorador de Resultados'** e abram o caso que vocês acabaram de criar — dá pra ver tudo o que ficou salvo.
> 4. Se quiserem brincar de 'revisor', tem uma aba de **'Revisão Humana'** onde dá pra cadastrar um usuário fictício e dar um parecer sobre a classificação."

### 2.4 Fechamento / convite

> "É isso — o foco não foi só treinar um modelinho e mostrar um notebook no Colab, foi mostrar um sistema de verdade, no ar, que qualquer um valida sem depender de mim. Testem à vontade, e se acharem algum bug me chamem que eu arrumo antes da entrega final!"

---

## 3. Dicas rápidas de apresentação

- **Ensaie com cronômetro.** Para a banca, 7–9 minutos de fala soa bem; para colegas, pode ser mais solto e aceitar interrupções/perguntas no meio.
- **Tenha a aba anônima já aberta** antes de começar, para não perder tempo digitando o endereço ao vivo — evita silêncio morto na apresentação.
- **Decore o usuário/senha** (ou deixe anotado fora da tela, nunca mostre a senha digitando-a visível na tela para a banca — digite e, se possível, mostre o campo mascarado).
- **Se o login der problema ao vivo**, não entre em pânico: mencione que o serviço roda via `systemd` no servidor e é independente do seu notebook — é só continuar explicando a arquitetura enquanto resolve, ou use um print de apoio como plano B.
- **Encerre sempre reforçando o limite ético**: dados sintéticos, não é ferramenta de decisão clínica — isso demonstra maturidade para a banca, não fraqueza do projeto.
