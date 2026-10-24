# Optogenética × Alzheimer/Parkinson: relatório da busca

_Gerado por `python3 -m litreview.report`. Buscas executadas em 2026-10-23 (última em 2026-10-23T13:47:30). Protocolo: [PROTOCOLO.md](PROTOCOLO.md)._

## Números principais

- **2.167** registros coletados em **6** bases consultadas por código
- **977** trabalhos únicos depois da deduplicação entre bases (1.190 registros duplicados removidos)
- **801 trabalhos únicos atendem à regra de inclusão** (palavras-chave reconferidas no título, resumo e palavras-chave); 131 não verificáveis (sem resumo) e 45 rejeitados como falsos positivos dos buscadores
- Registros de ensaios clínicos: **58** registros → **18** sobre optogenética → **11 ensaios optogenéticos de tratamento distintos**, **0 em Alzheimer ou Parkinson**

## Critérios de aceitação

| CA | Critério | Situação |
|---|---|---|
| CA-1 | Lista de bases pesquisáveis, consultadas por código sempre que possível | ✅ 6 bases de literatura e 5 registros de ensaios consultados por API; 6 bases licenciadas ou só web documentadas com buscas prontas |
| CA-2 | Busca quantitativa, com método explicado (optogenética E (alzheimer OU parkinson), em vários idiomas) | ✅ busca exata e número de resultados por base abaixo e em `data/search_log.json` |
| CA-3 | Contagem por base, exclusivos de cada base, total sem repetição, fácil de somar | ✅ `data/counts.csv`, `data/overlap_matrix.csv`, `data/works.csv` (coluna 0/1 por base) |
| CA-4 | Busca sistemática em registros de ensaios clínicos para qualquer uso de optogenética | ⚠️ parcial: um registro falhou na execução (ver tabela; o WHO ICTRP cobre ChiCTR, JPRN, ANZCTR, ReBEC, CTRI e DRKS); precisa ser refeito ou exportado manualmente. Decisões de triagem em `data/trials.csv` |

## Literatura: resultados por base

*Resultados* (`api_hits`) = número informado pela API da base; *Confirmados* (`confirmed`) = trabalhos cujo título/resumo/palavras-chave de fato contêm os dois conceitos; *Exclusivos* (`unique_confirmed`) = trabalhos confirmados encontrados **só** naquela base; *Participação* (`share_of_total_confirmed`) = fração de todos os trabalhos únicos confirmados coberta pela base.

| Base | Resultados | Coletados | Confirmados | Não verificáveis | Rejeitados | Exclusivos | Participação |
|---|---|---|---|---|---|---|---|
| PubMed / MEDLINE | 486 | 486 | 477 | 0 | 0 | 5 | 59,6% |
| Europe PMC (incl. preprints) | 589 | 589 | 535 | 0 | 21 | 18 | 66,8% |
| OpenAlex | 267 | 267 | 230 | 4 | 24 | 69 | 28,7% |
| Semantic Scholar | 786 | 786 | 637 | 128 | 0 | 138 | 79,5% |
| DOAJ | 33 | 33 | 33 | 0 | 0 | 2 | 4,1% |
| arXiv | 6 | 6 | 6 | 0 | 0 | 0 | 0,7% |
| TOTAL (sem repetição) | 2.167 | 2.167 | 801 | 131 | 45 |  | 100,0% |

As versões preprint e de periódico do mesmo estudo contam como um só trabalho (49 trabalhos confirmados unem mais de 1 DOI; ver `n_versions`).

### Matriz de sobreposição (trabalhos confirmados presentes nas duas bases)

|  | pubmed | epmc | openalex | s2 | doaj | arxiv |
|---|---|---|---|---|---|---|
| pubmed | 477 | 471 | 103 | 403 | 29 | 3 |
| epmc | 471 | 535 | 112 | 448 | 29 | 3 |
| openalex | 103 | 112 | 230 | 151 | 23 | 1 |
| s2 | 403 | 448 | 151 | 637 | 30 | 6 |
| doaj | 29 | 29 | 23 | 30 | 33 | 0 |
| arxiv | 3 | 3 | 1 | 6 | 0 | 6 |

### Fluxo (PRISMA 2020, etapa de identificação)

