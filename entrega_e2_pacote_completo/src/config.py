import os
from pathlib import Path
from dataclasses import dataclass
ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Config:
    api_key: str
    model: str
    db: dict

def carregar():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=False)
    required = ["GEMINI_API_KEY", "GEMINI_MODEL", "MYSQL_USER", "MYSQL_PASSWORD"]
    missing = [k for k in required if not os.getenv(k, "").strip()]
    if missing:
        raise ValueError("Configure no .env: " + ", ".join(missing))
    db = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.environ["MYSQL_USER"], "password": os.environ["MYSQL_PASSWORD"],
        "database": os.getenv("MYSQL_DATABASE", "tia_e2"),
        "connection_timeout": 10, "autocommit": False}
    if os.getenv("MYSQL_REQUIRE_TLS") == "1":
        ca = os.getenv("MYSQL_SSL_CA", "")
        if not ca or not Path(ca).is_file():
            raise ValueError("Certificado CA obrigatório para MySQL remoto")
        db.update(ssl_ca=ca, ssl_verify_cert=True, ssl_verify_identity=True)
    return Config(os.environ["GEMINI_API_KEY"], os.environ["GEMINI_MODEL"], db)
