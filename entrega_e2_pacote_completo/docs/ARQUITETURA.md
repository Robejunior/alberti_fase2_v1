# Arquitetura mínima
```mermaid
flowchart LR
 D[data/casos_sinteticos.json] --> M[src/main.py]
 C[src/config.py e .env local] --> M
 M --> A[src/ai_engine.py]
 A --> G[Gemini API / SDK google-genai]
 G --> A
 A --> V[Validação JSON]
 V --> B[src/database.py]
 B --> S[(MySQL baseline_execucao)]
 S --> R[SELECT após commit]
 R --> E[docs/evidencias]
```
A tabela guarda UUID, caso sintético, entrada JSON, resposta bruta, resposta JSON,
modelo, versão do prompt, hashes SHA256 e horário do servidor.
Não reutiliza classificacao, evitando misturar demonstração LLM com prognóstico clínico.
SQL parametrizado. Segredos somente por ambiente. Sem fallback que simule sucesso.
Falhas não recebem status de persistência confirmada.
