# 🗄️ Diagrama e Schema do Banco de Dados - TIA Fase 2

## 📊 Diagrama Entidade-Relacionamento (ER)

```
┌────────────────────────┐
│   LOTE_IMPORTACAO      │
├────────────────────────┤
│ PK│ lote_id            │
│   │ nome_arquivo       │
│   │ hash_sha256        │◄─────┐
│   │ competencia        │      │
│   │ total_registros    │      │
│   │ total_colunas      │      │
│   │ importado_em       │      │
└────────────────────────┘      │
         │                       │
         │ 1:N                   │
         │                       │
         ▼                       │
┌────────────────────────┐      │
│    REGISTRO_SIH        │      │
├────────────────────────┤      │
│ PK│ registro_id        │      │
│   │ lote_id         ───┼──────┘
│   │ linha_origem       │
│   │ idade_anos         │
│   │ sexo               │
│   │ diag_princ      ───┼────┐
│   │ elegivel_60        │    │
│   │ internacao_id   ───┼──┐ │
└────────────────────────┘  │ │
                            │ │
                            │ │
┌────────────────────────┐  │ │
│   DIAGNOSTICO          │  │ │
├────────────────────────┤  │ │
│ PK│ cid10              │◄─┤ │
│   │ descricao          │  │ │
│   │ peso_risco_decl    │  │ │
│   │ validado_termo     │  │ │
└────────────────────────┘  │ │
                            │ │
                            │ │
┌────────────────────────┐  │ │
│      PACIENTE          │  │ │
├────────────────────────┤  │ │
│ PK│ paciente_id        │◄─┼┼───┐
│   │ pseudonimo         │  │ │   │
│   │ metodo_vinculo     │  │ │   │
│   │ criado_em          │  │ │   │
└────────────────────────┘  │ │   │
         │                   │ │   │
         │ 1:N               │ │   │
         │                   │ │   │
         ▼                   │ │   │
┌────────────────────────┐  │ │   │
│    INTERNACAO          │  │ │   │
├────────────────────────┤  │ │   │
│ PK│ internacao_id   ───┼──┘ │   │
│   │ paciente_id     ───┼────┘   │
│   │ cid10           ───┼───────┐│
│   │ dt_internacao      │       ││
│   │ dt_saida           │       ││
│   │ criado_em          │       ││
└────────────────────────┘       ││
         │                       ││
         │ 1:N                   ││
         │                       ││
         ▼                       ││
┌────────────────────────┐      ││
│     MODELO             │      ││
├────────────────────────┤      ││
│ PK│ modelo_id          │      ││
│   │ versao             │      ││
│   │ algoritmo          │      ││
│   │ tipo_coorte        │      ││
│   │ hiperparametros    │      ││
│   │ metricas           │      ││
│   │ limite_baixo       │      ││
│   │ limite_alto        │      ││
│   │ treinado_em        │      ││
└────────────────────────┘      ││
         │                       ││
         │ 1:N                   ││
         │                       ││
         ▼                       ││
┌────────────────────────┐      ││
│  CLASSIFICACAO         │      ││
├────────────────────────┤      ││
│ PK│ classificacao_id   │      ││
│   │ modelo_id       ───┼──────┘│
│   │ paciente_ref       │       │
│   │ internacao_ref     │       │
│   │ internacao_id   ───┼───────┘
│   │ entrada_json       │
│   │ idade              │
│   │ diagnostico_princ  │
│   │ internacoes_ant    │
│   │ status             │
│   │ risco_readmissao   │
│   │ probabilidade_est  │
│   │ fatores_relevantes │
│   │ criado_em          │
└────────────────────────┘
         │
         │ 1:1
         │
         ▼
┌────────────────────────┐
│     EXPLICACAO         │
├────────────────────────┤
│ PK│ explicacao_id      │
│   │ classificacao_id ──┼┘
│   │ texto              │
│   │ status             │
│   │ origem             │
│   │ versao_prompt      │
│   │ modelo_llm         │
│   │ latencia_ms        │
│   │ tentativas         │
│   │ criado_em          │
└────────────────────────┘


┌────────────────────────┐
│    COORTE_TREINO       │
├────────────────────────┤
│ PK│ caso_id            │
│   │ origem             │
│   │ semente            │
│   │ particao           │
│   │ idade              │
│   │ cid10              │
│   │ internacoes_ant    │
│   │ readmitido_30d     │
└────────────────────────┘


┌────────────────────────┐      ┌────────────────────────┐
│      USUARIO           │      │      REVISAO           │
├────────────────────────┤      ├────────────────────────┤
│ PK│ usuario_id         │      │ PK│ revisao_id         │
│   │ nome               │      │   │ classificacao_id ──┼──┐
│   │ papel              │      │   │ usuario_id      ───┼──┤
└────────────────────────┘      │   │ parecer            │  │
         ▲                       │   │ observacao         │  │
         │                       │   │ criado_em          │  │
         │ 1:N                   └────────────────────────┘  │
         │                                                    │
         └────────────────────────────────────────────────────┘


┌────────────────────────────────────────────────────────┐
│            VIEW: vw_marco_funcional                    │
├────────────────────────────────────────────────────────┤
│ Combina:                                               │
│ • classificacao (dados principais)                     │
│ • modelo (versão e faixas)                             │
│ • explicacao (texto e status)                          │
│                                                         │
│ Resultado: Vista consolidada para relatórios           │
└────────────────────────────────────────────────────────┘
```

