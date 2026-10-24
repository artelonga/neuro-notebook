# Optogenética × Alzheimer/Parkinson: relatório da busca

Resumo em português de [REPORT.md](REPORT.md), com os números da execução de 23/10/2026.
O REPORT.md é regenerado a cada execução; este resumo é um retrato fixo. Se as buscas forem
refeitas, os números daqui precisam ser atualizados à mão. Protocolo: [PROTOCOLO.md](PROTOCOLO.md).

## Números principais

- **2.167** registros coletados em **6** bases consultadas por código.
- **977** trabalhos únicos depois da deduplicação entre bases (1.190 registros duplicados removidos).
- **801 trabalhos únicos atendem à regra** de inclusão (582 com revisão por pares), reconferida no título, resumo e
  palavras-chave.
  - 131 são não verificáveis, por não terem resumo.
  - 45 foram rejeitados como falsos positivos dos buscadores.
- **Registros de ensaios:** 58 registros → 18 sobre optogenética → **11 ensaios optogenéticos de
  tratamento distintos** → **0 em Alzheimer ou Parkinson**.

## Critérios de aceitação

| CA | Situação |
|---|---|
| CA-1 Bases | ✅ 6 bases de literatura e 5 registros consultados por API; 6 bases licenciadas ou só web documentadas com buscas prontas |
| CA-2 Busca | ✅ Busca exata e número de resultados por base (abaixo e em `data/search_log.json`) |
| CA-3 Contagens | ✅ `data/counts.csv`, `data/overlap_matrix.csv`, `data/works.csv` |
| CA-4 Ensaios | ⚠️ Parcial: o WHO ICTRP (que cobre ChiCTR, JPRN, ANZCTR, ReBEC, CTRI e DRKS) retornou erro 502; precisa ser refeito ou exportado manualmente |

## Resultados por base

**Como ler a tabela:**
- *Resultados:* o que a API informou.
- *Confirmados:* trabalhos que de fato contêm os dois conceitos.
- *Exclusivos:* trabalhos confirmados encontrados **só** naquela base.
- *Participação:* fração dos 801 trabalhos coberta pela base.

| Base | Resultados | Confirmados | Não verificáveis | Rejeitados | Exclusivos | Participação |
|---|---|---|---|---|---|---|
| PubMed / MEDLINE | 486 | 477 | 0 | 0 | 5 | 59,6% |
| Europe PMC (com preprints) | 589 | 535 | 0 | 21 | 18 | 66,8% |
| OpenAlex | 267 | 230 | 4 | 24 | 69 | 28,7% |
| Semantic Scholar | 786 | 637 | 128 | 0 | 138 | 79,5% |
| DOAJ | 33 | 33 | 0 | 0 | 2 | 4,1% |
| arXiv | 6 | 6 | 0 | 0 | 0 | 0,7% |
| **Total sem repetição** | 2.167 | **801** | 131 | 45 | 232 | 100% |

**O que mostram as contagens:**
- **Cobertura:** 260 dos 801 trabalhos (32%) não estão nem no PubMed nem na Europe PMC.
- **Exclusivos:** os trabalhos que só uma base encontrou são sobretudo literatura cinzenta: teses,
  trabalhos de congresso, preprints e periódicos fora do MEDLINE.
- **Preprints:** 49 trabalhos confirmados unem um preprint à versão publicada.
- **Por ano:** 4 trabalhos em 2009, 34 em 2015, 58 em 2020, 81 em 2024, 78 em 2025 e 79 até
  agora em 2026.

**Sobreposição** (trabalhos confirmados presentes nas duas bases):

| | PubMed | Europe PMC | OpenAlex | Sem. Scholar | DOAJ | arXiv |
|---|---|---|---|---|---|---|
| PubMed | 477 | 471 | 103 | 403 | 29 | 3 |
| Europe PMC | 471 | 535 | 112 | 448 | 29 | 3 |
| OpenAlex | 103 | 112 | 230 | 151 | 23 | 1 |
| Sem. Scholar | 403 | 448 | 151 | 637 | 30 | 6 |
| DOAJ | 29 | 29 | 23 | 30 | 33 | 0 |
| arXiv | 3 | 3 | 1 | 6 | 0 | 6 |

**Análises de sensibilidade:**
- PubMed só com MeSH (`"Optogenetics"[Mesh] AND ("Alzheimer Disease"[Mesh] OR "Parkinson
  Disease"[Mesh] OR "Parkinsonian Disorders"[Mesh])`): 111 resultados.
