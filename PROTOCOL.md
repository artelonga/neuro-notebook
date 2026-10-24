# Search protocol — Optogenetics in Alzheimer's and Parkinson's disease

Version 1.0 · 2026-10-23 · Reporting follows PRISMA 2020 (identification stage) and PRISMA-S
(search reporting). Results: [REPORT.md](REPORT.md).

## 0. Question

What literature exists that applies, discusses or reviews **optogenetics** in **Alzheimer's
disease (AD)** or **Parkinson's disease (PD)**? Has optogenetics been used in **any registered
clinical trial** (for any condition), and has any trial targeted AD or PD?

## 1. Acceptance criteria

Each step is done only when its checks pass. `REPORT.md` shows the status of each one.

| AC | Criterion | Verifiable check |
|---|---|---|
| **AC-1** | A list of searchable databases, queried by code wherever possible | §2 table; each "API" database has a working function in `litreview/literature.py` / `trials.py`; each non-programmatic one has a ready-to-paste query (REPORT.md) |
| **AC-2** | Quantitative search: records MUST contain an optogenetics term (all language variants, systematised) **AND** (`alzheimer` **OR** `parkinson`) | §3 vocabulary; the exact query sent to each database plus its hit count, stored in `data/search_log.json`; every record checked again locally (`verified`) |
| **AC-3** | Number of articles per database, number found **only** in that database, and the total with duplicates removed, all easy to add up | `data/counts.csv` (per DB: hits / confirmed / unique), `data/overlap_matrix.csv`, `data/works.csv` (one row per work, a 0/1 column per DB, so a pivot or `SUM` adds them up) |
| **AC-4** | Systematic search of clinical-trial registries for **any** use of optogenetics, with each record screened | §5; `data/trials_log.json` (registry × term counts), `data/trials_screening.csv` (decision and reason for every record), `data/trials.csv` |

## 2. Databases (AC-1)

### 2.1 Queried programmatically

| Database | Coverage | Interface | Fields searched |
|---|---|---|---|
| PubMed / MEDLINE | Biomedical, curated; includes PMC and some preprints | NCBI E-utilities (`esearch` + `efetch`) | `[tiab]` title/abstract + `[ot]` author keywords |
| Europe PMC | PubMed + PMC + preprints (bioRxiv, medRxiv, Research Square, …) + theses | REST API, cursor paging | `TITLE_ABS`, `KW` |
| OpenAlex | About 250M works across all disciplines, many languages, grey literature, theses | REST API | `title_and_abstract.search` (stemmed) |
| Semantic Scholar | About 200M works; strong on CS/neuroengineering and conference papers | Graph API `/paper/search/bulk` | title + abstract |
| DOAJ | Open-access journals, including Latin American and non-English ones | REST API (Lucene) | `bibjson.title/abstract/keywords` |
| arXiv | Preprints (q-bio.NC, physics.bio-ph, eess) | Atom API | `ti`, `abs` |

### 2.2 Not programmatic (licence or bot protection): queries supplied, run by hand

Scopus, Web of Science, Embase (licensed; Scopus and WoS have APIs, but only with an
institutional key), LILACS/BVS (the web portal blocks automated access), CNKI (licence),
CiNii. The query strings are in REPORT.md. Export the results as RIS/CSV to `data/manual/`
for the merge.

### 2.3 Trial registries

ClinicalTrials.gov (API v2), EU CTIS (public search API), EU Clinical Trials Register / EudraCT
(HTML), ISRCTN (API), and WHO ICTRP. ICTRP is a meta-registry covering ChiCTR, JPRN, ANZCTR,
**ReBEC (Brazil)**, CTRI, DRKS, IRCT, PACTR and others. It has no public API, so the portal is
attempted and a manual CSV export is the fallback.

## 3. Search vocabulary (AC-2)

### Concept A: optogenetics

| Form | Covers |
|---|---|
| `optogenet*` | EN optogenetic, optogenetics, optogenetically · PT/ES optogenética/o · IT optogenetica · FR optogénétique (diacritics folded) · DE Optogenetik, optogenetisch |
| `opto-genet*` | hyphenated spelling |
| `optigenet*` | misspelling (it appears in the request brief and occasionally in indexed records) |
| Non-Latin scripts | RU оптогенетика · ZH 光遗传 / 光遺傳 · JA 光遺伝, オプトジェネティクス · KO 광유전 |