```
Registros identificados nas bases                n = 2.167
  PubMed / MEDLINE                               n = 486
  Europe PMC (incl. preprints)                   n = 589
  OpenAlex                                       n = 267
  Semantic Scholar                               n = 786
  DOAJ                                           n = 33
  arXiv                                          n = 6
Registros duplicados removidos                   n = 1.190
Trabalhos únicos triados (palavras-chave)        n = 977
  excluídos: conceito ausente em TI/AB/KW        n = 45
  aguardando conferência manual: sem resumo      n = 131
Trabalhos que atendem à regra de inclusão        n = 801
```

Trabalhos confirmados por ano: 2009: 4, 2010: 3, 2011: 8, 2012: 15, 2013: 15, 2014: 28, 2015: 34, 2016: 44, 2017: 36, 2018: 50, 2019: 62, 2020: 58, 2021: 69, 2022: 64, 2023: 68, 2024: 81, 2025: 78, 2026: 79

### Buscas executadas (texto exato)

**PubMed / MEDLINE** — ok, executada em 2026-10-23T13:47:30

```
(optogenet*[tiab] OR optogenet*[ot] OR opto-genet*[tiab] OR opto-genet*[ot] OR optigenet*[tiab] OR optigenet*[ot]) AND (alzheimer*[tiab] OR alzheimer*[ot] OR parkinson*[tiab] OR parkinson*[ot])
```
- sensibilidade — busca só com MeSH: `"Optogenetics"[Mesh] AND ("Alzheimer Disease"[Mesh] OR "Parkinson Disease"[Mesh] OR "Parkinsonian Disorders"[Mesh])` → 111 resultados

**Europe PMC (incl. preprints)** — ok, executada em 2026-10-23T13:47:30

```
(TITLE_ABS:optogenet* OR KW:optogenet* OR TITLE_ABS:"opto-genet*" OR KW:"opto-genet*" OR TITLE_ABS:optigenet* OR KW:optigenet*) AND (TITLE_ABS:alzheimer* OR KW:alzheimer* OR TITLE_ABS:parkinson* OR KW:parkinson*)
```
- sensibilidade — todos os campos, incluindo texto completo: `(optogenet* OR "opto-genet*" OR optigenet*) AND (alzheimer* OR parkinson*)` → 9.495 resultados

**OpenAlex** — ok, executada em 2026-10-23T13:47:30

```
title_and_abstract.search, union of: [(optogenetic OR optogenetics) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(optogenetically OR "opto-genetic") AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [("opto-genetics" OR optigenetic) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(optigenetics OR optogenética) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(optogenético OR optogenetica) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(optogenetico OR optogénétique) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(optogenetique OR optogenetik) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(optogenetisch) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(光遗传 OR 光遺傳) AND (阿尔茨海默 OR 阿茲海默 OR 阿兹海默 OR 帕金森)] ∪ [(光遗传 OR 光遺傳) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(光遺伝 OR オプトジェネティクス) AND (アルツハイマー OR パーキンソン)] ∪ [(光遺伝 OR オプトジェネティクス) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(оптогенетика OR оптогенетический) AND (альцгеймер OR паркинсон)] ∪ [(оптогенетика OR оптогенетический) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)] ∪ [(광유전) AND (알츠하이머 OR 파킨슨)] ∪ [(광유전) AND (alzheimer OR parkinson OR parkinsonism OR parkinsonian)]
```

**DOAJ** — ok, executada em 2026-10-23T13:47:30

```
(bibjson.title:(optogenetic OR optogenetics OR optogenetically OR "opto-genetic" OR "opto-genetics" OR optigenetic OR optigenetics OR optogenética OR optogenético OR optogenetica OR optogenetico OR optogénétique OR optogenetique OR optogenetik OR optogenetisch) OR bibjson.abstract:(optogenetic OR optogenetics OR optogenetically OR "opto-genetic" OR "opto-genetics" OR optigenetic OR optigenetics OR optogenética OR optogenético OR optogenetica OR optogenetico OR optogénétique OR optogenetique OR optogenetik OR optogenetisch) OR bibjson.keywords:(optogenetic OR optogenetics OR optogenetically OR "opto-genetic" OR "opto-genetics" OR optigenetic OR optigenetics OR optogenética OR optogenético OR optogenetica OR optogenetico OR optogénétique OR optogenetique OR optogenetik OR optogenetisch)) AND (bibjson.title:(alzheimer OR parkinson OR alzheimers OR parkinsons OR parkinsonism OR parkinsonian) OR bibjson.abstract:(alzheimer OR parkinson OR alzheimers OR parkinsons OR parkinsonism OR parkinsonian) OR bibjson.keywords:(alzheimer OR parkinson OR alzheimers OR parkinsons OR parkinsonism OR parkinsonian))
```

