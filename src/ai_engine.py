# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Motor IA - Integração com Gemini API
"""

import google.generativeai as genai
from config import Config

class AIEngine:
    """Motor de IA que integra com Gemini"""

    def __init__(self, config=None):
        self.config = config or Config()
        self.api_key = self.config.GEMINI_API_KEY

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não configurada em .env")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.config.LLM_MODEL)

    def processar_classificacao(self, dados_paciente):
        """
        Processar dados do paciente através de Gemini

        Args:
            dados_paciente (dict): Dados estruturados do paciente
                - idade: int
                - diagnostico_principal: str
                - internacoes_anteriores_12_meses: int

        Returns:
            dict: Resposta estruturada de Gemini
        """
        try:
            prompt = self._construir_prompt(dados_paciente)

            response = self.model.generate_content(prompt)

            resultado = {
                'sucesso': True,
                'resposta_gemini': response.text,
                'dados_entrada': dados_paciente,
                'modelo': self.config.LLM_MODEL
            }

            return resultado

        except Exception as e:
            return {
                'sucesso': False,
                'erro': str(e),
                'dados_entrada': dados_paciente
            }

    def _construir_prompt(self, dados_paciente):
        """Construir prompt estruturado para Gemini"""

        prompt = f"""
        Você é um assistente de IA especializado em saúde e readmissão hospitalar.

        Analise os seguintes dados do paciente e forneça uma avaliação de risco de readmissão:

        DADOS DO PACIENTE:
        - Idade: {dados_paciente.get('idade', 'N/A')} anos
        - Diagnóstico Principal: {dados_paciente.get('diagnostico_principal', 'N/A')}
        - Internações nos últimos 12 meses: {dados_paciente.get('internacoes_anteriores_12_meses', 0)}

        TAREFAS:
        1. Classificar o risco de readmissão (BAIXO, MÉDIO ou ALTO)
        2. Listar os principais fatores de risco identificados
        3. Fornecer recomendações clínicas
        4. Estimar probabilidade de readmissão (0-100%)

        Responda em formato JSON com a seguinte estrutura:
        {{
            "risco": "BAIXO|MÉDIO|ALTO",
            "probabilidade": 0-100,
            "fatores_risco": ["fator1", "fator2"],
            "recomendacoes": ["rec1", "rec2"],
            "justificativa": "explicação breve"
        }}
        """

        return prompt.strip()

def get_ai_engine(config=None):
    """Obter instância única de AIEngine"""
    return AIEngine(config)
