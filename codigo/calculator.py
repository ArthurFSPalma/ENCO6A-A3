"""
calculator.py — Camada de processamento.
Responsabilidade: calcular o IQAr por poluente conforme CONAMA 491/2018.

Padrão de projeto: Strategy.
PollutantCalculator é a interface; cada subclasse define seus breakpoints e o
nome do poluente. A fórmula de interpolação linear é compartilhada na base.

Breakpoints: tabela do IQAr da CETESB (implementação da Resolução CONAMA
491/2018). O índice varia de 0 a 400 em cinco faixas. O cálculo segue a
equação de interpolação linear do Anexo da CONAMA 491/2018:

    IQAr = ((Ifin - Iini) / (Cfin - Cini)) * (C - Cini) + Iini

Não se usa a Resolução CONAMA 506/2024, posterior ao período dos dados
analisados (2020), quando a 491/2018 estava em vigor.
"""

from abc import ABC, abstractmethod

# Formato dos breakpoints:
# (concentracao_min, concentracao_max, iqar_min, iqar_max, nome_faixa)
Breakpoint = tuple[float, float, float, float, str]

IQAR_MAXIMO: int = 400  # Topo da escala do índice (faixa Péssima).


class PollutantCalculator(ABC):
    """
    Interface Strategy para cálculo de IQAr.
    Subclasses definem BREAKPOINTS e o nome conforme o poluente.
    """

    BREAKPOINTS: list[Breakpoint] = []

    def calcular(self, concentracao: float) -> tuple[int, str]:
        """
        Calcula o IQAr por interpolação linear entre os breakpoints.

        Args:
            concentracao: Concentração medida do poluente, na unidade da
                faixa (µg/m³ para a maioria; ppm para o CO).

        Returns:
            Tupla (iqar, faixa): iqar é um inteiro de 0 a 400 e faixa é a
            classificação textual da qualidade do ar correspondente.
        """
        for c_min, c_max, i_min, i_max, faixa in self.BREAKPOINTS:
            if concentracao <= c_max:
                iqar = ((i_max - i_min) / (c_max - c_min)) * (concentracao - c_min) + i_min
                return round(iqar), faixa

        # Concentração acima do maior breakpoint: limita no topo da escala.
        return IQAR_MAXIMO, "Péssima"

    @abstractmethod
    def nome(self) -> str:
        """Retorna o nome do poluente."""


class MP10Calculator(PollutantCalculator):
    """IQAr para MP10. Unidade: µg/m³ (média de 24 h)."""
    BREAKPOINTS: list[Breakpoint] = [
        (0.0,   50.0,  0.0,   40.0,  "Boa"),
        (50.0,  100.0, 40.0,  80.0,  "Moderada"),
        (100.0, 150.0, 80.0,  120.0, "Ruim"),
        (150.0, 250.0, 120.0, 200.0, "Muito Ruim"),
        (250.0, 600.0, 200.0, 400.0, "Péssima"),
    ]

    def nome(self) -> str:
        return "MP10"


class MP25Calculator(PollutantCalculator):
    """IQAr para MP2,5. Unidade: µg/m³ (média de 24 h)."""
    BREAKPOINTS: list[Breakpoint] = [
        (0.0,   25.0,  0.0,   40.0,  "Boa"),
        (25.0,  50.0,  40.0,  80.0,  "Moderada"),
        (50.0,  75.0,  80.0,  120.0, "Ruim"),
        (75.0,  125.0, 120.0, 200.0, "Muito Ruim"),
        (125.0, 300.0, 200.0, 400.0, "Péssima"),
    ]

    def nome(self) -> str:
        return "MP2,5"


class O3Calculator(PollutantCalculator):
    """IQAr para O3 (ozônio). Unidade: µg/m³ (média de 8 h)."""
    BREAKPOINTS: list[Breakpoint] = [
        (0.0,   100.0, 0.0,   40.0,  "Boa"),
        (100.0, 130.0, 40.0,  80.0,  "Moderada"),
        (130.0, 160.0, 80.0,  120.0, "Ruim"),
        (160.0, 200.0, 120.0, 200.0, "Muito Ruim"),
        (200.0, 800.0, 200.0, 400.0, "Péssima"),
    ]

    def nome(self) -> str:
        return "O3"


class COCalculator(PollutantCalculator):
    """IQAr para CO (monóxido de carbono). Unidade: ppm (média de 8 h)."""
    BREAKPOINTS: list[Breakpoint] = [
        (0.0,  9.0,  0.0,   40.0,  "Boa"),
        (9.0,  11.0, 40.0,  80.0,  "Moderada"),
        (11.0, 13.0, 80.0,  120.0, "Ruim"),
        (13.0, 15.0, 120.0, 200.0, "Muito Ruim"),
        (15.0, 50.0, 200.0, 400.0, "Péssima"),
    ]

    def nome(self) -> str:
        return "CO"


class NO2Calculator(PollutantCalculator):
    """IQAr para NO2 (dióxido de nitrogênio). Unidade: µg/m³ (média de 1 h)."""
    BREAKPOINTS: list[Breakpoint] = [
        (0.0,    200.0,  0.0,   40.0,  "Boa"),
        (200.0,  240.0,  40.0,  80.0,  "Moderada"),
        (240.0,  320.0,  80.0,  120.0, "Ruim"),
        (320.0,  1130.0, 120.0, 200.0, "Muito Ruim"),
        (1130.0, 3750.0, 200.0, 400.0, "Péssima"),
    ]

    def nome(self) -> str:
        return "NO2"


class SO2Calculator(PollutantCalculator):
    """IQAr para SO2 (dióxido de enxofre). Unidade: µg/m³ (média de 24 h)."""
    BREAKPOINTS: list[Breakpoint] = [
        (0.0,   20.0,   0.0,   40.0,  "Boa"),
        (20.0,  40.0,   40.0,  80.0,  "Moderada"),
        (40.0,  365.0,  80.0,  120.0, "Ruim"),
        (365.0, 800.0,  120.0, 200.0, "Muito Ruim"),
        (800.0, 2620.0, 200.0, 400.0, "Péssima"),
    ]

    def nome(self) -> str:
        return "SO2"


# Registro de calculadoras disponíveis (Strategy).
# Chave: string exata do campo "poluente" no CSV, na convenção do contrato.
CALCULADORAS: dict[str, PollutantCalculator] = {
    "MP10":  MP10Calculator(),
    "MP2,5": MP25Calculator(),
    "O3":    O3Calculator(),
    "CO":    COCalculator(),
    "NO2":   NO2Calculator(),
    "SO2":   SO2Calculator(),
}
