SELECT execucao_id, caso_id, modelo, versao_prompt, criado_em, resposta_sha256 FROM baseline_execucao ORDER BY criado_em DESC;
SELECT execucao_id, entrada_json, resposta_bruta, resposta_json FROM baseline_execucao ORDER BY criado_em DESC;