---

## 🗂️ Schema Detalhado

### 1. LOTE_IMPORTACAO
**Propósito:** Rastrear importações de dados do SIH/SUS

```sql
CREATE TABLE lote_importacao (
  lote_id          INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome_arquivo     VARCHAR(255) NOT NULL,           -- ex: "dados_2024_02.csv"
  hash_sha256      CHAR(64) NOT NULL UNIQUE,        -- Integridade do arquivo
  competencia      CHAR(7),                         -- Format: "2024-02"
  total_registros  INT NOT NULL,                    -- Quantos registros
  total_colunas    INT NOT NULL,                    -- Quantas colunas
  importado_em     DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT ck_lote_totais CHECK (total_registros >= 0 AND total_colunas >= 0)
);

Índices:
  PRIMARY KEY: lote_id
  UNIQUE: hash_sha256
```

---

### 2. DIAGNOSTICO
**Propósito:** Catálogo de diagnósticos (CID-10)

```sql
CREATE TABLE diagnostico (
  cid10                  VARCHAR(8) NOT NULL PRIMARY KEY,  -- ex: "I50.0"
  descricao              VARCHAR(255),                     -- ex: "Insuficiência cardíaca"
  peso_risco_declarado   DECIMAL(4,2),                     -- 0.00 a 1.00
  validado_terminologia  TINYINT NOT NULL DEFAULT 0,       -- 0 ou 1
  
  CONSTRAINT ck_diag_validado CHECK (validado_terminologia IN (0, 1))
);

Índices:
  PRIMARY KEY: cid10
```

---

### 3. PACIENTE
**Propósito:** Dados do paciente (pseudonimizado)

```sql
CREATE TABLE paciente (
  paciente_id      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  pseudonimo       VARCHAR(64) NOT NULL UNIQUE,           -- Hash do ID real
  metodo_vinculo   VARCHAR(40) NOT NULL,                  -- Como foi vinculado
  criado_em        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
);

Índices:
  PRIMARY KEY: paciente_id
  UNIQUE: pseudonimo
```

---

### 4. INTERNACAO
**Propósito:** Registros de internação de cada paciente

```sql
CREATE TABLE internacao (
  internacao_id    INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  paciente_id      INT NOT NULL,                          -- FK → paciente
  cid10            VARCHAR(8),                            -- FK → diagnostico
  dt_internacao    DATE,                                  -- Data de entrada
  dt_saida         DATE,                                  -- Data de saída
  criado_em        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_internacao_paciente 
    FOREIGN KEY (paciente_id) REFERENCES paciente (paciente_id),
  CONSTRAINT fk_internacao_diagnostico 
    FOREIGN KEY (cid10) REFERENCES diagnostico (cid10)
);

Índices:
  PRIMARY KEY: internacao_id
  FOREIGN KEY: paciente_id
  FOREIGN KEY: cid10
```

