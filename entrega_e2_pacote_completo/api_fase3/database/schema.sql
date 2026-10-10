-- =====================================================================
-- TIA - Projeto 10 - Fase 2 (Baseline e Arquitetura Mínima Viável)
-- Schema do banco de dados MySQL 8.0 — tia_fase2
--
-- Consolidado a partir de docs/DIAGRAMA_BANCO_DADOS.md, corrigindo:
--   - vírgulas sobrando antes do fechamento de parênteses (PACIENTE, USUARIO)
--   - referências de FOREIGN KEY sem a coluna de destino explícita
--   - ordem de criação das tabelas respeitando as dependências de FK
--
-- Como executar:
--   mysql -u root -p < database/schema.sql
--   (ou use: python src/init_db.py, que lê este arquivo e roda cada
--    instrução contra o banco configurado no seu .env)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS tia_fase2
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE tia_fase2;

-- ---------------------------------------------------------------------
-- 1. DIAGNOSTICO — catálogo de diagnósticos (CID-10)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS diagnostico (
  cid10                  VARCHAR(8) NOT NULL PRIMARY KEY,
  descricao              VARCHAR(255),
  peso_risco_declarado   DECIMAL(4,2),
  validado_terminologia  TINYINT NOT NULL DEFAULT 0,

  CONSTRAINT ck_diag_validado CHECK (validado_terminologia IN (0, 1))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. LOTE_IMPORTACAO — rastreio de importações de dados do SIH/SUS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lote_importacao (
  lote_id          INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome_arquivo     VARCHAR(255) NOT NULL,
  hash_sha256      CHAR(64) NOT NULL UNIQUE,
  competencia      CHAR(7),
  total_registros  INT NOT NULL,
  total_colunas    INT NOT NULL,
  importado_em     DATETIME DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT ck_lote_totais CHECK (total_registros >= 0 AND total_colunas >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. PACIENTE — dados do paciente (pseudonimizado)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS paciente (
  paciente_id      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  pseudonimo       VARCHAR(64) NOT NULL UNIQUE,
  metodo_vinculo   VARCHAR(40) NOT NULL,
  criado_em        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 4. INTERNACAO — internações de cada paciente
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS internacao (
  internacao_id    INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  paciente_id      INT NOT NULL,
  cid10            VARCHAR(8),
  dt_internacao    DATE,
  dt_saida         DATE,
  criado_em        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_internacao_paciente
    FOREIGN KEY (paciente_id) REFERENCES paciente (paciente_id),
  CONSTRAINT fk_internacao_diagnostico
    FOREIGN KEY (cid10) REFERENCES diagnostico (cid10)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 5. REGISTRO_SIH — registros brutos do SIH/SUS
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS registro_sih (
  registro_id      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  lote_id          INT NOT NULL,
  linha_origem     INT NOT NULL,
  idade_anos       INT,
  sexo             VARCHAR(2),
  diag_princ       VARCHAR(8),
  dt_inter         DATE,
  dt_saida         DATE,
  dias_perm        INT,
  morte            TINYINT,
  elegivel_60      TINYINT NOT NULL DEFAULT 0,
  internacao_id    INT,

  CONSTRAINT fk_registro_lote
    FOREIGN KEY (lote_id) REFERENCES lote_importacao (lote_id),
  CONSTRAINT fk_registro_internacao
    FOREIGN KEY (internacao_id) REFERENCES internacao (internacao_id),
  CONSTRAINT uq_registro_linha UNIQUE (lote_id, linha_origem),
  CONSTRAINT ck_registro_elegivel CHECK (elegivel_60 IN (0, 1))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 6. MODELO — versões do modelo de machine learning
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS modelo (
  modelo_id                 INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  versao                    VARCHAR(60) NOT NULL UNIQUE,
  algoritmo                 VARCHAR(60) NOT NULL,
  tipo_coorte               VARCHAR(12) NOT NULL,
  versao_preprocessamento   VARCHAR(40) NOT NULL,
  hiperparametros           JSON NOT NULL,
  metricas                  JSON NOT NULL,
  limite_baixo              DECIMAL(4,3) NOT NULL,
  limite_alto               DECIMAL(4,3) NOT NULL,
  treinado_em               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT ck_modelo_coorte CHECK (tipo_coorte IN ('SINTETICA', 'REAL')),
  CONSTRAINT ck_modelo_limites CHECK (limite_baixo > 0 AND limite_alto < 1)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 7. CLASSIFICACAO — resultado de cada classificação de risco (★ principal)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS classificacao (
  classificacao_id                 INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  modelo_id                        INT NOT NULL,
  paciente_ref                     VARCHAR(64),
  internacao_ref                   VARCHAR(64),
  internacao_id                    INT,
  entrada_json                     JSON NOT NULL,
  idade                            INT,
  diagnostico_principal            VARCHAR(8),
  internacoes_anteriores_12_meses  INT,
  status                           VARCHAR(24) NOT NULL,
  motivos                          JSON,
  risco_readmissao                 VARCHAR(8),
  probabilidade_estimada           DECIMAL(6,5),
  fatores_relevantes               JSON,
  criado_em                        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_class_modelo
    FOREIGN KEY (modelo_id) REFERENCES modelo (modelo_id),
  CONSTRAINT fk_class_internacao
    FOREIGN KEY (internacao_id) REFERENCES internacao (internacao_id),
  CONSTRAINT ck_class_status CHECK (status IN ('OK', 'ERRO_VALIDACAO', 'DADOS_INSUFICIENTES')),
  CONSTRAINT ck_class_risco CHECK (risco_readmissao IN ('BAIXO', 'MEDIO', 'ALTO') OR risco_readmissao IS NULL),
  CONSTRAINT ck_class_probabilidade CHECK (probabilidade_estimada BETWEEN 0 AND 1 OR probabilidade_estimada IS NULL),
  CONSTRAINT ck_class_status_risco CHECK (
    (status = 'OK' AND risco_readmissao IS NOT NULL) OR
    (status <> 'OK' AND risco_readmissao IS NULL)
  ),

  INDEX idx_class_criado_em (criado_em),
  INDEX idx_class_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 8. EXPLICACAO — explicações/segunda opinião geradas por LLM (Gemini)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS explicacao (
  explicacao_id     INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  classificacao_id  INT NOT NULL UNIQUE,
  texto             TEXT NOT NULL,
  status            VARCHAR(24) NOT NULL,
  origem            VARCHAR(8) NOT NULL,
  versao_prompt     VARCHAR(20) NOT NULL,
  modelo_llm        VARCHAR(80),
  latencia_ms       INT,
  tentativas        INT NOT NULL DEFAULT 0,
  detalhe_falha     VARCHAR(255),
  criado_em         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_explicacao_class
    FOREIGN KEY (classificacao_id) REFERENCES classificacao (classificacao_id),
  CONSTRAINT ck_explicacao_status
    CHECK (status IN ('GERADA', 'INDISPONIVEL', 'FORA_DO_CONTRATO')),
  CONSTRAINT ck_explicacao_origem
    CHECK (origem IN ('GEMINI', 'RESERVA'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 9. USUARIO — usuários que fazem revisão humana (Fase 3+)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario (
  usuario_id  INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(120) NOT NULL,
  papel       VARCHAR(40) NOT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 10. REVISAO — revisão humana das classificações (Fase 3+)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS revisao (
  revisao_id        INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  classificacao_id  INT NOT NULL,
  usuario_id        INT NOT NULL,
  parecer           VARCHAR(16) NOT NULL,
  observacao        TEXT,
  criado_em         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_revisao_class
    FOREIGN KEY (classificacao_id) REFERENCES classificacao (classificacao_id),
  CONSTRAINT fk_revisao_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuario (usuario_id),
  CONSTRAINT ck_revisao_parecer
    CHECK (parecer IN ('CONCORDA', 'DISCORDA', 'INCONCLUSIVO'))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 11. COORTE_TREINO — coorte sintética usada para treinar a Árvore de
--     Decisão (decisão aprovada na Fase 1: dado o SIH/SUS não ter rótulo
--     de readmissão em 30 dias, o treino usa dados sintéticos documentados)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coorte_treino (
  caso_id                          INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  origem                           VARCHAR(12) NOT NULL,
  semente                          INT NOT NULL,
  particao                         VARCHAR(8) NOT NULL,
  idade                            INT NOT NULL,
  cid10                            VARCHAR(8) NOT NULL,
  internacoes_anteriores_12_meses  INT NOT NULL,
  readmitido_30d                   TINYINT NOT NULL,

  CONSTRAINT ck_coorte_origem
    CHECK (origem IN ('SINTETICA', 'REAL')),
  CONSTRAINT ck_coorte_particao
    CHECK (particao IN ('TREINO', 'TESTE')),
  CONSTRAINT ck_coorte_idade CHECK (idade >= 60),
  CONSTRAINT ck_coorte_historico CHECK (internacoes_anteriores_12_meses >= 0),
  CONSTRAINT ck_coorte_rotulo CHECK (readmitido_30d IN (0, 1))
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 12. VIEW vw_marco_funcional — vista consolidada do marco funcional
--     exigido pelo professor (entrada → IA → persistência)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_marco_funcional AS
SELECT
  c.classificacao_id,
  c.criado_em,
  c.paciente_ref,
  c.internacao_ref,
  c.idade,
  c.diagnostico_principal,
  c.internacoes_anteriores_12_meses,
  c.status,
  c.motivos,
  c.risco_readmissao,
  c.probabilidade_estimada,
  m.versao AS modelo_versao,
  m.tipo_coorte,
  m.limite_baixo,
  m.limite_alto,
  e.explicacao_id,
  e.status AS explicacao_status,
  e.origem AS explicacao_origem,
  e.modelo_llm,
  e.latencia_ms,
  e.texto AS explicacao_texto
FROM classificacao c
JOIN modelo m ON m.modelo_id = c.modelo_id
LEFT JOIN explicacao e ON e.classificacao_id = c.classificacao_id;

-- ---------------------------------------------------------------------
-- Seed: catálogo de diagnósticos já usado pelo projeto (README.md e
-- src/modelo.py citam estes mesmos 5 códigos CID-10) — dado de referência,
-- não é dado de paciente.
-- ---------------------------------------------------------------------
INSERT INTO diagnostico (cid10, descricao, peso_risco_declarado, validado_terminologia) VALUES
  ('I50.0', 'Insuficiência cardíaca', 0.40, 1),
  ('I10',   'Hipertensão essencial',  0.20, 1),
  ('E11',   'Diabetes mellitus tipo 2', 0.25, 1),
  ('J18',   'Pneumonia',              0.30, 1),
  ('R51',   'Cefaleia',               0.10, 1)
ON DUPLICATE KEY UPDATE descricao = VALUES(descricao);

-- Observação: a tabela `modelo` NÃO é semeada aqui de propósito — o
-- registro do modelo ativo (versão, métricas, limites) é inserido pelo
-- próprio pipeline Python (src/modelo.py / src/init_db.py) depois de
-- treinar a Árvore de Decisão sobre a coorte sintética, para que o
-- banco reflita métricas reais do treino, não valores fixos no SQL.
