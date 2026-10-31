"""Benchmark: embedding x reducer x clusterer (the BERTopic pipeline), plus LDA/NMF.

    uv run python benchmark.py

BERTopic = embeddings -> dimensionality reduction -> clustering -> c-TF-IDF.
Each stage is swapped here, every configuration run with 3 seeds:

  reducers    umap    UMAP, 5-d, cosine, n_neighbors=15, min_dist=0 (BERTopic default)
              pacmap  PaCMAP, 5-d (keeps local AND global structure; newer alternative)
              pca     PCA, 10-d (linear baseline)
              none    no reduction (only for k-means / Ward on normalised embeddings)
  clusterers  hdbscan  HDBSCAN, min_cluster_size 8 / 15 (BERTopic default; finds k, marks noise)
              dbscan   DBSCAN, eps from the k-distance knee (fixed density; marks noise)
              optics   OPTICS, min_samples 8 (density with varying eps)
              kmeans   k-means, k = 10 / 15 / 20 (no noise; k fixed)
              ward     agglomerative Ward, k = 10 / 15 / 20
              gmm      Gaussian mixture, k = 10 / 15 / 20 (soft assignments)
  baselines   lda / nmf on the bag of words, k = 10 / 15 / 20

Metrics (per run; summary = mean over seeds):
  npmi        topic coherence, doc-level NPMI of the top-10 c-TF-IDF words (-1..1)
  diversity   unique share of all top-10 words (0..1)
  silhouette  cosine silhouette of the clusters in the ORIGINAL embedding space
  coverage    share of documents assigned to a topic (1 - noise)
  stability   bootstrap: refit on three 90% subsamples, mean adjusted Rand index
              over the documents two subsamples share (fair to deterministic
              methods, whose seed-to-seed agreement is trivially 1)
Composite score = mean percentile rank of the five, only for configs where EVERY
seed gives 6..40 topics (a mean hides seeds that collapse to 2-3 trivial topics,
which score high coherence and diversity).

    uv run python benchmark.py --summarize   # re-rank from the saved runs

Writes data/topicos/benchmark_runs.csv and benchmark_summary.csv.
"""
from __future__ import annotations

import itertools
import time
import warnings

import numpy as np
import pandas as pd
import pacmap
import umap
from hdbscan import HDBSCAN
from sklearn.cluster import DBSCAN, OPTICS, AgglomerativeClustering, KMeans
from sklearn.decomposition import NMF, PCA, LatentDirichletAllocation
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors

from common import OUT, Coherence, ctfidf_top_words, diversity, load_corpus, vectorizer
from embed import MODELS

warnings.filterwarnings("ignore")
SEEDS = [0, 1, 2]
KS = [10, 15, 20]


def reduce(name, X, seed):
    if name == "umap":
        return umap.UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine",
                         random_state=seed).fit_transform(X)
    if name == "pacmap":
        return pacmap.PaCMAP(n_components=5, n_neighbors=15, random_state=seed).fit_transform(X)
    if name == "pca":
        return PCA(n_components=10, random_state=seed).fit_transform(X)
    return X


def knee_eps(Z, k=5):
    """eps for DBSCAN: the point of the sorted k-distance curve farthest from its chord."""
    d = np.sort(NearestNeighbors(n_neighbors=k + 1).fit(Z).kneighbors(Z)[0][:, -1])
    x = np.linspace(0, 1, len(d))
    y = (d - d[0]) / max(d[-1] - d[0], 1e-12)
    return float(d[np.argmax(x - y)])


def clusterers(reducer):
    out = [] if reducer == "none" else [
        ("hdbscan", "mcs=8", lambda Z, s: HDBSCAN(min_cluster_size=8).fit_predict(Z)),
        ("hdbscan", "mcs=15", lambda Z, s: HDBSCAN(min_cluster_size=15).fit_predict(Z)),
        ("dbscan", "knee k=5", lambda Z, s: DBSCAN(eps=knee_eps(Z), min_samples=5).fit_predict(Z)),
        ("optics", "min_samples=8", lambda Z, s: OPTICS(min_samples=8).fit_predict(Z)),
    ]
    for k in KS:
        out.append(("kmeans", f"k={k}", lambda Z, s, k=k: KMeans(k, n_init=10, random_state=s).fit_predict(Z)))
        out.append(("ward", f"k={k}", lambda Z, s, k=k: AgglomerativeClustering(k).fit_predict(Z)))
        if reducer != "none":
            out.append(("gmm", f"k={k}", lambda Z, s, k=k: GaussianMixture(k, random_state=s).fit(Z).predict(Z)))
    return out


def score(texts, labels, X, coh):
    labels = np.asarray(labels)
    topics = ctfidf_top_words(texts, labels)
    mask = labels != -1
    sil = (silhouette_score(X[mask], labels[mask], metric="cosine")
           if len(set(labels[mask])) > 1 and mask.sum() > len(set(labels[mask])) else np.nan)
    return {"n_topics": len(topics), "coverage": float(mask.mean()), "npmi": coh.model(topics),
            "diversity": diversity(topics), "silhouette": float(sil)}


