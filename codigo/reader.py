"""
reader.py — Camada de entrada.
Responsabilidade: ler e validar o CSV de medições de qualidade do ar.
"""

import csv
from dataclasses import dataclass

COLUNAS_OBRIGATORIAS = {"data", "estacao", "poluente", "concentracao", "unidade"}


@dataclass
class Medicao:
    """Representa uma linha válida do CSV de entrada."""
    data: str
    estacao: str
    poluente: str
    concentracao: float
    unidade: str


def ler_csv(caminho: str) -> list[Medicao]:
    """
    Lê e valida o CSV de entrada conforme o contrato definido em HU-01.

    Args:
        caminho: Caminho para o arquivo CSV.

    Returns:
        Lista de Medicao com as linhas válidas.

    Raises:
        ValueError: Se colunas obrigatórias estiverem ausentes no cabeçalho.
        FileNotFoundError: Se o arquivo não for encontrado.
    """
    medicoes = []

    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        colunas_presentes = set(reader.fieldnames or [])
        faltando = COLUNAS_OBRIGATORIAS - colunas_presentes
        if faltando:
            raise ValueError(f"CSV inválido — colunas ausentes: {faltando}")

        for numero_linha, linha in enumerate(reader, start=2):
            try:
                concentracao = float(linha["concentracao"])
                if concentracao < 0:
                    raise ValueError("Concentração negativa.")
                medicoes.append(Medicao(
                    data=linha["data"].strip(),
                    estacao=linha["estacao"].strip(),
                    poluente=linha["poluente"].strip(),
                    concentracao=concentracao,
                    unidade=linha["unidade"].strip(),
                ))
            except (ValueError, KeyError):
                print(f"[AVISO] Linha {numero_linha} ignorada: dados inválidos.")

    return medicoes
