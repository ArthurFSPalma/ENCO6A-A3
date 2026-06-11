# Requisitos — Sistema Analisador de Qualidade do Ar

**Sprint 1 · Engenharia de Requisitos**

**Membros:**
- Arthur Francisco da Silva Palma — 2369060
- Luiz Fernando Rolim Vieira — 2419939

---

## 1. Pitch da proposta

### Problema

O Brasil contabilizou 570 estações de monitoramento da qualidade do ar em 2024 — crescimento de 44% desde 2022, segundo o Relatório Anual de Acompanhamento da Qualidade do Ar 2025 do Ministério do Meio Ambiente. Apesar desse volume crescente de dados públicos disponíveis, pesquisadores como Sousa, Tsai e Diniz (2024) apontam que o avanço na avaliação da qualidade do ar ainda é limitado pela ausência de ferramentas padronizadas para processar esses dados. O cálculo do IQAr conforme a Resolução CONAMA 491/2018 envolve fórmulas específicas por poluente e faixas de classificação bem definidas, mas não existe ferramenta acessível e automatizada que aplique esse padrão sobre os CSVs exportados pelas estações — obrigando profissionais a realizarem o processo manualmente, com risco de inconsistência e sem escala.

### Público-alvo

| Segmento | Descrição |
|---|---|
| **Principal** | Pesquisadores e técnicos de órgãos ambientais que processam dados de estações de monitoramento |
| **Secundário** | Jornalistas que precisam identificar episódios críticos de poluição para pautar reportagens |

### Por que é relevante

- O volume de dados públicos cresceu 44% em dois anos (MMA, 2025), mas a capacidade de processá-los padronizadamente não acompanhou esse crescimento.
- A CONAMA 491/2018 é o padrão legal brasileiro vigente para cálculo do IQAr, mas sua aplicação manual é propensa a erro e não escalável.
- Dados de estações como CETESB (SP) e IAT (PR) já são exportados em CSV — o formato de entrada do sistema existe e é real.

### Base de dados utilizada no protótipo

O protótipo é validado sobre dados **reais e públicos**: a série histórica do estado do **Paraná referente a 2020**, publicada em formato aberto pelo **IEMA — Instituto de Energia e Meio Ambiente**, que consolida e disponibiliza os dados das redes estaduais de monitoramento. O ano de 2020 está sob vigência da **Resolução CONAMA 491/2018**, garantindo coerência entre o dado e a norma aplicada no cálculo.

O conjunto cobre **8 estações de monitoramento** e cinco dos seis poluentes da norma — **MP10, O₃, CO, NO₂ e SO₂** (essa rede não monitora MP2,5; ainda assim, o sistema suporta o cálculo dos seis poluentes previstos na CONAMA 491/2018). Os dados brutos vêm em **frequência horária**, com os gases expressos em **ppb** e o monóxido de carbono em **ppm**.

Como esse formato bruto não corresponde ao contrato de entrada do sistema, a preparação fica a cargo de um **utilitário separado** (`conversor.py`): ele agrega as medições horárias em **médias diárias**, converte os gases de ppb para **µg/m³** e padroniza a saída nas cinco colunas do contrato (`data`, `estacao`, `poluente`, `concentracao`, `unidade`). Dessa forma, o sistema permanece **desacoplado da fonte** — ele lê apenas o contrato, e a origem específica do dado é responsabilidade do conversor.

### Fontes

- MMA — Relatório Anual de Acompanhamento da Qualidade do Ar 2025
- Resolução CONAMA 491/2018
- SOUSA, H. C. L.; TSAI, D. S.; DINIZ, I. N. Uso de dados abertos para avançar na avaliação da qualidade do ar. *Revista Brasileira de Avaliação*, v. 13, n. 2spe, e133124, 2024. Instituto de Energia e Meio Ambiente (IEMA).
- IEMA — Instituto de Energia e Meio Ambiente. Plataforma de dados abertos de qualidade do ar (série do Paraná, 2020). Disponível em: https://energiaeambiente.org.br/qualidadedoar

---

## 2. Roteiro de elicitação

### Técnicas utilizadas