def subsample(n, seed, frac=0.9):
    return np.sort(np.random.default_rng(100 + seed).choice(n, int(n * frac), replace=False))


def boot_ari(n, boot):
    """boot = [(idx, labels)] -> mean ARI over the documents each pair of subsamples shares."""
    out = []
    for (ia, la), (ib, lb) in itertools.combinations(boot, 2):
        common, pa, pb = np.intersect1d(ia, ib, return_indices=True)
        out.append(adjusted_rand_score(la[pa], lb[pb]))
    return float(np.mean(out))


def lda_nmf(name, k, seed, bow):
    m = (LatentDirichletAllocation(k, random_state=seed) if name == "lda"
         else NMF(k, random_state=seed, init="nndsvda", max_iter=500))
    return m, m.fit_transform(bow).argmax(1)


def baselines(texts, coh, embs):
    rows, stab = [], {}
    cv = vectorizer()
    bow = cv.fit_transform(texts)
    vocab = np.array(cv.get_feature_names_out())
    for name, k in itertools.product(["lda", "nmf"], KS):
        boot = []
        for seed in SEEDS:
            m, labels = lda_nmf(name, k, seed, bow)
            topics = {i: list(vocab[np.argsort(-c)[:10]]) for i, c in enumerate(m.components_)}
            # no embedding space of its own: silhouette averaged over the four embeddings
            sil = np.mean([silhouette_score(E, labels, metric="cosine") for E in embs.values()])
            rows.append({"embedding": "bow", "reducer": "-", "clusterer": name, "params": f"k={k}", "seed": seed,
                         "n_topics": k, "coverage": 1.0, "npmi": coh.model(topics),
                         "diversity": diversity(topics), "silhouette": float(sil)})
            idx = subsample(len(texts), seed)
            boot.append((idx, lda_nmf(name, k, seed, bow[idx])[1]))
        stab[("bow", "-", name, f"k={k}")] = boot_ari(len(texts), boot)
    return rows, stab


def main():
    docs = load_corpus()
    texts = [d["text"] for d in docs]
    coh = Coherence(texts)
    embs = {emb: np.load(OUT / f"emb_{emb}.npy") for emb in MODELS}
    rows, stab = baselines(texts, coh, embs)
    boot = {}
    t0 = time.time()
    for emb, X in embs.items():
        for red in ["umap", "pacmap", "pca", "none"]:
            for seed in SEEDS:
                Z = reduce(red, X, seed)
                idx = subsample(len(texts), seed)
                Zb = reduce(red, X[idx], seed)
                for cl, params, fn in clusterers(red):
                    labels = fn(Z, seed)
                    rows.append({"embedding": emb, "reducer": red, "clusterer": cl, "params": params,
                                 "seed": seed, **score(texts, labels, X, coh)})
                    boot.setdefault((emb, red, cl, params), []).append((idx, np.asarray(fn(Zb, seed))))
            print(f"{emb:9} {red:7} done ({time.time() - t0:.0f}s)", flush=True)
    stab.update({k: boot_ari(len(texts), v) for k, v in boot.items()})
    runs = pd.DataFrame(rows)
    runs.to_csv(OUT / "benchmark_runs.csv", index=False)
    summarize(runs, stab)


KEYS = ["embedding", "reducer", "clusterer", "params"]


def summarize(runs, stab):
    summ = []
    for key, g in runs.groupby(KEYS, sort=False):
        summ.append({**dict(zip(KEYS, key)), **g[["n_topics", "coverage", "npmi", "diversity", "silhouette"]]
                     .mean().round(4).to_dict(), "n_topics_min": int(g["n_topics"].min()),
                     "n_topics_max": int(g["n_topics"].max()), "stability": round(stab[key], 4)})
    summ = pd.DataFrame(summ)
    ok = (summ["n_topics_min"] >= 6) & (summ["n_topics_max"] <= 40)
    metrics = ["npmi", "diversity", "silhouette", "coverage", "stability"]
    ranks = summ.loc[ok, metrics].rank(pct=True)
    summ.loc[ok, "score"] = ranks.mean(axis=1, skipna=True).round(4)
    summ = summ.sort_values("score", ascending=False)
    summ.to_csv(OUT / "benchmark_summary.csv", index=False)
    print(summ.head(15).to_string(index=False))


if __name__ == "__main__":
    import sys
    if "--summarize" in sys.argv:
        old = pd.read_csv(OUT / "benchmark_summary.csv")
        summarize(pd.read_csv(OUT / "benchmark_runs.csv"),
                  {tuple(r[k] for k in KEYS): r["stability"] for _, r in old.iterrows()})
    else:
        main()
