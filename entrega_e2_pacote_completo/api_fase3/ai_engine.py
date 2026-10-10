# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Motor de IA em nuvem — Integração com Gemini API (Google GenAI / AI Studio)

Decisão de arquitetura (ver src/modelo.py para o porquê):
  O Gemini NÃO decide o risco de readmissão. A Árvore de Decisão
  (src/modelo.py) já decidiu isso antes de este módulo ser chamado.
  Aqui o Gemini roda EM PARALELO só para:
    1) escrever uma explicação em linguagem natural sobre a decisão
       já tomada pela árvore, e
    2) opcionalmente registrar sua própria "segunda opinião" de risco,
       guardada apenas como enriquecimento em `explicacao.texto` —
       nunca sobrescreve `classificacao.risco_readmissao`.

Se a chamada ao Gemini falhar (sem chave configurada, erro de rede, etc.),
o pipeline não deve quebrar: cai num texto de RESERVA gerado localmente a
partir dos fatores já calculados pela árvore, e marca origem='RESERVA'.
"""

import time

try:
    # SDK atual do Google ("Google GenAI SDK", pacote google-genai).
    # O pacote antigo `google-generativeai` (import google.generativeai)
    # foi descontinuado pela Google — ver aviso de depreciação no próprio
    # pacote — por isso usamos aqui o substituto oficial.
    from google import genai
    _GENAI_DISPONIVEL = True
except ImportError:
    _GENAI_DISPONIVEL = False

from config import Config

VERSAO_PROMPT = 'v2.0'
MAX_TENTATIVAS = 2


class AIEngine:
    """Motor de enriquecimento via Gemini (explicação + segunda opinião)."""

    def __init__(self, config=None):
        self.config = config or Config()
        self.api_key = self.config.GEMINI_API_KEY
        self._pronto = False

        if _GENAI_DISPONIVEL and self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
                self._pronto = True
            except Exception:
                self._pronto = False

    def processar_classificacao(self, dados_paciente, resultado_arvore):
        """
        Gera a explicação/segunda opinião do Gemini sobre uma classificação
        que a Árvore de Decisão JÁ TOMOU.

        Args:
            dados_paciente (dict): idade, diagnostico_principal,
                internacoes_anteriores_12_meses (dados de entrada)
            resultado_arvore (dict): saída de ModeloIA.classificar_risco()
                (status, risco, probabilidade) — a decisão oficial

        Returns:
            dict pronto para persistir na tabela `explicacao`:
                {status, origem, texto, modelo_llm, versao_prompt,
                 latencia_ms, tentativas, detalhe_falha}
        """
        inicio = time.time()

        if resultado_arvore.get('status') != 'OK':
            return {
                'status': 'FORA_DO_CONTRATO',
                'origem': 'RESERVA',
                'texto': 'Sem explicação: a Árvore de Decisão não classificou este caso (dados inválidos).',
                'modelo_llm': None,
                'versao_prompt': VERSAO_PROMPT,
                'latencia_ms': 0,
                'tentativas': 0,
                'detalhe_falha': resultado_arvore.get('motivos'),
            }

        if not self._pronto:
            return self._resposta_reserva(
                dados_paciente, resultado_arvore, inicio, tentativas=0,
                motivo='GEMINI_API_KEY não configurada ou SDK indisponível',
            )

        prompt = self._construir_prompt(dados_paciente, resultado_arvore)

        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                response = self._client.models.generate_content(
                    model=self.config.LLM_MODEL,
                    contents=prompt,
                )
                latencia_ms = int((time.time() - inicio) * 1000)
                return {
                    'status': 'GERADA',
                    'origem': 'GEMINI',
                    'texto': response.text,
                    'modelo_llm': self.config.LLM_MODEL,
                    'versao_prompt': VERSAO_PROMPT,
                    'latencia_ms': latencia_ms,
                    'tentativas': tentativa,
                    'detalhe_falha': None,
                }
            except Exception as e:
                ultimo_erro = str(e)
                continue

        return self._resposta_reserva(
            dados_paciente, resultado_arvore, inicio, tentativas=MAX_TENTATIVAS,
            motivo=ultimo_erro,
        )

    def _construir_prompt(self, dados_paciente, resultado_arvore):
        """Prompt pede explicação sobre uma decisão JÁ TOMADA, não uma nova classificação."""
        prompt = f"""
        Você é um assistente de IA especializado em saúde e readmissão hospitalar.

        A Árvore de Decisão do sistema JÁ CLASSIFICOU o risco de readmissão
        deste paciente. Sua tarefa NÃO é reclassificar — é explicar essa
        decisão em linguagem natural para a equipe clínica, e opcionalmente
        oferecer sua própria leitura como segunda opinião (deixando claro
        que é apenas uma segunda opinião, não a decisão oficial).

        DADOS DO PACIENTE:
        - Idade: {dados_paciente.get('idade', 'N/A')} anos
        - Diagnóstico Principal: {dados_paciente.get('diagnostico_principal', 'N/A')}
        - Internações nos últimos 12 meses: {dados_paciente.get('internacoes_anteriores_12_meses', 0)}

        DECISÃO OFICIAL DA ÁRVORE DE DECISÃO (não deve ser contradita, só explicada):
        - Risco: {resultado_arvore.get('risco')}
        - Probabilidade estimada: {resultado_arvore.get('probabilidade')}

        TAREFAS:
        1. Explicar, em linguagem simples, por que esse risco faz sentido clinicamente
        2. Listar recomendações clínicas práticas
        3. (Opcional) Registrar sua segunda opinião sobre o risco, rotulada
           claramente como "segunda_opiniao" e não como decisão final

        Responda em formato JSON com a seguinte estrutura:
        {{
            "explicacao": "texto explicando a decisão da árvore",
            "recomendacoes": ["rec1", "rec2"],
            "segunda_opiniao": {{"risco": "BAIXO|MEDIO|ALTO", "justificativa": "..."}}
        }}
        """
        return prompt.strip()

    def _resposta_reserva(self, dados_paciente, resultado_arvore, inicio, tentativas, motivo):
        """Fallback local quando o Gemini não está disponível: usa os próprios
        fatores já calculados pela árvore para montar um texto determinístico,
        para que o pipeline nunca fique sem explicação persistida."""
        risco = resultado_arvore.get('risco')
        probabilidade = resultado_arvore.get('probabilidade')
        texto = (
            f"[RESERVA — Gemini indisponível: {motivo}] "
            f"A Árvore de Decisão classificou o risco de readmissão como {risco} "
            f"(probabilidade estimada {probabilidade}), considerando idade "
            f"{dados_paciente.get('idade')}, diagnóstico "
            f"{dados_paciente.get('diagnostico_principal')} e "
            f"{dados_paciente.get('internacoes_anteriores_12_meses')} internação(ões) "
            f"anterior(es) em 12 meses."
        )
        return {
            'status': 'INDISPONIVEL',
            'origem': 'RESERVA',
            'texto': texto,
            'modelo_llm': None,
            'versao_prompt': VERSAO_PROMPT,
            'latencia_ms': int((time.time() - inicio) * 1000),
            'tentativas': tentativas,
            'detalhe_falha': motivo,
        }


def get_ai_engine(config=None):
    """Obter instância de AIEngine"""
    return AIEngine(config)
