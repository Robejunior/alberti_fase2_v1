# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Autenticação JWT e Segurança
"""

import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from config import Config

class JWTManager:
    """Gerenciador de tokens JWT"""

    def __init__(self, config=None):
        self.config = config or Config()
        self.secret_key = self.config.SECRET_KEY
        self.algorithm = 'HS256'
        self.expiration_hours = 24

    def gerar_token(self, usuario_id, papel='usuario'):
        """Gerar novo token JWT"""
        try:
            payload = {
                'usuario_id': usuario_id,
                'papel': papel,
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=self.expiration_hours)
            }
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token, None
        except Exception as e:
            return None, str(e)

    def validar_token(self, token):
        """Validar token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, 'Token expirado'
        except jwt.InvalidTokenError:
            return None, 'Token inválido'
        except Exception as e:
            return None, str(e)

    def extrair_token(self, authorization_header):
        """Extrair token do header Authorization"""
        if not authorization_header:
            return None

        partes = authorization_header.split()
        if len(partes) != 2 or partes[0].lower() != 'bearer':
            return None

        return partes[1]

# Instância global
jwt_manager = None

def get_jwt_manager(config=None):
    """Obter instância de JWTManager (singleton)"""
    global jwt_manager
    if jwt_manager is None:
        jwt_manager = JWTManager(config)
    return jwt_manager

def autenticado_requerido(f):
    """Decorator para proteger endpoints com autenticação JWT"""
    @wraps(f)
    def decorador(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'sucesso': False,
                'erro': 'Token de autenticação ausente'
            }), 401

        jwt_mgr = get_jwt_manager()
        token = jwt_mgr.extrair_token(auth_header)

        if not token:
            return jsonify({
                'sucesso': False,
                'erro': 'Formato de token inválido (use: Bearer <token>)'
            }), 401

        payload, erro = jwt_mgr.validar_token(token)

        if not payload:
            return jsonify({
                'sucesso': False,
                'erro': f'Erro ao validar token: {erro}'
            }), 401

        # Armazenar payload no request context
        request.usuario_id = payload.get('usuario_id')
        request.papel = payload.get('papel')

        return f(*args, **kwargs)

    return decorador

def admin_requerido(f):
    """Decorator para proteger endpoints que requerem papel de admin"""
    @wraps(f)
    def decorador(*args, **kwargs):
        if not hasattr(request, 'papel') or request.papel != 'admin':
            return jsonify({
                'sucesso': False,
                'erro': 'Acesso negado: privilégios de admin necessários'
            }), 403

        return f(*args, **kwargs)

    return decorador

# Função auxiliar para validar entrada
def sanitizar_entrada(dados, campos_obrigatorios=None):
    """Sanitizar e validar entrada JSON"""
    if not dados:
        return None, 'Nenhum dado fornecido'

    if campos_obrigatorios:
        for campo in campos_obrigatorios:
            if campo not in dados or dados[campo] is None:
                return None, f'Campo obrigatório faltando: {campo}'

    # Remover campos inesperados (whitelist)
    campos_permitidos = set(campos_obrigatorios) if campos_obrigatorios else set(dados.keys())
    dados_limpos = {k: v for k, v in dados.items() if k in campos_permitidos}

    return dados_limpos, None

# Função para registrar tentativas de acesso
def registrar_acesso(endpoint, usuario_id=None, ip=None, status=200):
    """Registrar tentativa de acesso (para auditoria)"""
    try:
        timestamp = datetime.datetime.utcnow().isoformat()
        ip = ip or request.remote_addr

        # TODO: Salvar em arquivo de log ou banco de dados
        log_msg = f"[{timestamp}] {endpoint} | Usuario: {usuario_id} | IP: {ip} | Status: {status}"
        print(log_msg)

    except Exception as e:
        print(f"Erro ao registrar acesso: {e}")
