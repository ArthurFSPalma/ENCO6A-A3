"""
main.py — Orquestrador.

Conecta as camadas (preparação opcional dos dados → entrada → processamento →
saída) por um menu interativo no terminal:

    1. Escolhe a ação: converter dados brutos ou usar dados já convertidos.
    2. Seleciona o arquivo CSV de uma lista (arquivos .csv da pasta do projeto).
    3. Escolhe o público do relatório: pesquisador ou jornalista.
    4. Exibe o relatório e encerra.

Uso:
    python main.py

Observação: por usar input(), deve ser executado em um terminal real (não
no painel de saída de extensões como o Code Runner).
"""

import sys
from pathlib import Path

from conversor import converter
from reader import ler_csv
from consolidador import consolidar, filtrar_criticos
from reporter import ResearcherReport, JournalistReport, SEPARADOR

# Garante saída em UTF-8 no terminal (necessário no Windows/cp1252 por "µ").
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Pasta deste script, resolvida em relação ao arquivo: usada para listar os
# CSVs e gravar os convertidos. Funciona em qualquer computador.
PASTA: Path = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent


def listar_csvs(pasta: Path) -> list[Path]:
    """Retorna os arquivos .csv da pasta, em ordem alfabética."""
    return sorted(pasta.glob("*.csv"), key=lambda caminho: caminho.name.lower())


def selecionar_arquivo(pasta: Path, titulo: str) -> Path:
    """
    Lista os arquivos .csv da pasta e deixa o usuário escolher um pelo número.

    Args:
        pasta: Pasta onde procurar os arquivos .csv.
        titulo: Texto exibido no prompt de escolha.

    Returns:
        O caminho (Path) do arquivo escolhido.
    """
    arquivos = listar_csvs(pasta)
    if not arquivos:
        print("  Nenhum arquivo .csv encontrado na pasta.")
        return Path(input("  Caminho do arquivo .csv: ").strip())

    print("Arquivos .csv disponíveis:")
    for indice, arquivo in enumerate(arquivos, start=1):
        print(f"  [{indice}] {arquivo.name}")
    print("  [0] Digitar outro caminho")

    while True:
        escolha = input(f"{titulo}: ").strip()
        if escolha == "0":
            return Path(input("  Caminho do arquivo: ").strip())
        if escolha.isdigit() and 1 <= int(escolha) <= len(arquivos):
            return arquivos[int(escolha) - 1]
        print(f"  Opção inválida. Digite de 1 a {len(arquivos)}, ou 0.")


def escolher_acao() -> str:
    """Pergunta se o usuário quer converter dados ou usar dados já convertidos."""
    print("O que deseja fazer?")
    print("  [1] Converter dados brutos")
    print("  [2] Usar dados já convertidos")
    while True:
        opcao = input("Opção (1/2): ").strip()
        if opcao == "1":
            return "converter"
        if opcao == "2":
            return "convertido"
        print("  Opção inválida. Digite 1 ou 2.")


def escolher_modo() -> str:
    """Pergunta o público do relatório e retorna o modo escolhido."""
    print("Tipo de relatório:")
    print("  [1] Pesquisador — relatório técnico completo (HU-01)")
    print("  [2] Jornalista  — episódios críticos, linguagem leiga (HU-02)")
    while True:
        opcao = input("Opção (1/2): ").strip()
        if opcao == "1":
            return "pesquisador"
        if opcao == "2":
            return "jornalista"
        print("  Opção inválida. Digite 1 ou 2.")


def gerar_relatorio(caminho_csv: Path, modo: str) -> None:
    """
    Executa o pipeline (entrada → processamento → saída) e imprime o relatório.

    Args:
        caminho_csv: Caminho do CSV no contrato de entrada (já convertido).
        modo: 'pesquisador' (HU-01) ou 'jornalista' (HU-02).
    """
    medicoes = ler_csv(str(caminho_csv))   # Camada de entrada (HU-01.1)
    indices = consolidar(medicoes)         # Camada de processamento (HU-01.2/01.3)

    if modo == "jornalista":
        indices = filtrar_criticos(indices)   # HU-02.1
        relatorio = JournalistReport()
    else:
        relatorio = ResearcherReport()

    print(relatorio.gerar(indices))        # Camada de saída (Template Method)


def main() -> None:
    """Ponto de entrada: menu interativo no terminal."""
    print(SEPARADOR)
    print("  ANALISADOR DE QUALIDADE DO AR — IQAr (CONAMA 491/2018)")
    print(SEPARADOR)

    try:
        acao = escolher_acao()
        print()

        if acao == "converter":
            bruto = selecionar_arquivo(PASTA, "Escolha o arquivo bruto")
            print("\nConvertendo...")
            caminho_csv = converter(bruto)
        else:
            caminho_csv = selecionar_arquivo(PASTA, "Escolha o arquivo já convertido")

        print()
        modo = escolher_modo()
        gerar_relatorio(caminho_csv, modo)

    except FileNotFoundError as erro:
        alvo = getattr(erro, "filename", None) or erro
        print(f"[ERRO] Arquivo não encontrado: {alvo}")
        sys.exit(1)
    except ValueError as erro:
        print(f"[ERRO] {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()
