"""Painel local E2 com formulário conectado à API de classificação existente."""
import json
import os
import re
import secrets
import socket
import threading
import time
from http.cookies import SimpleCookie
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .config import ROOT

# Usuário/senha vêm de variáveis de ambiente definidas no serviço systemd —
# nunca ficam gravados neste arquivo nem versionados no Git. Os valores
# abaixo só entram em uso se essas variáveis não existirem no ambiente.
PAINEL_USUARIO = os.environ.get("PAINEL_USUARIO", "aluno")
PAINEL_SENHA = os.environ.get("PAINEL_SENHA", "troque-esta-senha")

# Sessão de login baseada em cookie (substitui o HTTP Basic Auth): permite
# um botão "Sair" de verdade, algo que o Basic Auth não oferece — o
# navegador guarda a credencial até ser fechado, sem nenhuma forma limpa de
# descartá-la. Aqui, autenticar gera um token aleatório guardado só em
# memória (reinicia o serviço, todo mundo precisa logar de novo).
NOME_COOKIE = "tia_sessao"
DURACAO_SESSAO_SEGUNDOS = 12 * 60 * 60  # 12 horas
_SESSOES = {}
_SESSOES_LOCK = threading.Lock()

def _nova_sessao():
    token = secrets.token_urlsafe(32)
    with _SESSOES_LOCK:
        _SESSOES[token] = time.time() + DURACAO_SESSAO_SEGUNDOS
    return token

def _sessao_valida(token):
    if not token:
        return False
    with _SESSOES_LOCK:
        validade = _SESSOES.get(token)
        if validade is None:
            return False
        if time.time() > validade:
            _SESSOES.pop(token, None)
            return False
    return True

def _encerrar_sessao(token):
    with _SESSOES_LOCK:
        _SESSOES.pop(token, None)

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

# Arquivos estáticos servidos sem exigir login (a própria tela de login
# precisa deles, e não há dado sensível no HTML/CSS/JS em si).
ROTAS_PUBLICAS = {
    "/login": ("login.html", "text/html"),
    "/login.js": ("login.js", "text/javascript"),
    "/style.css": ("style.css", "text/css"),
    "/app.js": ("app.js", "text/javascript"),
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass

    def _token_sessao(self):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get("Cookie", ""))
        except Exception:
            return None
        item = cookies.get(NOME_COOKIE)
        return item.value if item else None

    def _logado(self):
        return _sessao_valida(self._token_sessao())

    def _definir_cookie_sessao(self, token):
        self.send_header("Set-Cookie", f"{NOME_COOKIE}={token}; Path=/; Max-Age={DURACAO_SESSAO_SEGUNDOS}; HttpOnly; SameSite=Lax")

    def _limpar_cookie_sessao(self):
        self.send_header("Set-Cookie", f"{NOME_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")

    def _negar_acesso_api(self):
        corpo = json.dumps({"sucesso": False, "erro": "Sessão expirada ou não autenticada. Atualize a página."}, ensure_ascii=False).encode("utf-8")
        self.send_response(401)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def _responder(self, status, data, mime):
        self.send_response(status)
        self.send_header("Content-Type", mime+"; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(data)

    def _tratar_login(self):
        if self.headers.get("Host") not in HOSTS_PERMITIDOS:
            self.send_error(403); return
        try:
            comprimento = int(self.headers.get("Content-Length", "0"))
            if not 0 < comprimento <= 1024 or self.headers.get_content_type() != "application/json":
                raise ValueError()
            dado = json.loads(self.rfile.read(comprimento))
            usuario, senha = dado.get("usuario"), dado.get("senha")
            if not isinstance(usuario, str) or not isinstance(senha, str):
                raise ValueError()
        except (ValueError, TypeError):
            corpo = json.dumps({"sucesso": False, "erro": "Dados inválidos."}, ensure_ascii=False).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers(); self.wfile.write(corpo); return

        if usuario == PAINEL_USUARIO and senha == PAINEL_SENHA:
            token = _nova_sessao()
            corpo = json.dumps({"sucesso": True}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._definir_cookie_sessao(token)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers(); self.wfile.write(corpo)
        else:
            corpo = json.dumps({"sucesso": False, "erro": "Usuário ou senha incorretos."}, ensure_ascii=False).encode("utf-8")
            self.send_response(401)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers(); self.wfile.write(corpo)

    def do_POST(self):
        if self.path == "/login":
            self._tratar_login(); return
        if not self._logado():
            self._negar_acesso_api(); return
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
        if self.headers.get("Host") not in HOSTS_PERMITIDOS:
            self.send_error(403); return

        if self.path == "/logout":
            token = self._token_sessao()
            if token:
                _encerrar_sessao(token)
            self.send_response(302)
            self.send_header("Location", "/login")
            self._limpar_cookie_sessao()
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if self.path in ROTAS_PUBLICAS:
            nome, mime = ROTAS_PUBLICAS[self.path]
            self._responder(200, (ROOT/"web"/nome).read_bytes(), mime)
            return

        logado = self._logado()

        if self.path == "/":
            if not logado:
                self.send_response(302)
                self.send_header("Location", "/login")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            self._responder(200, (ROOT/"web"/"index.html").read_bytes(), "text/html")
            return

        if self.path in ("/api/usuarios", "/api/pendentes"):
            if not logado:
                self._negar_acesso_api(); return
            endpoint={"/api/usuarios":"usuarios","/api/pendentes":"revisao/pendentes?limite=100"}[self.path]
            try:
                with urlopen("http://127.0.0.1:5000/api/v1/"+endpoint,timeout=15) as response:
                    data=response.read()
                json.loads(data)
            except (OSError,ValueError):
                data=json.dumps({"sucesso":False,"erro":"Não foi possível consultar a API da porta 5000."}).encode()
            self._responder(200, data, "application/json")
            return

        if self.path == "/api/painel":
            if not logado:
                self._negar_acesso_api(); return
            data=json.dumps(snapshot(),ensure_ascii=False).encode("utf-8")
            self._responder(200, data, "application/json")
            return

        self.send_error(404)

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