---

### 5. REGISTRO_SIH
**Propósito:** Registros originais do SIH/SUS (dados brutos)

```sql
CREATE TABLE registro_sih (
  registro_id      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  lote_id          INT NOT NULL,                          -- FK → lote_importacao
  linha_origem     INT NOT NULL,                          -- Linha no arquivo original
  idade_anos       INT,                                   -- 60-120
  sexo             VARCHAR(2),                           -- 'M' ou 'F'
  diag_princ       VARCHAR(8),                           -- Código CID
  dt_inter         DATE,                                 -- Data internação
  dt_saida         DATE,                                 -- Data saída
  dias_perm        INT,                                  -- Dias de permanência
  morte            TINYINT,                              -- 0 ou 1
  elegivel_60      TINYINT NOT NULL DEFAULT 0,           -- Atende critério 60+
  internacao_id    INT,                                  -- FK → internacao (quando vinculado)
  
  CONSTRAINT fk_registro_lote 
    FOREIGN KEY (lote_id) REFERENCES lote_importacao (lote_id),
  CONSTRAINT fk_registro_internacao 
    FOREIGN KEY (internacao_id) REFERENCES internacao (internacao_id),
  CONSTRAINT uq_registro_linha UNIQUE (lote_id, linha_origem),
  CONSTRAINT ck_registro_elegivel CHECK (elegivel_60 IN (0, 1))
);

Índices:
  PRIMARY KEY: registro_id
  UNIQUE: (lote_id, linha_origem)
  FOREIGN KEY: lote_id
  FOREIGN KEY: internacao_id
```

---

### 6. MODELO
**Propósito:** Versões do modelo de machine learning

```sql
CREATE TABLE modelo (
  modelo_id                 INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  versao                    VARCHAR(60) NOT NULL UNIQUE,  -- ex: "v1.0.0"
  algoritmo                 VARCHAR(60) NOT NULL,         -- ex: "DecisionTree"
  tipo_coorte               VARCHAR(12) NOT NULL,         -- "SINTETICA" ou "REAL"
  versao_preprocessamento   VARCHAR(40) NOT NULL,         -- ex: "v1.0"
  hiperparametros           JSON NOT NULL,                -- {"max_depth": 4, ...}
  metricas                  JSON NOT NULL,                -- {"roc_auc": 0.67, ...}
  limite_baixo              DECIMAL(4,3) NOT NULL,        -- 0.333 (BAIXO)
  limite_alto               DECIMAL(4,3) NOT NULL,        -- 0.667 (ALTO)
  treinado_em               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT uq_modelo_versao UNIQUE (versao),
  CONSTRAINT ck_modelo_coorte CHECK (tipo_coorte IN ('SINTETICA', 'REAL')),
  CONSTRAINT ck_modelo_limites CHECK (limite_baixo > 0 AND limite_alto < 1)
);

Índices:
  PRIMARY KEY: modelo_id
  UNIQUE: versao
```

---

### 7. CLASSIFICACAO (⭐ Principal)
**Propósito:** Resultado de cada classificação de risco

