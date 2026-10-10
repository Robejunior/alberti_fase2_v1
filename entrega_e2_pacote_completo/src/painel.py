"""Painel local E2 com formulário conectado à API de classificação existente."""
import base64
import json
import os
import re
import socket
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .config import ROOT

# Autenticação básica (HTTP Basic Auth) para restringir o acesso ao painel.
# Usuário/senha vêm de variáveis de ambiente definidas no serviço systemd —
# nunca ficam gravados neste arquivo nem versionados no Git. Os valores
# abaixo só entram em uso se essas variáveis não existirem no ambiente.
PAINEL_USUARIO = os.environ.get("PAINEL_USUARIO", "aluno")
PAINEL_SENHA = os.environ.get("PAINEL_SENHA", "troque-esta-senha")

def snapshot():
    """Resumo para a aba 'Explorador de Resultados': relatórios locais do
    pipeline Colab + classificações/explicações/pareceres reais, consultados
    direto da API de Prognóstico (porta 5000), que é quem efetivamente grava
    tudo isso no MySQL (tia_fase2). Não há mais uma segunda conexão direta
    ao banco aqui — uma única fonte de verdade evita os dois ficarem
    dessincronizados."""
    result = {"online": False, "registros": [], "relatorios": [], "erro": None}
    for p in sorted((ROOT/"docs/evidencias").glob("*.json"), key=lambda p:p.stat().st_mtime, reverse=True)[:30]:
        try:
            r=json.loads(p.read_text(encoding="utf-8"))
            result["relatorios"].append({"data":r.get("inicio_utc"),"sucesso":r.get("sucesso") is True,
                "casos":[{"caso":c.get("caso_id"),"status":c.get("status")} for c in r.get("casos",[])]})
        except (ValueError,OSError): pass
    try:
        with urlopen("http://127.0.0.1:5000/api/v1/classificacoes?limite=200", timeout=15) as response:
            payload=json.load(response)
        if not payload.get("sucesso"):
            raise ValueError(payload.get("erro") or "A API não confirmou a consulta.")
        result.update(online=True, registros=(payload.get("dados") or {}).get("classificacoes") or [])
    except HTTPError as exc:
        try:
            corpo=json.load(exc)
            result["erro"]=corpo.get("erro") or f"A API retornou HTTP {exc.code}."
        except (ValueError, OSError):
            result["erro"]=f"A API retornou HTTP {exc.code}."
    except (URLError, OSError):
        result["erro"]="API de classificação indisponível na porta 5000. Confira se api_fase3/app.py está rodando."
    except ValueError as e:
        result["erro"]=str(e) or "Não foi possível consultar as classificações."
    return result

def validar_avaliacao(dado):
    campos={"paciente_id","idade","diagnostico_principal","internacoes_anteriores_12_meses"}
    if not isinstance(dado,dict) or set(dado)!=campos:
        raise ValueError("Campos inválidos")
    if not isinstance(dado["paciente_id"],str) or not re.fullmatch(r"(?:SINT|PAC)_[0-9]{3}",dado["paciente_id"]):
        raise ValueError("Identificador sintético inválido")
    for campo,baixo,alto in [("idade",60,120),("internacoes_anteriores_12_meses",0,100)]:
        if type(dado[campo]) is not int or not baixo<=dado[campo]<=alto:
            raise ValueError("Número inválido")
    if not isinstance(dado["diagnostico_principal"],str) or not re.fullmatch(r"[A-Z][0-9]{2}(?:\.?[0-9A-Z]{1,2})?",dado["diagnostico_principal"]):
        raise ValueError("CID inválido")

