import sys
from pathlib import Path

# Adiciona a pasta 'codigo' no PYTHONPATH para permitir importação
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "codigo"))

import unittest
from calculator import MP10Calculator, O3Calculator, IQAR_MAXIMO

class TestCalculator(unittest.TestCase):
    """
    Testes automatizados para a camada de calculadoras de poluentes (Padrão Strategy).
    Requisito da Sprint 4: Mínimo de 3 casos por método (sucesso, falha/limite, edge case).
    """

    def setUp(self):
        self.calc_mp10 = MP10Calculator()
        self.calc_o3 = O3Calculator()

    # --- Testes para MP10Calculator ---

    def test_mp10_sucesso_faixa_normal(self):
        """Caso 1 (Sucesso): Concentração no meio de uma faixa (Boa)."""
        # Faixa Boa para MP10: 0 a 50. IQAr: 0 a 40.
        # Interpolação: se for 25.0, IQAr deve ser 20.
        iqar, faixa = self.calc_mp10.calcular(25.0)
        self.assertEqual(iqar, 20)
        self.assertEqual(faixa, "Boa")

    def test_mp10_edge_case_fronteira(self):
        """Caso 2 (Edge Case): Concentração exata no limite entre duas faixas."""
        # Limite exato de 50.0 no MP10. A faixa Boa vai até 50.0 (IQAr 40).
        iqar, faixa = self.calc_mp10.calcular(50.0)
        self.assertEqual(iqar, 40)
        self.assertEqual(faixa, "Boa")

    def test_mp10_falha_extremo_superior(self):
        """Caso 3 (Falha/Extremo): Concentração absurdamente alta."""
        # Limite máximo da tabela de MP10 é 600.0. Concentrações acima devem retornar 
        # o IQAR_MAXIMO e faixa "Péssima", sem quebrar o sistema.
        iqar, faixa = self.calc_mp10.calcular(9999.0)
        self.assertEqual(iqar, IQAR_MAXIMO)
        self.assertEqual(faixa, "Péssima")

    # --- Testes para O3Calculator (para cobrir 2 classes diferentes do Strategy) ---

    def test_o3_sucesso_faixa_ruim(self):
        """Caso 1 (Sucesso): Concentração no meio da faixa Ruim."""
        # Faixa Ruim para O3: 130 a 160. IQAr: 80 a 120.
        # Concentração 145 deve retornar IQAr no meio, ou seja, 100.
        iqar, faixa = self.calc_o3.calcular(145.0)
        self.assertEqual(iqar, 100)
        self.assertEqual(faixa, "Ruim")

    def test_o3_edge_case_zero(self):
        """Caso 2 (Edge Case): Concentração zero absoluta."""
        iqar, faixa = self.calc_o3.calcular(0.0)
        self.assertEqual(iqar, 0)
        self.assertEqual(faixa, "Boa")

    def test_o3_extremo_superior(self):
        """Caso 3 (Falha/Extremo): Concentração acima do breakpoint final."""
        iqar, faixa = self.calc_o3.calcular(1000.0) # Breakpoint final é 800.0
        self.assertEqual(iqar, IQAR_MAXIMO)
        self.assertEqual(faixa, "Péssima")

if __name__ == "__main__":
    unittest.main()
