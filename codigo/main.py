"""
main.py — Orquestrador.
Responsabilidade: conectar as camadas (entrada → processamento → saída) e
executar o fluxo principal por um menu interativo no terminal.

Uso:
    python main.py
        Inicia o menu interativo: escolhe o tipo de relatório e o arquivo
        CSV (com sample_data.csv como padrão).

    python main.py <arquivo.csv> <pesquisador|jornalista>
        Modo direto (opcional), sem menu, útil para execução rápida.

Observação: por usar input(), deve ser executado em um terminal real (não
no painel de saída de extensões como o Code Runner).
"""

import sys

from reader import ler_csv
from consolidador import consolidar, filtrar_criticos
from reporter import ResearcherReport, JournalistReport, SEPARADOR

# Garante saída em UTF-8 no terminal (necessário no Windows/cp1252 por "µ").
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ARQUIVO_PADRAO: str = "sample_data.csv"
MODOS: dict[str, str] = {"1": "pesquisador", "2": "jornalista"}


def escolher_modo() -> str:
    """Pergunta ao usuário o tipo de relatório e retorna o modo escolhido."""
    print("Selecione o tipo de relatório:")
    print("  [1] Pesquisador — relatório técnico completo (HU-01)")
    print("  [2] Jornalista  — episódios críticos, linguagem leiga (HU-02)")
    while True:
        opcao = input("Opção (1/2): ").strip()
        if opcao in MODOS:
            return MODOS[opcao]
        print("Opção inválida. Digite 1 ou 2.")


def escolher_arquivo() -> str:
    """Pergunta o caminho do CSV, usando ARQUIVO_PADRAO se nada for digitado."""
    entrada = input(f"Arquivo CSV [{ARQUIVO_PADRAO}]: ").strip()
    return entrada or ARQUIVO_PADRAO


def processar(caminho_csv: str, modo: str) -> None:
    """
    Executa o pipeline completo: leitura → consolidação → relatório.

    Args:
        caminho_csv: Caminho para o arquivo CSV de entrada.
        modo: 'pesquisador' (relatório técnico, HU-01) ou
              'jornalista' (episódios críticos, HU-02).
    """
    medicoes = ler_csv(caminho_csv)        # Camada de entrada (HU-01.1)
    indices = consolidar(medicoes)         # Camada de processamento (HU-01.2/01.3)

    if modo == "jornalista":
        indices = filtrar_criticos(indices)   # HU-02.1
        relatorio = JournalistReport()
    else:
        relatorio = ResearcherReport()

    print(relatorio.gerar(indices))        # Camada de saída (Template Method)


def main() -> None:
    """Ponto de entrada: monta o menu (ou lê argumentos) e dispara o pipeline."""
    print(SEPARADOR)
    print("  ANALISADOR DE QUALIDADE DO AR — IQAr (CONAMA 491/2018)")
    print(SEPARADOR)

    # Modo direto por argumentos, se fornecidos e válidos; senão, menu.
    if len(sys.argv) == 3 and sys.argv[2] in MODOS.values():
        caminho, modo = sys.argv[1], sys.argv[2]
    else:
        modo = escolher_modo()
        caminho = escolher_arquivo()

    try:
        processar(caminho, modo)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        sys.exit(1)
    except ValueError as erro:
        print(f"[ERRO] {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()
