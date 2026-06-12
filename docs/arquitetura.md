# Arquitetura — Analisador de Qualidade do Ar

> Sistema em Python que lê medições de poluentes de um arquivo CSV, calcula o **Índice de Qualidade do Ar (IQAr)** segundo a **Resolução CONAMA 491/2018** e gera relatórios no terminal para dois públicos: **pesquisadores** e **jornalistas**.

---

## 1. Visão geral

A aplicação é organizada em **camadas de responsabilidade única**, conectadas por um **orquestrador** (`main.py`) que conduz toda a interação por um **menu no terminal**.

O uso segue quatro passos: o usuário escolhe a **ação** (converter dados brutos ou usar dados já convertidos), **seleciona o arquivo** de uma lista, escolhe o **público** do relatório (pesquisador ou jornalista) e recebe o resultado. Quando a ação é converter, o sistema executa antes uma etapa de **preparação** que transforma o arquivo bruto no contrato de entrada; quando os dados já estão prontos, essa etapa é pulada.

Internamente, o dado sempre chega à análise no mesmo **contrato fixo** (CSV de cinco colunas), é validado, processado em duas etapas (cálculo do IQAr por poluente e consolidação do índice diário por estação) e formatado na saída.

Dois padrões de projeto estruturam os pontos onde o sistema varia. Na camada de processamento, o **Strategy** (`calculator.py`) trata cada poluente como uma estratégia de cálculo com seus próprios limites de faixa (*breakpoints*), mantendo única a fórmula de interpolação. Na camada de saída, o **Template Method** (`reporter.py`) fixa o esqueleto do relatório e deixa cada público implementar só os passos que mudam.

---

## 2. Diagrama de arquitetura

```mermaid
flowchart TB
    subgraph SYS["Sistema · Analisador de Qualidade do Ar"]
        direction TB
        MAIN["main.py — Orquestração<br/>menu de ação + seleção de arquivo no terminal"]
        RAW[("CSV bruto do IEMA<br/>ex.: PR2020.csv")]
        CONV["conversor.py — Preparação opcional<br/>bruto → contrato · gera o _convertido.csv"]
        CSV[("CSV no contrato<br/>data · estacao · poluente · concentracao · unidade")]
        READER["reader.py — Entrada<br/>leitura + validação · HU-01.1"]
        subgraph PROC["Processamento"]
            direction LR
            CONS["consolidador.py<br/>índice diário + filtro · HU-01.3 / HU-02.1"]
            CALC["calculator.py<br/>IQAr por poluente · Strategy · HU-01.2"]
        end
        REP["reporter.py — Saída<br/>relatórios · Template Method · HU-01.4 / 02.2 / 02.3"]
        TERM["Terminal<br/>relatório pesquisador / jornalista"]

        MAIN -->|"opção 1 · escolhe o bruto"| RAW
        RAW --> CONV
        CONV --> CSV
        MAIN -->|"opção 2 · escolhe o contrato"| CSV
        CSV --> READER
        READER -->|"lista de Medicao"| CONS
        CONS -.->|"usa por poluente"| CALC
        CONS -->|"lista de IndiceDiario"| REP
        REP --> TERM
    end

    classDef dados fill:#eef2ff,stroke:#6366f1,color:#1e1b4b;
    classDef orq  fill:#fef9c3,stroke:#ca8a04,color:#422006;
    classDef prep fill:#ffedd5,stroke:#ea580c,color:#431407;
    classDef ent  fill:#dcfce7,stroke:#16a34a,color:#052e16;
    classDef proc fill:#dbeafe,stroke:#2563eb,color:#172554;
    classDef sai  fill:#fae8ff,stroke:#c026d3,color:#4a044e;
    classDef term fill:#ffffff,stroke:#475569,color:#0f172a;

    class RAW,CSV dados
    class MAIN orq
    class CONV prep
    class READER ent
    class CONS,CALC proc
    class REP sai
    class TERM term
```

As cores indicam a responsabilidade de cada peça: dados e contrato em índigo, orquestração em âmbar, preparação opcional em laranja, entrada em verde, processamento em azul, saída em magenta. As setas `opção 1` e `opção 2` são os dois caminhos do menu de ação — converter um dado bruto ou usar um já convertido. A seta tracejada de `consolidador` para `calculator` é uma **dependência de uso** (Strategy), não um passo do fluxo.

