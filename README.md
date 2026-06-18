# Analisador de Qualidade do Ar — IQAr (CONAMA 491/2018)

> **Sprint 4 — Entrega Final**
> Sistema desenvolvido em Python para o processamento, cálculo e geração de relatórios do Índice de Qualidade do Ar (IQAr) com base nos critérios estabelecidos pela Resolução CONAMA 491/2018.

---

## 📌 Visão Geral

Este projeto é uma ferramenta de terminal capaz de ler bases de dados brutas de redes de monitoramento ambiental (como o formato do IEMA do Estado do Paraná), converter medições horárias em dados diários, calcular o Índice de Qualidade do Ar (IQAr) para diversos poluentes e exportar relatórios customizados em `.txt`.

O projeto foi criado para atender a duas histórias de usuário principais:
1. **O Pesquisador:** Precisa de uma visão técnica e detalhada de todas as estações e poluentes.
2. **O Repórter/Jornalista:** Precisa de uma linguagem acessível e o isolamento de eventos onde o ar atingiu as faixas de poluição mais graves (Ruim, Muito Ruim ou Péssima).

---

## 📁 Estrutura do Repositório

Conforme os padrões da entrega final, o projeto possui a seguinte divisão de responsabilidades:

```text
/
├── .gitignore              # Ignora cache, arquivos gerados e relatórios
├── README.md               # Visão geral, uso e decisões de projeto (Este arquivo)
├── codigo/                 # Código-fonte principal em Python
│   ├── calculator.py       # Padrão Strategy para o cálculo do IQAr
│   ├── consolidador.py     # Lógica de agrupamento diário
│   ├── conversor.py        # Transforma o arquivo do IEMA no formato aceito
│   ├── main.py             # Orquestrador do sistema e interações via terminal
│   ├── pipeline.py         # Padrão Template Method da execução do programa
│   ├── reader.py           # Leitura e validação anti-falhas
│   └── reporter.py         # Template Method de formatação textual
├── dados/                  # Arquivos CSV brutos (entrada do sistema)
├── docs/                   # Documentação extensa do projeto
│   ├── Sprints.pdf         # Histórico de sprints
│   ├── arquitetura.md      # Padrões de projeto, diagramas e trade-offs
│   ├── requisitos.md       # Elicitação, histórias de usuário e validações
│   └── testes.md           # Estratégia de testes, cobertura e lacunas
├── relatorios/             # Diretório de saída onde os arquivos .txt são salvos
└── tests/                  # Testes automatizados (unittest)
    ├── test_calculator.py
    └── test_consolidador.py
```

---

## 🚀 Instruções de Uso

### Pré-requisitos
- Ter o **Python 3.10+** instalado.
- Ter a biblioteca **Pandas** instalada para o conversor de arquivos (`pip install pandas`).

### Executando o Analisador
1. Abra o terminal e navegue até a pasta `codigo`:
   ```bash
   cd codigo
   ```
2. Execute o arquivo principal:
   ```bash
   python main.py
   ```
3. **Responda ao fluxo interativo:**
   - **Arquivo CSV:** Digite o nome do arquivo que está na pasta `dados` (ex: `PR2020.csv`).
   - **Data:** Digite a data que deseja extrair do relatório no formato DD-MM-YYYY (ex: `18-01-2020`).
   - **Opção:** Digite `1` para gerar um relatório completo (Pesquisador) ou `2` para o formato de linguagem simples focado em episódios críticos (Repórter).
4. O resultado será salvo automaticamente em formato de texto (`.txt`) dentro da pasta `relatorios/`.

### Rodando os Testes Automatizados
O projeto conta com uma suíte de testes focados nas lógicas cruciais de negócio (Casos de Sucesso, Falha e Edge Cases). Para rodá-los, acesse a pasta raiz do repositório no terminal e execute:
```bash
python -m unittest discover tests
```

---

## 🏗️ Decisões de Projeto e Padrões de Arquitetura

O sistema foi modularizado para respeitar o Princípio de Responsabilidade Única (SRP) e o Princípio Aberto/Fechado (OCP) do SOLID. As principais decisões de design envolveram:

### 1. Padrão *Strategy* (`calculator.py`)
A regra matemática de interpolação linear do IQAr é a mesma para todos os poluentes, mas cada um possui limites e tabelas radicalmente diferentes. Implementamos o padrão **Strategy** para encapsular os `BREAKPOINTS` de cada poluente em classes separadas (`MP10Calculator`, `O3Calculator`, etc.). Isso evita um arquivo infestado de `if/else` e permite que amanhã adicionemos novos poluentes criando apenas uma classe nova.

### 2. Padrão *Template Method* (`pipeline.py` e `reporter.py`)
Temos dois cenários de Template Method:
- **Fluxo Geral:** A execução segue um esqueleto imutável (preparar dados -> ler dados -> filtrar pela data -> consolidar métricas -> formatar -> exportar txt). O `PipelineRelatorio` fixa essa ordem, deixando apenas a etapa de formatação pendente para ser implementada pelas subclasses de Pesquisador e Repórter.
- **Relatório Textual:** A classe `Report` define que a string do documento final sempre tem a estrutura `_titulo()` -> `_corpo()` -> `_rodape()`.

### 3. Blindagem de Entradas (Orquestração Anti-Falhas)
O arquivo `main.py` utiliza laços `while True` e blocos de `try/except` para garantir que o sistema recuse entradas inválidas (ex: uma data que não existe no calendário, ou tentar analisar uma data do ano de 2020 enviando um arquivo de 2019) e solicite a correção, sem abortar a execução do programa na cara do usuário.

### 4. Isolamento do Conversor
A conversão de medições horárias (`ppb`) para diárias (`µg/m³`) é feita à parte (`conversor.py`). Isso significa que a base central do projeto não se "suja" com as particularidades dos arquivos do Estado do Paraná. O código espera um contrato fixo. Se mudarmos de estado, basta mudar o conversor.
