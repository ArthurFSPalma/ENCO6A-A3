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

### Fontes

- MMA — Relatório Anual de Acompanhamento da Qualidade do Ar 2025
- Resolução CONAMA 491/2018
- SOUSA, H. C. L.; TSAI, D. S.; DINIZ, I. N. Uso de dados abertos para avançar na avaliação da qualidade do ar. *Revista Brasileira de Avaliação*, v. 13, n. 2spe, e133124, 2024. Instituto de Energia e Meio Ambiente (IEMA).

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

| ID | Prioridade | História de Usuário | Critérios de Aceitação |
|---|---|---|---|
| **HU-01** Pesquisador | Alta | Como pesquisador, quero carregar um arquivo CSV com colunas `data`, `estacao`, `poluente`, `concentracao` e `unidade` e receber o IQAr calculado por poluente por dia, classificado conforme a CONAMA 491/2018, para agilizar minhas análises sem fazer os cálculos manualmente. | 1. O sistema aceita CSV com as colunas obrigatórias: `data` (YYYY-MM-DD), `estacao` (string), `poluente` (string, ex: PM2.5), `concentracao` (float) e `unidade` (string, ex: µg/m³). 2. Linhas com campos ausentes ou valores inválidos são ignoradas com aviso no terminal indicando a linha rejeitada. 3. O IQAr é calculado conforme as fórmulas e breakpoints da CONAMA 491/2018 para cada poluente presente no arquivo. 4. Cada resultado exibe: poluente, concentração, IQAr calculado e faixa (Boa / Moderada / Ruim / Muito Ruim / Péssima). 5. O índice geral do dia é o pior IQAr entre os poluentes calculados. |
| **HU-02** Jornalista | Média | Como jornalista, quero receber uma listagem dos dias em que a qualidade do ar ultrapassou a faixa "Moderada" conforme a CONAMA 491/2018, com data, local e classificação descritos em linguagem acessível, para embasar reportagens sem precisar interpretar dados técnicos. | 1. O sistema filtra automaticamente os registros com IQAr acima de "Moderada" (faixas Ruim, Muito Ruim ou Péssima). 2. A saída apresenta data, estação e faixa em linguagem acessível, sem siglas técnicas não explicadas (ex: "Qualidade do ar Ruim em 12/03/2024 na Estação Centro"). 3. O relatório lista os episódios em ordem cronológica. 4. Quando nenhum episódio crítico é encontrado no período, o sistema exibe mensagem informativa. |

---

## 4. Registro de validação

### Ambiguidades resolvidas

- **Formato do CSV:** definido pelos critérios da HU-01 — colunas obrigatórias são `data`, `estacao`, `poluente`, `concentracao` e `unidade`. Linhas inválidas são descartadas com aviso.
- **Formato da saída ("relatório"):** definido por HU — HU-01 recebe saída técnica no terminal; HU-02 recebe listagem em linguagem acessível no terminal. Nenhuma das duas gera arquivo externo no escopo atual.

### Conflitos identificados

- HU-01 e HU-02 compartilham a mesma entrada CSV e o mesmo processamento de cálculo. O que muda é exclusivamente o formato da saída. Isso será tratado na arquitetura via padrão Strategy no módulo de relatórios.

### Questões em aberto

- O sistema processará múltiplos poluentes simultaneamente em um único CSV ou apenas um por vez? (A ser definido na Sprint 2 com base na implementação do calculador.)
- O período de análise será fixo (ex: todos os dados do CSV) ou configurável pelo usuário via parâmetro de linha de comando?
