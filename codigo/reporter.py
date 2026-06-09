"""
reporter.py — Camada de saída.
Responsabilidade: formatar e exibir os resultados calculados.

Padrão de projeto: Strategy.
ReportStrategy é a interface; ResearcherReport e JournalistReport
implementam formatos distintos para os públicos de HU-01 e HU-02.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

FAIXAS_CRITICAS = {"Ruim", "Muito Ruim", "Péssima"}
SEPARADOR = "=" * 62


@dataclass
class Resultado:
    """Representa o resultado do cálculo de IQAr para uma medição."""
    data: str
    estacao: str
    poluente: str
    concentracao: float
    unidade: str
    iqar: float
    faixa: str


class ReportStrategy(ABC):
    """Interface Strategy para geração de relatórios."""

    @abstractmethod
    def gerar(self, resultados: list[Resultado]) -> str:
        """
        Gera o relatório a partir dos resultados calculados.

        Args:
            resultados: Lista de Resultado com IQAr e faixa já calculados.

        Returns:
            String formatada pronta para exibição no terminal.
        """


class ResearcherReport(ReportStrategy):
    """
    Relatório técnico para pesquisadores e órgãos ambientais (HU-01).
    Exibe todos os registros com IQAr, faixa e índice geral do período.
    """

    def gerar(self, resultados: list[Resultado]) -> str:
        linhas = [
            SEPARADOR,
            "  RELATÓRIO TÉCNICO — IQAr (CONAMA 491/2018)",
            SEPARADOR,
        ]

        if not resultados:
            linhas.append("  Nenhum dado válido para exibir.")
        else:
            for r in resultados:
                linhas.append(
                    f"  {r.data} | {r.estacao:<12} | {r.poluente:<6} | "
                    f"Conc.: {r.concentracao:>7.2f} {r.unidade:<6} | "
                    f"IQAr: {r.iqar:>6.1f} | {r.faixa}"
                )

            pior = max(resultados, key=lambda r: r.iqar)
            linhas.append("-" * 62)
            linhas.append(
                f"  Índice Geral: {pior.iqar} ({pior.faixa})"
                f" — Poluente crítico: {pior.poluente}"
            )

        linhas.append(SEPARADOR)
        return "\n".join(linhas)


class JournalistReport(ReportStrategy):
    """
    Relatório acessível para jornalistas (HU-02).
    Lista apenas episódios com IQAr acima de Moderada, em linguagem simples.
    """

    def gerar(self, resultados: list[Resultado]) -> str:
        criticos = sorted(
            [r for r in resultados if r.faixa in FAIXAS_CRITICAS],
            key=lambda r: r.data,
        )

        linhas = [
            SEPARADOR,
            "  EPISÓDIOS CRÍTICOS DE QUALIDADE DO AR",
            SEPARADOR,
        ]

        if not criticos:
            linhas.append(
                "  Nenhum episódio crítico encontrado no período analisado."
            )
        else:
            for r in criticos:
                linhas.append(
                    f"  Qualidade do ar {r.faixa} em {r.data} "
                    f"na estação {r.estacao} "
                    f"(poluente monitorado: {r.poluente})."
                )

        linhas.append(SEPARADOR)
        return "\n".join(linhas)