---

## 3. Fluxo de execução

```mermaid
sequenceDiagram
    actor U as Usuário
    participant M as main.py
    participant K as conversor.py
    participant R as reader.py
    participant C as consolidador.py
    participant L as calculator.py
    participant P as reporter.py

    U->>M: python main.py
    M->>U: menu de ação + lista de arquivos
    U-->>M: escolhe ação e arquivo

    alt ação = converter dados brutos
        M->>K: converter(bruto)
        K-->>M: caminho do arquivo convertido
    end

    M->>U: menu de relatório (pesquisador/jornalista)
    U-->>M: escolhe o público

    M->>R: ler_csv(arquivo)
    R-->>M: lista de Medicao
    M->>C: consolidar(medicoes)
    loop para cada poluente medido
        C->>L: calcular(concentracao)
        L-->>C: IQAr e faixa
    end
    C-->>M: lista de IndiceDiario

    alt modo = jornalista
        M->>C: filtrar_criticos(indices)
        C-->>M: apenas os dias críticos
    end

    M->>P: gerar(indices)
    P-->>M: texto do relatório
    M->>U: imprime no terminal
```

A leitura **descarta as linhas inválidas com aviso individual** (HU-01.1) sem abortar o processamento. O cálculo do IQAr acontece **dentro da consolidação**, uma vez por poluente de cada grupo (data, estação). E o **filtro de dias críticos** (HU-02.1) só entra no modo jornalista — o pesquisador recebe todos os índices.

---

## 4. Camadas e responsabilidades

A **orquestração** (`main.py`) conduz o menu, seleciona o arquivo e coordena a passagem de dados entre as camadas. A **preparação** (`conversor.py`) é opcional: quando o usuário escolhe converter, ela transforma o CSV bruto no contrato e gera um arquivo `<nome>_convertido.csv`. A **entrada** (`reader.py`) lê o contrato e devolve apenas medições válidas. O **processamento** divide-se em dois módulos: `calculator.py` calcula o IQAr de um poluente isolado, e `consolidador.py` agrupa as medições por dia/estação, define o pior índice de cada grupo e expõe o filtro de dias críticos. A **saída** (`reporter.py`) formata o resultado para o público escolhido.

### Mapeamento HU → módulo

| HU | Módulo responsável | Responsabilidade |
|----|--------------------|------------------|
| HU-01.1 | `reader.py` | leitura e validação do CSV (extensão, colunas, data, concentração) |
| HU-01.2 | `calculator.py` | cálculo do IQAr por poluente (Strategy) |
| HU-01.3 | `consolidador.py` | índice diário consolidado por estação (pior IQAr + poluente crítico) |
| HU-01.4 | `reporter.py` · `ResearcherReport` | relatório técnico para o pesquisador |
| HU-02.1 | `consolidador.py` · `filtrar_criticos` | filtro dos dias críticos a partir do índice diário |
| HU-02.2 | `reporter.py` · `JournalistReport` | relatório em linguagem leiga (máscara) |
| HU-02.3 | `reporter.py` · `JournalistReport` | ordem cronológica e mensagem de período sem críticos |

> A conversão (`conversor.py`) não corresponde a uma HU: é uma etapa de infraestrutura que prepara o dado para o contrato de entrada.

---

## 5. Padrões de projeto

### 5.1 Strategy — `calculator.py`

```mermaid
classDiagram
    class PollutantCalculator {
        <<abstract>>
        +calcular(concentracao) tuple
        +nome() str
    }
    PollutantCalculator <|-- MP10Calculator
    PollutantCalculator <|-- MP25Calculator
    PollutantCalculator <|-- O3Calculator
    PollutantCalculator <|-- COCalculator
    PollutantCalculator <|-- NO2Calculator
    PollutantCalculator <|-- SO2Calculator
    note for PollutantCalculator "calcular() é compartilhado (interpolação linear da CONAMA 491). Cada subclasse define seus BREAKPOINTS e nome()."
```

O cálculo do IQAr difere entre os poluentes **apenas nos limites de concentração de cada faixa** (e na unidade de medida); a fórmula de interpolação linear é idêntica para todos. O Strategy isola exatamente essa variação: a classe-base `PollutantCalculator` concentra a fórmula em `calcular()`, e cada subclasse declara somente os seus `BREAKPOINTS` e o seu `nome()`. As estratégias ficam registradas no dicionário `CALCULADORAS`, cuja chave é o código do poluente no contrato. Adicionar um novo poluente passa a ser **criar uma classe e registrá-la**, sem alterar o que já funciona — o princípio aberto/fechado na prática.

