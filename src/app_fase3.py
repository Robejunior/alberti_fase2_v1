# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - API REST Flask (Fase 3 - Simplificada)
Sistema de Prognóstico de Readmissão Hospitalar
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Criar app Flask
app = Flask(__name__)
CORS(app)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# =====================================================================
# ROTAS
# =====================================================================

@app.route('/api/v1/saude', methods=['GET'])
@limiter.limit("60 per minute")
def health_check():
    """Health check - Verificar se API está rodando"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'mensagem': 'API TIA Fase 3 rodando!'
    }), 200


@app.route('/api/v1/info', methods=['GET'])
@limiter.limit("60 per minute")
def info():
    """Informações da API"""
    return jsonify({
        'projeto': 'TIA - Prognóstico de Readmissão Hospitalar',
        'fase': 3,
        'versao': '1.0.0',
        'endpoints': {
            'saude': '/api/v1/saude',
            'info': '/api/v1/info',
            'classificar': '/api/v1/classificar',
            'estatisticas': '/api/v1/estatisticas'
        }
    }), 200


@app.route('/api/v1/classificar', methods=['POST'])
@limiter.limit("30 per minute")
def classificar():
    """
    Classificar risco de readmissão para paciente

    Request JSON:
    {
        "paciente_id": "PAC_001",
        "idade": 75,
        "diagnostico_principal": "I50.0",
        "internacoes_anteriores_12_meses": 2
    }
    """
    try:
        dados = request.json

        # Validação básica
        if not dados:
            return jsonify({'erro': 'Dados vazios'}), 400

        idade = dados.get('idade', 0)
        internacoes = dados.get('internacoes_anteriores_12_meses', 0)
        diagnostico = dados.get('diagnostico_principal', '')
        paciente_id = dados.get('paciente_id', 'DESCONHECIDO')

        # Validar entrada
        if idade < 60 or idade > 120:
            return jsonify({'erro': 'Idade deve estar entre 60 e 120'}), 400

        if not diagnostico:
            return jsonify({'erro': 'Diagnóstico é obrigatório'}), 400

        # Algoritmo simples de classificação (sem ML)
        # Baseado em heurística: internações + idade
        score = (internacoes * 20) + ((idade - 60) * 0.5)

        if score < 30:
            risco = 'BAIXO'
            probabilidade = score / 100
        elif score < 60:
            risco = 'MEDIO'
            probabilidade = (score + 20) / 100
        else:
            risco = 'ALTO'
            probabilidade = min((score + 40) / 100, 0.95)

        # Fatores relevantes
        fatores = []
        if internacoes > 2:
            fatores.append(f"Múltiplas internações ({internacoes}) em 12 meses")
        if idade > 80:
            fatores.append(f"Idade avançada ({idade} anos)")
        if not fatores:
            fatores.append("Dados dentro dos padrões esperados")

        return jsonify({
            'dados': {
                'paciente_id': paciente_id,
                'idade': idade,
                'diagnostico_principal': diagnostico,
                'internacoes_anteriores_12_meses': internacoes,
                'risco_readmissao': risco,
                'probabilidade_estimada': round(probabilidade, 2),
                'fatores_relevantes': fatores,
                'timestamp': datetime.now().isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/v1/estatisticas', methods=['GET'])
@limiter.limit("60 per minute")
def estatisticas():
    """Retornar estatísticas básicas"""
    return jsonify({
        'total_avaliacoes': 0,
        'riscos_baixos': 0,
        'riscos_medios': 0,
        'riscos_altos': 0,
        'probabilidade_media': 0.0
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Tratamento de erro 404"""
    return jsonify({
        'erro': 'Endpoint não encontrado',
        'mensagem': 'Verifique a URL da requisição'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Tratamento de erro 500"""
    return jsonify({
        'erro': 'Erro interno do servidor',
        'mensagem': 'Tente novamente mais tarde'
    }), 500


# =====================================================================
# MAIN
# =====================================================================

if __name__ == '__main__':
    PORT = int(os.getenv('FLASK_PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'

    print("╔════════════════════════════════════════════════════════════╗")
    print("║  TIA - Projeto 10 - API REST Flask (Fase 3)              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"\n📍 API rodando em: http://127.0.0.1:{PORT}")
    print(f"📊 Docs: http://127.0.0.1:{PORT}/api/v1/info")
    print(f"🔄 Health: http://127.0.0.1:{PORT}/api/v1/saude\n")

    app.run(
        host='127.0.0.1',
        port=PORT,
        debug=DEBUG
    )
