"""
pipeline.py — Camada de Orquestração do Fluxo (Template Method).

Responsabilidade: definir o fluxo principal do sistema usando o padrão
Template Method. O método executar() fixa a ordem das operações:
preparar os dados, ler, filtrar pela data solicitada, consolidar,
formatar o relatório (passo variável) e exportar para arquivo de texto.

Dessa forma, o padrão Template Method passa a englobar a execução inteira,
e não apenas a formatação textual.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from conversor import converter
from reader import ler_csv, Medicao
from consolidador import consolidar, filtrar_criticos, IndiceDiario
from reporter import ResearcherReport, JournalistReport

class PipelineRelatorio(ABC):
    """
    Classe abstrata que implementa o Template Method para a geração de relatórios.
    """

    def executar(self, caminho_bruto: str | Path, data: str, caminho_saida: str | Path) -> None:
        """
        Template Method: fixa a ordem de execução do fluxo.
        Não deve ser sobrescrito pelas subclasses.
        """
        caminho_convertido = self.preparar_dados(caminho_bruto)
        todas_medicoes = self.ler_dados(caminho_convertido)
        medicoes_filtradas = self.filtrar_por_data(todas_medicoes, data)
        teve_dados = len(medicoes_filtradas) > 0
        indices = self.processar(medicoes_filtradas)
        texto_relatorio = self.formatar(indices, data, teve_dados)
        self.exportar(texto_relatorio, caminho_saida)

    def preparar_dados(self, caminho_bruto: str | Path) -> Path:
        """Passo 1: Converte o arquivo bruto para o formato do contrato."""
        # Se falhar porque não é bruto, podemos assumir que já era convertido para facilitar.
        try:
            return converter(caminho_bruto)
        except ValueError as e:
            if "faltam colunas" in str(e):
                print(f"[Aviso] O arquivo '{Path(caminho_bruto).name}' pode já estar convertido.")
                return Path(caminho_bruto)
            raise e

    def ler_dados(self, caminho_csv: Path) -> list[Medicao]:
        """Passo 2: Lê o CSV no formato do contrato e retorna lista de Medicao."""
        return ler_csv(str(caminho_csv))

    def filtrar_por_data(self, medicoes: list[Medicao], data: str) -> list[Medicao]:
        """Passo 3: Filtra as medições para exibir apenas a data solicitada."""
        return [m for m in medicoes if m.data == data]

    def processar(self, medicoes: list[Medicao]) -> list[IndiceDiario]:
        """Passo 4: Processa e consolida as medições utilizando o Strategy interno."""
        return consolidar(medicoes)

    @abstractmethod
    def formatar(self, indices: list[IndiceDiario], data: str, teve_dados: bool) -> str:
        """
        Passo 5: Formata o relatório (Passo variável - implementado pela subclasse).
        """
        pass

    def exportar(self, conteudo: str, caminho_saida: str | Path) -> None:
        """Passo 6: Salva o relatório gerado em um arquivo de texto."""
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"\nRelatório gerado com sucesso em: {Path(caminho_saida).resolve()}")


class PipelinePesquisador(PipelineRelatorio):
    """Implementação do pipeline para Pesquisadores (HU-01)."""

    def formatar(self, indices: list[IndiceDiario], data: str, teve_dados: bool) -> str:
        # Reutilizamos o Template Method já existente em reporter.py para gerar a string
        report = ResearcherReport()
        return report.gerar(indices, data, teve_dados)


class PipelineJornalista(PipelineRelatorio):
    """Implementação do pipeline para Jornalistas (HU-02)."""

    def formatar(self, indices: list[IndiceDiario], data: str, teve_dados: bool) -> str:
        # O jornalista apenas visualiza os índices críticos
        indices_criticos = filtrar_criticos(indices)
        report = JournalistReport()
        return report.gerar(indices_criticos, data, teve_dados)
