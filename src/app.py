# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
API REST - Sistema de Prognóstico de Readmissão Hospitalar
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import json

# Importações removidas (Fase 3 simplificada - sem dependências de sklearn)
# from config import get_config
# from database import Database
# from modelo import ModeloIA
# from auth import get_jwt_manager, autenticado_requerido, admin_requerido, sanitizar_entrada, registrar_acesso

# =====================================================================
# INICIALIZAÇÃO
# =====================================================================

app = Flask(__name__)
CORS(app)

# Inicializar (simplificado para Fase 3)
# db = Database(config)
# modelo_ia = ModeloIA()
# jwt_manager = get_jwt_manager(config)

# Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# =====================================================================
# MIDDLEWARE E UTILITÁRIOS
# =====================================================================

def conectar_db():
    """Conectar ao banco de dados antes de cada request"""
    if not db.conectar():
        return resposta_erro('Erro ao conectar no banco de dados', 503)

def desconectar_db(response):
    """Desconectar do banco após cada request"""
    db.desconectar()
    return response

app.before_request(conectar_db)
app.after_request(desconectar_db)

def resposta_sucesso(dados=None, mensagem='Sucesso', status_code=200):
    """Gerar resposta de sucesso"""
    return jsonify({
        'sucesso': True,
        'mensagem': mensagem,
        'dados': dados
    }), status_code

def resposta_erro(erro, status_code=400):
    """Gerar resposta de erro"""
    return jsonify({
        'sucesso': False,
        'erro': erro
    }), status_code

# =====================================================================
# ENDPOINTS - AUTENTICAÇÃO
# =====================================================================

