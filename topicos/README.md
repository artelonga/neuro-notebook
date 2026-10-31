# topicos: tópicos e rede de termos da base de revisão

Modelagem de tópicos (BERTopic e alternativas) e rede de termos dos 801 trabalhos de
`articles/`, com visualização na visão de grafo do Obsidian (`grafo/`) e num visualizador web.

Ambiente separado do pipeline principal (que segue só com a biblioteca padrão): Python 3.13 com
uv, embeddings locais no M4 (MPS).

```bash
cd topicos
uv sync --python /opt/homebrew/bin/python3.13
./run.sh                 # embed -> benchmark -> modelo -> grafo -> notas do Obsidian
```

## Etapas

| Script | O que faz | Saídas (`data/topicos/`) |
|---|---|---|
| `translate.py` | Traduz para o inglês, com LLM local (Ollama), os 26 títulos/resumos em francês, japonês, chinês etc. | `translations.json` (cache) |
| `embed.py` | Embeddings de título + resumo com 4 modelos | `emb_<modelo>.npy` (cache, fora do git) |
| `benchmark.py` | Compara redutor × agrupador × embedding, mais LDA/NMF | `benchmark_runs.csv`, `benchmark_summary.csv` |
| `model.py` | BERTopic final com a melhor configuração; agrupa os tópicos em ≤ 8 temas | `topics.csv`, `doc_topics.csv`, `topic_similarity.csv`, `topics_over_time.csv`, `model.json` |
| `labels.py` | Nomeia cada tópico com LLM local (pt-BR, inglês e uma frase de descrição); aplica `rotulos_revisados.csv` | colunas `llm_*` e `label_source` em `topics.csv`, `llm_labels.json` (cache) |
| `visuals.py` | Visualizações nativas do BERTopic (distância entre tópicos, hierarquia, similaridade, frases, tempo, por doença, por seleção, mapa dos trabalhos e por nível da hierarquia, diagnóstico) e painéis por ano; PNG via Kaleido para o Obsidian e o `RELATORIO.md` | `viz/<nome>.json`, `.html` e `.png`, `viz/insights.json` |
| `gallery.html` | Página com as visualizações e notas de leitura (lê `viz/*.json`) | — |
| `graph.py` | Rede de termos (palavras-chave + frases do texto), coocorrência por NPMI | `terms.csv`, `term_edges.csv`, `term_graph.gexf` (Gephi), `graph.json` |
| `obsidian.py` | Notas ligadas em `grafo/` e grupos de cor em `.obsidian/graph.json` | `grafo/Mapa.md`, `grafo/topicos/`, `grafo/termos/` |
| `viewer.html` | Visualizador web do `graph.json` (d3-force, estilo Obsidian) | — |

## Benchmark

O BERTopic é uma sequência de etapas trocáveis: embeddings → redução de dimensão → agrupamento →
c-TF-IDF. O `benchmark.py` troca cada uma e roda cada configuração com 3 sementes.

- **Embeddings:** all-MiniLM-L6-v2 (padrão do BERTopic), bge-small-en-v1.5, SPECTER (treinado em
  citações científicas), multilingual-e5-small (há trabalhos em fr/ja/zh/ru).
- **Redutores:** UMAP (padrão), PaCMAP (alternativa mais nova, preserva estrutura local e global),
  PCA, nenhum.
- **Agrupadores:** HDBSCAN (padrão), DBSCAN (eps pelo joelho da curva de k-distância), OPTICS,
  k-means, Ward, mistura gaussiana.
- **Referências clássicas:** LDA e NMF sobre a bolsa de palavras.

Métricas: coerência NPMI das 10 palavras de cada tópico, diversidade, silhueta (no espaço original
dos embeddings), cobertura (fração fora do ruído) e **estabilidade por bootstrap** (reajuste em
três subamostras de 90%, ARI nos trabalhos em comum). A nota composta é a média dos percentis, só
para configurações em que **toda** semente dá de 6 a 40 tópicos.

Achados (a tabela completa está em `benchmark_summary.csv`):

- **Escolhido: MiniLM + UMAP + k-means, k = 20** (depois da tradução dos textos em outras
  línguas). Cobertura de 100%, NPMI 0,21, diversidade 0,76, estabilidade 0,61. Logo atrás vêm e5 +
  UMAP + k-means k = 20 (0,744 contra 0,748) e MiniLM + UMAP + Ward k = 20 (0,733): o topo é quase
  um empate, e a escolha mudou duas vezes com correções no corpus (antes, SPECTER + Ward k = 15).
  Trate o número de tópicos e o agrupador como uma escolha razoável, não como a única.