- Europe PMC em todos os campos, incluindo texto completo: 9.495 resultados. A regra de
  palavra-chave é estrita de propósito.

## Buscas executadas

As buscas ficam no idioma de cada base:

```
PubMed:     (optogenet*[tiab] OR optogenet*[ot] OR opto-genet*[tiab] OR opto-genet*[ot]
             OR optigenet*[tiab] OR optigenet*[ot]) AND (alzheimer*[tiab] OR alzheimer*[ot]
             OR parkinson*[tiab] OR parkinson*[ot])
Europe PMC: (TITLE_ABS:optogenet* OR KW:optogenet* OR TITLE_ABS:"opto-genet*" OR KW:"opto-genet*"
             OR TITLE_ABS:optigenet* OR KW:optigenet*) AND (TITLE_ABS:alzheimer* OR KW:alzheimer*
             OR TITLE_ABS:parkinson* OR KW:parkinson*)
Semantic Scholar: (optogenet* | "opto-genet*" | optigenet*) + (alzheimer* | parkinson*)
arXiv:      (ti:optogenet* OR abs:optogenet* OR ti:optigenet* OR abs:optigenet*)
             AND (ti:alzheimer* OR abs:alzheimer* OR ti:parkinson* OR abs:parkinson*)
```

- **OpenAlex:** união de 16 subconsultas de `title_and_abstract.search`, cada uma com até 5
  operadores, cobrindo as 15 formas latinas e os termos em chinês, japonês, russo e coreano.
- **DOAJ:** as mesmas formas listadas em título, resumo e palavras-chave.
- **Texto exato:** as buscas completas, com data e hora de execução, estão em
  `data/search_log.json`.

## Bases para busca manual

Exporte os resultados em RIS/CSV para `data/manual/` e inclua-os na deduplicação.

| Base | Acesso | Busca |
|---|---|---|
| Scopus | API Elsevier (chave institucional) | `TITLE-ABS-KEY(optogenet* OR "opto-genet*" OR optigenet*) AND TITLE-ABS-KEY(alzheimer* OR parkinson*)` |
| Web of Science | API WoS (chave Clarivate) | `TS=(optogenet* OR "opto-genet*" OR optigenet*) AND TS=(alzheimer* OR parkinson*)` |
| Embase | Ovid/Elsevier (licença) | `(optogenet* OR 'opto-genet*' OR optigenet*):ti,ab,kw AND (alzheimer* OR parkinson*):ti,ab,kw` |
| LILACS / BVS | Só web (bloqueio a robôs) | `(tw:(optogenet* OR optogenétic*)) AND (tw:(alzheimer* OR parkinson*))` |
| CNKI | Só web (licença) | `SU=('光遗传'+'光遺傳') AND SU=('阿尔茨海默'+'帕金森')` |
| CiNii / J-STAGE | API OpenSearch (gratuita) | `光遺伝 OR オプトジェネティクス AND (アルツハイマー OR パーキンソン)` |

## Base de artigos e revisão por pares

`articles/` tem um arquivo Markdown para cada trabalho confirmado (801).
- **Cabeçalho YAML:** título, DOI, autores, identificadores, trilha de identificação PRISMA e
  campos de triagem ainda vazios.
- **Corpo:** o resumo.
- **Cobertura:** 761 trabalhos têm resumo e 750 têm DOI.
- **Pastas:** os trabalhos com revisão por pares ficam em `articles/peer_reviewed/`; os demais
  ficam direto em `articles/`.
- **Índice:** `data/articles_index.csv`.

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

**Como é decidido:** nenhuma base informa diretamente se houve revisão por pares, então isso é
inferido do tipo de publicação e do veículo.
- **Ordem de confiança:** PubMed, depois Europe PMC, depois DOAJ (que só lista periódicos com
  revisão por pares), depois OpenAlex (consultado pelo DOI), depois Semantic Scholar. A evidência
  usada para cada trabalho fica no campo `peer_review_basis`.
- **Versão publicada vale:** o trabalho conta como revisado se qualquer versão dele saiu em
  periódico como artigo ou revisão. Um preprint unido à versão publicada é `true`.
- **Preprints:** reconhecidos pelo prefixo do DOI ou pelo nome do servidor (bioRxiv, incluindo
  `10.64898`, medRxiv, Research Square, SSRN etc.).
- **Resumos de congresso:** reconhecidos por DOIs de suplemento e títulos numerados como
  "P1‐172: …". O OpenAlex e o Semantic Scholar costumam classificá-los como artigos.

