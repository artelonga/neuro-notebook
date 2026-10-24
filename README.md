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

Soma rápida: filtre `works.csv` por `status == confirmed`. O número de linhas é o total sem
repetição. `SUM(in_pubmed)` é a contagem do PubMed. As linhas com `n_databases == 1` são os
trabalhos exclusivos de uma base.

## Base de artigos (`articles/`)

Um arquivo Markdown por trabalho **confirmado** (801), com o nome do título (`<title>.md`;
`<title> (W0123).md` se dois títulos coincidirem). Os trabalhos com revisão por pares
(`peer_reviewed: true`) ficam em `articles/peer_reviewed/`; todo o resto (preprints, teses,
resumos de congresso, …) fica direto em `articles/`. O corpo é o resumo. O front matter YAML é:

```yaml
title, doi, work_id, authors[], year, journal
peer_reviewed: true          # inferred: published as a journal article or review (see below)
document_type                # journal-article | review | preprint | thesis | conference-abstract |
                             # conference-paper | book | editorial-or-news | other | unknown
peer_review_basis            # the evidence used, e.g. "pubmed: Journal Article; Review"
publication_type, language, keywords[]
identifiers: {pmid, pmcid, arxiv, openalex}
other_dois[]                 # other versions merged into this work (preprint <-> journal)
abstract_source, authors_source
prisma:
  identification: {search_date, search_rule, databases[], n_databases,
                   source_records[], keyword_check, duplicates_merged}
  screening:                 # filled in by the reviewers
    title_abstract: pending  # include | exclude | pending
    title_abstract_reason: null
    full_text: pending       # include | exclude | pending | not_retrieved
    full_text_reason: null
    reviewers: []
    notes: ""
  included: null             # true/false once screening is done
```

`data/articles_index.csv` liga `work_id` ao nome do arquivo, com `peer_reviewed` e
`document_type`.

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
