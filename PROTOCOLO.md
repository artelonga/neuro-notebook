# Protocolo de busca: optogenética nas doenças de Alzheimer e Parkinson

Versão 1.0 · 23/10/2026 · Resumo em português de [PROTOCOL.md](PROTOCOL.md), que é a versão de
referência. Segue PRISMA 2020 (etapa de identificação) e PRISMA-S. Resultados:
[RELATORIO.md](RELATORIO.md).

## 1. Pergunta

Que literatura aplica, discute ou revisa a **optogenética** na **doença de Alzheimer (DA)** ou na
**doença de Parkinson (DP)**? A optogenética já foi usada em algum **ensaio clínico registrado**,
para qualquer condição? Algum desses ensaios foi em DA ou DP?

## 2. Critérios de aceitação

| CA | Critério | Como verificar |
|---|---|---|
| **CA-1** | Lista de bases pesquisáveis, consultadas por código sempre que possível | Cada base "API" tem uma função em `litreview/`; cada base manual tem uma busca pronta no relatório |
| **CA-2** | Busca quantitativa: o registro DEVE conter um termo de optogenética (em todas as variantes de idioma) **E** (`alzheimer` **OU** `parkinson`) | Vocabulário da §4; busca exata e número de resultados por base em `data/search_log.json`; cada registro reconferido localmente |
| **CA-3** | Número de artigos por base, quantos são **exclusivos** de cada base e o total **sem repetição**, fácil de somar | `data/counts.csv`, `data/overlap_matrix.csv`, `data/works.csv` (uma linha por trabalho, coluna 0/1 por base) |
| **CA-4** | Busca sistemática em registros de ensaios clínicos para **qualquer** uso de optogenética, com triagem de cada registro | `data/trials_log.json`, `data/trials_screening.csv` (decisão e justificativa por registro), `data/trials.csv` |

## 3. Bases

- **Por código (6):** PubMed/MEDLINE (E-utilities), Europe PMC (inclui preprints e teses),
  OpenAlex, Semantic Scholar, DOAJ, arXiv.
- **Manuais (6), por licença ou bloqueio a robôs:** Scopus, Web of Science, Embase, LILACS/BVS,
  CNKI, CiNii. As buscas prontas estão no relatório; as exportações (RIS/CSV) vão para
  `data/manual/`.
- **Registros de ensaios (5):** ClinicalTrials.gov (API v2), EU CTIS, EU Clinical Trials Register
  (EudraCT), ISRCTN e WHO ICTRP. O ICTRP é um meta-registro que cobre ChiCTR, JPRN, ANZCTR,
  **ReBEC (Brasil)**, CTRI, DRKS e outros. Ele não tem API pública; se o portal falhar, a
  alternativa é exportar um CSV manualmente.

## 4. Vocabulário

**Conceito A, optogenética:**
- `optogenet*` cobre EN, PT, ES, IT, FR (sem acentos) e DE.
- `opto-genet*` cobre a grafia com hífen.
- `optigenet*` cobre o erro de grafia que aparece no pedido.
- Formas não latinas: RU оптогенетика · ZH 光遗传/光遺傳 · JA 光遺伝, オプトジェネティクス · KO 광유전.

**Conceito B, doença:** `alzheimer*` e `parkinson*`, que se escrevem igual em todas as línguas de
alfabeto latino e incluem parkinsonismo e parkinsoniano. Formas não latinas em RU, ZH, JA e KO.

**Lógica:** `A E B`, buscada em **título + resumo + palavras-chave dos autores**.
- MeSH e texto completo ficam fora da busca principal, porque o critério é a *palavra-chave*
  aparecer. Os dois entram apenas como contagens de sensibilidade.
- **Adaptação por buscador:** truncamento (`*`) onde é aceito. Onde não é aceito (OpenAlex, DOAJ),
  todas as formas da palavra são listadas. O OpenAlex limita buscas a 5 operadores booleanos, então
  a busca é dividida em subconsultas e os resultados são unidos pelo ID.
- **Reverificação local:** as APIs casam termos de forma frouxa (stemming, MeSH, tokenização de
  chinês/japonês, resumos ocultos). Por isso cada registro é reconferido com expressões regulares
  sobre título + resumo + palavras-chave, sem acentos e em minúsculas.

## 5. Deduplicação e contagem

- **Mesmo trabalho:** dois registros que compartilham DOI, PMID, PMCID, ID arXiv ou título
  normalizado (≥25 letras/dígitos). A ligação é transitiva (union-find).
- **Preprints:** um preprint e sua versão publicada viram **um só trabalho**. A coluna
  `n_versions` permite separá-los de novo.
- **Situação de cada trabalho:**
  - `confirmed`: os dois conceitos aparecem em algum registro do trabalho.
  - `rejected`: há resumo, mas falta um conceito.
  - `unverifiable`: sem resumo em lugar nenhum. Esses vão para triagem manual e ficam fora do total.
- **Exclusivo da base X:** trabalho confirmado cuja única fonte é X.

## 6. Ensaios clínicos

- **Escopo:** qualquer uso de optogenética, em qualquer condição. Depois, cada ensaio é marcado se
  título, condição ou resumo mencionam DA, DP, demência ou comprometimento cognitivo.
- **Termos:** cada um é buscado separadamente e os resultados são unidos.
  - As formas de "optogenético".
  - Os nomes de opsinas: channelrhodopsin, ChR2, ChrimsonR, halorhodopsin, multi-characteristic
    opsin.
  - Os códigos dos produtos que já chegaram à clínica: GS030, RST-001, MCO-010/sonpiretigene
    isteparvovec, BS01/Bionic Sight. Os códigos são necessários porque alguns registros (como o
    EudraCT) não indexam a palavra "optogenetic".
- **Triagem:** feita por um revisor até agora; **um segundo revisor independente é obrigatório**
  antes da publicação.
  - *incluir, tratamento*: a intervenção entrega um gene de opsina, com ou sem dispositivo de luz.
  - *incluir, seguimento*: extensão de segurança de longo prazo de um ensaio incluído.
  - *incluir, observacional*: estudo sem intervenção que existe para viabilizar a terapia
    optogenética (por exemplo, seleção de pacientes).
  - *excluir*: menção incidental (como o nome do centro) ou código ambíguo que coincidiu com outro
    estudo.
- **Registros duplicados:** o mesmo ensaio registrado em vários lugares é ligado por
  `same_trial_as` e contado uma vez.

## 7. Fora do escopo desta etapa

1. Triagem de **relevância** (título/resumo) dos trabalhos confirmados, por dois revisores.
2. Buscas manuais nas bases da §3 e incorporação das exportações.
3. Exportação do WHO ICTRP, se o portal continuar fora do ar.
4. Busca por citações (para trás e para frente) a partir das revisões incluídas.