# Lista de "Host" aceitos — proteção contra DNS rebinding. Inclui o IP
# público do servidor Hetzner para permitir acesso externo ao painel.
HOSTS_PERMITIDOS = ("127.0.0.1:8503", "localhost:8503", "204.168.165.21:8503")

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass

    def _autenticado(self):
        """Confere usuário/senha enviados via HTTP Basic Auth."""
        cabecalho = self.headers.get("Authorization", "")
        if not cabecalho.startswith("Basic "):
            return False
        try:
            usuario, _, senha = base64.b64decode(cabecalho[6:]).decode("utf-8").partition(":")
        except (ValueError, UnicodeDecodeError):
            return False
        return usuario == PAINEL_USUARIO and senha == PAINEL_SENHA

    def _exigir_login(self):
        corpo = "Acesso restrito ao Projeto Integrador (TIA). Informe usuário e senha.".encode("utf-8")
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="TIA - Acesso restrito"')
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_POST(self):
        if not self._autenticado():
            self._exigir_login(); return
        allowed = HOSTS_PERMITIDOS
        if self.headers.get("Host") not in allowed or self.headers.get("Origin") not in tuple("http://"+h for h in allowed):
            self.send_error(403); return
        if self.path not in ("/api/validar", "/api/avaliar", "/api/revisao", "/api/usuarios"):
            self.send_error(404); return
        status = 200
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096 or self.headers.get_content_type() != "application/json":
                raise ValueError("Envie os campos do formulário em JSON.")
            dado = json.loads(self.rfile.read(length))
            if self.path in ("/api/validar", "/api/avaliar"):
                validar_avaliacao(dado)
            elif self.path == "/api/usuarios":
                if not isinstance(dado,dict) or set(dado)!={"nome","papel"} or not isinstance(dado["nome"],str) or not 1<=len(dado["nome"].strip())<=100 or dado["papel"] not in ("medico","enfermeiro","pesquisador","outro"):
                    raise ValueError()
            else:
                if not isinstance(dado,dict) or set(dado)!={"classificacao_id","usuario_id","parecer","observacao"}:
                    raise ValueError()
                if any(type(dado[k]) is not int or dado[k]<=0 for k in ("classificacao_id","usuario_id")) or dado["parecer"] not in ("CONCORDA","DISCORDA","INCONCLUSIVO") or not isinstance(dado["observacao"],str) or len(dado["observacao"])>2000:
                    raise ValueError()
            if self.path == "/api/validar":
                result = {"sucesso": True, "mensagem": "Dados válidos. Nenhuma avaliação foi executada."}
            else:
                endpoint={"/api/avaliar":"classificar","/api/revisao":"revisao","/api/usuarios":"usuarios"}[self.path]
                req = Request("http://127.0.0.1:5000/api/v1/"+endpoint, data=json.dumps(dado).encode(), headers={"Content-Type":"application/json"}, method="POST")
                with urlopen(req, timeout=120) as response:
                    result = json.load(response)
                if not isinstance(result, dict) or not result.get("sucesso"):
                    raise ValueError("A API não confirmou a avaliação.")
        except (ValueError, TypeError):
            status=400; result={"sucesso":False,"erro":"Dados inválidos. Confira os campos obrigatórios e seus limites."}
        except HTTPError as exc:
            status=502; result={"sucesso":False,"erro":f"A API de avaliação retornou HTTP {exc.code}. Confira o terminal da API antes de repetir."}
        except (TimeoutError, socket.timeout):
            status=504; result={"sucesso":False,"erro":"Tempo de espera excedido. A avaliação pode ter sido salva; confira a API antes de repetir."}
        except (URLError, OSError):
            status=503; result={"sucesso":False,"erro":"API de risco indisponível. Inicie src/app.py na porta 5000."}
        data=json.dumps(result,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers();self.wfile.write(data)

    def do_GET(self):
        if not self._autenticado():
            self._exigir_login(); return
        if self.headers.get("Host") not in HOSTS_PERMITIDOS:
            self.send_error(403); return
        routes={"/":("index.html","text/html"),"/style.css":("style.css","text/css"),"/app.js":("app.js","text/javascript")}
        if self.path in ("/api/usuarios", "/api/pendentes"):
            endpoint={"/api/usuarios":"usuarios","/api/pendentes":"revisao/pendentes?limite=100"}[self.path]
            try:
                with urlopen("http://127.0.0.1:5000/api/v1/"+endpoint,timeout=15) as response:
                    data=response.read()
                json.loads(data)
            except (OSError,ValueError):
                data=json.dumps({"sucesso":False,"erro":"Não foi possível consultar a API da porta 5000."}).encode()
            mime="application/json"
        elif self.path=="/api/painel":
            data=json.dumps(snapshot(),ensure_ascii=False).encode("utf-8");mime="application/json"
        elif self.path in routes:
            name,mime=routes[self.path];data=(ROOT/"web"/name).read_bytes()
        else:
            self.send_error(404);return
        self.send_response(200)
        self.send_header("Content-Type",mime+"; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers();self.wfile.write(data)

class PainelServer(ThreadingHTTPServer):
    allow_reuse_address = False
    def server_bind(self):
        if hasattr(socket,"SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()

if __name__=="__main__":
    servidor=PainelServer(("0.0.0.0",8503),Handler)
    print("Painel E2: http://204.168.165.21:8503 (ou http://127.0.0.1:8503 localmente) — Ctrl+C para encerrar",flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
