import json
import time

PROMPT_VERSION = "e2-v1"
PROMPT = """Demonstração acadêmica de integração com dados inteiramente sintéticos.
Resuma em português os campos recebidos e descreva limitações dos dados para estudar
readmissão. Não estime probabilidades, não classifique risco clínico, não recomende
tratamentos e não acrescente fatos. Retorne um objeto JSON com exatamente duas chaves:
resumo (texto não vazio) e limitacoes (lista não vazia de textos).
Dados: """

MAX_TENTATIVAS = 3
ESPERA_BASE_SEGUNDOS = 2  # 2s, 4s, 8s (backoff exponencial)


def validar_resposta(texto):
    obj = json.loads(texto)
    if not isinstance(obj, dict) or set(obj) != {"resumo", "limitacoes"}:
        raise ValueError("Contrato de resposta inválido")
    if not isinstance(obj["resumo"], str) or not obj["resumo"].strip():
        raise ValueError("Resumo vazio")
    if (not isinstance(obj["limitacoes"], list) or not obj["limitacoes"]
        or any(not isinstance(x, str) or not x.strip() for x in obj["limitacoes"])):
        raise ValueError("Limitações inválidas")
    return obj


class AIEngine:
    def __init__(self, config):
        from google import genai
        from google.genai import types
        self.client = genai.Client(api_key=config.api_key,
                                  http_options=types.HttpOptions(timeout=60000))
        self.model = config.model

    def processar(self, dado):
        # O Gemini (sobretudo modelos "flash" recém-lançados) pode devolver
        # 503 UNAVAILABLE em picos de demanda, que costumam ser passageiros.
        # Erros de cliente (4xx: chave inválida, modelo inexistente, payload
        # malformado) não são retentados — só re-tentamos erro de servidor (5xx).
        from google.genai import errors as genai_errors

        ultimo_erro = None
        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                resposta = self.client.models.generate_content(
                    model=self.model, contents=PROMPT + json.dumps(dado, ensure_ascii=False),
                    config={"response_mime_type": "application/json", "temperature": 0})
                texto = resposta.text
                if not texto:
                    raise ValueError("Gemini não retornou texto")
                return texto, validar_resposta(texto)
            except genai_errors.ServerError as exc:
                ultimo_erro = exc
                if tentativa < MAX_TENTATIVAS:
                    time.sleep(ESPERA_BASE_SEGUNDOS * (2 ** (tentativa - 1)))
                    continue
                raise

        raise ultimo_erro

    def close(self):
        self.client.close()
