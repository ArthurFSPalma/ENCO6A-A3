# Arquitetura — Sistema Analisador de Qualidade do Ar

**Sprint 2 · Projeto da Aplicação**

**Membros:**
- Arthur Francisco da Silva Palma — 2369060
- Luiz Fernando Rolim Vieira — 2419939

---

## 1. Padrões de Codificação e Gestão de Qualidade

### Estilo de código
- **PEP 8**: indentação com 4 espaços, linhas de até 100 caracteres, nomes em `snake_case` para variáveis e funções, `PascalCase` para classes.
- **Type hints**: todas as funções públicas anotadas com tipos (`-> str`, `list[Resultado]`, etc.).
- **Docstrings**: toda função pública documentada com descrição, `Args:` e `Returns:`.
- **Sem valores mágicos**: constantes nomeadas em maiúsculas (`FAIXAS_CRITICAS`, `SEPARADOR`, `COLUNAS_OBRIGATORIAS`).

### Gestão do repositório
- Commits realizados a cada aula de desenvolvimento e antes de cada review.
- Mensagens de commit descritivas em português (ex: `Adiciona PM10Calculator com breakpoints CONAMA 491`).
- Estrutura de pastas conforme especificação do professor:

```
codigo/
  main.py
  reader.py
  calculator.py
  reporter.py
  sample_data.csv
  tests/
    test_calculator.py
    test_reporter.py
docs/
  requisitos.md
  arquitetura.md
```

### Qualidade
- Nenhum `import *`; todos os imports são explícitos.
- Tratamento de erro em todas as entradas externas (CSV, argumentos de linha de comando).
- Avisos ao usuário para linhas inválidas sem interromper o processamento.

---

## 2. Diagrama de Arquitetura

O sistema segue uma **arquitetura em camadas (Layered Architecture)** com três camadas de responsabilidade única, orquestradas pelo `main.py`.

```mermaid
graph TD
    Usuario["Usuário\n(terminal)"]
    Main["main.py\nOrquestrador"]
    Reader["reader.py\nCamada de Entrada"]
    Calculator["calculator.py\nCamada de Processamento"]
    Reporter["reporter.py\nCamada de Saída"]
    CSV["arquivo.csv"]

    Usuario -->|"python main.py arquivo.csv modo"| Main
    Main --> Reader
    Main --> Calculator
    Main --> Reporter
    CSV --> Reader
    Reporter -->|"relatório no terminal"| Usuario
```

### Responsabilidades por componente

| Componente | Responsabilidade |
|---|---|
| `main.py` | Orquestra o pipeline; recebe argumentos da linha de comando; instancia o relatório correto (subclasse de `Report`) conforme o modo. |
| `reader.py` | Lê e valida o CSV; descarta linhas inválidas com aviso; retorna lista de `Medicao`. |
| `calculator.py` | Aplica as fórmulas e breakpoints da CONAMA 491/2018 por poluente; retorna IQAr e faixa. |
| `reporter.py` | Formata e exibe os resultados conforme o público-alvo (pesquisador ou jornalista). |

### Trade-offs justificados

**Layered Architecture foi escolhida porque:**
- Cada camada tem uma única razão para mudar (SRP): se o formato do CSV mudar, só `reader.py` é alterado; se uma fórmula mudar, só `calculator.py`.
- Facilita os testes automatizados: cada camada pode ser testada isoladamente com dados fictícios.
- Adequada ao escopo do projeto: pipeline linear sem necessidade de flexibilidade entre camadas em tempo de execução.

**Custo aceito:**
- Pouco flexível para mudanças de formato de entrada que afetem a interface entre camadas (ex: trocar CSV por API REST exigiria refatorar `reader.py` e ajustar `main.py`).

---

## 3. Padrões de Projeto

### Padrão 1 — Strategy em `calculator.py`

**Problema resolvido:** cada poluente tem breakpoints e unidades distintas, mas o fluxo de cálculo (interpolação linear + classificação) é idêntico. Sem o padrão, o código seria um bloco `if/elif` por poluente impossível de estender sem modificar código existente.

**Solução:** `PollutantCalculator` define a interface e a fórmula compartilhada. Cada subclasse declara apenas seus breakpoints e nome. `main.py` seleciona a calculadora certa pela chave do poluente, via o registro `CALCULADORAS` definido em `calculator.py`.