- **O padrão do BERTopic (MiniLM + UMAP + HDBSCAN) tem a melhor coerência** (NPMI 0,27), mas
  deixa 21% como ruído e a estabilidade por bootstrap é 0,32: com 800 resumos curtos, o
  agrupamento por densidade muda muito quando se retira 10% dos trabalhos.
- **DBSCAN não serve para este corpus.** Um só eps global junta tudo em 2 a 5 grupos (com PaCMAP
  ou PCA) ou fragmenta (com UMAP); a densidade varia entre regiões do espaço, que é o que o HDBSCAN
  e o OPTICS tratam. O OPTICS acha 25 a 35 grupos, mas deixa metade como ruído.
- **PaCMAP** dá a melhor silhueta entre os redutores, mas com HDBSCAN deixa até 45% como ruído.
- **O e5 multilíngue colapsa com HDBSCAN** (2 grupos em várias sementes): sua média alta escondia
  isso, por isso a regra de "toda semente entre 6 e 40".
- **LDA é o pior** (NPMI 0,11, estabilidade 0,09), como se espera em textos curtos. **NMF** é
  estável (0,77), mas seus tópicos não se separam no espaço semântico (silhueta −0,01).

## Idiomas

O SPECTER e o vocabulário do c-TF-IDF só leem inglês. Na primeira versão, os trabalhos em francês
(sobretudo teses do theses.fr) formaram um tópico próprio, cujas palavras distintivas eram "des,
les, dans". Duas correções, nesta ordem:

1. Em resumos bilíngues, as frases em francês saem (`common.drop_french`).
2. Os textos inteiros em outra língua são traduzidos para o inglês pelo LLM local antes dos
   embeddings (`translate.py`; marcados com `translated` no corpus).

## Nomes dos tópicos

`labels.py` pede a um LLM (`llm.py`: Claude Haiku 5.5 quando há credenciais da Anthropic,
`ANTHROPIC_API_KEY` ou `ant auth login`; senão o local `qwen3.8:27b`; force com `LLM=haiku` ou
`LLM=ollama`, e `MODEL=qwen2.5:7b` para um local mais leve) um
nome em português e em inglês e uma frase de descrição, a partir das palavras distintivas
(c-TF-IDF) e dos títulos mais representativos de cada tópico. O modelo é descarregado da memória
no fim. Os nomes são automáticos: confira-os e registre correções em
`topicos/rotulos_revisados.csv` (`topic,guard,rotulo,label_en,motivo`); o `guard` (as três
primeiras palavras c-TF-IDF) impede que uma correção caia noutro tópico depois de um novo ajuste.

## Rede de termos

- **Termos:** palavras-chave normalizadas (variantes unidas) e as 8 frases mais representativas de
  cada resumo (método do KeyBERT: frases de 2 a 3 palavras que não atravessam stopwords,
  escolhidas pela similaridade com o embedding do trabalho, com MMR para diversidade). Uma frase
  contida em outra mais longa é unida a ela quando ≥ 80% dos seus trabalhos têm a longa.
- **Fora da rede:** optogenética, Alzheimer e Parkinson, presentes em todos os trabalhos.
- **Arestas:** coocorrência em ≥ 3 trabalhos com NPMI ≥ 0,15; cada termo guarda as 8 mais fortes.
- **Atributos:** tópico e tema dominantes, comunidade (Louvain), tendência (parcela dos trabalhos
  em 2021–2026 contra 2016–2020) e origem (palavra-chave, texto ou ambos).

## Glossário

`graph.py` também grava `glossary.csv`, o vocabulário que `litreview/vincular.py` liga nos
artigos: todo termo (palavra-chave ou frase de 2 a 3 palavras do texto) presente em ≥ 4
trabalhos, menos os termos de busca e os que aparecem em mais de 40% dos trabalhos. Para tirar
termos genéricos, edite `termos_excluidos.txt` e rode de novo `graph.py`, `obsidian.py` e o
`vincular` (o `run.sh` faz tudo). A rede de coocorrência usa só parte desse vocabulário: os
termos com ligações fortes.

## Obsidian

`obsidian.py` refaz `grafo/` a cada execução (não edite à mão) e ajusta `.obsidian/graph.json`
(o original fica em `graph.json.bak`): filtro `path:grafo`, que esconde as 801 notas de artigos, e
uma cor por tema (tag `tema/<n>`). Abra a visão de grafo e comece por `grafo/Mapa.md`. As notas de
termo e de tópico ligam aos artigos por links Markdown, então os backlinks aparecem nas notas de
`articles/`.
