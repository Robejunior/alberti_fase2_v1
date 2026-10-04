# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Gerenciador do Modelo de Machine Learning
"""

import json
from sklearn.tree import DecisionTreeClassifier
import numpy as np

class ModeloIA:
    """Classe para gerenciar o modelo de IA"""

    def __init__(self):
        self.modelo = None
        self.metricas = None
        self.limites = {
            'baixo': 0.333,
            'alto': 0.667
        }

    def classificar_risco(self, idade, diagnostico_principal, internacoes_anteriores_12_meses):
        """
        Classificar risco de readmissão

        Args:
            idade: Idade do paciente (int)
            diagnostico_principal: Código CID-10 (str)
            internacoes_anteriores_12_meses: Número de internações (int)

        Returns:
            dict com classificação e probabilidade
        """

        # Validar entrada
        if not self._validar_entrada(idade, diagnostico_principal, internacoes_anteriores_12_meses):
            return {
                'status': 'ERRO_VALIDACAO',
                'risco': None,
                'probabilidade': None,
                'motivos': ['Dados inválidos ou incompletos']
            }

        try:
            # Aqui você colocaria a lógica real do modelo
            # Por agora, usamos uma simulação baseada em heurísticas

            probabilidade = self._calcular_probabilidade(
                idade,
                diagnostico_principal,
                internacoes_anteriores_12_meses
            )

            risco = self._mapear_para_faixa(probabilidade)

            return {
                'status': 'OK',
                'risco': risco,
                'probabilidade': probabilidade,
                'motivos': None
            }

        except Exception as e:
            return {
                'status': 'ERRO_VALIDACAO',
                'risco': None,
                'probabilidade': None,
                'motivos': [f'Erro ao processar: {str(e)}']
            }

    def _validar_entrada(self, idade, diagnostico, internacoes):
        """Validar dados de entrada"""
        if not isinstance(idade, int) or idade < 60:
            return False
        if not isinstance(diagnostico, str) or len(diagnostico) == 0:
            return False
        if not isinstance(internacoes, int) or internacoes < 0:
            return False
        return True

    def _calcular_probabilidade(self, idade, diagnostico, internacoes):
        """
        Calcular probabilidade de readmissão
        Heurística baseada em: idade, internações anteriores e diagnóstico
        """

        # Pesos para cada fator
        peso_idade = (idade - 60) * 0.002  # Aumenta com idade
        peso_internacoes = internacoes * 0.15  # Muito importante
        peso_diagnostico = self._obter_peso_diagnostico(diagnostico)

        # Calcular probabilidade
        probabilidade = min(
            0.95,
            max(0.05, peso_idade + peso_internacoes + peso_diagnostico)
        )

        return round(probabilidade, 5)

    def _obter_peso_diagnostico(self, diagnostico):
        """Obter peso de risco do diagnóstico"""
        pesos = {
            'I50.0': 0.40,  # Insuficiência cardíaca
            'I10': 0.20,    # Hipertensão
            'E11': 0.25,    # Diabetes
            'J18': 0.30,    # Pneumonia
            'R51': 0.10,    # Cefaleia
        }
        return pesos.get(diagnostico, 0.15)  # Padrão

    def _mapear_para_faixa(self, probabilidade):
        """Mapear probabilidade para faixa de risco"""
        if probabilidade < self.limites['baixo']:
            return 'BAIXO'
        elif probabilidade < self.limites['alto']:
            return 'MEDIO'
        else:
            return 'ALTO'

    def obter_fatores_relevantes(self, idade, diagnostico, internacoes, probabilidade):
        """Obter fatores relevantes que influenciaram a classificação"""
        fatores = []

        if internacoes >= 3:
            fatores.append({
                'fator': 'internacoes_anteriores',
                'valor': internacoes,
                'importancia': 0.71,
                'descricao': f'{internacoes} internações nos últimos 12 meses'
            })

        if idade >= 75:
            fatores.append({
                'fator': 'idade_avancada',
                'valor': idade,
                'importancia': 0.24,
                'descricao': f'Idade de {idade} anos'
            })

        peso_diag = self._obter_peso_diagnostico(diagnostico)
        if peso_diag >= 0.25:
            fatores.append({
                'fator': 'diagnostico_risco',
                'valor': diagnostico,
                'importancia': 0.04,
                'descricao': f'Diagnóstico principal: {diagnostico}'
            })

        return fatores