```sql
CREATE TABLE classificacao (
  classificacao_id                 INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  modelo_id                        INT NOT NULL,                 -- FK → modelo
  paciente_ref                     VARCHAR(64),                  -- ID de negócio
  internacao_ref                   VARCHAR(64),                  -- ID de negócio
  internacao_id                    INT,                          -- FK → internacao
  entrada_json                     JSON NOT NULL,                -- Dados enviados
  idade                            INT,                          -- Extraído
  diagnostico_principal            VARCHAR(8),                   -- Extraído
  internacoes_anteriores_12_meses  INT,                          -- Extraído
  status                           VARCHAR(24) NOT NULL,         -- OK, ERRO_VALIDACAO, etc
  motivos                          JSON,                         -- {"erro": "msg"}
  risco_readmissao                 VARCHAR(8),                   -- BAIXO, MEDIO, ALTO
  probabilidade_estimada           DECIMAL(6,5),                 -- 0.00000 a 1.00000
  fatores_relevantes               JSON,                         -- Explanability
  criado_em                        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_class_modelo FOREIGN KEY (modelo_id) REFERENCES modelo,
  CONSTRAINT fk_class_internacao FOREIGN KEY (internacao_id) REFERENCES internacao,
  CONSTRAINT ck_class_status CHECK (status IN ('OK', 'ERRO_VALIDACAO', 'DADOS_INSUFICIENTES')),
  CONSTRAINT ck_class_risco CHECK (risco_readmissao IN ('BAIXO', 'MEDIO', 'ALTO')),
  CONSTRAINT ck_class_probabilidade CHECK (probabilidade_estimada BETWEEN 0 AND 1),
  CONSTRAINT ck_class_status_risco CHECK (
    (status = 'OK' AND risco_readmissao IS NOT NULL) OR
    (status <> 'OK' AND risco_readmissao IS NULL)
  )
);

Índices:
  PRIMARY KEY: classificacao_id
  FOREIGN KEY: modelo_id
  FOREIGN KEY: internacao_id
  INDEX: criado_em (para ordenação)
  INDEX: status (para filtros)
```

---

### 8. EXPLICACAO
**Propósito:** Explicações geradas por LLM

```sql
CREATE TABLE explicacao (
  explicacao_id     INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  classificacao_id  INT NOT NULL UNIQUE,                  -- 1:1 com classificacao
  texto             TEXT NOT NULL,                       -- Explicação completa
  status            VARCHAR(24) NOT NULL,                -- GERADA, INDISPONIVEL, etc
  origem            VARCHAR(8) NOT NULL,                 -- GEMINI, RESERVA
  versao_prompt     VARCHAR(20) NOT NULL,                -- v1.0, v1.1, etc
  modelo_llm        VARCHAR(80),                         -- ex: "gemini-pro"
  latencia_ms       INT,                                 -- Tempo de resposta
  tentativas        INT NOT NULL DEFAULT 0,              -- Quantas tentativas
  detalhe_falha     VARCHAR(255),                        -- Motivo da falha
  criado_em         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_explicacao_class 
    FOREIGN KEY (classificacao_id) REFERENCES classificacao,
  CONSTRAINT uq_explicacao_class UNIQUE (classificacao_id),
  CONSTRAINT ck_explicacao_status 
    CHECK (status IN ('GERADA', 'INDISPONIVEL', 'FORA_DO_CONTRATO')),
  CONSTRAINT ck_explicacao_origem 
    CHECK (origem IN ('GEMINI', 'RESERVA'))
);

Índices:
  PRIMARY KEY: explicacao_id
  UNIQUE: classificacao_id (1:1)
  FOREIGN KEY: classificacao_id
```

---

### 9. USUARIO
**Propósito:** Usuários que fazem revisão humana

```sql
CREATE TABLE usuario (
  usuario_id  INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(120) NOT NULL,                     -- ex: "Dr. João Silva"
  papel       VARCHAR(40) NOT NULL,                      -- ex: "Revisor Clínico"
);

Índices:
  PRIMARY KEY: usuario_id
```

---

### 10. REVISAO
**Propósito:** Revisão humana das classificações

```sql
CREATE TABLE revisao (
  revisao_id        INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  classificacao_id  INT NOT NULL,                        -- FK → classificacao
  usuario_id        INT NOT NULL,                        -- FK → usuario
  parecer           VARCHAR(16) NOT NULL,                -- CONCORDA, DISCORDA, etc
  observacao        TEXT,                                -- Comentários
  criado_em         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_revisao_class 
    FOREIGN KEY (classificacao_id) REFERENCES classificacao,
  CONSTRAINT fk_revisao_usuario 
    FOREIGN KEY (usuario_id) REFERENCES usuario,
  CONSTRAINT ck_revisao_parecer 
    CHECK (parecer IN ('CONCORDA', 'DISCORDA', 'INCONCLUSIVO'))
);

Índices:
  PRIMARY KEY: revisao_id
  FOREIGN KEY: classificacao_id
  FOREIGN KEY: usuario_id
```

