# Protocolo de busca: optogenética nas doenças de Alzheimer e Parkinson

Versão 1.0 · 23/10/2026 · O relato segue o PRISMA 2020 (fluxo completo, §6) e o PRISMA-S
(relato da busca). Resultados: [RELATORIO.md](RELATORIO.md).

## 0. Pergunta

Que literatura aplica, discute ou revisa a **optogenética** na **doença de Alzheimer (DA)** ou na
**doença de Parkinson (DP)**? A optogenética já foi usada em **algum ensaio clínico registrado**
(para qualquer condição)? Algum ensaio foi direcionado a DA ou DP?

## 1. Critérios de aceitação

Cada etapa só está concluída quando suas verificações passam. O `RELATORIO.md` mostra a situação
de cada uma.

| CA | Critério | Verificação |
|---|---|---|
| **CA-1** | Lista de bases pesquisáveis, consultadas por código sempre que possível | Tabela da §2; cada base "API" tem uma função funcionando em `litreview/literature.py` / `trials.py`; cada base não programática tem uma busca pronta para colar (RELATORIO.md) |
| **CA-2** | Busca quantitativa: os registros DEVEM conter um termo de optogenética (todas as variantes de idioma, sistematizadas) **E** (`alzheimer` **OU** `parkinson`) | Vocabulário da §3; a busca exata enviada a cada base e seu número de resultados, guardados em `data/search_log.json`; cada registro reconferido localmente (`verified`) |
| **CA-3** | Número de artigos por base, número encontrado **só** naquela base e o total sem repetição, tudo fácil de somar | `data/counts.csv` (por base: resultados / confirmados / exclusivos), `data/overlap_matrix.csv`, `data/works.csv` (uma linha por trabalho, uma coluna 0/1 por base, de modo que uma tabela dinâmica ou um `SUM` faz as somas) |
| **CA-4** | Busca sistemática em registros de ensaios clínicos para **qualquer** uso de optogenética, com triagem de cada registro | §5; `data/trials_log.json` (contagens por registro × termo), `data/trials_screening.csv` (decisão e justificativa de cada registro), `data/trials.csv` |

## 2. Bases (CA-1)

### 2.1 Consultadas por código

| Base | Cobertura | Interface | Campos pesquisados |
|---|---|---|---|
| PubMed / MEDLINE | Biomédica, curada; inclui PMC e alguns preprints | NCBI E-utilities (`esearch` + `efetch`) | `[tiab]` título/resumo + `[ot]` palavras-chave dos autores |
| Europe PMC | PubMed + PMC + preprints (bioRxiv, medRxiv, Research Square, …) + teses | API REST, paginação por cursor | `TITLE_ABS`, `KW` |
| OpenAlex | Cerca de 250 milhões de trabalhos de todas as áreas, em muitos idiomas, literatura cinzenta, teses | API REST | `title_and_abstract.search` (com stemming) |
| Semantic Scholar | Cerca de 200 milhões de trabalhos; forte em computação/neuroengenharia e trabalhos de congresso | Graph API `/paper/search/bulk` | título + resumo |
| DOAJ | Periódicos de acesso aberto, incluindo latino-americanos e em outros idiomas além do inglês | API REST (Lucene) | `bibjson.title/abstract/keywords` |
| arXiv | Preprints (q-bio.NC, physics.bio-ph, eess) | API Atom | `ti`, `abs` |

### 2.2 Não programáticas (licença ou bloqueio a robôs): buscas fornecidas, executadas à mão

Scopus, Web of Science, Embase (licenciadas; Scopus e WoS têm APIs, mas só com chave
institucional), LILACS/BVS (o portal web bloqueia acesso automatizado), CNKI (licença), CiNii.
As buscas estão no RELATORIO.md. Exporte os resultados em RIS/CSV para `data/manual/` para
incorporá-los à deduplicação.

### 2.3 Registros de ensaios