```mermaid
classDiagram
    class PollutantCalculator {
        <<abstract>>
        +BREAKPOINTS: list
        +calcular(concentracao: float) tuple
        +nome()* str
    }

    class PM25Calculator {
        +BREAKPOINTS: list
        +nome() str
    }

    class PM10Calculator {
        +BREAKPOINTS: list
        +nome() str
    }

    class calculator {
        <<module>>
        +CALCULADORAS: dict
    }

    PollutantCalculator <|-- PM25Calculator
    PollutantCalculator <|-- PM10Calculator
    calculator ..> PollutantCalculator : registra instâncias
    main ..> calculator : importa CALCULADORAS
```

**Como adicionar um novo poluente (ex: O₃):** criar `O3Calculator(PollutantCalculator)` com seus breakpoints e registrá-lo em `CALCULADORAS` (em `calculator.py`). Nenhuma outra classe é modificada — Open/Closed Principle.

---

### Padrão 2 — Template Method em `reporter.py`

**Problema resolvido:** HU-01 (pesquisador) e HU-02 (jornalista) produzem relatórios com a **mesma estrutura geral** (cabeçalho com separadores e título, corpo, rodapé), mas com conteúdo diferente em cada parte. Sem o padrão, cada relatório repetiria a montagem do esqueleto (separadores, ordem dos blocos, junção com `\n`), gerando duplicação e risco de os dois formatos divergirem na estrutura.

**Solução:** a classe-base `Report` define o **template method** `gerar()`, que fixa a ordem dos passos (cabeçalho → corpo → rodapé) e os une com `\n`. As subclasses implementam apenas os passos que variam: `_titulo()` e `_corpo()` (passos abstratos, obrigatórios) e, opcionalmente, o **hook** `_rodape()` — que por padrão apenas fecha com o separador. `ResearcherReport` sobrescreve `_rodape()` para acrescentar o índice geral; `JournalistReport` usa o comportamento padrão.

```mermaid
classDiagram
    class Report {
        <<abstract>>
        +gerar(resultados: list) str
        +_titulo()* str
        +_corpo(resultados: list)* str
        +_rodape(resultados: list) str
    }

    class ResearcherReport {
        +_titulo() str
        +_corpo(resultados: list) str
        +_rodape(resultados: list) str
    }

    class JournalistReport {
        +_titulo() str
        +_corpo(resultados: list) str
    }

    Report <|-- ResearcherReport
    Report <|-- JournalistReport
    main ..> Report : instancia conforme o modo
```

**Por que Template Method (e não Strategy):** aqui o que varia são os **passos** de um algoritmo de montagem fixo, não o algoritmo inteiro. A classe-base controla o fluxo e chama os passos das subclasses — inversão de controle ("não me chame, eu te chamo"). Para este caso, herança com passos sobrescritos é mais direta do que plugar objetos de estratégia. (O domínio é distinto do Padrão 1: lá variam os dados/algoritmo de cálculo por poluente; aqui varia o conteúdo de um relatório de estrutura fixa.)

**Como adicionar um novo formato (ex: relatório resumido):** criar `SummaryReport(Report)` implementando `_titulo()` e `_corpo()` (e o hook `_rodape()`, se precisar). `gerar()` e a estrutura geral não mudam — Open/Closed Principle.

---

## 4. Demonstração Funcional

Executar a partir da pasta `codigo/`:

```bash
# Relatório técnico (HU-01 — pesquisador)
python main.py sample_data.csv pesquisador

# Episódios críticos (HU-02 — jornalista)
python main.py sample_data.csv jornalista
```

**Saída esperada — modo pesquisador:**
```
[AVISO] Linha 10 ignorada: dados inválidos.
==============================================================
  RELATÓRIO TÉCNICO — IQAr (CONAMA 491/2018)
==============================================================
  2024-03-10 | Centro       | PM2.5  | Conc.:   18.50 µg/m³  | IQAr:   29.6 | Boa
  2024-03-10 | Centro       | PM10   | Conc.:   45.00 µg/m³  | IQAr:   36.0 | Boa
  2024-03-11 | Centro       | PM2.5  | Conc.:   55.20 µg/m³  | IQAr:   88.3 | Ruim
  ...
  Índice Geral: 234.3 (Péssima) — Poluente crítico: PM10
==============================================================
```

**Saída esperada — modo jornalista:**
```
==============================================================
  EPISÓDIOS CRÍTICOS DE QUALIDADE DO AR
==============================================================
  Qualidade do ar Ruim em 2024-03-11 na estação Centro (poluente monitorado: PM2.5).
  Qualidade do ar Muito Ruim em 2024-03-12 na estação Norte (poluente monitorado: PM2.5).
  Qualidade do ar Péssima em 2024-03-14 na estação Sul (poluente monitorado: PM10).
==============================================================
```
