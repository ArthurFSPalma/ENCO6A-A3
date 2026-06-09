"""
main.py — Orquestrador.
Responsabilidade: conectar as três camadas e executar o fluxo principal.

Uso:
    python main.py <arquivo.csv> <pesquisador|jornalista>

Exemplos:
    python main.py sample_data.csv pesquisador
    python main.py sample_data.csv jornalista
"""

import sys

from reader import ler_csv
from calculator import CALCULADORAS
from reporter import ResearcherReport, JournalistReport, Resultado


def processar(caminho_csv: str, modo: str) -> None:
    """
    Executa o pipeline completo: leitura → cálculo → relatório.

    Args:
        caminho_csv: Caminho para o arquivo CSV de entrada.
        modo: 'pesquisador' para relatório técnico (HU-01)
              'jornalista'  para episódios críticos (HU-02)
    """
    # Camada 1 — Leitura
    medicoes = ler_csv(caminho_csv)

    # Camada 2 — Processamento
    resultados: list[Resultado] = []
    for m in medicoes:
        calc = CALCULADORAS.get(m.poluente)
        if calc is None:
            print(f"[AVISO] Poluente '{m.poluente}' não suportado. Linha ignorada.")
            continue
        iqar, faixa = calc.calcular(m.concentracao)
        resultados.append(Resultado(
            data=m.data,
            estacao=m.estacao,
            poluente=m.poluente,
            concentracao=m.concentracao,
            unidade=m.unidade,
            iqar=iqar,
            faixa=faixa,
        ))

    # Camada 3 — Saída (Strategy)
    reporter = ResearcherReport() if modo == "pesquisador" else JournalistReport()
    print(reporter.gerar(resultados))


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[2] not in ("pesquisador", "jornalista"):
        print("Uso: python main.py <arquivo.csv> <pesquisador|jornalista>")
        sys.exit(1)

    try:
        processar(sys.argv[1], sys.argv[2])
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {sys.argv[1]}")
        sys.exit(1)
    except ValueError as e:
        print(f"[ERRO] {e}")
        sys.exit(1)
