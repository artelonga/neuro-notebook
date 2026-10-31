"""BERTopic's built-in visualizations of the final model, plus the numbers behind them.

    uv run python visuals.py

Refits the model chosen in model.json (deterministic, seed 0) and writes, per
figure, data/topicos/viz/<name>.json (Plotly figure, for the web gallery) and
<name>.html (standalone, opens in a browser):

  intertopic   visualize_topics            intertopic distance map (topic size = works)
  hierarchy    visualize_hierarchy         dendrogram of hierarchical_topics (c-TF-IDF, Ward)
  heatmap      visualize_heatmap           topic similarity on c-TF-IDF, ordered in 8 clusters
  barchart     visualize_barchart          top phrases per topic with c-TF-IDF scores
  over_time    visualize_topics_over_time  topics per publication year
  disease      visualize_topics_per_class  topics in works citing Alzheimer, Parkinson or both
  selection    visualize_topics_per_class  topics inside / outside the PRISMA final selection
  documents    visualize_documents         2-D map of the 801 works (hover = title)
  doc_hierarchy visualize_hierarchical_documents  the same map, coloured at a chosen level of the hierarchy
  term_rank    visualize_term_rank         c-TF-IDF score decline per topic (diagnostic)
  over_time_facets  (own figure)           topics over time as small multiples, sorted by
                                           growth, shared y axis (the static version of over_time)

insights.json holds the derived numbers quoted in the gallery captions,
including how often marker terms (amyloid, tau, synuclein...) occur in each
topic's texts, which keeps captions tied to the texts rather than to labels.
"""
from __future__ import annotations

import json
import re
import warnings

import numpy as np
import pandas as pd

import benchmark as B
from common import OUT
from model import SEED, fit

warnings.filterwarnings("ignore")
VIZ = OUT / "viz"
VIZ.mkdir(exist_ok=True)
FONT = "IBM Plex Sans, Helvetica Neue, Arial, sans-serif"


def disease(text):
    t = text.lower()
    ad, pd_ = "alzheimer" in t, "parkinson" in t
    return "Ambas" if ad and pd_ else "Alzheimer" if ad else "Parkinson" if pd_ else "Outra menção"


MARKERS = {"amiloide": r"amyloid|aβ\b|abeta", "tau": r"\btau\b|tauopath", "sinucleína": r"synuclein",
           "DBS": r"deep brain stim", "terapia gênica/vetor": r"\baav\b|viral vector|gene therap",
           "discinesia": r"dyskinesi", "células-tronco/enxerto": r"stem cell|ipsc|graft|transplant",
           "gama/40 Hz": r"gamma|40.hz", "fluxo sanguíneo": r"blood flow|neurovascular|vascular",
           "memória/hipocampo": r"memory|hippocamp", "astrócitos": r"astrocyt", "sono": r"\bsleep",
           "colinérgico": r"cholinergic"}


def save(name, fig, title):
    # BERTopic shows only the first topic of per-class / over-time charts (the rest
    # "legendonly"): fine to click through, empty as a static image. Show them all,
    # with per-class bars stacked so each class bar is its topic composition.
    hidden = [t for t in fig.data if getattr(t, "visible", None) == "legendonly"]
    for t in hidden:
        t.visible = True
    if hidden and all(t.type == "bar" for t in fig.data):
        fig.update_layout(barmode="stack")
    fig.update_layout(title=None, font_family=FONT, margin=dict(l=10, r=10, t=30, b=10))
    (VIZ / f"{name}.json").write_text(fig.to_json())
    fig.update_layout(title=title, margin=dict(l=10, r=10, t=60, b=10), template="plotly_white")
    fig.write_html(VIZ / f"{name}.html", include_plotlyjs="cdn")
    fig.write_image(VIZ / f"{name}.png", scale=2)
    print(f"  {name}")


