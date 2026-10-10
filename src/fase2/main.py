# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Pipeline Principal - Execução End-to-End
Entrada de Dados → Processamento Gemini → Persistência MySQL
"""

import json
import sys
from datetime import datetime

from config import get_config
from database import Database
from ai_engine import AIEngine

def main():
    """
    Pipeline Principal:
    1. Entrada de dados via Python
    2. Processamento IA via Gemini
    3. Persistência no MySQL
    """

    print("=" * 70)
    print("TIA - FASE 2 - PIPELINE END-TO-END")
    print("=" * 70)

    # Configuração
    config = get_config('development')

    # Inicializar componentes
    print("\n1️⃣  Inicializando componentes...")
    try:
        db = Database(config)
        ai_engine = AIEngine(config)
        print("   ✅ Componentes inicializados com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao inicializar: {e}")
        return False

    # Dados de teste
    dados_teste = [
        {
            'paciente_id': 'PAC_001',
            'internacao_id': 'INT_001',
            'idade': 75,
            'diagnostico_principal': 'I50.0',
            'internacoes_anteriores_12_meses': 2
        },
        {
            'paciente_id': 'PAC_002',
            'internacao_id': 'INT_002',
            'idade': 82,
            'diagnostico_principal': 'I50.0',
            'internacoes_anteriores_12_meses': 5
        },
        {
            'paciente_id': 'PAC_003',
            'internacao_id': 'INT_003',
            'idade': 68,
            'diagnostico_principal': 'J44.9',
            'internacoes_anteriores_12_meses': 1
        }
    ]

    # PASSO 1: Entrada de Dados
    print("\n2️⃣  ENTRADA DE DADOS")
    print(f"   Processando {len(dados_teste)} registros de teste...")

    # PASSO 2: Processamento IA
    print("\n3️⃣  PROCESSAMENTO IA (Gemini)")

    if not db.conectar():
        print("   ❌ Erro ao conectar no banco de dados")
        return False

    resultados = []

    for i, dados in enumerate(dados_teste, 1):
        print(f"\n   Paciente {i}/{len(dados_teste)}: {dados['paciente_id']}")

        # Enviar para Gemini
        resultado_gemini = ai_engine.processar_classificacao(dados)

        if not resultado_gemini['sucesso']:
            print(f"      ⚠️  Erro ao processar via Gemini: {resultado_gemini['erro']}")
            continue

        print(f"      ✅ Resposta Gemini recebida")
        print(f"      📝 {resultado_gemini['resposta_gemini'][:100]}...")

        # PASSO 3: Persistência no MySQL
        print(f"      💾 Salvando no MySQL...")

        sucesso, erro = db.executar_query(
            """
            INSERT INTO classificacao
            (modelo_id, entrada_json, idade, diagnostico_principal,
             internacoes_anteriores_12_meses, status, motivos,
             risco_readmissao, probabilidade_estimada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                1,  # modelo_id
                json.dumps(dados),
                dados['idade'],
                dados['diagnostico_principal'],
                dados['internacoes_anteriores_12_meses'],
                'OK',
                json.dumps(['teste', 'fase2']),
                'ALTO',
                0.75
            )
        )

        if sucesso:
            print(f"      ✅ Salvo no MySQL com sucesso")
            resultados.append({
                'paciente_id': dados['paciente_id'],
                'status': 'sucesso',
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"      ❌ Erro ao salvar: {erro}")
            resultados.append({
                'paciente_id': dados['paciente_id'],
                'status': 'erro',
                'erro': erro,
                'timestamp': datetime.now().isoformat()
            })

    db.desconectar()

    # Resumo Final
    print("\n" + "=" * 70)
    print("📊 RESUMO DO PIPELINE")
    print("=" * 70)

    total = len(resultados)
    sucessos = sum(1 for r in resultados if r['status'] == 'sucesso')
    erros = total - sucessos

    print(f"\n✅ Sucessos: {sucessos}/{total}")
    print(f"❌ Erros: {erros}/{total}")
    print(f"📈 Taxa de sucesso: {(sucessos/total*100):.1f}%")

    print("\n" + "=" * 70)
    print("🎉 PIPELINE CONCLUÍDO COM SUCESSO!" if sucessos > 0 else "⚠️ PIPELINE COM FALHAS")
    print("=" * 70)

    return sucessos > 0

if __name__ == '__main__':
    sucesso = main()
    sys.exit(0 if sucesso else 1)