### Concept B: disease

`alzheimer*` and `parkinson*` are spelled the same in every Latin-script language. Truncation
also covers Alzheimer's, Alzheimers, parkinsonism and parkinsonian. Non-Latin: RU альцгеймер,
паркинсон · ZH 阿尔茨海默, 帕金森 · JA アルツハイマー, パーキンソン · KO 알츠하이머, 파킨슨.

**Logic:** `A AND B`. Search scope is **title + abstract + author keywords**. MeSH and full
text are deliberately excluded from the main search, because the criterion is that the
*keyword* appears. Full-text matching mostly picks up passing mentions. Both are reported as
sensitivity counts: PubMed MeSH-only, and Europe PMC all-fields including full text.

### Syntax adaptation per engine

- Truncation (`*`) where supported: PubMed, Europe PMC, Semantic Scholar, arXiv.
- No truncation (OpenAlex, DOAJ): every word form is listed explicitly. OpenAlex throttles
  queries with more than 5 boolean operators, so the query is split into sub-queries of 5
  operators or fewer and the results are unioned on the OpenAlex ID. Non-Latin terms are
  paired with disease terms from the same language.
- Most indexes store an English title and abstract even for non-English papers, so the English
  stems already capture most foreign-language work. The translated forms add sensitivity for
  records stored only in the original language (OpenAlex, DOAJ).

### Local verification

APIs match loosely: stemming, MeSH expansion inside `KW`, CJK bigram tokenisation, and
Semantic Scholar's hidden abstracts. So every retrieved record is checked again locally with
regexes over title + abstract + keywords (case- and diacritic-folded; `litreview/common.py:matches`).

## 4. Deduplication and counting (AC-3)

- Two records are the **same work** if they share a DOI, PMID, PMCID or arXiv ID, or their
  normalised title (25 or more alphanumeric characters). Matching is transitive (union-find).
- A preprint and its journal version therefore become **one work** ("multiple reports of the
  same study"). The `n_versions` column flags these, so they can be split again if the review
  protocol prefers.
- Work status:
  - `confirmed`: both concepts found in at least one record of the work.
  - `rejected`: an abstract exists and a concept is missing.
  - `unverifiable`: no abstract anywhere. These are listed for manual screening and are not
    included in the totals.
- **Unique to database X** = confirmed works whose only source is X.

## 5. Clinical-trial review (AC-4)

- **Scope:** any optogenetic use, for any condition (not limited to AD/PD). A trial is then
  flagged when its title, conditions or summary mention AD, PD, dementia or cognitive impairment.
- **Terms**, each run separately and unioned: the optogenetics word forms; the opsin names
  channelrhodopsin, ChR2, ChrimsonR, halorhodopsin, "multi-characteristic opsin" and
  "light-sensitive opsin"; and every optogenetic product known to have reached the clinic:
  GS030, RST-001, MCO-010 / sonpiretigene isteparvovec, BS01 / Bionic Sight. Product codes are
  needed because some registries (e.g. EUCTR) do not index the word "optogenetic" for these trials.
- **Screening** (`data/trials_screening.csv`; one reviewer for now, a **second independent
  reviewer is required** before publication):
  - *include, interventional*: the intervention delivers a light-sensitive opsin gene, with or
    without a light-delivery device.
  - *include, follow-up*: a long-term safety extension of an included trial.
  - *include, observational*: no intervention, but the study exists to enable optogenetic
    therapy (e.g. candidate selection).
  - *exclude*: optogenetics appears only incidentally (e.g. the site name), or the match came
    from an ambiguous code ("BS01" or "ChR2" in unrelated studies, "bionic" devices).
- Registrations of the **same trial** in several registries are linked with `same_trial_as`
  and counted once.

## 6. Out of scope for this stage / next steps

1. Title/abstract **relevance** screening of the confirmed works (two reviewers, e.g. in
   Rayyan/ASReview). The keyword rule decides *identification*, not eligibility for the review.
2. Manual searches in the §2.2 databases, then merging their exports.
3. WHO ICTRP export, if the portal is still down at run time.
4. Citation chasing (backward and forward) from the included reviews.
