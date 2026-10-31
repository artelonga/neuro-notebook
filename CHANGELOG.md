# Changelog

Todas as mudanças relevantes do projeto ficam registradas aqui
([Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), [SemVer](https://semver.org/lang/pt-BR/)).

## [Não publicado]

## [0.7.0] - 2026-10-31

### Adicionado
- `topicos/`: modelagem de tópicos (BERTopic) com benchmark de embeddings, redutores (UMAP, PaCMAP, PCA) e agrupadores (HDBSCAN, DBSCAN, OPTICS, k-means, Ward, GMM), mais LDA/NMF; estabilidade por bootstrap. Ambiente próprio (Python 3.13 + uv); o pipeline principal segue só com a biblioteca padrão.
- Rede de termos (palavras-chave + frases do texto, NPMI, comunidades Louvain, tendência) em `data/topicos/`, exportada para Gephi (`term_graph.gexf`).
- `grafo/`: notas do Obsidian por tópico e por termo, com grupos de cor por tema na visão de grafo; `topicos/viewer.html`, visualizador web do grafo.
- Visualizações nativas do BERTopic (`topicos/visuals.py`) em HTML, JSON e PNG, com painéis por ano e mapa hierárquico dos trabalhos; seção de tópicos no `RELATORIO.md` e imagens em `grafo/Mapa.md`.
- Nomes dos tópicos por LLM (`topicos/labels.py`, Claude Haiku ou Ollama local via `topicos/llm.py`) com revisão à mão em `topicos/rotulos_revisados.csv`.
- Tradução para o inglês dos 26 títulos/resumos em outras línguas antes dos embeddings (`topicos/translate.py`), que desfaz o tópico formado só pelo idioma francês.
- `litreview/vincular.py`: liga cada artigo (selecionados, não selecionados ou todos) ao seu tópico e aos termos do glossário com `[[ ]]`, e mede cobertura, prevalência e termos por tópico em `data/termos/<conjunto>/`; glossário em `grafo/termos/` com lista de exclusões editável (`topicos/termos_excluidos.txt`).
- Grafos por escopo no Obsidian: notas de termo e tópico em `articles/grafo-todos/` (801) e `articles/selected/grafo-selecionados/` (370), com filtros documentados; artigos com tag `tema/<n>`.
- Cabeçalho dos artigos: `topico`, `topico_nome`, `n_termos` e `tags`; bloco `<!-- vinculos:inicio/fim -->` com o tópico e os termos depois do resumo.
- `litreview/keywords.py`: perfil das palavras-chave (idioma, outras palavras-chave, ano, periódico, tipos, origem autor vs. OpenAlex) em `data/keywords_profile.json` e `data/keywords_prevalence.csv`.
- Seções "Tópicos (BERTopic)" e "Termos do glossário" no `RELATORIO.md`; README explica os vínculos, as medidas dos termos e os três filtros do grafo.

### Alterado
- `./run.sh` roda `litreview.vincular` nos três conjuntos depois do `export` (que recria `articles/`), quando as saídas de `topicos/` existem.
- `.gitignore`: `.venv/`, `data/topicos/emb_*.npy` (cache de embeddings) e `topicos/__pycache__/`.

### Corrigido
- `grafo/` é atualizado no lugar, sem apagar e recriar a pasta, o que fazia o Obsidian perder o índice e criar notas vazias ao clicar nos links.

## [0.6.0] - 2026-10-29

### Adicionado
- Fluxo PRISMA 2020 (`python3 -m litreview.prisma`): o n de cada etapa em `data/prisma.json`, diagrama em `data/prisma_flow.svg` (pt-BR) e `data/prisma_flow.en.svg`, etapa de saída de cada trabalho em `data/prisma_works.csv` e seleção final em `data/included.csv`.
- Critérios de elegibilidade (publicado em 2020 ou depois; com revisão por pares) em `litreview/common.py` e no `PROTOCOLO.md` §6.
- `study_type` (pesquisa original, revisão, revisão sistemática, meta-análise, metodologia, outros) e `prisma.eligibility` no cabeçalho de cada artigo; `study_type` e `eligible` em `data/articles_index.csv`.
- Seção "Fluxo PRISMA 2020 e seleção final" no `RELATORIO.md`, que substitui o fluxo só de identificação.
- `articles/selected/`: a seleção final; `litreview.prisma` move os arquivos conforme as decisões dos revisores.

### Removido
- `articles/peer_reviewed/`: `articles/` passa a ser a base de revisão e a revisão por pares fica só no campo `peer_reviewed`.

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