def main():
    cfg = json.loads((OUT / "model.json").read_text())
    tm, docs, texts, X, topics, _ = fit({k: cfg[k] for k in ("embedding", "reducer", "clusterer", "params")})
    words = {t: [w for w, _ in tm.get_topic(t)] for t in sorted(set(topics))}
    tab = pd.read_csv(OUT / "topics.csv").set_index("topic")
    name = {t: tab.loc[t, "llm_label"] if "llm_label" in tab and isinstance(tab.loc[t, "llm_label"], str)
            else ", ".join(w[:2]) for t, w in words.items()}
    tm.set_topic_labels({t: f"T{t:02d} {name[t]}" for t in words})
    years = [int(d["year"]) if d["year"] else 0 for d in docs]
    titles = [d["title"] for d in docs]
    dis = [disease(x) for x in texts]
    sel = ["Seleção final" if d["included"] else "Fora da seleção" for d in docs]
    n = len(words)

    save("intertopic", tm.visualize_topics(custom_labels=True, width=900, height=650), "Mapa de distância entre tópicos")
    hier = tm.hierarchical_topics(texts)
    save("hierarchy", tm.visualize_hierarchy(hierarchical_topics=hier, custom_labels=True, width=1000, height=600),
         "Hierarquia de tópicos")
    save("heatmap", tm.visualize_heatmap(n_clusters=min(8, n - 1), use_ctfidf=True, custom_labels=True,
                                         width=900, height=800), "Similaridade entre tópicos")
    save("barchart", tm.visualize_barchart(top_n_topics=n, n_words=6, custom_labels=True, width=260, height=260),
         "Frases de cada tópico")
    tot = tm.topics_over_time(texts, years, global_tuning=True, evolution_tuning=True)
    tot = tot[tot["Timestamp"] > 0]
    save("over_time", tm.visualize_topics_over_time(tot, top_n_topics=n, custom_labels=True, width=1000, height=500),
         "Tópicos ao longo do tempo")
    # small multiples: one panel per topic, most growing first, same y scale
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    yrs = sorted(tot["Timestamp"].unique())
    late = lambda t: sum(1 for y, k in zip(years, topics) if k == t and y >= 2021) / max(sum(1 for y in years if y >= 2021), 1)
    mid = lambda t: sum(1 for y, k in zip(years, topics) if k == t and 2016 <= y <= 2020) / max(
        sum(1 for y in years if 2016 <= y <= 2020), 1)
    order = sorted(words, key=lambda t: -(late(t) / mid(t) if mid(t) else 99))
    cols = 4
    rows = -(-len(order) // cols)
    fx = make_subplots(rows=rows, cols=cols, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.06,
                       horizontal_spacing=0.03,
                       subplot_titles=[f"T{t:02d} {name[t][:34]} (×{late(t) / mid(t):.1f})".replace(".", ",")
                                       if mid(t) else f"T{t:02d} {name[t][:34]}" for t in order])
    for i, t in enumerate(order):
        g = tot[tot["Topic"] == t].set_index("Timestamp")["Frequency"].reindex(yrs, fill_value=0)
        fx.add_trace(go.Scatter(x=yrs, y=g.values, mode="lines", line=dict(color="#2a78d6", width=2),
                                fill="tozeroy", fillcolor="rgba(42,120,214,0.15)", showlegend=False,
                                hovertemplate="%{x}: %{y} trabalhos<extra></extra>"),
                     row=i // cols + 1, col=i % cols + 1)
    fx.update_annotations(font_size=11)
    fx.update_layout(width=1400, height=230 * rows)
    save("over_time_facets", fx, "Tópicos por ano (×: parcela em 2021–26 sobre 2016–20)")
    tpc = tm.topics_per_class(texts, classes=dis)
    save("disease", tm.visualize_topics_per_class(tpc, top_n_topics=n, normalize_frequency=False, custom_labels=True,
                                                  width=1000, height=600), "Tópicos por doença citada")
    tps = tm.topics_per_class(texts, classes=sel)
    save("selection", tm.visualize_topics_per_class(tps, top_n_topics=n, custom_labels=True, width=1000, height=600),
         "Tópicos dentro e fora da seleção final")
    xy = B.umap.UMAP(n_neighbors=15, n_components=2, min_dist=0.1, metric="cosine", random_state=SEED).fit_transform(X)
    save("documents", tm.visualize_documents(titles, reduced_embeddings=xy, custom_labels=True, width=1000, height=700),
         "Mapa dos trabalhos")
    save("doc_hierarchy", tm.visualize_hierarchical_documents(titles, hier, reduced_embeddings=xy, custom_labels=True,
                                                             nr_levels=5, width=1000, height=700),
         "Mapa dos trabalhos por nível da hierarquia")
    save("term_rank", tm.visualize_term_rank(log_scale=True, custom_labels=True, width=900, height=450),
         "Queda do escore c-TF-IDF por posição")

    # numbers for the captions
    df = pd.DataFrame({"topic": topics, "year": years, "disease": dis, "included": [d["included"] for d in docs]})
    per = []
    for t in sorted(words):
        g = df[df["topic"] == t]
        mid = ((g["year"] >= 2016) & (g["year"] <= 2020)).sum() / max(((df["year"] >= 2016) & (df["year"] <= 2020)).sum(), 1)
        late = (g["year"] >= 2021).sum() / max((df["year"] >= 2021).sum(), 1)
        txt = [texts[i].lower() for i in np.where(topics == t)[0]]
        per.append({"topic": int(t), "label": name[t],
                    "markers": {k: round(sum(bool(re.search(p, x)) for x in txt) / len(txt), 2) for k, p in MARKERS.items()},
                    "n": int(len(g)), "alzheimer": round(float((g["disease"].isin(["Alzheimer", "Ambas"])).mean()), 3),
                    "parkinson": round(float((g["disease"].isin(["Parkinson", "Ambas"])).mean()), 3),
                    "both": round(float((g["disease"] == "Ambas").mean()), 3),
                    "included": round(float(g["included"].mean()), 3),
                    "share_2016_2020": round(float(mid), 4), "share_2021_2026": round(float(late), 4),
                    "growth": round(float(late / mid), 2) if mid else None,
                    "median_year": int(g.loc[g["year"] > 0, "year"].median())})
    sim = tm.c_tf_idf_[1:] if tm._outliers else tm.c_tf_idf_
    from sklearn.metrics.pairwise import cosine_similarity
    S = cosine_similarity(sim)
    np.fill_diagonal(S, 0)
    pairs = sorted(((S[i, j], i, j) for i in range(n) for j in range(i + 1, n)), reverse=True)[:5]
    out = {"model": cfg, "disease_counts": pd.Series(dis).value_counts().to_dict(),
           "topics": per, "closest_pairs_ctfidf": [{"a": int(i), "b": int(j), "sim": round(float(s), 3)} for s, i, j in pairs],
           "first_merges": hier.sort_values("Distance").head(6)[["Parent_Name", "Child_Left_Name", "Child_Right_Name",
                                                                 "Distance"]].round(3).to_dict("records")}
    (VIZ / "insights.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    print(json.dumps(out["disease_counts"], ensure_ascii=False))
    for p in sorted(per, key=lambda p: -(p["growth"] or 0)):
        top = sorted(p["markers"].items(), key=lambda kv: -kv[1])[:3]
        print(f"  T{p['topic']:02d} n={p['n']:3d} AD={p['alzheimer']:.0%} PD={p['parkinson']:.0%} sel={p['included']:.0%} "
              f"growth={p['growth']} median={p['median_year']}  {p['label']}  {top}")
    print("closest:", out["closest_pairs_ctfidf"])


if __name__ == "__main__":
    main()
