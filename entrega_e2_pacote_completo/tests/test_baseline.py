import json
import unittest
from unittest.mock import patch, MagicMock
from src.config import ROOT
from src.main import carregar_dados, main
from src.ai_engine import validar_resposta
class TestBaseline(unittest.TestCase):
    def test_massa(self):
        self.assertEqual(len(carregar_dados(ROOT / "data/casos_sinteticos.json")), 3)
    def test_contrato(self):
        self.assertEqual(validar_resposta('{"resumo":"Exemplo","limitacoes":["Sintético"]}')["resumo"], "Exemplo")
    def test_invalido(self):
        for text in ['{}','{"resumo":"","limitacoes":[]}', '{"resumo":"x","limitacoes":["x"],"probabilidade":0.95}', 'não JSON']:
            with self.assertRaises(ValueError):
                validar_resposta(text)
    @patch("src.main.sys.argv", ["main", "--validar-dados"])
    @patch("src.main.carregar")
    def test_validacao_sem_servicos(self, config):
        self.assertEqual(main(), 0)
        config.assert_not_called()
    def test_pii_rejeitada(self):
        dado={"caso_id":"SINT_001","origem":"SINTETICA","idade":75,
        "diagnostico_principal":"I50.0","internacoes_anteriores_12_meses":2,"nome":"Pessoa"}
        path=MagicMock()
        path.read_text.return_value=json.dumps([dado])
        with self.assertRaises(ValueError):
            carregar_dados(path)
if __name__ == "__main__":
    unittest.main()
