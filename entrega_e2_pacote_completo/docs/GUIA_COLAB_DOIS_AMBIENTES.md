# Colab: demonstração local e banca
Preparado em 07/10/2026. Configurações geradas; conexão real Colab/Gemini/MySQL ainda não testada.
## Hoje: computador pessoal
1. Mantenha o MySQL disponível. Não pare serviços ou altere portas para executar este notebook.
2. Na pasta entrega_e2, crie .env a partir de .env.example somente se não existir; configure localmente o usuário do banco tia_e2, senha, chave e modelo Gemini.
3. PowerShell:
```powershell
cd C:\Users\ralbertijuni\Desktop\tia_api\entrega_e2
.\iniciar_colab_local.ps1
```
Se a política institucional bloquear scripts, não a altere sem autorização. Execute os comandos do script manualmente no PowerShell permitido.
4. Acesse https://colab.research.google.com e envie APRESENTACAO_COLAB.ipynb por Arquivo > Fazer upload de notebook.
5. No menu Conectar escolha conexão ao ambiente de execução local. Cole a URL com token exibida pelo Jupyter. Nunca publique essa URL.
6. Escolha MODO = "LOCAL" e execute célula por célula.
O código é executado pela interface Colab, no seu computador. Confirme com o professor se execução local atende à demonstração de hoje.
## Banca: Colab na nuvem + MySQL remoto
1. Suba o pacote sem .env nem ambientes virtuais para Meu Drive/TIA/entrega_e2. Envie só src, data, docs, tests, certificados, notebook e requirements.txt.
2. Providencie MySQL remoto autorizado com banco tia_e2, usuário de escopo limitado e TLS, sem contratar serviço até aprovar custos.
3. Obtenha host, porta, usuário, senha e certificado CA do serviço. A conectividade/firewall deve permitir o runtime Colab; IP de saída pode mudar entre sessões.
4. Salve a CA pública em certificados/ca.pem. Cadastre os sete Secrets listados no notebook, autorizando seu acesso.
5. No Colab conectado ao runtime Google, escolha NUVEM e execute na ordem.
6. Faça o ensaio completo antes da banca, usando a rede e o equipamento do curso. Somente o navegador é necessário no computador do curso se esse cenário funcionar.
Não foi provisionado banco remoto; o notebook está preparado, não validado nesse destino.
## Banca mantendo MySQL em casa: alternativa condicionada
É possível somente com caminho privado autorizado (VPN ou túnel SSH). O computador precisa ficar ligado, com internet e MySQL disponível.
Um túnel SSH requer um endpoint SSH alcançável/autorizado; abrir a porta MySQL 3306 no roteador não é a solução proposta.
A rede do curso pode bloquear VPN/SSH ou impedir instalação. Precisamos confirmar essas condições antes de fornecer configuração operacional.
Se a execução permanecer no PC pessoal, a interface Colab na faculdade precisa alcançar o runtime por encaminhamento SSH privado, conforme documentação oficial. LOCAL, nesse caso, descreve o runtime remoto no PC pessoal, não o PC do curso.
Não se deve compartilhar o Jupyter publicamente nem desativar autenticação.
## Evidência e contingência
Guarde notebook executado, relatório JSON e SELECT dos UUIDs. Um vídeo de execução anterior serve como evidência complementar, não substitui execução ao vivo exigida.
Três respostas confirmadas não significam modelo preditivo clinicamente validado.
## Fonte
https://research.google.com/colaboratory/local-runtimes.html
