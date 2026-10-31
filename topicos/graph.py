"""Term network: keyphrases from the text + keywords, linked by co-occurrence.

    uv run python graph.py

Terms of a document = its normalised keywords (any source) + its top
keyphrases from title/abstract (KeyBERT method: 2-3-word phrases that never
cross a stopword, scored by
cosine to the document embedding, MMR for diversity), in one key space
(litreview.keywords.kw_key). The search concepts (optogenetics, Alzheimer,
Parkinson) are left out: every document has them.

  node   term in >= MIN_DF documents; attributes: document frequency, source
         (keyword / text / both), dominant topic and its purity, Louvain
         community, degree, betweenness, trend (share of works in 2021-2026 vs
         2016-2020: x1.5 = emergente, x0.67 = em queda)
  edge   co-occurrence in >= MIN_CO documents with NPMI >= MIN_NPMI; each node
         keeps its TOP_K strongest edges (the backbone used for display)

Writes data/topicos/terms.csv, term_edges.csv, term_graph.gexf and graph.json
(nodes, links, topics and documents for the viewers), and glossary.csv: the
controlled vocabulary that litreview/vincular.py links in the articles (every
term in >= MIN_DF works and in at most MAX_SHARE of them; the network above
keeps only the terms with strong co-occurrence edges).
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from common import OPTO, OUT, kw_key, load_corpus, phrase_vectorizer
from embed import MODELS

MIN_DF, MIN_CO, MIN_NPMI, TOP_K, N_PHRASES = 4, 3, 0.15, 8, 8
MAX_SHARE = 0.4  # glossary: a term in more than 40% of the works is too generic to link
# Too generic to be a glossary entry; edited by hand in topicos/termos_excluidos.txt.
GENERIC = {l.strip() for l in (Path(__file__).parent / "termos_excluidos.txt").read_text().splitlines()
           if l.strip() and not l.startswith("#")}
SEARCH = re.compile(r"\b(alzheimer|parkinson)(s)?( disease)?$|^(ad|pd|disease|neurodegenerative disease)$")
PERIODS = [("até 2015", 0, 2015), ("2016–2020", 2016, 2020), ("2021–2026", 2021, 2100)]


def keyphrases(docs, X, st, prefix):
    cv = phrase_vectorizer(min_df=3, ngram=(2, 3))  # single words enter only as keywords
    bow = cv.fit_transform([d["text"] for d in docs])
    vocab = np.array(cv.get_feature_names_out())
    V = st.encode([prefix + v for v in vocab], batch_size=128, normalize_embeddings=True, show_progress_bar=False)
    out = []
    for i in range(len(docs)):
        cand = bow[i].indices
        if len(cand) == 0:
            out.append([])
            continue
        rel = V[cand] @ X[i]
        chosen = [int(np.argmax(rel))]
        while len(chosen) < min(N_PHRASES, len(cand)):  # MMR, lambda = 0.6
            red = (V[cand] @ V[cand][chosen].T).max(1)
            mmr = 0.6 * rel - 0.4 * red
            mmr[chosen] = -np.inf
            chosen.append(int(np.argmax(mmr)))
        out.append([vocab[cand[j]] for j in chosen])
    return out


def main():
    docs = load_corpus()
    model = json.loads((OUT / "model.json").read_text())
    name, prefix = MODELS[model["embedding"]]
    X = np.load(OUT / f"emb_{model['embedding']}.npy")
    st = SentenceTransformer(name, device="mps")
    dt = pd.read_csv(OUT / "doc_topics.csv").set_index("work_id")
    topics = pd.read_csv(OUT / "topics.csv").set_index("topic")

    phrases = keyphrases(docs, X, st, prefix)
    surface, src = defaultdict(Counter), defaultdict(Counter)
    doc_terms = []
    for d, ph in zip(docs, phrases):
        terms = set()
        for k in d["keywords"]:
            key = kw_key(k)
            if key and not OPTO.search(k) and not SEARCH.search(key):
                terms.add(key)
                surface[key][k.lower().replace("’", "'")] += 1
                src[key]["keyword"] += 1
        for p in ph:
            key = kw_key(p)
            if not SEARCH.search(key):
                terms.add(key)
                surface[key][p] += 1
                src[key]["text"] += 1
        doc_terms.append(terms)

    n = len(docs)
    df = Counter(t for ts in doc_terms for t in ts)
    # Fold a phrase into a longer one that contains it ("deep brain" -> "deep brain stimulation")
    # when >= 80% of its documents also have the longer phrase.
    cand = [t for t, c in df.items() if c >= MIN_DF]
    fold = {}
    for t in cand:
        longer = [L for L in cand if L != t and f" {t} " in f" {L} "]
        best = max(longer, key=lambda L: sum(1 for ts in doc_terms if t in ts and L in ts), default=None)
        if best and sum(1 for ts in doc_terms if t in ts and best in ts) >= 0.8 * df[t]:
            fold[t] = best
    for t, L in fold.items():
        while L in fold:
            L = fold[L]
        fold[t] = L
    doc_terms = [{fold.get(t, t) for t in ts} for ts in doc_terms]
    df = Counter(t for ts in doc_terms for t in ts)
    keep = {t for t, c in df.items() if c >= MIN_DF}
    co = Counter()
    for ts in doc_terms:
        co.update(combinations(sorted(ts & keep), 2))
    edges = []
    for (a, b), c in co.items():
        if c < MIN_CO:
            continue
        p_ab = c / n
        npmi = math.log(p_ab / (df[a] / n * df[b] / n)) / -math.log(p_ab)
        if npmi >= MIN_NPMI:
            edges.append((a, b, c, npmi))
    # backbone: each node keeps its TOP_K strongest edges (by NPMI)
    by_node = defaultdict(list)
    for e in edges:
        by_node[e[0]].append(e)
        by_node[e[1]].append(e)
    backbone = {(e[0], e[1]): e for es in by_node.values() for e in sorted(es, key=lambda e: -e[3])[:TOP_K]}

    G = nx.Graph()
    for a, b, c, npmi in backbone.values():
        G.add_edge(a, b, weight=round(npmi, 4), count=c)
    comms = nx.community.louvain_communities(G, weight="weight", seed=0)
    comm = {t: i for i, cset in enumerate(sorted(comms, key=len, reverse=True)) for t in cset}
    btw = nx.betweenness_centrality(G, weight=None, k=min(300, len(G)), seed=0)

    term_docs = defaultdict(list)
    for d, ts in zip(docs, doc_terms):
        for t in ts & set(G):
            term_docs[t].append(d)
    rows = []
    for t in G:
        ds = term_docs[t]
        tc = Counter(int(dt.loc[d["work_id"], "topic"]) for d in ds)
        top_t, top_n = tc.most_common(1)[0]
        yrs = [int(d["year"]) for d in ds if d["year"]]
        share = []
        for _, lo, hi in PERIODS:
            tot = sum(1 for d in docs if d["year"] and lo <= int(d["year"]) <= hi)
            share.append(sum(1 for y in yrs if lo <= y <= hi) / tot if tot else 0)
        # recent (2021-2026) vs previous five years; the early period is small and noisy
        trend = ("emergente" if share[2] > 1.5 * max(share[1], 1e-9) else
                 "em queda" if share[2] < 0.67 * share[1] else "estável")
        s = src[t]
        rows.append({
            "term": t, "label": surface[t].most_common(1)[0][0], "docs": len(ds),
            "source": "ambos" if s["keyword"] and s["text"] else ("palavra-chave" if s["keyword"] else "texto"),
            "topic": top_t, "theme": int(topics.loc[top_t, "theme"]), "topic_purity": round(top_n / len(ds), 3),
            "community": comm[t],
            "degree": G.degree(t), "betweenness": round(btw[t], 5),
            "share_early": round(share[0], 4), "share_mid": round(share[1], 4), "share_late": round(share[2], 4),
            "trend": trend, "opto_keyword_share": round(np.mean([d["opto_keyword"] for d in ds]), 3),
            "work_ids": " ".join(d["work_id"] for d in ds),
        })
    terms = pd.DataFrame(rows).sort_values("docs", ascending=False)
    terms.to_csv(OUT / "terms.csv", index=False)
    pd.DataFrame([{"source": a, "target": b, "count": c, "npmi": round(w, 4)} for a, b, c, w in backbone.values()]) \
        .to_csv(OUT / "term_edges.csv", index=False)
    for t, r in terms.set_index("term").iterrows():
        G.nodes[t].update(label=r["label"], docs=int(r["docs"]), topic=int(r["topic"]), theme=int(r["theme"]),
                          community=int(r["community"]), source=r["source"], trend=r["trend"])
    nx.write_gexf(G, OUT / "term_graph.gexf")

    used = {w for r in rows for w in r["work_ids"].split()}
    graph = {
        "nodes": [{k: r[k] for k in ("term", "label", "docs", "source", "topic", "theme", "topic_purity", "community",
                                     "degree", "trend")} | {"work_ids": r["work_ids"].split()[:40]} for r in rows],
        "links": [{"source": a, "target": b, "count": c, "npmi": round(w, 3)} for a, b, c, w in backbone.values()],
        "topics": [{"topic": int(t), "label": r.get("llm_label") if isinstance(r.get("llm_label"), str) else r["label"],
                    "phrases": r["label"], "description": r.get("llm_description") if isinstance(r.get("llm_description"), str) else "",
                    "label_source": r.get("label_source", "frases"),
                    "theme": int(r["theme"]), "theme_label": r["theme_label"],
                    "n_docs": int(r["n_docs"]), "top_words": r["top_words"],
                    "npmi": r["npmi"], "share_opto_keyword": r["share_opto_keyword"], "median_year": int(r["median_year"])}
                   for t, r in topics.iterrows()],
        "docs": {d["work_id"]: {"title": d["title"], "year": d["year"], "journal": d["journal"], "doi": d["doi"],
                                "topic": int(dt.loc[d["work_id"], "topic"]), "included": d["included"],
                                "file": d["file"]} for d in docs if d["work_id"] in used},
        "params": {"min_df": MIN_DF, "min_co": MIN_CO, "min_npmi": MIN_NPMI, "top_k": TOP_K,
                   "phrases_per_doc": N_PHRASES, "embedding": model["embedding"]},
    }
    (OUT / "graph.json").write_text(json.dumps(graph, ensure_ascii=False))
    gloss = []
    for t, c in sorted(df.items(), key=lambda kv: -kv[1]):
        if c < MIN_DF or c / n > MAX_SHARE or t in GENERIC:
            continue
        tc = Counter(int(dt.loc[d["work_id"], "topic"]) for d, ts in zip(docs, doc_terms) if t in ts)
        sv = src[t]
        gloss.append({"term": t, "label": surface[t].most_common(1)[0][0] if surface[t] else t, "docs": c,
                      "source": "ambos" if sv["keyword"] and sv["text"] else ("palavra-chave" if sv["keyword"] else "texto"),
                      "topic": tc.most_common(1)[0][0], "in_graph": int(t in G)})
    pd.DataFrame(gloss).to_csv(OUT / "glossary.csv", index=False)
    print(f"glossary: {len(gloss)} terms ({sum(g['in_graph'] for g in gloss)} also in the network)")
    print(f"folded {len(fold)} sub-phrases into longer ones, e.g. {list(fold.items())[:4]}")
    print(f"{len(G)} terms, {G.number_of_edges()} edges (of {len(edges)} above threshold), "
          f"{len(comms)} communities; sources: {Counter(r['source'] for r in rows)}")
    print("trends:", Counter(r["trend"] for r in rows))
    print(terms.head(25)[["label", "docs", "source", "topic", "community", "trend"]].to_string(index=False))


if __name__ == "__main__":
    main()
