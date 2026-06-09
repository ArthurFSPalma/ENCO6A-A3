"""
calculator.py — Camada de processamento.
Responsabilidade: calcular o IQAr por poluente conforme CONAMA 491/2018.

Padrão de projeto: Strategy.
PollutantCalculator é a interface; cada subclasse implementa os breakpoints
e o nome do poluente. A fórmula de interpolação linear é compartilhada.
"""

from abc import ABC, abstractmethod

# Formato dos breakpoints:
# (concentracao_min, concentracao_max, iqar_min, iqar_max, nome_faixa)
# Fonte: Resolução CONAMA 491/2018, Anexo I.
Breakpoint = tuple[float, float, float, float, str]


class PollutantCalculator(ABC):
    """
    Interface Strategy para cálculo de IQAr.
    Subclasses definem BREAKPOINTS conforme o poluente.
    """

    BREAKPOINTS: list[Breakpoint] = []

    def calcular(self, concentracao: float) -> tuple[float, str]:
        """
        Calcula o IQAr usando interpolação linear entre os breakpoints.

        Args:
            concentracao: Concentração medida do poluente.

        Returns:
            Tupla (iqar, faixa) onde iqar é o índice calculado e
            faixa é a classificação textual.
        """
        for c_min, c_max, i_min, i_max, faixa in self.BREAKPOINTS:
            if concentracao <= c_max:
                iqar = ((i_max - i_min) / (c_max - c_min)) * (concentracao - c_min) + i_min
                return round(iqar, 1), faixa

        # Concentração acima do maior breakpoint: Péssima no limite superior
        c_min, c_max, i_min, i_max, faixa = self.BREAKPOINTS[-1]
        iqar = ((i_max - i_min) / (c_max - c_min)) * (concentracao - c_min) + i_min
        return round(min(iqar, 400.0), 1), "Péssima"

    @abstractmethod
    def nome(self) -> str:
        """Retorna o nome do poluente."""


class PM25Calculator(PollutantCalculator):
    """
    Calcula IQAr para PM2,5.
    Unidade: µg/m³ (média de 24 horas). Fonte: CONAMA 491/2018.
    """
    BREAKPOINTS: list[Breakpoint] = [
        (0.0,   25.0,  0.0,   40.0,  "Boa"),
        (25.0,  50.0,  40.0,  80.0,  "Moderada"),
        (50.0,  75.0,  80.0,  120.0, "Ruim"),
        (75.0,  125.0, 120.0, 200.0, "Muito Ruim"),
        (125.0, 325.0, 200.0, 400.0, "Péssima"),
    ]

    def nome(self) -> str:
        return "PM2,5"


class PM10Calculator(PollutantCalculator):
    """
    Calcula IQAr para PM10.
    Unidade: µg/m³ (média de 24 horas). Fonte: CONAMA 491/2018.
    """
    BREAKPOINTS: list[Breakpoint] = [
        (0.0,   50.0,  0.0,   40.0,  "Boa"),
        (50.0,  100.0, 40.0,  80.0,  "Moderada"),
        (100.0, 150.0, 80.0,  120.0, "Ruim"),
        (150.0, 250.0, 120.0, 200.0, "Muito Ruim"),
        (250.0, 600.0, 200.0, 400.0, "Péssima"),
    ]

    def nome(self) -> str:
        return "PM10"


# Registro de calculadoras disponíveis.
# Chave: string exata do campo "poluente" no CSV.
CALCULADORAS: dict[str, PollutantCalculator] = {
    "PM2.5": PM25Calculator(),
    "PM10":  PM10Calculator(),
}
