"""Fit the final BERTopic model with the configuration chosen by the benchmark.

    uv run python model.py                      # best-scoring config in benchmark_summary.csv
    uv run python model.py bge umap hdbscan mcs=8   # or name one explicitly

Representation: c-TF-IDF words refined with KeyBERTInspired + MMR (diversity
0.3). With a noise-marking clusterer (HDBSCAN/DBSCAN/OPTICS), outliers are
reassigned to the nearest topic by embedding similarity (BERTopic
reduce_outliers) and both coverages are reported.

Writes data/topicos/topics.csv, doc_topics.csv, topic_similarity.csv,
topics_over_time.csv and model.json (configuration + metrics).
"""
from __future__ import annotations

import sys
import warnings

import numpy as np
import pandas as pd
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

import benchmark as B
from common import OUT, Coherence, ctfidf_top_words, diversity, load_corpus, phrase_vectorizer, save_json, vectorizer
from embed import MODELS

warnings.filterwarnings("ignore")
SEED = 0
MAX_THEMES = 8  # colours stay distinguishable in a network only up to ~8 hues


class Fixed:
    """Wrap a precomputed reduction/clustering so BERTopic can use it as a model."""

    def __init__(self, fn):
        self.fn = fn

    def fit(self, X, y=None):
        self.labels_ = self.embedding_ = self.fn(X)
        return self

    def transform(self, X):
        return self.embedding_


def choose(argv):
    if len(argv) == 4:
        return dict(zip(["embedding", "reducer", "clusterer", "params"], argv))
    s = pd.read_csv(OUT / "benchmark_summary.csv")
    s = s[(s["embedding"] != "bow") & s["score"].notna()]
    return s.iloc[0][["embedding", "reducer", "clusterer", "params"]].to_dict()


def fit(cfg):
    """Fit BERTopic with one benchmark configuration -> (model, docs, texts, X, topics, raw coverage)."""
    docs = load_corpus()
    texts = [d["text"] for d in docs]
    X = np.load(OUT / f"emb_{cfg['embedding']}.npy")
    name, prefix = MODELS[cfg["embedding"]]
    st = SentenceTransformer(name, device="mps")
    clus = next(fn for c, p, fn in B.clusterers(cfg["reducer"]) if c == cfg["clusterer"] and p == cfg["params"])

    topic_model = BERTopic(
        embedding_model=st,
        umap_model=Fixed(lambda E: B.reduce(cfg["reducer"], E, SEED)),
        hdbscan_model=Fixed(lambda Z: clus(Z, SEED)),
        vectorizer_model=phrase_vectorizer(),
        representation_model=[KeyBERTInspired(), MaximalMarginalRelevance(diversity=0.3)],
        calculate_probabilities=False, verbose=False,
    )
    topics, _ = topic_model.fit_transform(texts, embeddings=X)
    topics = np.asarray(topics)
    coverage_raw = float((topics != -1).mean())
    if (topics == -1).any():
        topics = np.asarray(topic_model.reduce_outliers(texts, topics, strategy="embeddings", embeddings=X))
        topic_model.update_topics(texts, topics=topics, vectorizer_model=phrase_vectorizer(),
                                  representation_model=[KeyBERTInspired(), MaximalMarginalRelevance(diversity=0.3)])
    return topic_model, docs, texts, X, topics, coverage_raw


def main():
    cfg = choose(sys.argv[1:])
    topic_model, docs, texts, X, topics, coverage_raw = fit(cfg)
    info = topic_model.get_topic_info()
    # labels: phrases refined by KeyBERTInspired + MMR; quality: plain c-TF-IDF words, as in the benchmark
    words = {t: [w for w, _ in topic_model.get_topic(t)][:10] for t in info["Topic"] if t != -1}
    ctfidf = ctfidf_top_words(texts, topics)
    coh = Coherence(texts)
    # 2-D layout for plots (same reducer family, 2 components).
    xy = B.umap.UMAP(n_neighbors=15, n_components=2, min_dist=0.1, metric="cosine", random_state=SEED).fit_transform(X)
    t_emb = np.vstack([X[topics == t].mean(0) for t in sorted(words)])
    sim = cosine_similarity(t_emb)
    # Macro-themes: topics grouped by their centroids (average linkage, cosine).
    k = min(MAX_THEMES, len(words))
    th = AgglomerativeClustering(k, metric="cosine", linkage="average").fit_predict(t_emb)
    sizes = {t: int((topics == t).sum()) for t in sorted(words)}
    order = sorted(set(th), key=lambda c: -sum(sizes[t] for t, x in zip(sorted(words), th) if x == c))
    theme = {t: order.index(c) + 1 for t, c in zip(sorted(words), th)}  # 1 = largest theme
    doc_theme = np.array([theme.get(t, 0) for t in topics])
    theme_words = ctfidf_top_words(texts, doc_theme, n=6)

    rows = []
    for t in sorted(words):
        m = topics == t
        ds = [d for d, k in zip(docs, m) if k]
        centre = X[m].mean(0)
        rep = [ds[i]["work_id"] for i in np.argsort(-(X[m] @ centre))[:5]]
        rows.append({
            "topic": t, "label": ", ".join(words[t][:4]), "n_docs": int(m.sum()),
            "theme": theme[t], "theme_label": ", ".join(theme_words[theme[t]][:3]),
            "top_words": "; ".join(words[t]), "ctfidf_words": "; ".join(ctfidf[t]),
            "npmi": round(coh.topic(ctfidf[t]), 4),
            "share_opto_keyword": round(np.mean([d["opto_keyword"] for d in ds]), 3),
            "share_included": round(np.mean([d["included"] for d in ds]), 3),
            "median_year": int(np.median([int(d["year"]) for d in ds if d["year"]])),
            "representative": " ".join(rep),
        })
    pd.DataFrame(rows).to_csv(OUT / "topics.csv", index=False)
    pd.DataFrame({"work_id": [d["work_id"] for d in docs], "topic": topics, "x": xy[:, 0].round(4),
                  "y": xy[:, 1].round(4)}).to_csv(OUT / "doc_topics.csv", index=False)
    ids = sorted(words)
    pd.DataFrame(sim.round(4), index=ids, columns=ids).to_csv(OUT / "topic_similarity.csv")
    years = pd.DataFrame({"year": [d["year"] for d in docs], "topic": topics})
    years[years["year"] != ""].groupby(["year", "topic"]).size().unstack(fill_value=0).to_csv(OUT / "topics_over_time.csv")
    save_json("model.json", {**cfg, "seed": SEED, "n_docs": len(docs), "n_topics": len(words), "n_themes": k,
                             "coverage_before_outlier_reduction": round(coverage_raw, 4),
                             "npmi": round(coh.model(ctfidf), 4), "diversity": round(diversity(ctfidf), 4),
                             "representation": "c-TF-IDF -> KeyBERTInspired -> MMR(0.3)"})
    print(f"{cfg} -> {len(words)} topics, coverage {coverage_raw:.0%} -> 100%")
    for r in rows:
        print(f"  T{r['topic']:02d} tema {r['theme']} n={r['n_docs']:3d} npmi={r['npmi']:+.2f} {r['label']}")


if __name__ == "__main__":
    main()