### 5.2 Template Method — `reporter.py`

```mermaid
classDiagram
    class Report {
        <<abstract>>
        +gerar(indices) str
        #_titulo() str
        #_corpo(indices) list
        #_rodape(indices) list
    }
    Report <|-- ResearcherReport
    Report <|-- JournalistReport
    note for Report "gerar() é o template method: fixa o esqueleto cabeçalho → corpo → rodapé. As subclasses implementam _titulo() e _corpo()."
```

Os dois relatórios seguem o **mesmo esqueleto** — cabeçalho, corpo e rodapé, unidos por quebras de linha —, mudando apenas o conteúdo de cada passo. `Report.gerar()` fixa essa ordem (o *template method*, que não deve ser sobrescrito) e delega os passos variáveis `_titulo()` e `_corpo()` às subclasses, oferecendo `_rodape()` como *hook* opcional. `ResearcherReport` produz o detalhamento técnico por dia/estação; `JournalistReport` produz as frases em linguagem leiga. O padrão garante relatórios **consistentes em forma** e torna trivial acrescentar um terceiro público no futuro.

---

## 6. Contrato de dados e a preparação

A análise lê **somente** o contrato abaixo — de onde o dado veio não importa para ela:

| coluna | tipo | exemplo |
|--------|------|---------|
| `data` | texto no formato `YYYY-MM-DD` | `2020-01-18` |
| `estacao` | texto | `CSN` |
| `poluente` | texto (`MP10`, `MP2,5`, `O3`, `CO`, `NO2`, `SO2`) | `SO2` |
| `concentracao` | decimal não negativo | `80.86` |
| `unidade` | texto | `µg/m³` |

A etapa de preparação (`conversor.py`) é quem cuida da origem do dado. Ela recebe o CSV bruto da rede de monitoramento IEMA-PR — medições **horárias**, com os gases em **ppb** — e produz um arquivo no contrato: médias **diárias**, gases convertidos para **µg/m³** e o CO em **ppm**. O nome do arquivo gerado é derivado do arquivo de origem (ex.: `PR2020.csv` → `PR2020_convertido.csv`), de modo que **cada conjunto convertido vira um arquivo próprio** e vários coexistem na pasta — o usuário escolhe qual analisar. Essa separação mantém o sistema **desacoplado da fonte**: trocar de fonte de dados é questão da preparação, sem tocar nas camadas de análise.

---

## 7. Decisões de arquitetura

**Sem interface gráfica.** Toda a interação é por menu no terminal (`main.py`): escolha da ação, seleção do arquivo a partir de uma lista e escolha do público do relatório. Não há janelas nem GUI, conforme o enunciado.

**Portabilidade e arquivos junto do código.** Os caminhos são resolvidos em relação à pasta do próprio script (`Path(__file__)`), então o sistema roda em qualquer computador, sem caminhos fixos a uma máquina. Os arquivos necessários ficam na pasta do projeto, e os convertidos são gravados ali, aparecendo na lista de seleção.

**Preparação integrada, mas isolada.** A conversão é um passo opcional oferecido no menu, e não um pré-requisito embutido na análise. A análise continua lendo apenas o contrato — a preparação existe só para produzir esse contrato a partir de um dado bruto.

**Consolidação como etapa explícita.** O índice diário por estação (HU-01.3) é uma etapa própria (`consolidador.py`), separada do cálculo por poluente (`calculator.py`). Isso mantém cada responsabilidade testável de forma isolada e faz a consolidação alimentar tanto o relatório técnico quanto o filtro de dias críticos.

**Dois padrões distintos, em camadas distintas.** Strategy (processamento) e Template Method (saída) resolvem tipos de variação diferentes — o *como calcular* e o *como apresentar* —, evitando forçar um padrão único onde ele não se encaixa.

**Norma CONAMA 491/2018.** Os *breakpoints* do IQAr seguem a tabela da CETESB referente à Resolução 491/2018. Não se utiliza a CONAMA 506/2024 por ser posterior ao período dos dados analisados (ano de 2020), quando a 491 estava em vigor.
