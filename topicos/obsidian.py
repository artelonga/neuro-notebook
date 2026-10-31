"""Write the term network as Obsidian notes, for the vault's native graph view.

    uv run python obsidian.py

grafo/ (regenerated on every run; do not edit by hand). Notes are updated in
place: only changed notes are rewritten and only notes that no longer exist are
removed. Deleting and recreating the folder made Obsidian's index lose track of
the notes, so a click on a link created an empty note next to the article.
  Mapa.md                 index: themes -> topics, how to read the graph
  topicos/T03 <label>.md  one note per topic: words, metrics, terms, related
                          topics, every work (markdown link into articles/)
  termos/<term>.md        glossary: one note per term of glossary.csv; network
                          terms also list their linked terms (backbone edges)
                          and works. litreview/vincular.py links the articles
                          to these notes, so a term's backlinks list every
                          article that uses it, and adds coverage fields

data/topicos/notes_index.json maps topic ids and glossary terms to their note
paths, for litreview/vincular.py.

Links between notes are the graph's edges. Every topic and term note carries
the tag tema/<n>; .obsidian/graph.json gets one colour group per theme (same
dark-mode palette as the web viewer) and the filter 'path:"grafo/"', so the
global graph shows the term network instead of the 801 article notes. The
previous graph.json is kept once as graph.json.bak.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from urllib.parse import quote

import pandas as pd

from common import OUT, ROOT

GRAFO = ROOT / "grafo"
# Categorical palette, dark-mode steps (validated order; see the dataviz palette reference).
PALETTE = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]


def safe(name):
    name = re.sub(r'[\\/:*?"<>|#^\[\]]', "-", name).strip(" .-")
    return name[:120] or "termo"


def link(folder, name, alias=None):
    return f"[[grafo/{folder}/{name}|{alias or name}]]"


def article(file, title, year, depth=2):
    t = re.sub(r"[\[\]]", "", title)
    return f"[{t} ({year or 's/d'})]({'../' * depth}articles/{quote(file)})"


def yaml(d):
    out = []
    for k, v in d.items():
        out.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    return "\n".join(out)


def num(x):
    return f"{x:,.0f}".replace(",", ".") if isinstance(x, (int, float)) and x == int(x) else str(x).replace(".", ",")


def main():
    model = json.loads((OUT / "model.json").read_text())
    topics = pd.read_csv(OUT / "topics.csv")
    terms = pd.read_csv(OUT / "terms.csv")
    gloss = pd.read_csv(OUT / "glossary.csv")
    edges = pd.read_csv(OUT / "term_edges.csv")
    sim = pd.read_csv(OUT / "topic_similarity.csv", index_col=0)
    sim.index = sim.index.astype(str)
    graph = json.loads((OUT / "graph.json").read_text())
    docs_meta = graph["docs"]
    dt = pd.read_csv(OUT / "doc_topics.csv")
    from common import load_corpus
    corpus = {d["work_id"]: d for d in load_corpus()}

    (GRAFO / "topicos").mkdir(parents=True, exist_ok=True)
    (GRAFO / "termos").mkdir(exist_ok=True)
    written = set()

    def put(path, text):
        written.add(path)
        if not path.exists() or path.read_text() != text:
            path.write_text(text)

    has_llm = "llm_label" in topics
    tlabel = {int(r.topic): (r.llm_label if has_llm and isinstance(r.llm_label, str) else r.label)
              for r in topics.itertuples()}
    tname = {t: f"T{t:02d} {safe(l)}" for t, l in tlabel.items()}
    term_file = {r.term: safe(r.label) for r in gloss.itertuples()}
    term_file.update({r.term: safe(r.label) for r in terms.itertuples()})
    seen = set()
    for t in list(term_file):  # case-insensitive filesystems
        n = term_file[t]
        while n.lower() in seen:
            n += " (2)"
        seen.add(n.lower())
        term_file[t] = n
    nbrs = defaultdict(list)
    for e in edges.itertuples():
        nbrs[e.source].append((e.target, e.count, e.npmi))
        nbrs[e.target].append((e.source, e.count, e.npmi))

    # topic notes
    for r in topics.itertuples():
        t = int(r.topic)
        mine = terms[terms["topic"] == t].sort_values("docs", ascending=False)
        rel = sim.loc[str(t)].drop(str(t)).sort_values(ascending=False).head(3)
        works = dt[dt["topic"] == t]["work_id"]
        body = [
            "---", yaml({"tipo": "topico", "topico": t, "nome": tlabel[t], "tema": int(r.theme), "trabalhos": int(r.n_docs),
                         "npmi": float(r.npmi), "ano_mediano": int(r.median_year),
                         "tags": ["topico", f"tema/{int(r.theme)}"]}), "---", "",
            f"# T{t:02d} · {tlabel[t]}", "",
            *([f"> {r.llm_description}", "",
               f"_Nome {'revisado à mão' if r.label_source == 'revisado' else 'dado por modelo de linguagem local'}; "
               f"frases do BERTopic: {r.label}._", ""] if has_llm and isinstance(r.llm_description, str) else []),
            f"**Tema {int(r.theme)}** ({r.theme_label}) · **{int(r.n_docs)} trabalhos** · ano mediano "
            f"{int(r.median_year)} · coerência NPMI {num(r.npmi)} · {r.share_opto_keyword:.0%} com a palavra-chave "
            f"optogenética · {r.share_included:.0%} na seleção final", "",
            f"Palavras do tópico: {r.top_words.replace(';', ',')}", "",
            "## Termos do tópico", "",
            " · ".join(link("termos", term_file[x.term], x.label) for x in mine.head(30).itertuples()) or "—", "",
            "## Tópicos próximos", "",
        ]
        body += [f"- {link('topicos', tname[int(k)])} (similaridade {num(round(v, 2))})" for k, v in rel.items()]
        body += ["", f"## Trabalhos ({len(works)})", ""]
        body += [f"- {article(corpus[w]['file'], corpus[w]['title'], corpus[w]['year'])}"
                 for w in sorted(works, key=lambda w: -(int(corpus[w]['year'] or 0)))]
        put(GRAFO / "topicos" / f"{tname[t]}.md", "\n".join(body) + "\n")

    # term notes
    for r in terms.itertuples():
        nb = sorted(nbrs[r.term], key=lambda x: -x[2])
        works = r.work_ids.split()
        body = [
            "---", yaml({"tipo": "termo", "termo": r.label, "trabalhos": int(r.docs), "fonte": r.source,
                         "topico": int(r.topic), "tema": int(r.theme), "comunidade": int(r.community),
                         "tendencia": r.trend, "tags": ["termo", f"tema/{int(r.theme)}"]}), "---", "",
            f"# {r.label}", "",
            f"**{int(r.docs)} trabalhos** · fonte: {r.source} · tópico dominante "
            f"{link('topicos', tname[int(r.topic)])} ({r.topic_purity:.0%} dos trabalhos) · comunidade "
            f"{int(r.community)} · tendência: {r.trend}", "",
            "## Termos ligados", "",
        ]
        body += [f"- {link('termos', term_file[o], terms.set_index('term').loc[o, 'label'])} · {c} trabalhos juntos · "
                 f"NPMI {num(round(w, 2))}" for o, c, w in nb]
        body += ["", f"## Trabalhos ({len(works)})", ""]
        body += [f"- {article(corpus[w]['file'], corpus[w]['title'], corpus[w]['year'])}" for w in works[:40]]
        if len(works) > 40:
            body.append(f"- … e mais {len(works) - 40} (lista completa em data/topicos/terms.csv)")
        put(GRAFO / "termos" / f"{term_file[r.term]}.md", "\n".join(body) + "\n")

    # glossary terms outside the network: short notes (their backlinks list the articles)
    theme_of = topics.set_index("topic")["theme"].to_dict()
    for r in gloss[gloss["in_graph"] == 0].itertuples():
        th = int(theme_of[int(r.topic)])
        body = ["---", yaml({"tipo": "termo", "termo": r.label, "trabalhos": int(r.docs), "fonte": r.source,
                             "topico": int(r.topic), "tema": th, "na_rede": False, "tags": ["termo", f"tema/{th}"]}),
                "---", "", f"# {r.label}", "",
                f"**{int(r.docs)} trabalhos** · fonte: {r.source} · tópico dominante "
                f"{link('topicos', tname[int(r.topic)])}", "",
                "Fora da rede de coocorrência (sem ligações fortes o bastante). Os artigos que usam o termo "
                "aparecem nos backlinks desta nota.", ""]
        put(GRAFO / "termos" / f"{term_file[r.term]}.md", "\n".join(body) + "\n")
    (OUT / "notes_index.json").write_text(json.dumps({
        "topics": {str(t): {"note": f"grafo/topicos/{n}", "label": tlabel[t]} for t, n in tname.items()},
        "terms": {t: {"note": f"grafo/termos/{n}", "label": gl} for t, n, gl in
                  [(r.term, term_file[r.term], r.label) for r in gloss.itertuples()]},
    }, ensure_ascii=False, indent=1))

    # index
    themes = topics.groupby("theme")
    idx = [
        "---", yaml({"tipo": "mapa", "tags": ["mapa"]}), "---", "",
        "# Mapa de termos e tópicos", "",
        f"Gerado por `topicos/` a partir dos {model['n_docs']} trabalhos de `articles/`: "
        f"{model['n_topics']} tópicos em {model['n_themes']} temas (BERTopic com {model['embedding']} + "
        f"{model['reducer']} + {model['clusterer']} {model['params']}) e {len(terms)} termos ligados por "
        f"coocorrência. Não edite: a pasta é refeita a cada execução.", "",
        "**Como ver:** abra a visão de grafo (Ctrl/Cmd+G). As cores são os temas; o filtro `path:\"grafo/\"` "
        "esconde as notas de artigos. Cada termo liga aos termos com que mais aparece junto (NPMI) e ao seu "
        "tópico dominante; cada tópico liga aos seus termos e trabalhos.", "",
        "**Três grafos** (cole o filtro na busca da visão de grafo):", "",
        "| Escopo | Filtro | Notas |",
        "|---|---|---|",
        "| Rede global de termos (esta pasta) | `path:\"grafo/\"` | `grafo/` |",
        "| Os 801 artigos | `path:articles -path:grafo-selecionados` | `articles/grafo-todos/` |",
        "| Os 370 da seleção final | `path:\"articles/selected\"` | `articles/selected/grafo-selecionados/` |", "",
    ]
    viz = ROOT / "data" / "topicos" / "viz"
    figs = [("intertopic", "Distância entre tópicos"), ("hierarchy", "Hierarquia de tópicos"),
            ("over_time_facets", "Tópicos por ano"), ("disease", "Tópicos por doença citada"),
            ("selection", "Tópicos dentro e fora da seleção final"), ("heatmap", "Similaridade entre tópicos")]
    if any((viz / f"{n}.png").exists() for n, _ in figs):
        idx += ["## Visualizações do BERTopic", "",
                "Versões interativas: `data/topicos/viz/*.html` (abrem no navegador).", ""]
        idx += [f"### {t}\n\n![{t}](../data/topicos/viz/{n}.png)\n" for n, t in figs if (viz / f"{n}.png").exists()]
    for th, g in themes:
        idx.append(f"## Tema {th} · {g['theme_label'].iloc[0]} ({PALETTE[(th - 1) % 8]})")
        idx.append("")
        idx += [f"- {link('topicos', tname[int(r.topic)])} · {int(r.n_docs)} trabalhos" for r in g.itertuples()]
        idx.append("")
    put(GRAFO / "Mapa.md", "\n".join(idx) + "\n")
    stale = [p for p in GRAFO.rglob("*.md") if p not in written]
    for p in stale:
        p.unlink()

    # graph view settings
    gpath = ROOT / ".obsidian" / "graph.json"
    if gpath.exists():
        cfg = json.loads(gpath.read_text())
        bak = gpath.with_suffix(".json.bak")
        if not bak.exists():
            bak.write_text(json.dumps(cfg, indent=2))
        cfg.update({
            "search": "path:\"grafo/\"", "showTags": False, "showOrphans": False, "colorGroups": [
                {"query": f"tag:#tema/{th}", "color": {"a": 1, "rgb": int(PALETTE[(th - 1) % 8][1:], 16)}}
                for th in sorted(topics["theme"].unique())],
            "repelStrength": 12, "linkDistance": 120, "linkStrength": 0.6, "nodeSizeMultiplier": 1.2,
        })
        gpath.write_text(json.dumps(cfg, indent=2))
    print(f"wrote grafo/: {len(topics)} topic notes, {len(term_file)} term notes ({len(terms)} in the network), Mapa.md; "
          f"graph.json colour groups: {topics['theme'].nunique()}")


if __name__ == "__main__":
    main()
