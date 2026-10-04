# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Testes de Segurança - JWT e Rate Limiting
"""

import requests
import time
import json

BASE_URL = 'http://localhost:5000/api/v1'

# Cores para output
class Cores:
    OK = '\033[92m'
    ERRO = '\033[91m'
    AVISO = '\033[93m'
    INFO = '\033[94m'
    FIM = '\033[0m'

def teste_login():
    """Teste 1: Login e geração de token"""
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}TESTE 1: Login e Geração de Token{Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    try:
        response = requests.post(f'{BASE_URL}/login', json={
            'usuario_id': 'alberti',
            'senha': 'senha123'
        })

        if response.status_code == 200:
            dados = response.json()
            token = dados['dados']['token']
            print(f"{Cores.OK}✅ Login bem-sucedido{Cores.FIM}")
            print(f"   Token gerado: {token[:50]}...")
            return token
        else:
            print(f"{Cores.ERRO}❌ Erro no login: {response.status_code}{Cores.FIM}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"{Cores.ERRO}❌ Erro: {str(e)}{Cores.FIM}")
        return None

def teste_autenticacao_requerida():
    """Teste 2: Endpoint protegido sem token"""
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}TESTE 2: Acesso a Endpoint Protegido SEM Token{Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    try:
        response = requests.get(f'{BASE_URL}/classificacoes')

        if response.status_code == 401:
            print(f"{Cores.OK}✅ Corretamente bloqueado (401 Unauthorized){Cores.FIM}")
            print(f"   Erro: {response.json()['erro']}")
            return True
        else:
            print(f"{Cores.ERRO}❌ Endpoint deveria retornar 401!{Cores.FIM}")
            return False
    except Exception as e:
        print(f"{Cores.ERRO}❌ Erro: {str(e)}{Cores.FIM}")
        return False

def teste_token_valido(token):
    """Teste 3: Endpoint protegido COM token válido"""
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}TESTE 3: Acesso a Endpoint Protegido COM Token Válido{Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/classificacoes', headers=headers)

        if response.status_code == 200:
            print(f"{Cores.OK}✅ Acesso permitido com token válido (200 OK){Cores.FIM}")
            dados = response.json()['dados']
            print(f"   Total de classificações: {dados['total']}")
            return True
        else:
            print(f"{Cores.ERRO}❌ Erro ao acessar com token: {response.status_code}{Cores.FIM}")
            return False
    except Exception as e:
        print(f"{Cores.ERRO}❌ Erro: {str(e)}{Cores.FIM}")
        return False

def teste_token_invalido():
    """Teste 4: Endpoint protegido com token inválido"""
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}TESTE 4: Acesso com Token Inválido{Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    try:
        headers = {'Authorization': 'Bearer token-falso-123'}
        response = requests.get(f'{BASE_URL}/classificacoes', headers=headers)

        if response.status_code == 401:
            print(f"{Cores.OK}✅ Corretamente bloqueado (401 Unauthorized){Cores.FIM}")
            print(f"   Erro: {response.json()['erro']}")
            return True
        else:
            print(f"{Cores.ERRO}❌ Deveria retornar 401!{Cores.FIM}")
            return False
    except Exception as e:
        print(f"{Cores.ERRO}❌ Erro: {str(e)}{Cores.FIM}")
        return False

def teste_rate_limiting(token):
    """Teste 5: Rate Limiting"""
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}TESTE 5: Rate Limiting (Login - 5/min){Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    try:
        print("   Enviando 6 requisições de login rapidamente...")
        bloqueado = False

        for i in range(6):
            response = requests.post(f'{BASE_URL}/login', json={
                'usuario_id': f'usuario{i}',
                'senha': 'senha'
            })

            if response.status_code == 429:
                print(f"   {i+1}. Bloqueado (429 Too Many Requests) ✅")
                bloqueado = True
                break
            else:
                print(f"   {i+1}. Permitido ({response.status_code})")

        if bloqueado:
            print(f"{Cores.OK}✅ Rate limiting funcionando corretamente{Cores.FIM}")
            return True
        else:
            print(f"{Cores.AVISO}⚠️ Rate limiting pode não estar ativo{Cores.FIM}")
            return False
    except Exception as e:
        print(f"{Cores.ERRO}❌ Erro: {str(e)}{Cores.FIM}")
        return False

def teste_formato_bearer(token):
    """Teste 6: Formato Bearer correto"""
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}TESTE 6: Validação de Formato Bearer{Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    try:
        # Teste 6a: Sem "Bearer"
        headers = {'Authorization': token}
        response = requests.get(f'{BASE_URL}/classificacoes', headers=headers)

        if response.status_code == 401:
            print(f"{Cores.OK}✅ Corretamente rejeitado formato inválido (sem Bearer){Cores.FIM}")
        else:
            print(f"{Cores.AVISO}⚠️ Não validou formato corretamente{Cores.FIM}")

        # Teste 6b: "Bearer " com espaço correto
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/classificacoes', headers=headers)

        if response.status_code == 200:
            print(f"{Cores.OK}✅ Formato Bearer correto aceito{Cores.FIM}")
            return True
        else:
            print(f"{Cores.ERRO}❌ Formato Bearer não funcionou{Cores.FIM}")
            return False
    except Exception as e:
        print(f"{Cores.ERRO}❌ Erro: {str(e)}{Cores.FIM}")
        return False

def teste_header_ausente():
    """Teste 7: Header ausente"""
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}TESTE 7: Header Authorization Ausente{Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    try:
        response = requests.get(f'{BASE_URL}/classificacoes')

        if response.status_code == 401:
            print(f"{Cores.OK}✅ Corretamente bloqueado (401 Unauthorized){Cores.FIM}")
            erro = response.json()['erro']
            if 'ausente' in erro or 'absent' in erro:
                print(f"   Mensagem apropriada: '{erro}'")
            return True
        else:
            print(f"{Cores.ERRO}❌ Deveria retornar 401!{Cores.FIM}")
            return False
    except Exception as e:
        print(f"{Cores.ERRO}❌ Erro: {str(e)}{Cores.FIM}")
        return False

def teste_saude_sem_autenticacao():
    """Teste 8: Endpoint público (saude) sem autenticação"""
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}TESTE 8: Endpoint Público (sem autenticação){Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    try:
        response = requests.get(f'{BASE_URL}/saude')

        if response.status_code == 200:
            print(f"{Cores.OK}✅ Endpoint público acessível sem token{Cores.FIM}")
            return True
        else:
            print(f"{Cores.ERRO}❌ Erro ao acessar endpoint público: {response.status_code}{Cores.FIM}")
            return False
    except Exception as e:
        print(f"{Cores.ERRO}❌ Erro: {str(e)}{Cores.FIM}")
        return False

def main():
    """Executar todos os testes"""
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}TESTES DE SEGURANÇA - TIA FASE 2{Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    resultados = []

    # Teste 1: Login
    token = teste_login()
    resultados.append(('Login', token is not None))

    if token:
        # Teste 2: Sem token
        resultados.append(('Bloqueio sem token', teste_autenticacao_requerida()))

        # Teste 3: Com token válido
        resultados.append(('Acesso com token válido', teste_token_valido(token)))

        # Teste 4: Token inválido
        resultados.append(('Bloqueio token inválido', teste_token_invalido()))

        # Teste 5: Rate Limiting
        resultados.append(('Rate Limiting', teste_rate_limiting(token)))

        # Teste 6: Formato Bearer
        resultados.append(('Formato Bearer', teste_formato_bearer(token)))

        # Teste 7: Header ausente
        resultados.append(('Header ausente', teste_header_ausente()))

        # Teste 8: Endpoint público
        resultados.append(('Endpoint público', teste_saude_sem_autenticacao()))

    # Resumo
    print(f"\n{Cores.INFO}{'='*60}{Cores.FIM}")
    print(f"{Cores.INFO}RESUMO DOS TESTES DE SEGURANÇA{Cores.FIM}")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}")

    aprovados = sum(1 for _, r in resultados if r)
    total = len(resultados)

    for nome, resultado in resultados:
        status = f"{Cores.OK}✅{Cores.FIM}" if resultado else f"{Cores.ERRO}❌{Cores.FIM}"
        print(f"{status} {nome}")

    print(f"\n{Cores.INFO}Total: {total} | Aprovados: {aprovados} | Reprovados: {total - aprovados}{Cores.FIM}")
    taxa_sucesso = (aprovados / total * 100) if total > 0 else 0
    print(f"Taxa de sucesso: {taxa_sucesso:.1f}%")
    print(f"{Cores.INFO}{'='*60}{Cores.FIM}\n")

if __name__ == '__main__':
    main()
