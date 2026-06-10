"""
reporter.py — Camada de saída.
Responsabilidade: formatar e exibir os resultados calculados.

Padrão de projeto: Template Method.
Report define o esqueleto fixo do relatório em gerar() (cabeçalho, corpo e
rodapé, unidos com quebras de linha). As subclasses ResearcherReport e
JournalistReport implementam apenas os passos que variam por público
(HU-01 e HU-02).
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


class Report(ABC):
    """
    Classe-base do padrão Template Method para geração de relatórios.

    gerar() é o template method: fixa a ordem dos passos
    (cabeçalho -> corpo -> rodapé) e não deve ser sobrescrito. As subclasses
    implementam os passos abstratos (_titulo, _corpo) e podem opcionalmente
    sobrescrever o hook _rodape.
    """

    def gerar(self, resultados: list[Resultado]) -> str:
        """
        Template method: monta o relatório na ordem fixa e o retorna pronto.

        Args:
            resultados: Lista de Resultado com IQAr e faixa já calculados.

        Returns:
            String formatada pronta para exibição no terminal.
        """
        linhas = [SEPARADOR, self._titulo(), SEPARADOR]
        linhas += self._corpo(resultados)
        linhas += self._rodape(resultados)
        return "\n".join(linhas)

    @abstractmethod
    def _titulo(self) -> str:
        """Passo: retorna o título do relatório."""

    @abstractmethod
    def _corpo(self, resultados: list[Resultado]) -> list[str]:
        """Passo: retorna as linhas do corpo do relatório."""

    def _rodape(self, resultados: list[Resultado]) -> list[str]:
        """Hook: rodapé do relatório. Por padrão, apenas fecha com o separador."""
        return [SEPARADOR]


class ResearcherReport(Report):
    """
    Relatório técnico para pesquisadores e órgãos ambientais (HU-01).
    Exibe todos os registros com IQAr, faixa e índice geral do período.
    """

    def _titulo(self) -> str:
        return "  RELATÓRIO TÉCNICO — IQAr (CONAMA 491/2018)"

    def _corpo(self, resultados: list[Resultado]) -> list[str]:
        if not resultados:
            return ["  Nenhum dado válido para exibir."]

        return [
            f"  {r.data} | {r.estacao:<12} | {r.poluente:<6} | "
            f"Conc.: {r.concentracao:>7.2f} {r.unidade:<6} | "
            f"IQAr: {r.iqar:>6.1f} | {r.faixa}"
            for r in resultados
        ]

    def _rodape(self, resultados: list[Resultado]) -> list[str]:
        if not resultados:
            return [SEPARADOR]

        pior = max(resultados, key=lambda r: r.iqar)
        return [
            "-" * 62,
            f"  Índice Geral: {pior.iqar} ({pior.faixa})"
            f" — Poluente crítico: {pior.poluente}",
            SEPARADOR,
        ]


class JournalistReport(Report):
    """
    Relatório acessível para jornalistas (HU-02).
    Lista apenas episódios com IQAr acima de Moderada, em linguagem simples.
    """

    def _titulo(self) -> str:
        return "  EPISÓDIOS CRÍTICOS DE QUALIDADE DO AR"

    def _corpo(self, resultados: list[Resultado]) -> list[str]:
        criticos = sorted(
            [r for r in resultados if r.faixa in FAIXAS_CRITICAS],
            key=lambda r: r.data,
        )

        if not criticos:
            return ["  Nenhum episódio crítico encontrado no período analisado."]

        return [
            f"  Qualidade do ar {r.faixa} em {r.data} "
            f"na estação {r.estacao} "
            f"(poluente monitorado: {r.poluente})."
            for r in criticos
        ]