@app.route('/api/v1/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Gerar token JWT para autenticação"""
    try:
        dados = request.get_json()

        if not dados:
            return resposta_erro('Nenhum dado fornecido')

        # Validação simples (em produção, verificar contra banco de usuários)
        usuario_id = dados.get('usuario_id')
        senha = dados.get('senha')

        if not usuario_id or not senha:
            return resposta_erro('usuario_id e senha obrigatórios')

        # TODO: Verificar credenciais contra banco de usuários
        # Por enquanto, aceitar qualquer credencial (apenas para demo)

        token, erro = jwt_manager.gerar_token(usuario_id, papel='usuario')

        if not token:
            return resposta_erro(f'Erro ao gerar token: {erro}')

        return resposta_sucesso({
            'token': token,
            'tipo': 'Bearer',
            'expira_em': '24 horas'
        }, 'Login bem-sucedido', 200)

    except Exception as e:
        return resposta_erro(f'Erro no login: {str(e)}', 500)

# =====================================================================
# ENDPOINTS - INFORMAÇÕES
# =====================================================================

@app.route('/api/v1/info', methods=['GET'])
def info():
    """Informações da API"""
    return resposta_sucesso({
        'titulo': config.API_TITLE,
        'descricao': config.API_DESCRIPTION,
        'versao': config.API_VERSION,
        'modelo': {
            'versao': config.MODEL_VERSION,
            'algoritmo': config.MODEL_ALGORITMO
        }
    })

@app.route('/api/v1/saude', methods=['GET'])
def saude():
    """Health check"""
    return resposta_sucesso({'status': 'ok'})

@app.route('/api/v1/estatisticas', methods=['GET'])
@autenticado_requerido
@limiter.limit("60 per minute")
def estatisticas():
    """Obter estatísticas do sistema"""
    try:
        stats = db.obter_estatisticas()
        registrar_acesso('/api/v1/estatisticas', request.usuario_id, status=200)
        return resposta_sucesso(stats)
    except Exception as e:
        registrar_acesso('/api/v1/estatisticas', request.usuario_id, status=500)
        return resposta_erro(str(e))

# =====================================================================
# ENDPOINTS - CLASSIFICAÇÃO
# =====================================================================

@app.route('/api/v1/classificar', methods=['POST'])
@autenticado_requerido
@limiter.limit("30 per minute")
def classificar():
    """
    Classificar risco de readmissão

    Payload esperado:
    {
        "paciente_id": "PAC_001",
        "internacao_id": "INT_001",
        "idade": 75,
        "diagnostico_principal": "I50.0",
        "internacoes_anteriores_12_meses": 3
    }
    """
    try:
        dados = request.get_json()

        # Validar dados
        if not dados:
            return resposta_erro('Nenhum dado fornecido')

        campos_obrigatorios = ['idade', 'diagnostico_principal', 'internacoes_anteriores_12_meses']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return resposta_erro(f'Campo obrigatório faltando: {campo}')

        # Extrair dados
        paciente_id = dados.get('paciente_id')
        internacao_id = dados.get('internacao_id')
        idade = dados.get('idade')
        diagnostico = dados.get('diagnostico_principal')
        internacoes_ant = dados.get('internacoes_anteriores_12_meses')

        # Obter modelo ativo
        modelo_info, erro = db.obter_modelo_ativo()
        if not modelo_info:
            return resposta_erro('Nenhum modelo ativo encontrado')

        modelo_id = modelo_info['modelo_id']

        # Classificar usando modelo
        resultado_modelo = modelo_ia.classificar_risco(idade, diagnostico, internacoes_ant)

        # Preparar dados para inserir no banco
        entrada_json = {
            'paciente_id': paciente_id,
            'internacao_id': internacao_id,
            'idade': idade,
            'diagnostico_principal': diagnostico,
            'internacoes_anteriores_12_meses': internacoes_ant
        }

        # Inserir classificação no banco
        classificacao_id, erro_insert = db.inserir_classificacao(
            modelo_id=modelo_id,
            entrada_json=entrada_json,
            idade=idade,
            diagnostico=diagnostico,
            internacoes_ant=internacoes_ant,
            status=resultado_modelo['status'],
            motivos=resultado_modelo['motivos'],
            risco=resultado_modelo['risco'],
            probabilidade=resultado_modelo['probabilidade']
        )

        if not classificacao_id:
            return resposta_erro(f'Erro ao inserir no banco: {erro_insert}')

        # Obter fatores relevantes
        fatores = modelo_ia.obter_fatores_relevantes(
            idade, diagnostico, internacoes_ant, resultado_modelo['probabilidade']
        )

        # Preparar resposta
        resposta = {
            'classificacao_id': classificacao_id,
            'modelo_versao': modelo_info['versao'],
            'status': resultado_modelo['status'],
            'risco_readmissao': resultado_modelo['risco'],
            'probabilidade_estimada': resultado_modelo['probabilidade'],
            'fatores_relevantes': fatores,
            'timestamp': datetime.now().isoformat()
        }

        return resposta_sucesso(resposta, 'Classificação realizada com sucesso', 201)

    except Exception as e:
        return resposta_erro(f'Erro na classificação: {str(e)}', 500)

@app.route('/api/v1/classificacoes/<int:classificacao_id>', methods=['GET'])
@autenticado_requerido
@limiter.limit("60 per minute")
def obter_classificacao(classificacao_id):
    """Obter uma classificação específica"""
    try:
        dados, erro = db.obter_classificacao(classificacao_id)
        if not dados:
            registrar_acesso(f'/api/v1/classificacoes/{classificacao_id}', request.usuario_id, status=404)
            return resposta_erro('Classificação não encontrada', 404)
        registrar_acesso(f'/api/v1/classificacoes/{classificacao_id}', request.usuario_id, status=200)
        return resposta_sucesso(dados)
    except Exception as e:
        registrar_acesso(f'/api/v1/classificacoes/{classificacao_id}', request.usuario_id, status=500)
        return resposta_erro(str(e), 500)

@app.route('/api/v1/classificacoes', methods=['GET'])
@autenticado_requerido
@limiter.limit("60 per minute")
def listar_classificacoes():
    """Listar classificações com paginação"""
    try:
        pagina = request.args.get('pagina', 0, type=int)
        limite = request.args.get('limite', 10, type=int)

        if limite > 100:
            limite = 100

        offset = pagina * limite

        dados, erro = db.listar_classificacoes(limite, offset)
        if erro:
            registrar_acesso('/api/v1/classificacoes', request.usuario_id, status=500)
            return resposta_erro(erro, 500)

        registrar_acesso('/api/v1/classificacoes', request.usuario_id, status=200)
        return resposta_sucesso({
            'total': len(dados) if dados else 0,
            'pagina': pagina,
            'limite': limite,
            'classificacoes': dados
        })
    except Exception as e:
        registrar_acesso('/api/v1/classificacoes', request.usuario_id, status=500)
        return resposta_erro(str(e), 500)

# =====================================================================
# ENDPOINTS - EXPLICAÇÃO (LLM)
# =====================================================================

@app.route('/api/v1/explicar/<int:classificacao_id>', methods=['POST'])
def explicar_classificacao(classificacao_id):
    """
    Gerar explicação para uma classificação usando LLM
    """
    try:
        # Obter classificação
        dados, erro = db.obter_classificacao(classificacao_id)
        if not dados:
            return resposta_erro('Classificação não encontrada', 404)

        # Por agora, retornar uma explicação genérica
        # Integração com Gemini/Claude seria feita aqui

        explicacao_texto = gerar_explicacao_padrao(
            dados['idade'],
            dados['diagnostico_principal'],
            dados['internacoes_anteriores_12_meses'],
            dados['risco_readmissao'],
            dados['probabilidade_estimada']
        )

        # Inserir explicação no banco
        sucesso, erro_insert = db.inserir_explicacao(
            classificacao_id=classificacao_id,
            texto=explicacao_texto,
            status='GERADA',
            origem='RESERVA',
            versao_prompt='v1.0',
            modelo_llm='reserva'
        )

        if not sucesso:
            return resposta_erro(f'Erro ao inserir explicação: {erro_insert}', 500)

        return resposta_sucesso({
            'classificacao_id': classificacao_id,
            'explicacao': explicacao_texto,
            'origem': 'RESERVA'
        }, 'Explicação gerada com sucesso', 201)

    except Exception as e:
        return resposta_erro(f'Erro ao gerar explicação: {str(e)}', 500)

# =====================================================================
# ENDPOINTS - VALIDAÇÃO
# =====================================================================

@app.route('/api/v1/validar-entrada', methods=['POST'])
def validar_entrada():
    """Validar dados de entrada antes de classificar"""
    try:
        dados = request.get_json()

        if not dados:
            return resposta_erro('Nenhum dado fornecido')

        # Validar cada campo
        validacoes = {
            'idade': validar_idade(dados.get('idade')),
            'diagnostico_principal': validar_diagnostico(dados.get('diagnostico_principal')),
            'internacoes_anteriores_12_meses': validar_internacoes(dados.get('internacoes_anteriores_12_meses'))
        }

        valido = all(v['valido'] for v in validacoes.values())

        return resposta_sucesso({
            'valido': valido,
            'validacoes': validacoes
        })

    except Exception as e:
        return resposta_erro(str(e), 500)

# =====================================================================
# FUNÇÕES AUXILIARES
# =====================================================================

def validar_idade(idade):
    """Validar idade"""
    if not isinstance(idade, int):
        return {'valido': False, 'erro': 'Idade deve ser inteiro'}
    if idade < 60:
        return {'valido': False, 'erro': 'Idade deve ser >= 60'}
    if idade > 120:
        return {'valido': False, 'erro': 'Idade parece inválida (> 120)'}
    return {'valido': True}

def validar_diagnostico(diagnostico):
    """Validar diagnóstico"""
    if not isinstance(diagnostico, str):
        return {'valido': False, 'erro': 'Diagnóstico deve ser string'}
    if len(diagnostico) == 0:
        return {'valido': False, 'erro': 'Diagnóstico não pode estar vazio'}
    return {'valido': True}

def validar_internacoes(internacoes):
    """Validar internações anteriores"""
    if not isinstance(internacoes, int):
        return {'valido': False, 'erro': 'Internações deve ser inteiro'}
    if internacoes < 0:
        return {'valido': False, 'erro': 'Internações não pode ser negativo'}
    return {'valido': True}

def gerar_explicacao_padrao(idade, diagnostico, internacoes, risco, probabilidade):
    """Gerar explicação padrão para a classificação"""
    return f"""
    Classificação de Risco de Readmissão - Relatório
    ================================================

    DADOS DO PACIENTE:
    - Idade: {idade} anos
    - Diagnóstico Principal: {diagnostico}
    - Internações nos últimos 12 meses: {internacoes}

    RESULTADO:
    - Risco Estimado: {risco}
    - Probabilidade: {probabilidade*100:.1f}%

    ANÁLISE:
    Este paciente apresenta um risco de readmissão {risco.lower()}.

    Fatores influenciadores:
    1. Histórico de internações: {internacoes} internações nos últimos 12 meses
       - Este é o fator mais importante (peso: 71%)

    2. Idade: {idade} anos
       - Idade avançada é fator de risco (peso: 24%)

    3. Diagnóstico: {diagnostico}
       - Diagnóstico também influencia o risco (peso: 4%)

    RECOMENDAÇÕES:
    - Acompanhamento clínico adequado
    - Aderência ao tratamento medicamentoso
    - Acompanhamento pós-alta hospitalar
    - Contato telefônico na primeira semana pós-alta

    Gerado em: {datetime.now().isoformat()}
    """

# =====================================================================
# TRATAMENTO DE ERROS
# =====================================================================

@app.errorhandler(404)
def nao_encontrado(erro):
    """Tratador para 404"""
    return resposta_erro('Endpoint não encontrado', 404)

@app.errorhandler(500)
def erro_interno(erro):
    """Tratador para 500"""
    return resposta_erro('Erro interno do servidor', 500)

# =====================================================================
# MAIN
# =====================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("TIA - Projeto 10 - Fase 2")
    print("API REST - Sistema de Prognóstico de Readmissão")
    print("=" * 60)
    print(f"Versão: {config.API_VERSION}")
    print(f"Debug: {config.DEBUG}")
    print("Iniciando servidor em http://localhost:5000")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.DEBUG
    )