**arXiv** — ok, executada em 2026-10-23T13:47:30

```
(ti:optogenet* OR abs:optogenet* OR ti:optigenet* OR abs:optigenet*) AND (ti:alzheimer* OR abs:alzheimer* OR ti:parkinson* OR abs:parkinson*)
```

**Semantic Scholar** — ok, executada em 2026-10-23T13:47:30

```
(optogenet* | "opto-genet*" | optigenet*) + (alzheimer* | parkinson*)
```

### Bases não consultadas por código (licença / bloqueio a robôs)

Faça estas buscas manualmente, exporte os resultados em RIS/CSV para `data/manual/` e inclua-os na deduplicação (ver README).

| Base | Acesso | Busca |
|---|---|---|
| Scopus | API Elsevier (chave institucional) | `TITLE-ABS-KEY(optogenet* OR "opto-genet*" OR optigenet*) AND TITLE-ABS-KEY(alzheimer* OR parkinson*)` |
| Web of Science Core Collection | API WoS Starter/Expanded (chave Clarivate) | `TS=(optogenet* OR "opto-genet*" OR optigenet*) AND TS=(alzheimer* OR parkinson*)` |
| Embase | Ovid/Elsevier (licença; sem API aberta) | `(optogenet* OR 'opto-genet*' OR optigenet*):ti,ab,kw AND (alzheimer* OR parkinson*):ti,ab,kw` |
| LILACS / BVS (pt/es) | Só web (bloqueio a robôs; exportar CSV) | `(tw:(optogenet* OR optogenétic* OR optogenétic*)) AND (tw:(alzheimer* OR parkinson*))` |
| CNKI (zh) | Só web (licença) | `SU=('光遗传'+'光遺傳') AND SU=('阿尔茨海默'+'帕金森')` |
| CiNii / J-STAGE (ja) | API OpenSearch do CiNii (gratuita) | `光遺伝 OR オプトジェネティクス AND (アルツハイマー OR パーキンソン)` |

## Base de artigos e revisão por pares

`articles/` tem um arquivo Markdown para cada trabalho confirmado (801): cabeçalho YAML (título, DOI, autores, identificadores, trilha de identificação PRISMA e campos de triagem ainda vazios) e o resumo como corpo. Os trabalhos com revisão por pares ficam em `articles/peer_reviewed/`; os demais ficam direto em `articles/`. Índice: `data/articles_index.csv`. 761 têm resumo e 750 têm DOI.

**582 dos 801 trabalhos (73%) passaram por revisão por pares** (`peer_reviewed: true`).

| Tipo de documento | Trabalhos | `peer_reviewed` |
|---|---|---|
| Artigo de periódico | 456 | true |
| Revisão | 126 | true |
| Preprint | 82 | false |
| Tese / dissertação | 44 | false |
| Resumo de congresso (suplemento de periódico) | 33 | false |
| Trabalho completo de congresso | 22 | false |
| Tipo desconhecido | 16 | false |
| Editorial / notícia / comentário | 10 | false |
| Livro ou capítulo | 8 | false |
| Outros (dataset, relatório) | 4 | false |

Como é decidido: nenhuma base informa diretamente se houve revisão por pares, então isso é inferido do tipo de publicação e do veículo.

- A ordem de confiança é PubMed > Europe PMC > DOAJ (só lista periódicos com revisão por pares) > OpenAlex (consultado pelo DOI) > Semantic Scholar. A evidência usada para cada trabalho fica no campo `peer_review_basis`.
- O trabalho conta como revisado se qualquer versão dele saiu em periódico como artigo ou revisão. Um preprint unido à versão publicada é, portanto, `true`.
- Preprints são reconhecidos pelo prefixo do DOI ou pelo nome do servidor (bioRxiv, incluindo `10.64898`, medRxiv, Research Square, SSRN etc.).
- Resumos de congresso são reconhecidos por DOIs de suplemento e títulos numerados como "P1‐172: …", porque o OpenAlex e o Semantic Scholar costumam classificá-los como artigos.

Ressalvas:

- `true` não é juízo de qualidade; alguns veículos são questionáveis.
- Trabalhos completos de anais IEEE/EMBC costumam ter revisão, mas aqui são marcados `false`, por cautela.
- Os trabalhos `unknown` (em geral teses ou itens em outros idiomas sem DOI) ficam `false`.
- A deduplicação por título pode falhar com títulos corrompidos, por exemplo "Aβ" escrito como "Ab" ou "A b". Vale conferir isso na triagem.

## Registros de ensaios clínicos: qualquer uso de optogenética

Termos de busca (cada um buscado separadamente, resultados unidos): `optogenetic`, `optogenetics`, `optogenetically`, `opto-genetic`, `optogenética`, `optogénétique`, `channelrhodopsin`, `ChrimsonR`, `halorhodopsin`, `ChR2`, `multi-characteristic opsin`, `light-sensitive opsin`, `GS030`, `RST-001`, `MCO-010`, `sonpiretigene isteparvovec`, `BS01`, `Bionic Sight`

| Registro | Termos com resultados | Registros | Incluídos | Situação |
|---|---|---|---|---|
| ClinicalTrials.gov (API v2) | optogenetic: 15, optogenetics: 14, optogenetically: 1, channelrhodopsin: 3, ChrimsonR: 1, ChR2: 4, multi-characteristic opsin: 6, GS030: 1, RST-001: 1, MCO-010: 3, BS01: 14, Bionic Sight: 24 | 55 | 16 | ok |
| EU CTIS (EU Clinical Trials Regulation, 2023-) | ChrimsonR: 1, GS030: 1 | 1 | 1 | ok |
| EU Clinical Trials Register (EudraCT, legacy) | ChrimsonR: 1, GS030: 1 | 1 | 1 | ok |
| ISRCTN registry | BS01: 1 | 1 | 0 | ok |
| WHO ICTRP (meta-registry: ChiCTR, JPRN, ANZCTR, ReBEC, CTRI, DRKS, ...) | 0 | 0 | 0 | falhou: <HTTPError 502: 'Bad Gateway'> |

Resultado da triagem (todos os registros de ensaios): falso positivo: 40, tratamento: terapia gênica optogenética: 13, seguimento de tratamento: terapia gênica optogenética (segurança de longo prazo): 3, observacional: preparação para optogenética (seleção de candidatos): 2

### Ensaios incluídos