---

### 11. COORTE_TREINO
**Propósito:** Dados de treino/teste do modelo

```sql
CREATE TABLE coorte_treino (
  caso_id                          INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  origem                           VARCHAR(12) NOT NULL,        -- SINTETICA ou REAL
  semente                          INT NOT NULL,                -- Random seed
  particao                         VARCHAR(8) NOT NULL,         -- TREINO ou TESTE
  idade                            INT NOT NULL,                -- >= 60
  cid10                            VARCHAR(8) NOT NULL,         -- Diagnóstico
  internacoes_anteriores_12_meses  INT NOT NULL,                -- >= 0
  readmitido_30d                   TINYINT NOT NULL,            -- 0 ou 1 (target)
  
  CONSTRAINT ck_coorte_origem 
    CHECK (origem IN ('SINTETICA', 'REAL')),
  CONSTRAINT ck_coorte_particao 
    CHECK (particao IN ('TREINO', 'TESTE')),
  CONSTRAINT ck_coorte_idade CHECK (idade >= 60),
  CONSTRAINT ck_coorte_historico CHECK (internacoes_anteriores_12_meses >= 0),
  CONSTRAINT ck_coorte_rotulo CHECK (readmitido_30d IN (0, 1))
);

Índices:
  PRIMARY KEY: caso_id
```

---

### 12. VIEW: vw_marco_funcional

**Propósito:** Vista consolidada para relatórios

```sql
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
```

---

## 📈 Statísticas do Schema

| Métrica | Valor |
|---------|-------|
| Total de tabelas | 11 |
| Total de views | 1 |
| Total de colunas | 98 |
| Chaves primárias | 11 |
| Chaves estrangeiras | 8 |
| Constraints CHECK | 15 |
| Índices recomendados | 8+ |

---

## 🔄 Relacionamentos

```
1:N Relationships:
  lote_importacao         → registro_sih
  paciente                → internacao
  internacao              → classificacao
  modelo                  → classificacao
  classificacao           → explicacao (1:1)
  classificacao           → revisao (1:N)
  usuario                 → revisao (1:N)

0..1:N Relationships:
  internacao              → registro_sih (nullable)
  diagnostico             → internacao (nullable)
```

---

## 🔑 Estratégia de Chaves

### Primary Keys
- Auto-increment INT
- Único e obrigatório
- Não reutiliza valores deletados

### Foreign Keys
- Referência integridade referencial
- DELETE: CASCADE (para auditoria) ou RESTRICT
- UPDATE: RESTRICT (histórico imutável)

### Natural Keys
- (lote_id, linha_origem) → Única combinação
- hash_sha256 → Integridade

---

## 🔐 Backup & Recovery

```sql
-- Backup full database
mysqldump -u root -p tia_fase2 > tia_fase2_backup.sql

-- Backup com locks
mysqldump -u root -p --lock-tables tia_fase2 > backup.sql

-- Restore
mysql -u root -p tia_fase2 < tia_fase2_backup.sql
```

---

## 📊 Crescimento de Dados

```
Estimativa de volume (1 ano de operação):

lote_importacao:        12 registros (1 por mês)
registro_sih:           ~50.000 registros (4.000/mês)
diagnostico:            ~500 registros (estável)
paciente:               ~10.000 registros
internacao:             ~15.000 registros
classificacao:          ~50.000 registros (crescimento)
explicacao:             ~45.000 registros (pode falhar)
usuario:                ~10 registros (estável)
revisao:                ~25.000 registros (crescimento)
coorte_treino:          ~10.000 registros (estável)

Total estimado: ~200.000 registros
Tamanho: ~50 MB (comprimido)
```

---

**Próximo documento:** Guia Técnico de Implementação e APIs
