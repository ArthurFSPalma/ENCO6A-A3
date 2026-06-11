"""
consolidador.py — Camada de processamento.
Responsabilidade: consolidar o índice de qualidade do ar diário por estação
(HU-01.3) a partir das medições validadas.

Para cada par (data, estação), o sistema calcula o IQAr de cada poluente
medido e define o índice geral do dia como o PIOR (maior) IQAr do grupo,
registrando qual poluente o determinou (poluente crítico). É a regra do
poluente determinante adotada pela CETESB / CONAMA 491/2018.
"""

from dataclasses import dataclass

from calculator import CALCULADORAS
from reader import Medicao


@dataclass
class ResultadoPoluente:
    """IQAr calculado para um poluente em uma data/estação."""
    poluente: str
    concentracao: float
    unidade: str
    iqar: int
    faixa: str


@dataclass
class IndiceDiario:
    """
    Índice de qualidade do ar consolidado para uma data e estação.

    O índice geral é o pior (maior) IQAr entre os poluentes medidos;
    poluente_critico é o poluente que o determinou.
    """
    data: str
    estacao: str
    iqar_geral: int
    faixa_geral: str
    poluente_critico: str
    resultados: list[ResultadoPoluente]


def _agrupar_por_dia_estacao(
    medicoes: list[Medicao],
) -> dict[tuple[str, str], list[Medicao]]:
    """Agrupa as medições por (data, estacao)."""
    grupos: dict[tuple[str, str], list[Medicao]] = {}
    for medicao in medicoes:
        chave = (medicao.data, medicao.estacao)
        grupos.setdefault(chave, []).append(medicao)
    return grupos


def _calcular_resultados(
    medicoes: list[Medicao],
) -> tuple[list[ResultadoPoluente], set[str]]:
    """
    Calcula o IQAr de cada poluente de um grupo (mesma data/estação).

    Se o mesmo poluente aparecer mais de uma vez no grupo, mantém o de
    maior IQAr (pior caso).

    Args:
        medicoes: Medições de uma mesma data/estação.

    Returns:
        Tupla (resultados, nao_suportados): resultados é a lista de
        ResultadoPoluente (um por poluente) e nao_suportados é o conjunto
        de poluentes sem calculadora registrada.
    """
    por_poluente: dict[str, ResultadoPoluente] = {}
    nao_suportados: set[str] = set()

    for medicao in medicoes:
        calculadora = CALCULADORAS.get(medicao.poluente)
        if calculadora is None:
            nao_suportados.add(medicao.poluente)
            continue

        iqar, faixa = calculadora.calcular(medicao.concentracao)
        resultado = ResultadoPoluente(
            poluente=medicao.poluente,
            concentracao=medicao.concentracao,
            unidade=medicao.unidade,
            iqar=iqar,
            faixa=faixa,
        )

        existente = por_poluente.get(medicao.poluente)
        if existente is None or iqar > existente.iqar:
            por_poluente[medicao.poluente] = resultado

    return list(por_poluente.values()), nao_suportados


def consolidar(medicoes: list[Medicao]) -> list[IndiceDiario]:
    """
    Consolida o índice diário por estação (HU-01.3).

    Args:
        medicoes: Lista de medições válidas (saída do reader).

    Returns:
        Lista de IndiceDiario, uma entrada por (data, estacao), ordenada
        por data e depois por estação. Grupos sem nenhum poluente
        suportado são descartados.
    """
    grupos = _agrupar_por_dia_estacao(medicoes)
    avisados: set[str] = set()
    indices: list[IndiceDiario] = []

    for (data, estacao), medicoes_grupo in grupos.items():
        resultados, nao_suportados = _calcular_resultados(medicoes_grupo)

        # Avisa uma única vez por poluente sem calculadora registrada.
        for poluente in sorted(nao_suportados - avisados):
            print(f"[AVISO] Poluente sem calculadora, ignorado no IQAr: '{poluente}'")
            avisados.add(poluente)

        if not resultados:
            continue

        critico = max(resultados, key=lambda r: r.iqar)
        indices.append(
            IndiceDiario(
                data=data,
                estacao=estacao,
                iqar_geral=critico.iqar,
                faixa_geral=critico.faixa,
                poluente_critico=critico.poluente,
                resultados=resultados,
            )
        )

    indices.sort(key=lambda indice: (indice.data, indice.estacao))
    return indices