ClinicalTrials.gov (API v2), EU CTIS (API pública de busca), EU Clinical Trials Register / EudraCT
(HTML), ISRCTN (API) e WHO ICTRP. O ICTRP é um meta-registro que cobre ChiCTR, JPRN, ANZCTR,
**ReBEC (Brasil)**, CTRI, DRKS, IRCT, PACTR e outros. Ele não tem API pública, então o pipeline
tenta o portal e, se falhar, a alternativa é exportar um CSV manualmente.

## 3. Vocabulário de busca (CA-2)

### Conceito A: optogenética

| Forma | Cobre |
|---|---|
| `optogenet*` | EN optogenetic, optogenetics, optogenetically · PT/ES optogenética/o · IT optogenetica · FR optogénétique (sem acentos) · DE Optogenetik, optogenetisch |
| `opto-genet*` | grafia com hífen |
| `optigenet*` | erro de grafia (aparece no pedido e, às vezes, em registros indexados) |
| Alfabetos não latinos | RU оптогенетика · ZH 光遗传 / 光遺傳 · JA 光遺伝, オプトジェネティクス · KO 광유전 |

### Conceito B: doença

`alzheimer*` e `parkinson*` se escrevem igual em todas as línguas de alfabeto latino. O
truncamento também cobre Alzheimer's, Alzheimers, parkinsonism e parkinsonian. Não latinas: RU
альцгеймер, паркинсон · ZH 阿尔茨海默, 帕金森 · JA アルツハイマー, パーキンソン · KO 알츠하이머,
파킨슨.

**Lógica:** `A AND B`. O escopo da busca é **título + resumo + palavras-chave dos autores**. MeSH
e texto completo ficam fora da busca principal de propósito, porque o critério é a
*palavra-chave* aparecer. A busca em texto completo pega sobretudo menções de passagem. Os dois
são informados como contagens de sensibilidade: PubMed só com MeSH e Europe PMC em todos os
campos, incluindo texto completo.

### Adaptação da sintaxe por buscador

- Truncamento (`*`) onde é aceito: PubMed, Europe PMC, Semantic Scholar, arXiv.
- Sem truncamento (OpenAlex, DOAJ): todas as formas da palavra são listadas explicitamente. O
  OpenAlex limita buscas com mais de 5 operadores booleanos, então a busca é dividida em
  subconsultas de no máximo 5 operadores e os resultados são unidos pelo ID do OpenAlex. Os
  termos não latinos são combinados com termos de doença do mesmo idioma.
- A maioria dos índices guarda título e resumo em inglês mesmo para artigos em outros idiomas,
  então os radicais em inglês já capturam a maior parte desses trabalhos. As formas traduzidas
  aumentam a sensibilidade para registros guardados só no idioma original (OpenAlex, DOAJ).

### Reverificação local

As APIs casam termos de forma frouxa: stemming, expansão MeSH dentro de `KW`, tokenização em
bigramas de chinês/japonês/coreano e os resumos ocultos do Semantic Scholar. Por isso cada
registro recuperado é reconferido localmente com expressões regulares sobre título + resumo +
palavras-chave (sem distinção de maiúsculas e sem acentos; `litreview/common.py:matches`).

## 4. Deduplicação e contagem (CA-3)

- Dois registros são o **mesmo trabalho** se compartilham DOI, PMID, PMCID ou ID arXiv, ou o
  título normalizado (25 ou mais caracteres alfanuméricos). A ligação é transitiva (union-find).
