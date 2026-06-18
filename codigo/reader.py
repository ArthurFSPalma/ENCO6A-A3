"""
reader.py — Camada de entrada.

Responsabilidade: ler e validar o CSV de medições de qualidade do ar,
conforme os critérios de aceitação da HU-01.1.
"""

import csv
import re
from dataclasses import dataclass
from datetime import datetime

# Colunas obrigatórias, em ordem (garante avisos determinísticos).
COLUNAS_OBRIGATORIAS: tuple[str, ...] = (
    "data", "estacao", "poluente", "concentracao", "unidade",
)
EXTENSAO_VALIDA: str = ".csv"
PADRAO_DATA: re.Pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD


@dataclass
class Medicao:
    """Representa uma linha válida do CSV de entrada."""
    data: str
    estacao: str
    poluente: str
    concentracao: float
    unidade: str


def _validar_linha(linha: dict[str, str]) -> Medicao:
    """
    Valida uma única linha do CSV e a converte em Medicao.

    Args:
        linha: Dicionário coluna -> valor de uma linha do CSV.

    Returns:
        Medicao com os campos já validados e convertidos.

    Raises:
        ValueError: Com a falha específica encontrada — campo vazio, data
            fora do formato YYYY-MM-DD, ou concentração não numérica/negativa.
    """
    valores = {col: (linha.get(col) or "").strip() for col in COLUNAS_OBRIGATORIAS}

    # Nenhum campo pode estar vazio.
    for coluna in COLUNAS_OBRIGATORIAS:
        if valores[coluna] == "":
            raise ValueError(f"campo vazio: '{coluna}'")

    # Data estritamente no formato YYYY-MM-DD e válida no calendário.
    data = valores["data"]
    if not PADRAO_DATA.match(data):
        raise ValueError(f"data fora do formato YYYY-MM-DD: '{data}'")
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"data inexistente no calendario: '{data}'")

    # Concentração numérica e não negativa (0 é uma medição válida).
    bruto = valores["concentracao"]
    try:
        concentracao = float(bruto)
    except ValueError:
        raise ValueError(f"concentracao nao numerica: '{bruto}'")
    if concentracao < 0:
        raise ValueError(f"concentracao negativa: {concentracao}")

    return Medicao(
        data=data,
        estacao=valores["estacao"],
        poluente=valores["poluente"],
        concentracao=concentracao,
        unidade=valores["unidade"],
    )


def ler_csv(caminho: str) -> list[Medicao]:
    """
    Lê e valida o CSV de entrada conforme a HU-01.1.

    Args:
        caminho: Caminho para o arquivo CSV.

    Returns:
        Lista de Medicao com as linhas válidas. Cada linha inválida é
        ignorada e gera um aviso no terminal com o número da linha e o
        motivo específico da falha.

    Raises:
        ValueError: Se o arquivo não tiver extensão .csv ou se faltarem
            colunas obrigatórias no cabeçalho.
        FileNotFoundError: Se o arquivo não for encontrado.
    """
    if not caminho.lower().endswith(EXTENSAO_VALIDA):
        raise ValueError(f"o arquivo deve ter extensao {EXTENSAO_VALIDA}: '{caminho}'")

    medicoes: list[Medicao] = []
    with open(caminho, newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)

        presentes = set(leitor.fieldnames or [])
        faltando = set(COLUNAS_OBRIGATORIAS) - presentes
        if faltando:
            raise ValueError(f"CSV invalido — colunas ausentes: {sorted(faltando)}")

        # start=2 porque a linha 1 é o cabeçalho.
        for numero_linha, linha in enumerate(leitor, start=2):
            try:
                medicoes.append(_validar_linha(linha))
            except ValueError as erro:
                print(f"[AVISO] Linha {numero_linha} ignorada: {erro}")

    return medicoes
