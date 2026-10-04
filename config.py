# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Configuração da API REST
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuração padrão"""

    # Flask
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'tia_fase2')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

    # API
    API_VERSION = '1.0.0'
    API_TITLE = 'TIA - Sistema de Prognóstico de Readmissão Hospitalar'
    API_DESCRIPTION = 'API REST para classificação de risco de readmissão em pacientes 60+'

    # Model
    MODEL_VERSION = 'v1.0.0'
    MODEL_ALGORITMO = 'DecisionTree'

    # LLM (Gemini)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    LLM_API_KEY = os.getenv('GEMINI_API_KEY', '')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-pro')

    # Limits
    MAX_RECORDS_PER_REQUEST = 100
    TIMEOUT_SECONDS = 30

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    MYSQL_DATABASE = 'tia_fase2_test'

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False

# Selecionar config baseado no ambiente
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

def get_config(env='development'):
    """Obter configuração baseado no ambiente"""
    return config_by_name.get(env, DevelopmentConfig)
