# Changelog

Todas as mudanças relevantes do projeto ficam registradas aqui
([Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), [SemVer](https://semver.org/lang/pt-BR/)).

## [0.5.0] - 2026-10-24

### Alterado
- `python3 -m litreview.report` gera o relatório completo em pt-BR em `RELATORIO.md` (números no formato brasileiro, critérios CA-1..CA-4).
- `PROTOCOLO.md` passa a ser o protocolo completo, traduzido do inglês; `README.md` traduzido para pt-BR.
- O slide final da apresentação cita `RELATORIO.md`.

### Removido
- `PROTOCOL.md` e `REPORT.md` (as versões em inglês continuam no histórico, até a tag `v0.4.1`).

## [0.4.1] - 2026-10-24

### Adicionado
- Fonte da apresentação em pt-BR (`slides/`: `deck.json` e um HTML por slide).

## [0.4.0] - 2026-10-23

### Adicionado
- Trabalhos com revisão por pares exportados para `articles/peer_reviewed/`; os demais ficam em `articles/`.
- `peer_reviewed` (booleano), `document_type` e `peer_review_basis` no front matter de cada artigo e em `data/articles_index.csv`.
- Seção com o resumo da revisão por pares no `REPORT.md` (gerado) e no `RELATORIO.md`.

## [0.3.0] - 2026-10-23

### Adicionado
- `articles/`: um arquivo Markdown por trabalho confirmado (front matter YAML + resumo), com campos PRISMA de identificação e triagem (`litreview/export.py`).
- Os registros brutos agora guardam resumo, palavras-chave (separadas por `; `) e autores; autores ausentes são buscados no OpenAlex pelo DOI.

## [0.2.0] - 2026-10-23

### Adicionado
- Resumos em português do protocolo e do relatório (`PROTOCOLO.md`, `RELATORIO.md`).

## [0.1.0] - 2026-10-23

### Adicionado
- Protocolo de busca com os critérios de aceitação CA-1..CA-4 (`PROTOCOL.md`).
- Busca programática na literatura: PubMed, Europe PMC, OpenAlex, Semantic Scholar, DOAJ e arXiv.
- Deduplicação entre bases, reverificação das palavras-chave e contagens por base e de sobreposição.
- Busca em registros de ensaios clínicos (ClinicalTrials.gov, EU CTIS, EUCTR, ISRCTN, WHO ICTRP) com arquivo de triagem.
- `REPORT.md` gerado automaticamente.