| ID | Registro | Categoria | Fase | Situação | Início | Patrocinador | Condição | Duplicata de | Observações |
|---|---|---|---|---|---|---|---|---|---|
| NCT02556736 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE1, PHASE2 | COMPLETED | 2015-12-14 | AbbVie | Advanced Retinitis Pigmentosa |  | RST-001 (AGN-151597): AAV2 channelrhodopsin-2 intravitreal, advanced RP; first-in-human optogenetic trial (RetroSense -> Allergan/AbbVie) |
| NCT03326336 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE1, PHASE2 | ACTIVE_NOT_RECRUITING | 2018-09-26 | GenSight Biologics | Non-syndromic Retinitis Pigmentosa |  | GS030 PIONEER: AAV2.7m8-ChrimsonR-tdTomato + light-stimulating goggles (GS030-MD), RP |
| NCT04278131 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE1, PHASE2 | RECRUITING | 2020-02-06 | Bionic Sight LLC | Retinitis Pigmentosa |  | BS01: AAV2-CAG-ChronosFP (Chronos opsin), RP |
| NCT04919473 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE1, PHASE2 | COMPLETED | 2019-10-23 | Nanoscope Therapeutics Inc. | Retinitis Pigmentosa; Retinal Diseases; Retinal Degeneration |  | vMCO-I (MCO-010, Nanoscope): multi-characteristic opsin, ambient-light activated, advanced RP, Ph1/2a |
| NCT04945772 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE2 | COMPLETED | 2021-07-13 | Nanoscope Therapeutics Inc. | Retinitis Pigmentosa; Retinitis; Retinal Diseases; Eye Diseases; Eye Diseases, Hereditary; Retinal Dystrophies; Retinal Degeneration |  | MCO-010 RESTORE Ph2b randomised sham-controlled, RP |
| NCT05294978 | ClinicalTrials.gov | observacional: preparação para optogenética (seleção de candidatos) |  | RECRUITING | 2021-07-01 | Institute of Molecular and Clinical Ophthalmology Basel | Retinal Dystrophies |  | EyeConic: imaging study to select patients for first-in-human cone optogenetics; no optogenetic intervention |
| NCT05417126 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE2 | COMPLETED | 2022-07-05 | Nanoscope Therapeutics Inc. | Stargardt Disease |  | vMCO-010 STARLIGHT Ph2a, Stargardt disease |
| NCT05921162 | ClinicalTrials.gov | seguimento de tratamento: terapia gênica optogenética (segurança de longo prazo) |  | ENROLLING_BY_INVITATION | 2023-07-14 | Nanoscope Therapeutics Inc. | Retinitis Pigmentosa; Retinal Disease; Retinal Degeneration | NCT04919473 | Long-term follow-up of the vMCO-I Ph1/2a cohort |
| NCT06048185 | ClinicalTrials.gov | seguimento de tratamento: terapia gênica optogenética (segurança de longo prazo) |  | ACTIVE_NOT_RECRUITING | 2023-10-19 | Nanoscope Therapeutics Inc. | Stargardt Disease | NCT05417126 | Long-term follow-up of STARLIGHT (MCO-010, Stargardt) |
| NCT06162585 | ClinicalTrials.gov | seguimento de tratamento: terapia gênica optogenética (segurança de longo prazo) |  | ACTIVE_NOT_RECRUITING | 2023-12-08 | Nanoscope Therapeutics Inc. | Retinitis Pigmentosa; Retinitis; Retinal Diseases; Eye Diseases; Eye Diseases, Hereditary; Retinal Dystrophies; Retinal Degeneration | NCT04945772 | Long-term follow-up of RESTORE (MCO-010, RP) |
| NCT06292650 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | EARLY_PHASE1 | RECRUITING | 2024-02-25 | Zhongmou Therapeutics | Retinitis Pigmentosa |  | ZM-02 MOON (Zhongmou): AAV optogenetic gene therapy (record keyword "optogenetics"), RP, early Ph1 |
| NCT06460844 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE1 | ACTIVE_NOT_RECRUITING | 2024-08-27 | Ray Therapeutics, Inc. | Retinitis Pigmentosa; Choroideremia |  | RTx-015 (Ray Therapeutics): "investigational optogenetic gene therapy", RP / choroideremia |
| NCT07056738 | ClinicalTrials.gov | observacional: preparação para optogenética (seleção de candidatos) |  | ENROLLING_BY_INVITATION | 2025-03-01 | University Medical Center Goettingen | Retinitis Pigmentosa |  | Observational RGC/inner-retina characterisation to define optogenetic treatment eligibility; no intervention |
| NCT07158775 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE1, PHASE2 | RECRUITING | 2026-01-08 | Bionic Sight LLC | Geographic Atrophy (GA) Secondary to Dry Age-related Macular Degeneration (AMD) |  | BS01: AAV2-CAG-ChronosFP, geographic atrophy secondary to dry AMD (first non-RP indication) |
| NCT07282457 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE1, PHASE2 | NOT_YET_RECRUITING | 2026-06-25 | Zhongmou Therapeutics | Retinitis Pigmentosa (RP) |  | ZM-02 Ph1/2 randomised sham-controlled; title: "Modified Optogenetic Gene Therapy", RP |
| NCT07439887 | ClinicalTrials.gov | tratamento: terapia gênica optogenética | PHASE1, PHASE2 | RECRUITING | 2026-01-28 | Ray Therapeutics, Inc. | Stargardt Disease |  | RTx-021 (Ray Therapeutics): "investigational optogenetic gene therapy", Stargardt |
| 2024-516059-42-00 | EU CTIS | tratamento: terapia gênica optogenética | Phase I and Phase II (Integrated)- Other | 4 |  | Gensight Biologics | Retinitis Pigmentosa | NCT03326336 | Same GS030 PIONEER trial, transitioned to CTIS under EU CTR 536/2014 |
| 2017-002204-27 | EUCTR | tratamento: terapia gênica optogenética |  |  |  |  | Retinitis Pigmentosa | NCT03326336 | Same GS030 PIONEER trial, legacy EudraCT registration |

**Alzheimer / Parkinson:** 0 ensaios optogenéticos registrados. Todas as intervenções optogenéticas registradas até hoje tratam doenças da retina (retinose pigmentar, doença de Stargardt, atrofia geográfica). Para a revisão, isso significa que a evidência em DA/DP é inteiramente pré-clínica.
