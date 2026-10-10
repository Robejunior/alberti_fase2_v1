# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 3
API REST - Sistema de Prognóstico de Readmissão Hospitalar

Reescrita em 07/10/2026: a versão anterior deste arquivo não funcionava —
importava `db`, `modelo_ia`, `config` e o decorator `@autenticado_requerido`
sem nunca criar essas instâncias (ver docs/AVALIACAO_CONFORMIDADE_E2.md,
item 14-18 do arquivo original). Esta versão liga de verdade em config.py,
database.py, modelo.py e ai_engine.py atuais, seguindo o mesmo fluxo de
src/main.py: Árvore de Decisão decide -> Gemini explica em paralelo ->
persistência (classificacao + explicacao).

Autenticação JWT (src/auth.py) não é exigida nestes endpoints por ora —
o frontend Streamlit não envia token nenhum, e autenticação já está listada
como melhoria futura em docs/GUIA_FASE3_FRONTEND.md. auth.py continua no
projeto, só não está "plugado" aqui ainda.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime

from config import get_config
from database import Database
from ai_engine import AIEngine
from modelo import get_modelo

app = Flask(__name__)
CORS(app)

limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

config = get_config('development')
modelo = get_modelo()          # treina a Árvore de Decisão uma vez, na subida do processo
ai_engine = AIEngine(config)   # cliente Gemini (cai em RESERVA se não houver chave)

# Registrar o modelo ativo no banco uma única vez, na subida do processo
# (mesmo padrão de src/main.py). Se o MySQL ainda não estiver no ar, a API
# sobe mesmo assim; /classificar responde 503 explicando o motivo, em vez
# de a API inteira recusar subir por causa do banco.
MODELO_ID = None
_erro_inicializacao = None
try:
    _db_boot = Database(config)
    if _db_boot.conectar():
        MODELO_ID, _erro_modelo = _db_boot.obter_ou_criar_modelo(modelo.metadados_para_persistencia())
        if _erro_modelo:
            _erro_inicializacao = f"Erro ao registrar modelo no banco: {_erro_modelo}"
        _db_boot.desconectar()
    else:
        _erro_inicializacao = "Não foi possível conectar ao MySQL na subida da API"
except Exception as exc:
    _erro_inicializacao = f"Erro ao inicializar: {exc}"

if _erro_inicializacao:
    print(f"⚠️  {_erro_inicializacao}")
    print("   Configure o MySQL (python src/init_db.py) e reinicie a API para habilitar /classificar.")
else:
    print(f"✅ Modelo ativo no banco: modelo_id={MODELO_ID} (versão {modelo.VERSAO})")


def resposta_sucesso(dados=None, mensagem='Sucesso', status_code=200):
    """Gerar resposta de sucesso"""
    return jsonify({'sucesso': True, 'mensagem': mensagem, 'dados': dados}), status_code


def resposta_erro(erro, status_code=400):
    """Gerar resposta de erro"""
    return jsonify({'sucesso': False, 'erro': erro}), status_code


# =====================================================================
# INFORMAÇÕES
# =====================================================================

