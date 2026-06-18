"""
reporter.py — Camada de saída.
Responsabilidade: formatar e exibir os relatórios a partir do índice diário
consolidado (IndiceDiario).

Padrão de projeto: Template Method.
Report define o esqueleto fixo do relatório em gerar() (cabeçalho, corpo e
rodapé, unidos por quebras de linha) e não deve ser sobrescrito. As
subclasses ResearcherReport (HU-01.4) e JournalistReport (HU-02.2 e HU-02.3)
implementam apenas os passos que variam por público.
"""

from abc import ABC, abstractmethod

from consolidador import IndiceDiario

SEPARADOR: str = "=" * 62
SUBSEPARADOR: str = "-" * 62
MENSAGEM_SEM_CRITICOS: str = (
    "Nenhum episódio crítico de poluição do ar foi encontrado "
    "no período analisado."
)


def _para_data_br(data_iso: str) -> str:
    """Converte uma data 'YYYY-MM-DD' para 'DD/MM/AAAA'."""
    ano, mes, dia = data_iso.split("-")
    return f"{dia}/{mes}/{ano}"


class Report(ABC):
    """
    Classe-base do padrão Template Method para geração de relatórios.

    gerar() é o template method: fixa a ordem dos passos
    (cabeçalho -> corpo -> rodapé) e não deve ser sobrescrito. As subclasses
    implementam os passos abstratos (_titulo, _corpo) e podem sobrescrever o
    hook _rodape.
    """

    def gerar(self, indices: list[IndiceDiario], data: str = "", teve_dados: bool = True) -> str:
        """
        Template method: monta o relatório na ordem fixa e o retorna pronto.

        Args:
            indices: Índices diários consolidados a serem exibidos. O que
                cada relatório recebe é decidido na orquestração (main): o
                relatório do pesquisador recebe todos; o do jornalista
                recebe apenas os dias críticos (HU-02.1).

        Returns:
            String formatada pronta para exibição no terminal.
        """
        linhas = [SEPARADOR, self._titulo(), SEPARADOR]
        linhas += self._corpo(indices, data, teve_dados)
        linhas += self._rodape(indices)
        return "\n".join(linhas)

    @abstractmethod
    def _titulo(self) -> str:
        """Passo: retorna o título do relatório."""

    @abstractmethod
    def _corpo(self, indices: list[IndiceDiario], data: str, teve_dados: bool) -> list[str]:
        """Passo: retorna as linhas do corpo do relatório."""

    def _rodape(self, indices: list[IndiceDiario]) -> list[str]:
        """Hook: rodapé. Por padrão, apenas fecha com o separador."""
        return [SEPARADOR]


class ResearcherReport(Report):
    """
    Relatório técnico para pesquisadores e órgãos ambientais (HU-01.4).

    Para cada data/estação, lista todos os poluentes medidos com
    concentração, unidade, IQAr e faixa, e sinaliza o poluente crítico que
    determinou o índice geral do dia.
    """

    def _titulo(self) -> str:
        return "  RELATÓRIO TÉCNICO — IQAr (CONAMA 491/2018)"

    def _corpo(self, indices: list[IndiceDiario], data: str, teve_dados: bool) -> list[str]:
        if not teve_dados:
            data_br = _para_data_br(data) if data else ""
            return [f"  Nenhum dado coletado para o dia {data_br}."]
        if not indices:
            return ["  Nenhum dado válido para exibir."]

        linhas: list[str] = []
        for indice in indices:
            linhas.append(f"  {indice.data} | Estação: {indice.estacao}")
            for resultado in sorted(indice.resultados, key=lambda r: r.poluente):
                critico = resultado.poluente == indice.poluente_critico
                marca = "  <<< POLUENTE CRÍTICO" if critico else ""
                linhas.append(
                    f"    {resultado.poluente:<6} | "
                    f"Conc.: {resultado.concentracao:>8.2f} {resultado.unidade:<6} | "
                    f"IQAr: {resultado.iqar:>3d} | {resultado.faixa}{marca}"
                )
            linhas.append(
                f"    -> Índice geral do dia: "
                f"{indice.iqar_geral} ({indice.faixa_geral})"
                f" | Poluente crítico: {indice.poluente_critico}"
            )
            linhas.append("")  # linha em branco entre blocos
        return linhas


class JournalistReport(Report):
    """
    Relatório acessível para jornalistas (HU-02.2 e HU-02.3).

    Exibe os episódios críticos recebidos em linguagem leiga, em ordem
    cronológica, na máscara:
        "Qualidade do ar [Faixa] em [DD/MM/AAAA] na [Estação]"
    Se não houver episódios, exibe a mensagem padrão do período sem críticos.
    """

    def _titulo(self) -> str:
        return "  EPISÓDIOS CRÍTICOS DE QUALIDADE DO AR"

    def _corpo(self, indices: list[IndiceDiario], data: str, teve_dados: bool) -> list[str]:
        if not teve_dados:
            data_br = _para_data_br(data) if data else ""
            return [f"  Nenhum dado coletado para o dia {data_br}."]
            
        if not indices:
            if data:
                data_br = _para_data_br(data)
                return [f"  Qualidade do ar boa no estado do Paraná no dia {data_br}."]
            return [f"  {MENSAGEM_SEM_CRITICOS}"]

        criticos = sorted(indices, key=lambda indice: (indice.data, indice.estacao))
        return [
            f"  Qualidade do ar {indice.faixa_geral} em "
            f"{_para_data_br(indice.data)} na {indice.estacao}"
            for indice in criticos
        ]
