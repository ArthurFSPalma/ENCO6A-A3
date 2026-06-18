# Estratégia de Testes — Analisador de Qualidade do Ar (Sprint 4)

---

## 1. Abordagem

A estratégia de testes adotada utiliza **testes unitários isolados** com o framework nativo `unittest` do Python, garantindo portabilidade e eliminando dependências externas. Os testes focam nas **camadas críticas de regra de negócio**: o cálculo do IQAr (padrão Strategy) e a consolidação do índice diário por estação.

Para cada método testado, foram implementados **três cenários obrigatórios**:
- **Sucesso**: caminho feliz com dados válidos.
- **Edge Case**: valores de fronteira ou situações limítrofes.
- **Falha/Extremo**: dados anômalos ou fora dos limites esperados.

---

## 2. Execução

A partir da **raiz do repositório**, executar:
```bash
python -m unittest discover tests
```

---

## 3. Mapeamento dos Testes

### `test_calculator.py` — Padrão Strategy (calculator.py)

| Caso | Método | Cenário | O que valida |
|------|--------|---------|-------------|
| 1 | `test_mp10_sucesso_faixa_normal` | Sucesso | MP10 com concentração 25.0 retorna IQAr 20 e faixa "Boa" |
| 2 | `test_mp10_edge_case_fronteira` | Edge Case | MP10 com concentração exata no limite (50.0) retorna IQAr 40 sem pular de faixa |
| 3 | `test_mp10_falha_extremo_superior` | Falha | MP10 com concentração absurda (9999.0) retorna o teto IQAR_MAXIMO (400) e "Péssima" |
| 4 | `test_o3_sucesso_faixa_ruim` | Sucesso | O3 com concentração 145.0 retorna IQAr 100 e faixa "Ruim" |
| 5 | `test_o3_edge_case_zero` | Edge Case | O3 com concentração 0.0 retorna IQAr 0 e faixa "Boa" |
| 6 | `test_o3_extremo_superior` | Falha | O3 com concentração 1000.0 (acima do breakpoint final) retorna IQAR_MAXIMO |

### `test_consolidador.py` — Consolidação (consolidador.py)

| Caso | Método | Cenário | O que valida |
|------|--------|---------|-------------|
| 7 | `test_consolidar_sucesso_multiplos_poluentes` | Sucesso | Dois poluentes na mesma data/estação: o índice geral é o pior (O3 = 100), faixa "Ruim" |
| 8 | `test_consolidar_edge_case_mesmo_poluente` | Edge Case | Duas medições do mesmo poluente: mantém apenas a de pior IQAr (40 > 20) |
| 9 | `test_consolidar_falha_poluente_invalido` | Falha | Poluente inexistente ("POLUENTE_FALSO"): lista de índices retorna vazia, sem crash |

---

## 4. Cobertura e Lacunas

### O que está coberto
- Fórmula de interpolação linear do IQAr (2 estratégias: MP10 e O3).
- Fronteiras de faixa (concentrações exatas nos limites dos breakpoints).
- Comportamento defensivo: poluentes não registrados e valores extremos.
- Regra do poluente determinante (pior IQAr define o índice geral do dia).
- Deduplicação de medições repetidas do mesmo poluente.

### Lacunas conhecidas (fora do escopo desta Sprint)
- **Testes de integração E2E**: não há teste que rode o fluxo completo (CSV bruto → relatório `.txt`).
- **Testes de I/O**: validação do `reader.py` com arquivos corrompidos ou encodings diferentes.
- **Testes de formatação**: verificação das strings exatas geradas pelo `reporter.py`.
- **Testes do conversor**: conversão de ppb para µg/m³ com dados reais.

Essas lacunas são aceitáveis dentro do escopo e prazo da Sprint 4.
