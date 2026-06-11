"""
conversor.py — Utilitário de preparação de dados.

NÃO faz parte do pipeline do sistema. É executado uma única vez para
transformar o CSV bruto exportado da plataforma do IEMA (formato horário,
com unidades mistas) no contrato de entrada do sistema (sample_data.csv):

    data, estacao, poluente, concentracao, unidade

Etapas:
    1. Mantém apenas os poluentes do IQAr (CONAMA 491/2018) presentes no dado.
    2. Converte os gases de ppb para µg/m³ (unidade adotada pela CONAMA 491/2018).
    3. Agrega os valores horários em uma média diária por (data, estação, poluente).
    4. Grava o resultado no contrato de cinco colunas.

Uso:
    python conversor.py [arquivo_bruto_iema.csv]   (padrão: PR2020.csv)
"""

import sys

import pandas as pd

# Poluentes do IQAr (CONAMA 491/2018) monitorados no dado do IEMA-PR.
# O MP2,5 não é medido pela rede do Paraná, portanto não aparece aqui.
POLUENTES_IQAR: set[str] = {"MP10", "O3", "CO", "NO2", "SO2"}

# Conversão de ppb para µg/m³ a 25 °C e 1 atm (volume molar = 24,45 L/mol):
#     valor_ugm3 = valor_ppb * massa_molar / 24,45
VOLUME_MOLAR: float = 24.45
MASSA_MOLAR: dict[str, float] = {"O3": 48.00, "NO2": 46.01, "SO2": 64.07}

# Unidade final de cada poluente, conforme a CONAMA 491/2018.
UNIDADE_NORMA: dict[str, str] = {
    "MP10": "µg/m³",
    "O3": "µg/m³",
    "NO2": "µg/m³",
    "SO2": "µg/m³",
    "CO": "ppm",
}

ARQUIVO_PADRAO: str = "PR2020.csv"
ARQUIVO_SAIDA: str = "sample_data.csv"


def converter(caminho_bruto: str, caminho_saida: str = ARQUIVO_SAIDA) -> None:
    """
    Transforma o CSV bruto do IEMA no contrato de entrada do sistema.

    Args:
        caminho_bruto: Caminho do CSV exportado da plataforma do IEMA.
        caminho_saida: Caminho do CSV de saída no contrato de cinco colunas.

    Returns:
        None. Grava o arquivo de saída e imprime um resumo no terminal.
    """
    df = pd.read_csv(caminho_bruto)

    # 1. Apenas poluentes do IQAr, com valor numérico não negativo.
    df = df[df["Poluente"].isin(POLUENTES_IQAR)].copy()
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df = df[df["Valor"].notna() & (df["Valor"] >= 0)]

    # 2. ppb -> µg/m³ (apenas linhas em ppb; CO e MP10 já vêm na unidade certa).
    fator = df["Poluente"].map(MASSA_MOLAR) / VOLUME_MOLAR
    em_ppb = df["Unidade"].astype(str).str.strip() == "ppb"
    df["concentracao"] = df["Valor"].where(~em_ppb, df["Valor"] * fator)

    # 3. Média diária por (data, estação, poluente).
    diario = (
        df.groupby(["Data", "Estacao", "Poluente"])["concentracao"]
        .mean()
        .reset_index()
    )

    # 4. Monta o contrato e grava.
    contrato = pd.DataFrame({
        "data": diario["Data"],
        "estacao": diario["Estacao"],
        "poluente": diario["Poluente"],
        "concentracao": diario["concentracao"].round(2),
        "unidade": diario["Poluente"].map(UNIDADE_NORMA),
    })
    contrato = contrato.sort_values(
        ["data", "estacao", "poluente"]
    ).reset_index(drop=True)
    contrato.to_csv(caminho_saida, index=False, encoding="utf-8")

    print(f"'{caminho_saida}' gerado com sucesso.")
    print(f"  Linhas:    {len(contrato)}")
    print(f"  Estacoes:  {contrato['estacao'].nunique()}")
    print(f"  Poluentes: {sorted(contrato['poluente'].unique())}")
    print(f"  Periodo:   {contrato['data'].min()} a {contrato['data'].max()}")


if __name__ == "__main__":
    origem = sys.argv[1] if len(sys.argv) > 1 else ARQUIVO_PADRAO
    converter(origem)
