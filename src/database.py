# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Gerenciador de Banco de Dados
"""

import mysql.connector
from mysql.connector import Error
import json
from config import Config

class Database:
    """Classe para gerenciar conexões e queries MySQL"""

    def __init__(self, config=None):
        self.config = config or Config()
        self.connection = None
        self.cursor = None

    def conectar(self):
        """Estabelecer conexão com MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.MYSQL_HOST,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                database=self.config.MYSQL_DATABASE,
                port=self.config.MYSQL_PORT,
                autocommit=True
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            return False

    def desconectar(self):
        """Fechar conexão com MySQL"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def executar_query(self, query, params=None):
        """Executar query (INSERT, UPDATE, DELETE)"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True, None
        except Error as e:
            self.connection.rollback()
            return False, str(e)

    def obter_dados(self, query, params=None):
        """Obter dados de uma query (SELECT)"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall(), None
        except Error as e:
            return None, str(e)

    def obter_um(self, query, params=None):
        """Obter um registro"""
        dados, erro = self.obter_dados(query, params)
        return dados[0] if dados else None, erro

    def obter_modelo_ativo(self):
        """Obter modelo ativo"""
        query = "SELECT modelo_id, versao, algoritmo, tipo_coorte, limite_baixo, limite_alto, metricas FROM modelo ORDER BY treinado_em DESC LIMIT 1"
        return self.obter_um(query)

    def inserir_classificacao(self, modelo_id, entrada_json, idade, diagnostico, internacoes_ant, status, motivos=None, risco=None, probabilidade=None):
        """Inserir classificação"""
        query = """
        INSERT INTO classificacao
        (modelo_id, entrada_json, idade, diagnostico_principal, internacoes_anteriores_12_meses,
         status, motivos, risco_readmissao, probabilidade_estimada)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            modelo_id,
            json.dumps(entrada_json),
            idade,
            diagnostico,
            internacoes_ant,
            status,
            json.dumps(motivos) if motivos else None,
            risco,
            probabilidade
        )

        sucesso, erro = self.executar_query(query, params)
        if sucesso:
            # Obter o ID da classificação inserida
            resultado, _ = self.obter_um("SELECT LAST_INSERT_ID() as classificacao_id")
            return resultado['classificacao_id'], None
        return None, erro

    def inserir_explicacao(self, classificacao_id, texto, status, origem, versao_prompt, modelo_llm=None, latencia_ms=None):
        """Inserir explicação"""
        query = """
        INSERT INTO explicacao
        (classificacao_id, texto, status, origem, versao_prompt, modelo_llm, latencia_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            classificacao_id,
            texto,
            status,
            origem,
            versao_prompt,
            modelo_llm,
            latencia_ms
        )

        return self.executar_query(query, params)

    def obter_classificacao(self, classificacao_id):
        """Obter classificação completa com explicação"""
        query = """
        SELECT c.*, e.texto, e.status as explicacao_status, e.modelo_llm
        FROM classificacao c
        LEFT JOIN explicacao e ON c.classificacao_id = e.classificacao_id
        WHERE c.classificacao_id = %s
        """
        return self.obter_um(query, (classificacao_id,))

    def listar_classificacoes(self, limite=100, offset=0):
        """Listar classificações com paginação"""
        query = """
        SELECT c.*, e.texto, e.status as explicacao_status
        FROM classificacao c
        LEFT JOIN explicacao e ON c.classificacao_id = e.classificacao_id
        ORDER BY c.criado_em DESC
        LIMIT %s OFFSET %s
        """
        return self.obter_dados(query, (limite, offset))

    def obter_estatisticas(self):
        """Obter estatísticas do sistema"""
        queries = {
            'total_classificacoes': "SELECT COUNT(*) as total FROM classificacao",
            'classificacoes_ok': "SELECT COUNT(*) as total FROM classificacao WHERE status = 'OK'",
            'classificacoes_erro': "SELECT COUNT(*) as total FROM classificacao WHERE status IN ('ERRO_VALIDACAO', 'DADOS_INSUFICIENTES')",
            'risco_baixo': "SELECT COUNT(*) as total FROM classificacao WHERE risco_readmissao = 'BAIXO'",
            'risco_medio': "SELECT COUNT(*) as total FROM classificacao WHERE risco_readmissao = 'MEDIO'",
            'risco_alto': "SELECT COUNT(*) as total FROM classificacao WHERE risco_readmissao = 'ALTO'",
            'modelo_ativo': "SELECT versao FROM modelo ORDER BY treinado_em DESC LIMIT 1"
        }

        resultado = {}
        for chave, query in queries.items():
            dados, _ = self.obter_um(query)
            resultado[chave] = dados.get('total') if chave != 'modelo_ativo' else dados.get('versao') if dados else None

        return resultado

# Singleton
_db_instance = None

def get_db(config=None):
    """Obter instância de database (singleton)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(config)
    return _db_instance
