# neuro-notebook: revisão de literatura sobre optogenética × Alzheimer/Parkinson

Um pipeline de busca reprodutível para um artigo de revisão. Python 3.9+ só com a biblioteca
padrão, sem dependências.

- **Protocolo e critérios de aceitação:** [PROTOCOLO.md](PROTOCOLO.md)
- **Resultados:** [RELATORIO.md](RELATORIO.md) (regenerado a cada execução)

## Execução

```bash
./run.sh            # uses the HTTP cache in data/cache/
./run.sh --refresh  # re-query every API (the date is logged)
```

Chaves opcionais (limites de requisição maiores; defina-as como variáveis de ambiente, nunca
as coloque no repositório): `NCBI_API_KEY`, `OPENALEX_API_KEY`, `S2_API_KEY`.

## Saídas (`data/`)

| Arquivo | Conteúdo |
|---|---|
| `search_log.json` | busca exata, número de resultados da API, contagens de recuperados e verificados por base, data e hora |
| `raw/<db>.jsonl` | registros normalizados por base |
| `works.csv` | **uma linha por trabalho único**: `status`, `n_databases`, colunas 0/1 `in_<db>`, identificadores |
| `counts.csv` | por base: resultados, confirmados, não verificáveis, rejeitados, **exclusivos**, participação; mais a linha de total |
| `overlap_matrix.csv` | sobreposição, par a par, dos trabalhos confirmados |
| `trials_raw.csv` / `trials.csv` | registros de ensaios (união entre os termos) e os mesmos registros unidos às decisões de triagem |
| `trials_screening.csv` | **editado à mão**: decisão, categoria, `same_trial_as`, justificativa |
| `prisma.json` | **o n de cada etapa do fluxo PRISMA 2020** (identificação, triagem, elegibilidade, incluídos, registros de ensaios) |
| `prisma_flow.svg` / `prisma_flow.en.svg` | diagrama de fluxo PRISMA 2020 (pt-BR / inglês) |
| `prisma_works.csv` | uma linha por trabalho único: `excluded_at` (etapa em que saiu do fluxo), `reason`, `included`, `study_type` |
| `included.csv` | **seleção final**: os trabalhos incluídos (≥ 2020 e com revisão por pares, menos as exclusões dos revisores) |

Soma rápida: filtre `works.csv` por `status == confirmed`. O número de linhas é o total sem
repetição. `SUM(in_pubmed)` é a contagem do PubMed. As linhas com `n_databases == 1` são os
trabalhos exclusivos de uma base.

## Base de artigos (`articles/`)

Um arquivo Markdown por trabalho **confirmado** (801), com o nome do título (`<title>.md`;
`<title> (W0123).md` se dois títulos coincidirem). `articles/` é a base de revisão: todos os
trabalhos triados. **`articles/selected/` é a seleção final do fluxo PRISMA** (publicados em 2020
ou depois, com revisão por pares, menos os excluídos pelos revisores); o resto fica direto em
`articles/`. O corpo é o resumo. O front matter YAML é:

```yaml
title, doi, work_id, authors[], year, journal
peer_reviewed: true          # inferred: published as a journal article or review (see below)
document_type                # journal-article | review | preprint | thesis | conference-abstract |
                             # conference-paper | book | editorial-or-news | other | unknown
peer_review_basis            # the evidence used, e.g. "pubmed: Journal Article; Review"
study_type                   # original-research | review | systematic-review | meta-analysis |
                             # methodology | other (heuristic, see PROTOCOLO.md §6)
publication_type, language, keywords[]
identifiers: {pmid, pmcid, arxiv, openalex}
other_dois[]                 # other versions merged into this work (preprint <-> journal)
abstract_source, authors_source
prisma:
  identification: {search_date, search_rule, databases[], n_databases,
                   source_records[], keyword_check, duplicates_merged}
  eligibility:               # automatic: year >= 2020 AND peer_reviewed
    {criteria, eligible, reason}   # reason: before_min_year | year_unknown | not_peer_reviewed
  screening:                 # filled in by the reviewers
    title_abstract: pending  # include | exclude | pending
    title_abstract_reason: null
    full_text: pending       # include | exclude | pending | not_retrieved
    full_text_reason: null
    reviewers: []
    notes: ""
  included: null             # true/false once screening is done
```

`data/articles_index.csv` liga `work_id` ao nome do arquivo, com `peer_reviewed`,
`document_type`, `study_type` e `eligible`.

## Vínculos: tópicos e glossário

`python3 -m litreview.vincular` (rodado pelo `./run.sh` depois do `export`) liga cada artigo ao
seu tópico e aos termos do glossário, e mede os termos:

```bash
python3 -m litreview.vincular                               # articles/selected/  (N = 370)
python3 -m litreview.vincular --conjunto nao-selecionados   # o resto de articles/ (N = 431)
python3 -m litreview.vincular --conjunto todos              # os 801
python3 -m litreview.vincular --todas-ocorrencias           # liga toda ocorrência, não só a primeira
```

- **No artigo:** a primeira ocorrência de cada termo do resumo vira `[[grafo/termos/<termo>|texto]]`
  (plurais, hífen/espaço e siglas como DBS, STN e 6-OHDA levam ao mesmo verbete); depois do
  resumo, um bloco entre `<!-- vinculos:inicio -->` e `<!-- vinculos:fim -->` liga ao tópico e
  lista os termos; o cabeçalho ganha `topico`, `topico_nome` e `n_termos`. Rodar de novo
  substitui tudo isso (só os links para `grafo/termos/` são desfeitos).