**Ressalvas:**
- `true` não é juízo de qualidade; alguns periódicos são questionáveis.
- Trabalhos completos de anais IEEE/EMBC costumam ter revisão, mas foram marcados `false`, por
  cautela.
- Os 16 de tipo desconhecido (em geral teses ou itens em outros idiomas sem DOI) ficaram `false`.
- A deduplicação por título pode falhar com títulos corrompidos ("Aβ" escrito como "Ab" ou
  "A b"). Vale conferir isso na triagem.

## Ensaios clínicos: qualquer uso de optogenética

| Registro | Registros | Incluídos | Situação |
|---|---|---|---|
| ClinicalTrials.gov | 55 | 16 | ok |
| EU CTIS | 1 | 1 | ok (mesmo ensaio GS030) |
| EU CTR / EudraCT | 1 | 1 | ok (mesmo ensaio GS030) |
| ISRCTN | 1 | 0 | ok |
| WHO ICTRP | 0 | 0 | falhou: erro 502 |

**Triagem dos 58 registros:**
- 40 falsos positivos (por exemplo "BS01", "ChR2" e dispositivos "bionic" em estudos sem relação).
- 13 registros de tratamento, que correspondem a 11 ensaios distintos (o GS030 tem 3 registros).
- 3 seguimentos de longo prazo.
- 2 estudos observacionais de seleção de pacientes.

### Os 11 ensaios de tratamento

| Produto | Patrocinador | Opsina | Condição | Fase | Situação | ID |
|---|---|---|---|---|---|---|
| RST-001 | AbbVie (Allergan) | ChR2 | RP avançada | 1/2 | Concluído | NCT02556736 |
| GS030 PIONEER (+ óculos estimuladores) | GenSight | ChrimsonR | RP | 1/2a | Ativo, sem recrutar | NCT03326336 (também EudraCT 2017-002204-27 e CTIS 2024-516059-42-00) |
| vMCO-I | Nanoscope | MCO | RP avançada | 1/2a | Concluído | NCT04919473 |
| MCO-010 RESTORE | Nanoscope | MCO | RP | 2b | Concluído | NCT04945772 |
| MCO-010 STARLIGHT | Nanoscope | MCO | Stargardt | 2a | Concluído | NCT05417126 |
| BS01 | Bionic Sight | ChronosFP | RP | 1/2 | Recrutando | NCT04278131 |
| BS01 | Bionic Sight | ChronosFP | AG (DMRI seca) | 1/2 | Recrutando | NCT07158775 |
| ZM-02 MOON | Zhongmou | não informada | RP | 1 inicial | Recrutando | NCT06292650 |
| ZM-02 | Zhongmou | não informada | RP | 1/2 | Ainda não aberto | NCT07282457 |
| RTx-015 | Ray Therapeutics | não informada | RP, coroideremia | 1 | Ativo, sem recrutar | NCT06460844 |
| RTx-021 | Ray Therapeutics | não informada | Stargardt | 1/2 | Recrutando | NCT07439887 |

**Outros incluídos:**
- **Seguimentos:** NCT05921162 (vMCO-I), NCT06048185 (STARLIGHT), NCT06162585 (RESTORE).
- **Observacionais:** NCT05294978 (EyeConic, seleção para optogenética de cones) e NCT07056738
  (elegibilidade para terapia optogenética).

Siglas: RP, retinose pigmentar; AG, atrofia geográfica; DMRI, degeneração macular relacionada à
idade; MCO, opsina multicaracterística.

## Conclusões

1. **A literatura é extensa e está crescendo:** 801 trabalhos únicos, cerca de 80 por ano desde
   2024.
2. **Uma base só não basta:** o PubMed cobre 60% dos trabalhos, e 232 trabalhos aparecem em uma
   única base.
3. **A optogenética clínica é oftalmológica:** os 11 ensaios tratam degeneração retiniana.
4. **Em Alzheimer e Parkinson a evidência é inteiramente pré-clínica.** Não há nenhum ensaio
   registrado. Isso ainda depende da busca no WHO ICTRP.

## Pendências

1. Refazer ou exportar manualmente o WHO ICTRP.
2. Executar as 6 buscas manuais e incorporar as exportações.
3. Segundo revisor para a triagem dos ensaios.
4. Checar manualmente os 131 trabalhos sem resumo.
5. Triagem de relevância dos 801 trabalhos por dois revisores (Rayyan ou ASReview).
6. Busca por citações e diagrama PRISMA final.
