# -*- coding: utf-8 -*-
"""
TIA - Projeto 10 - Fase 2
Gerenciador de Banco de Dados (MySQL)
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

    # ------------------------------------------------------------------
    # Modelo (versão ativa da Árvore de Decisão)
    # ------------------------------------------------------------------
    def obter_modelo_ativo(self):
        """Obter o modelo treinado mais recente"""
        query = "SELECT modelo_id, versao, algoritmo, tipo_coorte, limite_baixo, limite_alto, metricas FROM modelo ORDER BY treinado_em DESC LIMIT 1"
        return self.obter_um(query)

    def obter_modelo_por_versao(self, versao):
        """Obter um modelo pela versão exata (para evitar duplicar o registro a cada run)"""
        query = "SELECT modelo_id, versao, metricas FROM modelo WHERE versao = %s"
        return self.obter_um(query, (versao,))

    def inserir_modelo(self, metadados):
        """
        Inserir uma nova versão de modelo.

        Args:
            metadados (dict): saída de ModeloIA.metadados_para_persistencia()
                (versao, algoritmo, tipo_coorte, versao_preprocessamento,
                 hiperparametros, metricas, limite_baixo, limite_alto)
        """
        query = """
        INSERT INTO modelo
        (versao, algoritmo, tipo_coorte, versao_preprocessamento,
         hiperparametros, metricas, limite_baixo, limite_alto)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            metadados['versao'],
            metadados['algoritmo'],
            metadados['tipo_coorte'],
            metadados['versao_preprocessamento'],
            json.dumps(metadados['hiperparametros']),
            json.dumps(metadados['metricas']),
            metadados['limite_baixo'],
            metadados['limite_alto'],
        )
        sucesso, erro = self.executar_query(query, params)
        if sucesso:
            resultado, _ = self.obter_um("SELECT LAST_INSERT_ID() as modelo_id")
            return resultado['modelo_id'], None
        return None, erro

    def obter_ou_criar_modelo(self, metadados):
        """
        Garante que existe um registro em `modelo` para esta versão do
        código. Se a versão já foi persistida (run anterior), reaproveita
        o modelo_id em vez de inserir duplicado (há UNIQUE em `versao`).
        """
        existente, _ = self.obter_modelo_por_versao(metadados['versao'])
        if existente:
            return existente['modelo_id'], None
        return self.inserir_modelo(metadados)

    # ------------------------------------------------------------------
    # Classificação (decisão oficial da Árvore de Decisão)
    # ------------------------------------------------------------------
    def inserir_classificacao(self, modelo_id, entrada_json, idade, diagnostico, internacoes_ant,
                               status, motivos=None, risco=None, probabilidade=None,
                               fatores_relevantes=None, paciente_ref=None, internacao_ref=None):
        """Inserir classificação"""
        query = """
        INSERT INTO classificacao
        (modelo_id, paciente_ref, internacao_ref, entrada_json, idade, diagnostico_principal,
         internacoes_anteriores_12_meses, status, motivos, risco_readmissao,
         probabilidade_estimada, fatores_relevantes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            modelo_id,
            paciente_ref,
            internacao_ref,
            json.dumps(entrada_json),
            idade,
            diagnostico,
            internacoes_ant,
            status,
            json.dumps(motivos) if motivos else None,
            risco,
            probabilidade,
            json.dumps(fatores_relevantes) if fatores_relevantes else None,
        )

        sucesso, erro = self.executar_query(query, params)
        if sucesso:
            resultado, _ = self.obter_um("SELECT LAST_INSERT_ID() as classificacao_id")
            return resultado['classificacao_id'], None
        return None, erro

    # ------------------------------------------------------------------
    # Explicação (enriquecimento do Gemini — nunca a decisão final)
    # ------------------------------------------------------------------
    def inserir_explicacao(self, classificacao_id, texto, status, origem, versao_prompt,
                            modelo_llm=None, latencia_ms=None, tentativas=0, detalhe_falha=None):
        """Inserir explicação"""
        query = """
        INSERT INTO explicacao
        (classificacao_id, texto, status, origem, versao_prompt, modelo_llm, latencia_ms, tentativas, detalhe_falha)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            classificacao_id,
            texto,
            status,
            origem,
            versao_prompt,
            modelo_llm,
            latencia_ms,
            tentativas,
            detalhe_falha,
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

    # ------------------------------------------------------------------
    # Usuário (quem faz a revisão humana — Fase 3+)
    # ------------------------------------------------------------------
    def listar_usuarios(self):
        """Listar usuários cadastrados para revisão humana"""
        query = "SELECT usuario_id, nome, papel FROM usuario ORDER BY nome"
        return self.obter_dados(query)

    def inserir_usuario(self, nome, papel):
        """Cadastrar um novo usuário revisor"""
        query = "INSERT INTO usuario (nome, papel) VALUES (%s, %s)"
        sucesso, erro = self.executar_query(query, (nome, papel))
        if sucesso:
            resultado, _ = self.obter_um("SELECT LAST_INSERT_ID() as usuario_id")
            return resultado['usuario_id'], None
        return None, erro

    # ------------------------------------------------------------------
    # Revisão humana (Fase 3+): parecer de um usuário sobre uma classificação
    # ------------------------------------------------------------------
    def listar_pendentes_revisao(self, limite=20, offset=0):
        """Classificações OK que ainda não receberam nenhuma revisão humana"""
        query = """
        SELECT c.*, e.texto AS explicacao_texto, e.origem AS explicacao_origem,
               e.status AS explicacao_status
        FROM classificacao c
        LEFT JOIN explicacao e ON e.classificacao_id = c.classificacao_id
        LEFT JOIN revisao r ON r.classificacao_id = c.classificacao_id
        WHERE c.status = 'OK' AND r.revisao_id IS NULL
        ORDER BY c.criado_em ASC
        LIMIT %s OFFSET %s
        """
        return self.obter_dados(query, (limite, offset))

    def inserir_revisao(self, classificacao_id, usuario_id, parecer, observacao=None):
        """Registrar o parecer de um revisor humano sobre uma classificação"""
        query = """
        INSERT INTO revisao (classificacao_id, usuario_id, parecer, observacao)
        VALUES (%s, %s, %s, %s)
        """
        sucesso, erro = self.executar_query(query, (classificacao_id, usuario_id, parecer, observacao))
        if sucesso:
            resultado, _ = self.obter_um("SELECT LAST_INSERT_ID() as revisao_id")
            return resultado['revisao_id'], None
        return None, erro

    def listar_revisoes(self, classificacao_id):
        """Listar todas as revisões humanas já feitas para uma classificação"""
        query = """
        SELECT r.*, u.nome AS usuario_nome, u.papel AS usuario_papel
        FROM revisao r
        JOIN usuario u ON u.usuario_id = r.usuario_id
        WHERE r.classificacao_id = %s
        ORDER BY r.criado_em DESC
        """
        return self.obter_dados(query, (classificacao_id,))


# Singleton
_db_instance = None


def get_db(config=None):
    """Obter instância de database (singleton)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(config)
    return _db_instance