- **As duas bases:** `grafo/termos/` (glossário: um verbete por termo, com os backlinks de todos os
  artigos que o usam) e `grafo/topicos/` (um por tópico). Ambas vêm de `topicos/` (ver
  `topicos/README.md`); termos genéricos demais ficam fora pela lista `topicos/termos_excluidos.txt`.
- **Medidas** (em `data/termos/<conjunto>/`; o denominador é o número de artigos do conjunto):
  *cobertura* = % dos textos em que o termo aparece; *prevalência* = ocorrências por 10 mil
  palavras dos resumos; *média por texto* = ocorrências por texto onde aparece. Os links usam o
  termo mais específico ("dopamine release"), mas a contagem procura cada termo por si, então
  "dopamine" também conta dentro de "dopamine release".

| Arquivo | Conteúdo |
|---|---|
| `termos.csv` | por termo: `n_textos`, `cobertura`, `ocorrencias`, `prevalencia`, `media_por_texto`, tópico dominante |
| `termos_por_topico.csv` | cobertura de cada termo dentro de cada tópico (% dos textos do tópico) |
| `topicos.csv` | textos por tópico e seus termos característicos (lift = cobertura no tópico ÷ cobertura no conjunto) |
| `ocorrencias.csv` | tabela longa `work_id, termo, n`, para qualquer outra análise |

Os verbetes também recebem `cobertura_<conjunto>` e `textos_<conjunto>` no cabeçalho (o campo
`trabalhos` conta outra coisa: os trabalhos em que o termo foi palavra-chave ou frase extraída).

**Três grafos no Obsidian.** Os conjuntos `selecionados` e `todos` também geram notas próprias de
termo e de tópico ao lado dos seus artigos, com os números daquele conjunto e links só para os
artigos dele. Cole o filtro na busca da visão de grafo:

| Escopo | Filtro | Notas | O que liga |
|---|---|---|---|
| Rede global de termos | `path:"grafo/"` | `grafo/` | termo ↔ termo (coocorrência, NPMI) e tópicos |
| Os 801 artigos | `path:articles -path:grafo-selecionados` | `articles/grafo-todos/` | artigo ↔ termo ↔ tópico, números dos 801 |
| Os 370 da seleção final | `path:"articles/selected"` | `articles/selected/grafo-selecionados/` | artigo ↔ termo ↔ tópico, números dos 370 |

Os links nos resumos apontam sempre para o verbete geral (`grafo/termos/`); as notas de escopo é que
apontam para os artigos do seu conjunto, então cada filtro mostra só as ligações daquele conjunto.
As pastas não se chamam `grafo` para que um link `grafo/termos/…` nunca caia numa nota de escopo. Os
artigos ganham a tag `tema/<n>` e ficam coloridos pelo tema, como os termos.

**Obsidian aberto durante o `./run.sh`:** o `export` apaga e recria `articles/`; recarregue o
Obsidian depois (Cmd+P → "Reload app without saving"), ou ele pode criar notas vazias ao clicar em
links que ainda não reconhece.

## Fluxo PRISMA 2020

`python3 -m litreview.prisma` (incluído no `./run.sh`) conta cada etapa e desenha o diagrama.
Para registrar a triagem humana, preencha `prisma.screening` nos arquivos de `articles/` e rode de
novo só `python3 -m litreview.prisma && python3 -m litreview.report` (não o `export`, que
apagaria as decisões). O `prisma` move os arquivos para dentro ou para fora de
`articles/selected/` conforme as decisões e atualiza `data/articles_index.csv`.

**`peer_reviewed` é inferido.** Nenhuma base informa diretamente se houve revisão por pares. Um
trabalho é `true` quando qualquer versão dele foi publicada em periódico como artigo ou revisão.
A ordem de confiança da evidência é PubMed > Europe PMC > DOAJ > OpenAlex (consultado pelo DOI) >
Semantic Scholar. Todo o resto é `false`: preprints, teses, livros, trabalhos de congresso,
resumos de congresso em suplementos de periódicos, editoriais e notícias, e tipos desconhecidos.
Duas ressalvas:
- `true` não é juízo de qualidade; alguns veículos são questionáveis.
- Trabalhos completos de anais IEEE/EMBC costumam ter revisão, mas aqui contam como `false`, por
  cautela.

**Atenção:** `python3 -m litreview.export` (e `./run.sh`) reconstrói `articles/` do zero, então decisões de triagem registradas nos
arquivos seriam perdidas. Faça backup delas, ou pare de reexportar, quando a triagem começar.

## Como incluir bases pesquisadas à mão (Scopus, WoS, Embase, LILACS, …)

Execute as buscas listadas no RELATORIO.md e exporte os resultados para `data/manual/<db>.csv`.
Depois converta cada exportação em `data/raw/<db>.jsonl` com `litreview.common.record(...)` e
inclua-a em `SOURCES`, para que a deduplicação a considere.

## Triagem de novos ensaios

Registros de ensaios novos aparecem como `PENDING` em `data/trials.csv`. Adicione uma linha para
cada um em `data/trials_screening.csv` e execute de novo.