**Análise de normas (CONAMA 491/2018):** Âncora do projeto. Define os poluentes monitorados (PM2,5, PM10, O₃, NO₂, CO, SO₂), as fórmulas de cálculo do IQAr por poluente e a classificação por faixas (Boa, Moderada, Ruim, Muito Ruim, Péssima). Determinou toda a lógica de negócio do sistema: quais poluentes calcular, quais breakpoints aplicar e como classificar o resultado.

**Análise de similares:** Sistemas analisados: MonitorAr (Ministério do Meio Ambiente), CETESB (São Paulo) e AirNow (EPA, EUA). Confirmaram a estrutura da saída: relatório por faixas com destaque de episódios críticos; indicaram que o índice geral é sempre o pior poluente do período.

**Análise de dados públicos:** CETESB e IAT (Paraná) exportam CSVs históricos com colunas de data, estação, poluente, concentração e unidade. Esse levantamento definiu o formato exato de entrada do sistema e resolveu a ambiguidade sobre quais campos o CSV deve conter.

### Síntese

A norma definiu **o que calcular**. Os similares confirmaram **como estruturar a saída**. Os dados públicos confirmaram **o formato real de entrada** e eliminaram a principal ambiguidade do projeto.

---

## 3. Histórias de usuário

### Épico 01 — Módulo do Pesquisador

#### HU-01.1: Upload e Validação de Arquivo CSV
**Prioridade:** Alta

> Como pesquisador, quero que o sistema valide a estrutura e os dados do arquivo CSV carregado, para garantir que apenas dados íntegros sejam processados.

**Critérios de Aceitação:**
- O sistema deve aceitar arquivos obrigatoriamente com a extensão `.csv`.
- O sistema deve validar a presença das cinco colunas obrigatórias no cabeçalho: `data`, `estacao`, `poluente`, `concentracao` e `unidade`.
- O formato da coluna `data` deve ser validado estritamente como `YYYY-MM-DD`.
- A coluna `concentracao` deve aceitar apenas valores numéricos decimais (`float`) positivos.
- Linhas com campos nulos/vazios, tipos de dados incompatíveis ou colunas ausentes devem ser puladas/ignoradas.
- Para cada linha ignorada, o sistema deve imprimir um log/aviso no terminal indicando o número da linha e a falha de validação encontrada.

---

#### HU-01.2: Cálculo do IQAr por Poluente Individual
**Prioridade:** Alta

> Como pesquisador, quero que o sistema aplique as fórmulas e os intervalos de transição (*breakpoints*) da resolução CONAMA 491/2018 para cada poluente, para obter o índice individual correto.

**Critérios de Aceitação:**
- O sistema deve calcular o IQAr utilizando a fórmula de interpolação linear correspondente a cada faixa de concentração da CONAMA 491/2018.
- O sistema deve mapear e aceitar os parâmetros de cálculo para os principais poluentes previstos na norma (MP10, MP2,5, O₃, CO, NO₂, SO₂).
- Cada cálculo individual deve retornar o valor numérico inteiro do IQAr e sua respectiva classificação de faixa.

---

#### HU-01.3: Consolidação do Índice Geral Diário por Estação
**Prioridade:** Alta

> Como pesquisador, quero que o sistema identifique o pior índice entre os poluentes de uma mesma estação e data, para definir o índice geral do dia conforme as diretrizes regulatórias.

**Critérios de Aceitação:**
- O sistema deve agrupar as medições processadas combinando as chaves `data` e `estacao`.
- Para cada agrupamento diário por estação, o sistema deve comparar os valores de IQAr calculados para todos os poluentes daquela combinação.
- O índice geral do dia para a estação deve ser definido, obrigatoriamente, pelo maior (pior) valor de IQAr identificado entre eles.

---

#### HU-01.4: Apresentação do Relatório Técnico de IQAr
**Prioridade:** Alta

> Como pesquisador, quero visualizar os resultados detalhados dos cálculos formatados na tela, para analisar o comportamento de cada poluente de forma ágil e centralizada.

**Critérios de Aceitação:**
- O sistema deve exibir os dados calculados estruturados em formato de tabela textual ou listagem limpa no terminal.
- Cada registro de saída deve exibir explicitamente: Poluente, Concentração informada, Unidade, IQAr calculado e Classificação da faixa (Boa, Moderada, Ruim, Muito Ruim ou Péssima).
- O sistema deve sinalizar visualmente (ou em coluna própria) qual poluente determinou o Índice Geral Diário do respectivo dia/estação.

