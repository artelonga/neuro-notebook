# neuro-notebook: optogenetics × Alzheimer/Parkinson literature review

A reproducible search pipeline for a review paper. Stdlib-only Python 3.9+, no dependencies.

- **Protocol and acceptance criteria:** [PROTOCOL.md](PROTOCOL.md)
- **Results:** [REPORT.md](REPORT.md) (regenerated on every run)
- **Em português:** [PROTOCOLO.md](PROTOCOLO.md) e [RELATORIO.md](RELATORIO.md), summaries frozen at the 2026-10-23 run

## Run

```bash
./run.sh            # uses the HTTP cache in data/cache/
./run.sh --refresh  # re-query every API (the date is logged)
```

Optional keys (higher rate limits; set them as environment variables, never commit them):
`NCBI_API_KEY`, `OPENALEX_API_KEY`, `S2_API_KEY`.

## Outputs (`data/`)

| File | Content |
|---|---|
| `search_log.json` | exact query, API hit count, retrieved and verified counts per database, timestamp |
| `raw/<db>.jsonl` | normalised records per database |
| `works.csv` | **one row per unique work**: `status`, `n_databases`, `in_<db>` 0/1 columns, IDs |
| `counts.csv` | per database: hits, confirmed, unverifiable, rejected, **unique**, share; plus the total row |
| `overlap_matrix.csv` | pairwise overlap of confirmed works |
| `trials_raw.csv` / `trials.csv` | registry records (union over terms) and the same records joined with screening decisions |
| `trials_screening.csv` | **human-edited**: decision, category, `same_trial_as`, reason |

Quick aggregation: filter `works.csv` on `status == confirmed`. The row count is the total
with duplicates removed. `SUM(in_pubmed)` is PubMed's count. Rows with `n_databases == 1`
are works unique to one database.

## Article database (`articles/`)

One Markdown file per **confirmed** work (801), named after its title (`<title>.md`;
`<title> (W0123).md` if two titles collide). Peer-reviewed works (`peer_reviewed: true`) go in
`articles/peer_reviewed/`; everything else (preprints, theses, abstracts, …) stays directly in
`articles/`. The body is the abstract. The YAML front matter is:

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

`data/articles_index.csv` maps `work_id` to file name, with `peer_reviewed` and `document_type`.

**`peer_reviewed` is inferred.** No database records peer review directly. A work is `true`
when any version of it was published as a journal article or review. The evidence is ranked
PubMed > Europe PMC > DOAJ > OpenAlex (looked up by DOI) > Semantic Scholar. Everything else
is `false`: preprints, theses, books, conference papers, meeting abstracts in journal
supplements, editorials and news, and unknown types. Two caveats:
- `true` is not a quality judgement; a few venues are questionable.
- Full IEEE/EMBC proceedings papers are typically refereed but are counted as `false` here,
  which is conservative. **Warning:** `python3 -m litreview.export`
(and `./run.sh`) rebuilds `articles/` from scratch, so screening decisions entered in the files would
be lost. Back them up, or stop re-exporting, once screening starts.

## Adding manually searched databases (Scopus, WoS, Embase, LILACS, …)

Run the queries listed in REPORT.md and export the results to `data/manual/<db>.csv`. Then
convert each export to `data/raw/<db>.jsonl` with `litreview.common.record(...)` and add it
to `SOURCES`, so the merge counts it.

## Screening new trials

New registry records show up as `PENDING` in `data/trials.csv`. Add a row for each to
`data/trials_screening.csv`, then rerun.
