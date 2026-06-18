import sys
from pathlib import Path

# Adiciona a pasta 'codigo' no PYTHONPATH para permitir importação
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "codigo"))

import unittest
from consolidador import consolidar, IndiceDiario
from reader import Medicao

class TestConsolidador(unittest.TestCase):
    """
    Testes automatizados para a função consolidar() (Camada de Processamento).
    Requisito da Sprint 4: Mínimo de 3 casos por método (sucesso, falha/limite, edge case).
    """

    def test_consolidar_sucesso_multiplos_poluentes(self):
        """Caso 1 (Sucesso): Consolidação de vários poluentes para a mesma estação/data."""
        medicoes = [
            Medicao(data="2020-01-01", estacao="Centro", poluente="O3", concentracao=145.0, unidade="ug/m3"), # IQAr ~100
            Medicao(data="2020-01-01", estacao="Centro", poluente="CO", concentracao=2.0, unidade="ppm"), # IQAr < 40
        ]
        
        indices = consolidar(medicoes)
        
        self.assertEqual(len(indices), 1)
        indice = indices[0]
        self.assertEqual(indice.data, "2020-01-01")
        self.assertEqual(indice.estacao, "Centro")
        self.assertEqual(indice.poluente_critico, "O3") # O3 tem o pior IQAr
        self.assertEqual(indice.iqar_geral, 100)
        self.assertEqual(indice.faixa_geral, "Ruim")

    def test_consolidar_edge_case_mesmo_poluente(self):
        """Caso 2 (Edge Case): Múltiplas medições do mesmo poluente no mesmo dia."""
        medicoes = [
            Medicao(data="2020-01-02", estacao="Sul", poluente="MP10", concentracao=25.0, unidade="ug/m3"), # IQAr 20
            Medicao(data="2020-01-02", estacao="Sul", poluente="MP10", concentracao=50.0, unidade="ug/m3"), # IQAr 40 (pior)
        ]
        
        indices = consolidar(medicoes)
        
        self.assertEqual(len(indices), 1)
        indice = indices[0]
        # Deve manter apenas a medição com o pior IQAr para aquele poluente
        self.assertEqual(len(indice.resultados), 1)
        self.assertEqual(indice.resultados[0].iqar, 40)
        self.assertEqual(indice.iqar_geral, 40)
        self.assertEqual(indice.poluente_critico, "MP10")

    def test_consolidar_falha_poluente_invalido(self):
        """Caso 3 (Falha/Exceção): Poluentes desconhecidos ou não suportados."""
        medicoes = [
            Medicao(data="2020-01-03", estacao="Norte", poluente="POLUENTE_FALSO", concentracao=100.0, unidade="ug/m3"),
        ]
        
        # O sistema foi desenhado para ignorar poluentes sem calculadora
        # e retornar uma lista vazia se não houver dados válidos consolidados.
        indices = consolidar(medicoes)
        self.assertEqual(len(indices), 0)

if __name__ == "__main__":
    unittest.main()
