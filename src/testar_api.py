#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Script de Teste da API REST
"""

import requests
import json

# =====================================================================
# CONFIGURAÇÃO
# =====================================================================

BASE_URL = "http://localhost:5000/api/v1"
TIMEOUT = 5

# =====================================================================
# FUNÇÕES AUXILIARES
# =====================================================================

def fazer_request(metodo, endpoint, dados=None):
    """Fazer request HTTP"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if metodo == 'GET':
            resposta = requests.get(url, timeout=TIMEOUT)
        elif metodo == 'POST':
            resposta = requests.post(url, json=dados, timeout=TIMEOUT)
        else:
            return None

        return resposta.json() if resposta.status_code == 200 else resposta.json()

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não conseguiu conectar à API")
        print(f"   Certifique-se que a API está rodando em {BASE_URL}")
        return None
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None

def imprimir_resultado(teste_nome, resultado):
    """Imprimir resultado do teste"""
    if resultado is None:
        print(f"❌ {teste_nome}: FALHOU")
        return False

    sucesso = resultado.get('sucesso', False)
    if sucesso:
        print(f"✅ {teste_nome}: OK")
        return True
    else:
        print(f"❌ {teste_nome}: ERRO - {resultado.get('erro', 'Desconhecido')}")
        return False

# =====================================================================
# TESTES
# =====================================================================

def test_saude():
    """Teste 1: Health Check"""
    print("\n" + "="*60)
    print("TESTE 1: Health Check")
    print("="*60)

    resultado = fazer_request('GET', '/saude')
    return imprimir_resultado("Health Check", resultado)

def test_info():
    """Teste 2: Informações da API"""
    print("\n" + "="*60)
    print("TESTE 2: Informações da API")
    print("="*60)

    resultado = fazer_request('GET', '/info')
    if imprimir_resultado("Informações", resultado):
        print(f"\n📋 Dados:")
        print(f"   Título: {resultado['dados'].get('titulo')}")
        print(f"   Versão: {resultado['dados'].get('versao')}")
        print(f"   Modelo: {resultado['dados'].get('modelo', {}).get('versao')}")
        return True
    return False

def test_estatisticas():
    """Teste 3: Estatísticas"""
    print("\n" + "="*60)
    print("TESTE 3: Estatísticas")
    print("="*60)

    resultado = fazer_request('GET', '/estatisticas')
    if imprimir_resultado("Estatísticas", resultado):
        dados = resultado['dados']
        print(f"\n📊 Estatísticas:")
        print(f"   Total de classificações: {dados.get('total_classificacoes', 0)}")
        print(f"   Classificações OK: {dados.get('classificacoes_ok', 0)}")
        print(f"   Classificações com erro: {dados.get('classificacoes_erro', 0)}")
        print(f"   Risco BAIXO: {dados.get('risco_baixo', 0)}")
        print(f"   Risco MÉDIO: {dados.get('risco_medio', 0)}")
        print(f"   Risco ALTO: {dados.get('risco_alto', 0)}")
        return True
    return False

def test_validar_entrada():
    """Teste 4: Validação de Entrada"""
    print("\n" + "="*60)
    print("TESTE 4: Validação de Entrada")
    print("="*60)

    payload = {
        "idade": 75,
        "diagnostico_principal": "I50.0",
        "internacoes_anteriores_12_meses": 3
    }

    resultado = fazer_request('POST', '/validar-entrada', payload)
    if imprimir_resultado("Validação", resultado):
        valido = resultado['dados'].get('valido', False)
        print(f"\n✓ Dados válidos: {valido}")
        return True
    return False

def test_validar_entrada_invalida():
    """Teste 5: Validação de Entrada Inválida"""
    print("\n" + "="*60)
    print("TESTE 5: Validação de Entrada Inválida")
    print("="*60)

    payload = {
        "idade": 50,  # Inválido (< 60)
        "diagnostico_principal": "I50.0",
        "internacoes_anteriores_12_meses": 3
    }

    resultado = fazer_request('POST', '/validar-entrada', payload)
    if resultado and not resultado['dados'].get('valido', True):
        print("✅ Validação Inválida: OK (detectou erro como esperado)")
        return True
    else:
        print("❌ Validação Inválida: FALHOU (não detectou erro)")
        return False