@app.route('/api/v1/saude', methods=['GET'])
def saude():
    """Health check simples — não depende do MySQL, só confirma que a API subiu."""
    return resposta_sucesso({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/v1/info', methods=['GET'])
def info():
    """Informações reais do modelo atualmente treinado (não valores fixos)."""
    return resposta_sucesso({
        'titulo': config.API_TITLE,
        'descricao': config.API_DESCRIPTION,
        'versao_api': config.API_VERSION,
        'modelo': {
            'versao': modelo.VERSAO,
            'algoritmo': 'DecisionTreeClassifier',
            'tipo_coorte': modelo.TIPO_COORTE,
            'metricas': modelo.metricas,
            'limite_baixo': modelo.limites['baixo'],
            'limite_alto': modelo.limites['alto'],
        },
        'banco_disponivel': _erro_inicializacao is None,
    })


# =====================================================================
# CLASSIFICAÇÃO (Árvore decide, Gemini explica em paralelo, persiste)
# =====================================================================

@app.route('/api/v1/classificar', methods=['POST'])
@limiter.limit("30 per minute")
def classificar():
    """
    Payload esperado (mesmo contrato de data/pacientes_teste.json):
    {
        "paciente_id": "PAC_001",        (opcional)
        "internacao_id": "INT_001",      (opcional)
        "idade": 75,
        "diagnostico_principal": "I50.0",
        "internacoes_anteriores_12_meses": 2
    }
    """
    if _erro_inicializacao:
        return resposta_erro(f'API sem banco disponível: {_erro_inicializacao}', 503)

    dados = request.get_json(silent=True)
    if not dados:
        return resposta_erro('Nenhum dado fornecido')

    campos_obrigatorios = ['idade', 'diagnostico_principal', 'internacoes_anteriores_12_meses']
    faltando = [c for c in campos_obrigatorios if c not in dados]
    if faltando:
        return resposta_erro(f'Campo(s) obrigatório(s) faltando: {", ".join(faltando)}')

    paciente_id = dados.get('paciente_id')
    internacao_id = dados.get('internacao_id')
    idade = dados['idade']
    diagnostico = dados['diagnostico_principal']
    internacoes_ant = dados['internacoes_anteriores_12_meses']

    db = Database(config)
    if not db.conectar():
        return resposta_erro('Erro ao conectar no banco de dados', 503)

    try:
        # 1) Árvore de Decisão decide o risco oficial
        resultado_arvore = modelo.classificar_risco(idade, diagnostico, internacoes_ant)

        fatores = None
        if resultado_arvore['status'] == 'OK':
            fatores = modelo.obter_fatores_relevantes(idade, diagnostico, internacoes_ant,
                                                       resultado_arvore['probabilidade'])

        # 2) Persistir a classificação oficial
        classificacao_id, erro_class = db.inserir_classificacao(
            modelo_id=MODELO_ID,
            entrada_json=dados,
            idade=idade,
            diagnostico=diagnostico,
            internacoes_ant=internacoes_ant,
            status=resultado_arvore['status'],
            motivos=resultado_arvore['motivos'],
            risco=resultado_arvore['risco'],
            probabilidade=resultado_arvore['probabilidade'],
            fatores_relevantes=fatores,
            paciente_ref=paciente_id,
            internacao_ref=internacao_id,
        )
        if erro_class:
            return resposta_erro(f'Erro ao salvar classificação: {erro_class}', 500)

        # 3) Gemini explica a decisão em paralelo (nunca decide, nunca quebra o pipeline)
        resultado_gemini = ai_engine.processar_classificacao(dados, resultado_arvore)
        db.inserir_explicacao(
            classificacao_id=classificacao_id,
            texto=resultado_gemini['texto'],
            status=resultado_gemini['status'],
            origem=resultado_gemini['origem'],
            versao_prompt=resultado_gemini['versao_prompt'],
            modelo_llm=resultado_gemini['modelo_llm'],
            latencia_ms=resultado_gemini['latencia_ms'],
            tentativas=resultado_gemini['tentativas'],
            detalhe_falha=str(resultado_gemini['detalhe_falha']) if resultado_gemini['detalhe_falha'] else None,
        )

        return resposta_sucesso({
            'classificacao_id': classificacao_id,
            'modelo_versao': modelo.VERSAO,
            'status': resultado_arvore['status'],
            'risco_readmissao': resultado_arvore['risco'],
            'probabilidade_estimada': resultado_arvore['probabilidade'],
            'motivos': resultado_arvore['motivos'],
            'fatores_relevantes': fatores,
            'explicacao': {
                'texto': resultado_gemini['texto'],
                'origem': resultado_gemini['origem'],
                'status': resultado_gemini['status'],
            },
            'timestamp': datetime.now().isoformat(),
        }, 'Classificação realizada com sucesso', 201)
    finally:
        db.desconectar()


@app.route('/api/v1/classificacoes/<int:classificacao_id>', methods=['GET'])
def obter_classificacao(classificacao_id):
    """Obter uma classificação específica (com explicação, se houver)"""
    db = Database(config)
    if not db.conectar():
        return resposta_erro('Erro ao conectar no banco de dados', 503)
    try:
        dados, erro = db.obter_classificacao(classificacao_id)
        if erro:
            return resposta_erro(erro, 500)
        if not dados:
            return resposta_erro('Classificação não encontrada', 404)
        return resposta_sucesso(dados)
    finally:
        db.desconectar()


@app.route('/api/v1/classificacoes', methods=['GET'])
def listar_classificacoes():
    """Listar classificações com paginação"""
    pagina = request.args.get('pagina', 0, type=int)
    limite = min(request.args.get('limite', 10, type=int), 200)
    offset = pagina * limite

    db = Database(config)
    if not db.conectar():
        return resposta_erro('Erro ao conectar no banco de dados', 503)
    try:
        dados, erro = db.listar_classificacoes(limite, offset)
        if erro:
            return resposta_erro(erro, 500)
        return resposta_sucesso({'total': len(dados) if dados else 0, 'pagina': pagina,
                                  'limite': limite, 'classificacoes': dados})
    finally:
        db.desconectar()


@app.route('/api/v1/estatisticas', methods=['GET'])
def estatisticas():
    """Estatísticas agregadas (contagens reais, lidas do banco)"""
    db = Database(config)
    if not db.conectar():
        return resposta_erro('Erro ao conectar no banco de dados', 503)
    try:
        return resposta_sucesso(db.obter_estatisticas())
    finally:
        db.desconectar()


# =====================================================================
# REVISÃO HUMANA (Fase 3 — tabelas usuario/revisao do schema)
# =====================================================================

@app.route('/api/v1/usuarios', methods=['GET'])
def listar_usuarios():
    """Listar revisores já cadastrados"""
    db = Database(config)
    if not db.conectar():
        return resposta_erro('Erro ao conectar no banco de dados', 503)
    try:
        dados, erro = db.listar_usuarios()
        if erro:
            return resposta_erro(erro, 500)
        return resposta_sucesso({'usuarios': dados or []})
    finally:
        db.desconectar()


@app.route('/api/v1/usuarios', methods=['POST'])
def criar_usuario():
    """Cadastrar um revisor (sem login — só identificação para a revisão)"""
    dados = request.get_json(silent=True)
    if not dados or not dados.get('nome') or not dados.get('papel'):
        return resposta_erro('Campos obrigatórios: nome, papel')

    db = Database(config)
    if not db.conectar():
        return resposta_erro('Erro ao conectar no banco de dados', 503)
    try:
        usuario_id, erro = db.inserir_usuario(dados['nome'], dados['papel'])
        if erro:
            return resposta_erro(erro, 500)
        return resposta_sucesso({'usuario_id': usuario_id}, 'Usuário cadastrado', 201)
    finally:
        db.desconectar()


@app.route('/api/v1/revisao/pendentes', methods=['GET'])
def listar_pendentes_revisao():
    """Classificações OK que ainda não receberam nenhum parecer humano"""
    limite = min(request.args.get('limite', 20, type=int), 100)
    db = Database(config)
    if not db.conectar():
        return resposta_erro('Erro ao conectar no banco de dados', 503)
    try:
        dados, erro = db.listar_pendentes_revisao(limite=limite)
        if erro:
            return resposta_erro(erro, 500)
        return resposta_sucesso({'pendentes': dados or []})
    finally:
        db.desconectar()


@app.route('/api/v1/revisao', methods=['POST'])
def registrar_revisao():
    """
    Registrar o parecer de um revisor humano.

    Payload esperado:
    {
        "classificacao_id": 1,
        "usuario_id": 1,
        "parecer": "CONCORDA" | "DISCORDA" | "INCONCLUSIVO",
        "observacao": "texto livre"    (opcional)
    }
    """
    dados = request.get_json(silent=True)
    if not dados:
        return resposta_erro('Nenhum dado fornecido')

    campos_obrigatorios = ['classificacao_id', 'usuario_id', 'parecer']
    faltando = [c for c in campos_obrigatorios if c not in dados]
    if faltando:
        return resposta_erro(f'Campo(s) obrigatório(s) faltando: {", ".join(faltando)}')

    if dados['parecer'] not in ('CONCORDA', 'DISCORDA', 'INCONCLUSIVO'):
        return resposta_erro('parecer deve ser CONCORDA, DISCORDA ou INCONCLUSIVO')

    db = Database(config)
    if not db.conectar():
        return resposta_erro('Erro ao conectar no banco de dados', 503)
    try:
        revisao_id, erro = db.inserir_revisao(
            classificacao_id=dados['classificacao_id'],
            usuario_id=dados['usuario_id'],
            parecer=dados['parecer'],
            observacao=dados.get('observacao'),
        )
        if erro:
            return resposta_erro(erro, 500)
        return resposta_sucesso({'revisao_id': revisao_id}, 'Revisão registrada', 201)
    finally:
        db.desconectar()


# =====================================================================
# TRATAMENTO DE ERROS
# =====================================================================

@app.errorhandler(404)
def nao_encontrado(erro):
    return resposta_erro('Endpoint não encontrado', 404)


@app.errorhandler(500)
def erro_interno(erro):
    return resposta_erro('Erro interno do servidor', 500)


# =====================================================================
# MAIN
# =====================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("TIA - Projeto 10 - Fase 3")
    print("API REST - Sistema de Prognóstico de Readmissão")
    print("=" * 60)
    print(f"Versão: {config.API_VERSION}")
    print("Iniciando servidor em http://localhost:5000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=config.DEBUG)
