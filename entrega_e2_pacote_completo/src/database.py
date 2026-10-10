import json
from .config import ROOT

class Database:
    def __init__(self, config):
        import mysql.connector
        self.conn = mysql.connector.connect(**config.db)

    def inicializar(self):
        with self.conn.cursor() as cur:
            cur.execute((ROOT / "src/schema.sql").read_text(encoding="utf-8"))
        self.conn.commit()

    def salvar(self, registro):
        sql = """INSERT INTO baseline_execucao
        (execucao_id, caso_id, entrada_json, resposta_bruta, resposta_json, modelo,
         versao_prompt, entrada_sha256, resposta_sha256)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        keys = ["execucao_id", "caso_id", "entrada_json", "resposta_bruta",
                "resposta_json", "modelo", "versao_prompt", "entrada_sha256", "resposta_sha256"]
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, tuple(registro[k] for k in keys))
            self.conn.commit()
            with self.conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT * FROM baseline_execucao WHERE execucao_id=%s",
                            (registro["execucao_id"],))
                salvo = cur.fetchone()
            if (not salvo or salvo["resposta_bruta"] != registro["resposta_bruta"]
                or json.loads(salvo["entrada_json"]) != json.loads(registro["entrada_json"])
                or json.loads(salvo["resposta_json"]) != json.loads(registro["resposta_json"])):
                raise ValueError("Leitura após commit não confirmou os dados")
            return salvo["execucao_id"]
        except Exception:
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()
