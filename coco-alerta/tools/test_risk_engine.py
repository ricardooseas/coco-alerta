import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "wokwi"))

from risk_engine import simular_sequencia


class TesteRisco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pacote = json.loads((RAIZ / "shared" / "limites.json").read_text(encoding="utf-8"))
        cls.wokwi = json.loads((RAIZ / "wokwi" / "limites.json").read_text(encoding="utf-8"))
        cls.casos = json.loads((RAIZ / "tools" / "casos.json").read_text(encoding="utf-8"))

    def test_arquivos_de_limites_iguais(self):
        self.assertEqual(self.pacote, self.wokwi)

    def test_cenarios(self):
        limites = self.pacote["limites"]
        persistencia = self.pacote["persistencia_leituras"]
        for caso in self.casos["casos"]:
            with self.subTest(caso=caso["nome"]):
                obtido = simular_sequencia(caso["sequencia"], limites, persistencia)
                self.assertEqual(obtido, caso["esperado"])


if __name__ == "__main__":
    unittest.main()