- Assim, um preprint e sua versão em periódico viram **um só trabalho** ("vários relatos do
  mesmo estudo"). A coluna `n_versions` marca esses casos, para que possam ser separados de novo
  se o protocolo da revisão preferir.
- Situação de cada trabalho:
  - `confirmed`: os dois conceitos aparecem em pelo menos um registro do trabalho.
  - `rejected`: há resumo e falta um conceito.
  - `unverifiable`: sem resumo em lugar nenhum. Esses são listados para triagem manual e ficam
    fora dos totais.
- **Exclusivo da base X** = trabalhos confirmados cuja única fonte é X.

## 5. Revisão de ensaios clínicos (CA-4)

- **Escopo:** qualquer uso de optogenética, em qualquer condição (não só DA/DP). Depois, um
  ensaio é marcado quando título, condições ou resumo mencionam DA, DP, demência ou
  comprometimento cognitivo.
- **Termos**, cada um buscado separadamente e com os resultados unidos: as formas de
  "optogenético"; os nomes de opsinas channelrhodopsin, ChR2, ChrimsonR, halorhodopsin,
  "multi-characteristic opsin" e "light-sensitive opsin"; e todos os produtos optogenéticos que
  se sabe terem chegado à clínica: GS030, RST-001, MCO-010 / sonpiretigene isteparvovec, BS01 /
  Bionic Sight. Os códigos dos produtos são necessários porque alguns registros (como o EUCTR)
  não indexam a palavra "optogenetic" para esses ensaios.
- **Triagem** (`data/trials_screening.csv`; um revisor por enquanto, **um segundo revisor
  independente é obrigatório** antes da publicação):
  - *incluir, intervencional*: a intervenção entrega um gene de opsina sensível à luz, com ou
    sem dispositivo de emissão de luz.
  - *incluir, seguimento*: extensão de segurança de longo prazo de um ensaio incluído.
  - *incluir, observacional*: sem intervenção, mas o estudo existe para viabilizar a terapia
    optogenética (por exemplo, seleção de candidatos).
  - *excluir*: a optogenética aparece só de forma incidental (como o nome do centro), ou o
    resultado veio de um código ambíguo ("BS01" ou "ChR2" em estudos sem relação, dispositivos
    "bionic").
- Registros do **mesmo ensaio** em vários registros são ligados por `same_trial_as` e contados
  uma vez.

## 6. Elegibilidade e fluxo PRISMA 2020

O relato segue o diagrama de fluxo do PRISMA 2020 para revisões novas com bases, registros e outras
fontes (Page et al., *BMJ* 2021;372:n71). `python3 -m litreview.prisma` calcula o n de cada etapa
(`data/prisma.json`), desenha o diagrama (`data/prisma_flow.svg`, `data/prisma_flow.en.svg`) e grava
a seleção final (`data/included.csv`).

- **Unidade de contagem:** *registro* antes da deduplicação; depois dela, *estudo* = trabalho único,
  e *relatos* = suas versões (preprint e periódico).
- **Removidos antes da triagem:** duplicados; inelegíveis pela reverificação automática de
  palavras-chave (`rejected`); sem resumo em nenhuma fonte (`unverifiable`).
- **Triagem e texto completo:** decisões dos revisores nos campos `prisma.screening` de cada
  `articles/*.md` (`title_abstract: exclude`, `full_text: not_retrieved | exclude`, com o motivo).
- **Critérios de elegibilidade**, nesta ordem; cada trabalho é excluído uma vez, pelo primeiro
  critério que não cumpre:
  1. publicado em **2020 ou depois** (ano desconhecido também exclui);
  2. **com revisão por pares** (`peer_reviewed: true`, ver README);
  3. motivos de exclusão do texto completo dados pelos revisores.
- **Tipo de estudo** (`study_type`, heurístico): meta-análise e revisão sistemática pelo tipo de
  publicação do PubMed/Europe PMC ou pelo título; revisão pelo `document_type`; metodologia por
  periódicos de protocolos/métodos ou pelo título; o resto é pesquisa original ou "outros".
- Os **registros de ensaios** (§5) respondem a outra pergunta e têm fluxo próprio
  (`data/prisma.json` → `registers`).

## 7. Fora do escopo desta etapa / próximos passos

1. Triagem de **relevância** (título/resumo) dos trabalhos confirmados (dois revisores, por
   exemplo no Rayyan/ASReview). A regra de palavra-chave decide a *identificação*, não a
   elegibilidade para a revisão.
2. Buscas manuais nas bases da §2.2 e incorporação das exportações.
3. Exportação do WHO ICTRP, se o portal ainda estiver fora do ar no momento da execução.
4. Busca por citações (para trás e para frente) a partir das revisões incluídas.
