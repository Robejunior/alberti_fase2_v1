# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Geração da coorte sintética de treino/teste da Árvore de Decisão

Por que coorte sintética?
--------------------------
Na Fase 1 foi documentado que a amostra do SIH/SUS auditada não tem o
rótulo "readmitido em 1 a 30 dias pela mesma causa" diretamente disponível
(decisão aprovada: treinar sobre coorte sintética documentada, por falta
de rótulo na amostra real). Este script gera essa coorte de forma
determinística (semente fixa) e TOTALMENTE SINTÉTICA — nenhum dado de
paciente real é usado ou necessário para rodar este script.

A regra de geração é simples e documentada (não é um modelo caixa-preta):
  - idade: 60 a 95 anos, uniforme
  - diagnóstico principal: sorteado entre os 5 CID-10 já usados no
    projeto (README.md / src/modelo.py), cada um com o peso de risco
    já declarado no catálogo `diagnostico`
  - internações anteriores em 12 meses: Poisson(lambda=1.2), truncado em 0-8
  - probabilidade "verdadeira" de readmissão em 30 dias:
        p = peso_diagnostico + 0.002 * (idade - 60) + 0.12 * internacoes
    (mesmos fatores clínicos citados no projeto), mais ruído aleatório
    pequeno para não deixar as classes perfeitamente separáveis
  - rótulo readmitido_30d: Bernoulli(p)

Saída: data/coorte_treino_sintetica.json com os campos da tabela
`coorte_treino` do schema (database/schema.sql), já particionados em
TREINO (80%) e TESTE (20%).
"""

import json
import os
import random

SEMENTE = 42
N_CASOS = 400
PARTICAO_TESTE = 0.2

PESO_DIAGNOSTICO = {
    'I50.0': 0.40,  # Insuficiência cardíaca
    'I10': 0.20,    # Hipertensão essencial
    'E11': 0.25,    # Diabetes mellitus tipo 2
    'J18': 0.30,    # Pneumonia
    'R51': 0.10,    # Cefaleia
}

DIAGNOSTICOS = list(PESO_DIAGNOSTICO.keys())


def _poisson_truncado(rng, lam, minimo, maximo):
    """Amostra de Poisson sem depender de numpy, truncada em [minimo, maximo]."""
    l = 2.718281828459045 ** (-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= l:
            break
    valor = k - 1
    return max(minimo, min(maximo, valor))


def gerar_coorte(n_casos=N_CASOS, semente=SEMENTE):
    rng = random.Random(semente)
    casos = []

    for _ in range(n_casos):
        idade = rng.randint(60, 95)
        cid10 = rng.choice(DIAGNOSTICOS)
        internacoes = _poisson_truncado(rng, 1.2, 0, 8)

        peso_diag = PESO_DIAGNOSTICO[cid10]
        probabilidade_real = (
            peso_diag
            + 0.002 * (idade - 60)
            + 0.12 * internacoes
        )
        # ruído para não deixar as classes perfeitamente separáveis
        probabilidade_real += rng.uniform(-0.08, 0.08)
        probabilidade_real = max(0.02, min(0.98, probabilidade_real))

        readmitido_30d = 1 if rng.random() < probabilidade_real else 0

        casos.append({
            'origem': 'SINTETICA',
            'semente': semente,
            'particao': None,  # definido depois do embaralhamento
            'idade': idade,
            'cid10': cid10,
            'internacoes_anteriores_12_meses': internacoes,
            'readmitido_30d': readmitido_30d,
        })

    # particiona em TREINO/TESTE de forma determinística (mesma semente)
    indices = list(range(len(casos)))
    rng.shuffle(indices)
    n_teste = int(len(casos) * PARTICAO_TESTE)
    indices_teste = set(indices[:n_teste])

    for i, caso in enumerate(casos):
        caso['particao'] = 'TESTE' if i in indices_teste else 'TREINO'

    return casos


def salvar_coorte(caminho='data/coorte_treino_sintetica.json'):
    casos = gerar_coorte()
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(casos, f, ensure_ascii=False, indent=2)
    return caminho, len(casos)


if __name__ == '__main__':
    caminho, total = salvar_coorte()
    treino = sum(1 for _ in range(1))  # placeholder, contagem real abaixo
    print(f"Coorte sintética gerada: {total} casos -> {caminho}")
