import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from .config import ROOT, carregar
from .ai_engine import AIEngine, PROMPT_VERSION
from .database import Database

def carregar_dados(path):
    dados = json.loads(path.read_text(encoding="utf-8"))
    campos = {"caso_id", "origem", "idade", "diagnostico_principal", "internacoes_anteriores_12_meses"}
    if not isinstance(dados, list) or not dados:
        raise ValueError("Massa de teste vazia ou inválida")
    ids = set()
    for d in dados:
        if not isinstance(d, dict) or set(d) != campos or d["origem"] != "SINTETICA":
            raise ValueError("Use somente o contrato sintético, sem campos livres ou PII")
        if not isinstance(d["caso_id"], str) or not re.fullmatch(r"SINT_[0-9]{3}", d["caso_id"]) or d["caso_id"] in ids:
            raise ValueError("Identificador sintético inválido ou duplicado")
        ids.add(d["caso_id"])
        if type(d["idade"]) is not int or not 60 <= d["idade"] <= 120:
            raise ValueError("Idade fora do contrato 60 a 120")
        n = d["internacoes_anteriores_12_meses"]
        if type(n) is not int or not 0 <= n <= 100:
            raise ValueError("Histórico inválido")
        if not isinstance(d["diagnostico_principal"], str) or not re.fullmatch(r"[A-Z][0-9]{2}(?:\.?[0-9A-Z]{1,2})?", d["diagnostico_principal"]):
            raise ValueError("Formato CID inválido")
    return dados

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validar-dados", action="store_true")
    args = parser.parse_args()
    db = ai = None
    try:
        dados = carregar_dados(ROOT / "data/casos_sinteticos.json")
        if args.validar_dados:
            print(f"{len(dados)} casos válidos. Sem chamada externa.")
            return 0
        config = carregar()
        db = Database(config)
        db.inicializar()
        ai = AIEngine(config)
        relatorio = {"inicio_utc": datetime.now(timezone.utc).isoformat(), "casos": []}
        for dado in dados:
            eid = str(uuid.uuid4())
            try:
                bruto, obj = ai.processar(dado)
                entrada = json.dumps(dado, ensure_ascii=False, sort_keys=True)
                registro = {"execucao_id": eid, "caso_id": dado["caso_id"],
                    "entrada_json": entrada, "resposta_bruta": bruto,
                    "resposta_json": json.dumps(obj, ensure_ascii=False),
                    "modelo": config.model, "versao_prompt": PROMPT_VERSION,
                    "entrada_sha256": hashlib.sha256(entrada.encode()).hexdigest(),
                    "resposta_sha256": hashlib.sha256(bruto.encode()).hexdigest()}
                db.salvar(registro)
                relatorio["casos"].append({"caso_id": dado["caso_id"], "execucao_id": eid,
                    "status": "PERSISTIDO_E_RELIDO", "modelo": config.model,
                    "resposta_sha256": registro["resposta_sha256"]})
            except Exception as exc:
                relatorio["casos"].append({"caso_id": dado["caso_id"],
                    "status": "FALHA", "tipo_erro": type(exc).__name__,
                    "detalhe_erro": str(exc)[:300]})
        ok = all(c["status"] == "PERSISTIDO_E_RELIDO" for c in relatorio["casos"])
        relatorio["sucesso"] = ok
        destino = ROOT / "docs/evidencias" / (str(uuid.uuid4()) + ".json")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Relatório: {destino}. Sucesso integral: {ok}")
        return 0 if ok else 1
    except Exception as exc:
        print(f"Execução não concluída ({type(exc).__name__}). Confira dependências, .env, permissões e serviços.")
        return 1
    finally:
        if ai is not None:
            ai.close()
        if db is not None:
            db.close()

if __name__ == "__main__":
    sys.exit(main())