def test_classificacao():
    """Teste 6: Classificação Risco"""
    print("\n" + "="*60)
    print("TESTE 6: Classificação de Risco")
    print("="*60)

    payload = {
        "paciente_id": "PAC_TEST_001",
        "internacao_id": "INT_TEST_001",
        "idade": 75,
        "diagnostico_principal": "I50.0",
        "internacoes_anteriores_12_meses": 3
    }

    resultado = fazer_request('POST', '/classificar', payload)
    if imprimir_resultado("Classificação", resultado):
        dados = resultado['dados']
        print(f"\n📊 Resultado:")
        print(f"   ID Classificação: {dados.get('classificacao_id')}")
        print(f"   Status: {dados.get('status')}")
        print(f"   Risco: {dados.get('risco_readmissao')}")
        print(f"   Probabilidade: {dados.get('probabilidade_estimada')*100:.2f}%")
        print(f"   Modelo: {dados.get('modelo_versao')}")

        fatores = dados.get('fatores_relevantes', [])
        if fatores:
            print(f"\n🎯 Fatores Relevantes:")
            for fator in fatores:
                print(f"   - {fator.get('descricao')} (Importância: {fator.get('importancia')*100:.0f}%)")

        return True, dados.get('classificacao_id')
    return False, None

def test_obter_classificacao(classificacao_id):
    """Teste 7: Obter Classificação Específica"""
    if not classificacao_id:
        print("\n" + "="*60)
        print("TESTE 7: Obter Classificação")
        print("="*60)
        print("⚠️  Pulado (ID não disponível)")
        return False

    print("\n" + "="*60)
    print("TESTE 7: Obter Classificação Específica")
    print("="*60)

    resultado = fazer_request('GET', f'/classificacoes/{classificacao_id}')
    return imprimir_resultado("Obter Classificação", resultado)

def test_listar_classificacoes():
    """Teste 8: Listar Classificações"""
    print("\n" + "="*60)
    print("TESTE 8: Listar Classificações")
    print("="*60)

    resultado = fazer_request('GET', '/classificacoes?pagina=0&limite=10')
    if imprimir_resultado("Listar Classificações", resultado):
        dados = resultado['dados']
        print(f"\n📋 Resultado:")
        print(f"   Total: {dados.get('total')}")
        print(f"   Página: {dados.get('pagina')}")
        print(f"   Limite: {dados.get('limite')}")
        print(f"   Registros retornados: {len(dados.get('classificacoes', []))}")
        return True
    return False

# =====================================================================
# MAIN
# =====================================================================

def main():
    """Executar todos os testes"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  TIA - Projeto 10 - Fase 2".center(58) + "║")
    print("║" + "  Suite de Testes da API REST".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")

    resultados = []
    classificacao_id = None

    # Executar testes
    resultados.append(("Health Check", test_saude()))
    resultados.append(("Informações", test_info()))
    resultados.append(("Estatísticas", test_estatisticas()))
    resultados.append(("Validação OK", test_validar_entrada()))
    resultados.append(("Validação Inválida", test_validar_entrada_invalida()))

    sucesso, classificacao_id = test_classificacao()
    resultados.append(("Classificação", sucesso))

    resultados.append(("Obter Classificação", test_obter_classificacao(classificacao_id)))
    resultados.append(("Listar Classificações", test_listar_classificacoes()))

    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)

    total = len(resultados)
    aprovados = sum(1 for _, resultado in resultados if resultado)
    reprovados = total - aprovados

    for nome, resultado in resultados:
        status = "✅" if resultado else "❌"
        print(f"{status} {nome}")

    print("="*60)
    print(f"\n📊 Total: {total} | ✅ Aprovados: {aprovados} | ❌ Reprovados: {reprovados}")
    print(f"Taxa de sucesso: {(aprovados/total)*100:.1f}%\n")

if __name__ == '__main__':
    main()
