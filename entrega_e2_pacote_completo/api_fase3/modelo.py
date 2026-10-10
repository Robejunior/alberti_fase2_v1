# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Modelo de IA local — Árvore de Decisão (scikit-learn)

Decisão de arquitetura (aprovada pelo grupo na Fase 1, mantida na Fase 2):
  - A ÁRVORE DE DECISÃO é quem decide o risco de readmissão oficial,
    treinada sobre a coorte sintética documentada (sem rótulo real
    disponível na amostra do SIH/SUS — ver src/gerar_coorte_sintetica.py).
  - O Gemini (src/ai_engine.py) NÃO substitui esta decisão: ele roda em
    paralelo só para gerar uma explicação em linguagem natural / segunda
    opinião, registrada separadamente na tabela `explicacao`.

Limites de classificação (conforme docs/referencias/TIA_Fase1_Requisitos_
Arquitetura_Oliveira.docx, seção 4.3 "Faixas de classificação", e RF04):
  BAIXO se p < 0,30; MEDIO se 0,30 <= p < 0,60; ALTO se p >= 0,60.
  O próprio documento registra que esses limites são provisórios e
  demonstrativos — por isso continuam parametrizados (self.limites) em
  vez de fixos no código, conforme pedido no documento ("parâmetros
  configuráveis e versionados").
"""

import json
import os

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score

CAMINHO_COORTE_PADRAO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'data', 'coorte_treino_sintetica.json'
)

DIAGNOSTICOS_CONHECIDOS = ['I50.0', 'I10', 'E11', 'J18', 'R51']

HIPERPARAMETROS_PADRAO = {
    'max_depth': 4,
    'min_samples_leaf': 5,
    'random_state': 42,
}


class ModeloIA:
    """Árvore de Decisão treinada sobre a coorte sintética."""

    VERSAO = 'v2.0.0'
    TIPO_COORTE = 'SINTETICA'

    def __init__(self, caminho_coorte=None, hiperparametros=None):
        self.limites = {
            'baixo': 0.30,
            'alto': 0.60,
        }
        self.hiperparametros = hiperparametros or dict(HIPERPARAMETROS_PADRAO)
        self.caminho_coorte = caminho_coorte or CAMINHO_COORTE_PADRAO
        self.modelo = None
        self.metricas = None
        self._treinar()

    # ------------------------------------------------------------------
    # Treino
    # ------------------------------------------------------------------
    def _carregar_coorte(self):
        if not os.path.exists(self.caminho_coorte):
            # Garante que o pipeline nunca quebra por falta do arquivo:
            # gera a coorte sintética na hora, com a mesma semente padrão.
            from gerar_coorte_sintetica import salvar_coorte
            salvar_coorte(self.caminho_coorte)

        with open(self.caminho_coorte, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _vetorizar(self, idade, cid10, internacoes):
        """Transforma as features brutas em vetor numérico (one-hot do CID-10)."""
        vetor = [idade, internacoes]
        vetor += [1 if cid10 == d else 0 for d in DIAGNOSTICOS_CONHECIDOS]
        return vetor

    def _treinar(self):
        casos = self._carregar_coorte()

        treino = [c for c in casos if c['particao'] == 'TREINO']
        teste = [c for c in casos if c['particao'] == 'TESTE']

        X_treino = [self._vetorizar(c['idade'], c['cid10'], c['internacoes_anteriores_12_meses']) for c in treino]
        y_treino = [c['readmitido_30d'] for c in treino]

        self.modelo = DecisionTreeClassifier(**self.hiperparametros)
        self.modelo.fit(X_treino, y_treino)

        self.metricas = self._avaliar(teste)
        if self.metricas and 'n_treino' in self.metricas:
            self.metricas['n_treino'] = len(treino)

    def _avaliar(self, teste):
        if not teste:
            return {'aviso': 'conjunto de teste vazio'}

        X_teste = [self._vetorizar(c['idade'], c['cid10'], c['internacoes_anteriores_12_meses']) for c in teste]
        y_teste = [c['readmitido_30d'] for c in teste]
        y_pred = self.modelo.predict(X_teste)
        y_proba = self.modelo.predict_proba(X_teste)[:, 1]

        metricas = {
            'acuracia': round(accuracy_score(y_teste, y_pred), 4),
            'precisao': round(precision_score(y_teste, y_pred, zero_division=0), 4),
            'recall': round(recall_score(y_teste, y_pred, zero_division=0), 4),
            'n_teste': len(teste),
            'n_treino': None,  # preenchido pelo chamador, se quiser
        }

        # roc_auc exige as duas classes presentes no y_teste
        if len(set(y_teste)) == 2:
            metricas['roc_auc'] = round(roc_auc_score(y_teste, y_proba), 4)
        else:
            metricas['roc_auc'] = None

        return metricas

    # ------------------------------------------------------------------
    # Inferência
    # ------------------------------------------------------------------
    def classificar_risco(self, idade, diagnostico_principal, internacoes_anteriores_12_meses):
        """
        Classificar risco de readmissão usando a Árvore de Decisão treinada.

        Returns:
            dict com status, risco, probabilidade e motivos (em caso de erro)
        """
        # RF02 (Fase 1): paciente inelegível (idade < 60) é DADOS_INSUFICIENTES,
        # não ERRO_VALIDACAO — não é um erro de formato, é fora do público-alvo.
        if isinstance(idade, int) and idade < 60:
            return {
                'status': 'DADOS_INSUFICIENTES',
                'risco': None,
                'probabilidade': None,
                'motivos': ['Paciente inelegível: idade abaixo de 60 anos'],
            }

        if not self._validar_entrada(idade, diagnostico_principal, internacoes_anteriores_12_meses):
            return {
                'status': 'ERRO_VALIDACAO',
                'risco': None,
                'probabilidade': None,
                'motivos': ['Dados inválidos ou incompletos'],
            }

        try:
            vetor = [self._vetorizar(idade, diagnostico_principal, internacoes_anteriores_12_meses)]
            probabilidade = float(self.modelo.predict_proba(vetor)[0][1])
            probabilidade = round(probabilidade, 5)
            risco = self._mapear_para_faixa(probabilidade)

            return {
                'status': 'OK',
                'risco': risco,
                'probabilidade': probabilidade,
                'motivos': None,
            }
        except Exception as e:
            return {
                'status': 'ERRO_VALIDACAO',
                'risco': None,
                'probabilidade': None,
                'motivos': [f'Erro ao processar: {str(e)}'],
            }

    def _validar_entrada(self, idade, diagnostico, internacoes):
        if not isinstance(idade, int) or idade < 60:
            return False
        if not isinstance(diagnostico, str) or len(diagnostico) == 0:
            return False
        if not isinstance(internacoes, int) or internacoes < 0:
            return False
        return True

    def _mapear_para_faixa(self, probabilidade):
        if probabilidade < self.limites['baixo']:
            return 'BAIXO'
        elif probabilidade < self.limites['alto']:
            return 'MEDIO'
        else:
            return 'ALTO'

    def obter_fatores_relevantes(self, idade, diagnostico, internacoes, probabilidade):
        """Fatores relevantes com base na importância real aprendida pela árvore."""
        nomes_features = ['idade', 'internacoes_anteriores_12_meses'] + \
            [f'diagnostico_{d}' for d in DIAGNOSTICOS_CONHECIDOS]
        importancias = dict(zip(nomes_features, self.modelo.feature_importances_))

        fatores = []

        if internacoes >= 3:
            fatores.append({
                'fator': 'internacoes_anteriores',
                'valor': internacoes,
                'importancia': round(float(importancias.get('internacoes_anteriores_12_meses', 0)), 4),
                'descricao': f'{internacoes} internações nos últimos 12 meses',
            })

        if idade >= 75:
            fatores.append({
                'fator': 'idade_avancada',
                'valor': idade,
                'importancia': round(float(importancias.get('idade', 0)), 4),
                'descricao': f'Idade de {idade} anos',
            })

        chave_diag = f'diagnostico_{diagnostico}'
        if chave_diag in importancias and importancias[chave_diag] > 0:
            fatores.append({
                'fator': 'diagnostico_risco',
                'valor': diagnostico,
                'importancia': round(float(importancias[chave_diag]), 4),
                'descricao': f'Diagnóstico principal: {diagnostico}',
            })

        return fatores

    # ------------------------------------------------------------------
    # Metadados (para persistir a versão ativa na tabela `modelo`)
    # ------------------------------------------------------------------
    def metadados_para_persistencia(self):
        return {
            'versao': self.VERSAO,
            'algoritmo': 'DecisionTreeClassifier',
            'tipo_coorte': self.TIPO_COORTE,
            'versao_preprocessamento': 'v1.0',
            'hiperparametros': self.hiperparametros,
            'metricas': self.metricas,
            'limite_baixo': self.limites['baixo'],
            'limite_alto': self.limites['alto'],
        }


# Singleton simples: treina uma vez por processo
_modelo_instance = None


def get_modelo():
    global _modelo_instance
    if _modelo_instance is None:
        _modelo_instance = ModeloIA()
    return _modelo_instance