---

### Épico 02 — Módulo do Jornalista

#### HU-02.1: Filtragem de Dias Críticos da Qualidade do Ar
**Prioridade:** Média

> Como jornalista, quero que o sistema filtre os dados gerados para reter apenas os registros que violaram o nível considerado aceitável, para focar minha apuração nos casos de maior interesse público.

**Critérios de Aceitação:**
- O sistema deve ler o Índice Geral Diário consolidado na HU-01.3.
- O sistema deve isolar e reter exclusivamente os registros cujas faixas classificadas sejam: "Ruim", "Muito Ruim" ou "Péssima".
- Registros com faixas consideradas seguras ("Boa" ou "Moderada") devem ser completamente removidos desta visualização.

---

#### HU-02.2: Geração de Relatório em Linguagem Acessível
**Prioridade:** Média

> Como jornalista, quero que os episódios críticos sejam traduzidos em descrições textuais diretas e sem siglas técnicas, para que eu consiga utilizá-los imediatamente em rascunhos de notícias.

**Critérios de Aceitação:**
- O sistema deve traduzir as linhas brutas filtradas em sentenças de linguagem natural legíveis por leigos.
- O padrão da saída de texto deve seguir obrigatoriamente a máscara: `"Qualidade do ar [Faixa] em [Data formatada em DD/MM/AAAA] na [Estação]"` (Exemplo: *Qualidade do ar Ruim em 12/03/2024 na Estação Centro*).
- A saída voltada para o jornalista não deve exibir siglas como "IQAr" ou valores numéricos complexos de concentração (ex: µg/m³).

---

#### HU-02.3: Ordenação Cronológica e Mensagem de Ausência de Eventos
**Prioridade:** Baixa/Média

> Como jornalista, quero visualizar as ocorrências graves em ordem cronológica e ser informado caso o ar esteja limpo, para estruturar a linha do tempo da reportagem de forma correta.

**Critérios de Aceitação:**
- A lista de frases estruturada na HU-02.2 deve ser exibida em ordem ascendente pela data (da ocorrência mais antiga para a mais recente).
- Se o arquivo enviado não contiver nenhum registro com faixas "Ruim", "Muito Ruim" ou "Péssima", o sistema deve exibir a mensagem padrão: `"Nenhum episódio crítico de poluição do ar foi encontrado no período analisado."`

---

## 4. Registro de validação

### Ambiguidades resolvidas

- **Formato do CSV:** definido por HU-01.1 — colunas obrigatórias são `data`, `estacao`, `poluente`, `concentracao` e `unidade`; `data` estritamente em `YYYY-MM-DD`; `concentracao` float positivo. Linhas inválidas são descartadas com aviso indicando número da linha e motivo da rejeição.
- **Formato da saída:** definido por HU-01.4 e HU-02.2 — ambos os modos exibem no terminal, sem geração de arquivo externo no escopo atual. O modo pesquisador usa listagem técnica; o modo jornalista usa a máscara `"Qualidade do ar [Faixa] em [DD/MM/AAAA] na [Estação]"` sem siglas ou valores numéricos de concentração.
- **Índice geral diário:** definido por HU-01.3 — agrupamento por `data` + `estacao`; índice geral é obrigatoriamente o pior IQAr entre os poluentes daquele agrupamento.
- **Mensagem de ausência de eventos críticos:** definido por HU-02.3 — texto padrão fixo: `"Nenhum episódio crítico de poluição do ar foi encontrado no período analisado."`

### Conflitos identificados

- Épico 01 e Épico 02 compartilham a mesma entrada CSV e o mesmo processamento de cálculo (HU-01.1 a HU-01.3). O que muda é exclusivamente o formato da saída. Tratado na arquitetura via padrão Template Method no módulo de relatórios (`ResearcherReport` / `JournalistReport`).

### Questões em aberto

- **[Resolvido na Sprint 3]** O período de análise é **fixo**: o sistema processa todos os registros do CSV de entrada, sem recorte por intervalo de datas.
