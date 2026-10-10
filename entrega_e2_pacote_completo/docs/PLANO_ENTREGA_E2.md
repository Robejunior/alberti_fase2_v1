# Plano de entrega E2 — 15/10/2026
Planejamento de 30 horas, não registro de horas já realizadas. Peso: 25%.
## Escopo
Comprovar dado sintético → Python → Gemini real → MySQL → SELECT de conferência.
A baseline é de integração. Resumo produzido por LLM não é modelo preditivo validado.
## Plano
| Atividade | Horas previstas | Critério de aceite |
|---|---:|---|
| Conferir requisitos e organizar artefatos | 3 | Estrutura padronizada e inventário |
| Configuração segura e massa sintética | 3 | Sem segredos e sem PII |
| SDK oficial e contrato de resposta | 6 | Resposta real recebida e validada |
| MySQL e pipeline integrado | 6 | Commit e releitura idêntica |
| Testes e evidências | 4 | Relatório E2E real e consultas |
| Revisar documento anterior / ABNT | 5 | Modelo e correções do professor atendidos |
| Publicar no repositório e ensaiar | 3 | Histórico e link oficial conferidos |
| Total | 30 | |
## Situação em 07/10/2026
- Estrutura e implementação: preparadas nesta pasta.
- Execução real Gemini/MySQL: pendente. Não considerar testes simulados como prova E2E.
- Versionamento: repositório .git existe na pasta superior; histórico não conferido por restrição de ownership. Nenhuma alteração Git efetuada.
- ABNT/Fase 1: pendente documento entregue, feedback e padrão da última aula.
- Publicação Drive/Colab: pendente confirmar destino oficial e acesso da equipe.
## Auditoria da versão anterior
src/main.py original salvava ALTO/0.75 constantes e modelo_id=1, sem persistir o texto Gemini.
src/ai_engine.py usava google.generativeai; requirements original não listava SDK Gemini.
init.sql na raiz era diretório, não script SQL.
Afirmações anteriores de 100% de conformidade não são evidência de execução.
## Checklist final
- [ ] Configurar .env local e modelo disponível no AI Studio.
- [ ] Instalar dependências e registrar versões efetivas.
- [ ] Executar pipeline real com os 3 casos.
- [ ] Conferir SELECT no MySQL e guardar relatório em docs/evidencias.
- [ ] Corrigir documento Fase 1 no padrão do professor.
- [ ] Conferir commits e publicar pasta como raiz do repositório oficial.
- [ ] Ensaiar em outra máquina.

Documentos Fase 1 recebidos: veja docs/REVISAO_FASE1.md. A revisão final ABNT ainda exige conferência visual e o padrão da última aula.
