"""Link each article to its topic and to the glossary terms, and measure the terms.

    python3 -m litreview.vincular                                # articles/selected/ (N = 370)
    python3 -m litreview.vincular --conjunto nao-selecionados    # the rest of articles/ (N = 431)
    python3 -m litreview.vincular --conjunto todos               # all 801
    python3 -m litreview.vincular --todas-ocorrencias            # link every occurrence, not only the first

Inputs, written by topicos/ (see topicos/README.md): data/topicos/doc_topics.csv
(topic of each work), glossary.csv (the vocabulary) and notes_index.json (note
paths in grafo/).

In each article of the set:
  - abstract: the first occurrence of each glossary term becomes
    [[grafo/termos/<term>|<text as written>]]. Plurals, hyphen/space variants
    and a few acronyms (DBS, STN, 6-OHDA...) resolve to the same term.
  - after the abstract, between <!-- vinculos:inicio --> and <!-- vinculos:fim -->:
    the topic link and the list of terms found
  - front matter: topico, topico_nome, n_termos
Re-running is safe: the block is replaced and only links into grafo/termos/ are
undone first. litreview.export rebuilds articles/ from scratch, so run.sh runs
this again after it.

Statistics for the set (denominator N = articles in the set), in
data/termos/<conjunto>/. Links take the most specific term ("dopamine release",
not "dopamine"); the statistics search each term on its own, so a term also
counts where it sits inside a longer one ("dopamine" in "dopamine release"):
  termos.csv             n_textos, cobertura (% of the N texts), ocorrencias,
                         prevalencia (occurrences per 10,000 words of abstract),
                         media_por_texto (occurrences per text where present)
  termos_por_topico.csv  coverage of each term inside each topic (% of that topic's texts)
  topicos.csv            texts per topic and its characteristic terms (lift = coverage
                         in the topic / coverage in the set, at least 3 texts)
  ocorrencias.csv        long table work_id, term, count, for any other analysis
Glossary notes get cobertura_<conjunto> and textos_<conjunto> in their front
matter; topic notes get artigos_<conjunto>.

Scoped graphs for Obsidian. Besides the global network in grafo/ (term-term
co-occurrence), "selecionados" and "todos" write their own term and topic notes
next to their articles, with that set's numbers and links only to its articles:
  selecionados -> articles/selected/grafo-selecionados/   graph filter: path:"articles/selected"
  todos        -> articles/grafo-todos/                   graph filter: path:articles -path:grafo-selecionados
The inline links in the abstracts keep pointing to the global entries in
grafo/termos/; the folders are not called "grafo" so that those links never
resolve to a scoped note. Articles get the tag tema/<n> so the graph colours
them by theme, like the terms. Scoped notes are updated in place (only changed
notes rewritten, stale ones removed), which keeps Obsidian's index consistent.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

from .common import DATA, ROOT
from .keywords import kw_key

ART = ROOT / "articles"
TOP = DATA / "topicos"
START, END = "<!-- vinculos:inicio -->", "<!-- vinculos:fim -->"
BLOCK = re.compile(r"\n*" + re.escape(START) + r".*?" + re.escape(END) + r"\n*", re.S)
TERM_LINK = re.compile(r"\[\[grafo/termos/[^\]|]+\|([^\]]+)\]\]")
NO_ABSTRACT = "_Abstract not available in any source database._"
# Acronyms written in capitals in the abstracts -> the glossary term (as written in full).
ACRONYMS = {"DBS": "deep brain stimulation", "STN": "subthalamic nucleus", "6-OHDA": "6-hydroxydopamine",
            "ChR2": "channelrhodopsin-2", "LID": "levodopa-induced dyskinesia", "LIDs": "levodopa-induced dyskinesia",
            "GPe": "external globus pallidus", "SNc": "substantia nigra pars compacta",
            "SNr": "substantia nigra pars reticulata", "MLR": "mesencephalic locomotor region",
            "PPN": "pedunculopontine nucleus", "MSNs": "medium spiny neurons", "iPSCs": "induced pluripotent stem cells"}
SCOPES = {"selecionados": (ART / "selected" / "grafo-selecionados", 'path:"articles/selected"'),
          "todos": (ART / "grafo-todos", "path:articles -path:grafo-selecionados")}
SETS = {"selecionados": lambda f: f.startswith("selected/"), "nao-selecionados": lambda f: not f.startswith("selected/"),
        "todos": lambda f: True}


def matcher(vocab):
    """One regex for the whole glossary: longest alternatives first, so a longer term wins at a position."""
    pats = []
    for key in vocab:
        words = [re.escape(w).replace(r"\-", r"[\s-]?") for w in key.split(" ")]
        pats.append(r"[\s-]+".join(words) + r"(?:s|es)?")
    acr = {a: kw_key(t) for a, t in ACRONYMS.items() if kw_key(t) in vocab}
    pats.sort(key=len, reverse=True)
    alts = [f"(?-i:{re.escape(a)})" for a in sorted(acr, key=len, reverse=True)] + pats
    return re.compile(r"(?<![\w-])(" + "|".join(alts) + r")(?![\w-])", re.I), acr


def compact(s):
    """Normalised key without hyphens or spaces: "deep-brain stimulation" == "deep brain stimulation"."""
    return re.sub(r"[\s-]+", "", kw_key(s))


def resolve(surface, lookup, acr):
    return acr.get(surface) or lookup.get(compact(surface))


def term_patterns(vocab, acr):
    """One regex per term (with its acronyms), to count it wherever it appears."""
    by_term = defaultdict(list)
    for a, k in acr.items():
        by_term[k].append(f"(?-i:{re.escape(a)})")
    out = {}
    for key in vocab:
        words = [re.escape(w).replace(r"\-", r"[\s-]?") for w in key.split(" ")]
        alts = [r"[\s-]+".join(words) + r"(?:s|es)?"] + by_term.get(key, [])
        out[key] = re.compile(r"(?<![\w-])(?:" + "|".join(alts) + r")(?![\w-])", re.I)
    return out


def link_text(text, rx, lookup, acr, notes, every):
    counts, seen = Counter(), set()

    def sub(m):
        term = resolve(m.group(1), lookup, acr)
        if term is None:
            return m.group(1)
        counts[term] += 1
        if term in seen and not every:
            return m.group(1)
        seen.add(term)
        return f"[[{notes['terms'][term]['note']}|{m.group(1)}]]"

    return rx.sub(sub, text), counts


def set_front(text, fields):
    """Replace or add top-level front-matter keys (values JSON-quoted, which is valid YAML)."""
    end = text.index("\n---", 3)
    head, rest = text[:end], text[end:]
    lines = [l for l in head.split("\n") if not any(l.startswith(f"{k}:") for k in fields)]
    lines += [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fields.items()]
    return "\n".join(lines) + rest


def write_csv(path, rows, cols=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols or list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def scope_notes(conjunto, chosen, occ, per_topic, rows, trow, notes, theme, N):
    """Term and topic notes for one set, next to its articles (see the module docstring)."""
    root, query = SCOPES[conjunto]
    meta = {r["work_id"]: r for r in csv.DictReader((DATA / "prisma_works.csv").open())}
    files = {r["work_id"]: ART / r["file"] for r in chosen}
    vocab, topics = notes["terms"], notes["topics"]
    written = set()

    def put(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        written.add(path)
        if not path.exists() or path.read_text() != text:
            path.write_text(text)

    def art_link(from_dir, w):
        rel = os.path.relpath(files[w], from_dir)
        title = re.sub(r"[\[\]]", "", meta[w]["title"])
        return f"[{title} ({meta[w]['year'] or 's/d'})]({quote(rel)})"

    def front(d):
        return "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in d.items()) + "\n---\n"

    tname = {t: Path(v["note"]).name for t, v in topics.items()}
    term_name = {k: Path(v["note"]).name for k, v in vocab.items()}
    term_dir, topic_dir = root / "termos", root / "topicos"
    for r in rows:
        k = r["termo"]
        th = theme.get(str(int(r["topico"][1:])), "") if r["topico"] else ""
        works = sorted((w for w, c in occ.items() if k in c), key=lambda w: -int(meta[w]["year"] or 0))
        t = str(int(r["topico"][1:])) if r["topico"] else None
        put(term_dir / f"{term_name[k]}.md", front({
            "tipo": "termo", "escopo": conjunto, "termo": r["rotulo"], "textos": r["n_textos"], "N": N,
            "cobertura": r["cobertura"], "prevalencia": r["prevalencia"], "topico": r["topico"],
            "tags": ["termo"] + ([f"tema/{th}"] if th else [])}) + "\n".join([
            "", f"# {r['rotulo']}", "",
            f"**{r['n_textos']} de {N} textos ({r['cobertura']}%)** · prevalência {r['prevalencia']} por 10 mil "
            f"palavras · tópico dominante: " + (f"[[{os.path.relpath(topic_dir / tname[t], root.parent)}|"
                                               f"{r['topico']} · {topics[t]['label']}]]" if t else "—")
            + f" · verbete geral: [[{vocab[k]['note']}|{r['rotulo']}]]", "",
            f"## Artigos ({len(works)})", ""] + [f"- {art_link(term_dir, w)}" for w in works]) + "\n")
    lift = {x["topico"]: x["termos_caracteristicos"] for x in trow}
    for t, ws in per_topic.items():
        code = f"T{int(t):02d}"
        top_terms = [re.sub(r" \(×[^)]*\)$", "", x) for x in lift.get(code, "").split("; ") if x]
        label_to_key = {vocab[k]["label"]: k for k in vocab}
        links = [f"[[{os.path.relpath(term_dir / term_name[label_to_key[l]], root.parent)}|{l}]]"
                 for l in top_terms if l in label_to_key]
        put(topic_dir / f"{tname[t]}.md", front({
            "tipo": "topico", "escopo": conjunto, "topico": code, "nome": topics[t]["label"], "artigos": len(ws),
            "N": N, "tags": ["topico"] + ([f"tema/{theme[t]}"] if t in theme else [])}) + "\n".join([
            "", f"# {code} · {topics[t]['label']}", "",
            f"**{len(ws)} de {N} artigos** · tópico geral: [[{topics[t]['note']}|{code}]]", "",
            "## Termos característicos (lift)", "", " · ".join(links) or "—", "",
            f"## Artigos ({len(ws)})", ""] + [f"- {art_link(topic_dir, w)}" for w in
                                               sorted(ws, key=lambda w: -int(meta[w]['year'] or 0))]) + "\n")
    put(root / "Mapa.md", front({"tipo": "mapa", "escopo": conjunto, "N": N, "tags": ["mapa"]}) + "\n".join([
        "", f"# Grafo: {conjunto} ({N} artigos)", "",
        "Gerado por `python3 -m litreview.vincular`; não edite (a pasta é atualizada a cada execução).", "",
        f"**Filtro da visão de grafo:** `{query}`", "",
        "Os nós são os artigos deste conjunto, os termos do glossário e os tópicos; cada nota de termo liga aos "
        "artigos em que o termo aparece, então dois artigos com o mesmo termo ficam a dois passos. As cores são os "
        "temas (tags `tema/<n>`). Para a rede global de coocorrência entre termos, use `path:\"grafo/\"`.", "",
        "## Tópicos", ""] + [f"- [[{os.path.relpath(topic_dir / tname[t], root.parent)}|T{int(t):02d} · "
                              f"{topics[t]['label']}]] · {len(per_topic[t])} artigos" for t in sorted(per_topic, key=int)])
        + "\n")
    for p in root.rglob("*.md"):
        if p not in written:
            p.unlink()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--conjunto", choices=list(SETS), default="selecionados")
    ap.add_argument("--todas-ocorrencias", action="store_true", help="link every occurrence, not only the first")
    args = ap.parse_args()
    if not (TOP / "notes_index.json").exists():
        print("data/topicos/notes_index.json missing: run topicos/run.sh first (topic model and glossary)")
        return
    notes = json.loads((TOP / "notes_index.json").read_text())
    vocab = notes["terms"]
    topic_of = {r["work_id"]: r["topic"] for r in csv.DictReader((TOP / "doc_topics.csv").open())}
    rx, acr = matcher(vocab)
    lookup = {compact(k): k for k in vocab}
    per_term = term_patterns(vocab, acr)
    index = list(csv.DictReader((DATA / "articles_index.csv").open()))
    chosen = [r for r in index if SETS[args.conjunto](r["file"])]
    tag = args.conjunto.replace("-", "_")
    theme = {r["topic"]: r["theme"] for r in csv.DictReader((TOP / "topics.csv").open())}

    occ, words, per_topic = {}, {}, defaultdict(list)
    for r in chosen:
        path = ART / r["file"]
        text = path.read_text()
        end = text.index("\n---", 3) + 4
        head, body = text[:end], text[end:]
        body = TERM_LINK.sub(r"\1", BLOCK.sub("\n", body)).strip()
        t = topic_of.get(r["work_id"])
        counts = Counter()
        if body != NO_ABSTRACT:
            plain = body
            body, counts = link_text(body, rx, lookup, acr, notes, args.todas_ocorrencias)
            # statistics: every term counted on its own, nested occurrences included
            occ[r["work_id"]] = Counter({k: n for k, p in per_term.items() if (n := len(p.findall(plain)))})
            words[r["work_id"]] = len(re.findall(r"\w+", plain))
        else:
            occ[r["work_id"]] = Counter()
            words[r["work_id"]] = 0
        block = [START]
        if t is not None:
            tn = notes["topics"][t]
            block.append(f"**Tópico:** [[{tn['note']}|T{int(t):02d} · {tn['label']}]]")
            per_topic[t].append(r["work_id"])
        if counts:
            block += ["", f"**Termos ({len(counts)}):** " + " · ".join(
                f"[[{vocab[k]['note']}|{vocab[k]['label']}]]" for k in sorted(counts, key=lambda k: vocab[k]['label']))]
        block.append(END)
        text = head + "\n" + body + "\n\n" + "\n".join(block) + "\n"
        text = set_front(text, {"topico": f"T{int(t):02d}" if t is not None else None,
                                "topico_nome": notes["topics"][t]["label"] if t is not None else None,
                                "n_termos": len(counts),
                                "tags": ["artigo"] + ([f"tema/{theme[t]}"] if t in theme else [])})
        path.write_text(text)

    N = len(chosen)
    total_words = sum(words.values()) or 1
    tot = Counter()
    df = Counter()
    for c in occ.values():
        tot.update(c)
        df.update(c.keys())
    out = DATA / "termos" / args.conjunto
    rows = []
    for k in sorted(df, key=lambda k: (-df[k], vocab[k]["label"])):
        tc = Counter(topic_of[w] for w, c in occ.items() if k in c and w in topic_of)
        rows.append({"termo": k, "rotulo": vocab[k]["label"], "n_textos": df[k], "cobertura": round(100 * df[k] / N, 2),
                     "ocorrencias": tot[k], "prevalencia": round(10000 * tot[k] / total_words, 2),
                     "media_por_texto": round(tot[k] / df[k], 2),
                     "topico": f"T{int(tc.most_common(1)[0][0]):02d}" if tc else ""})
    write_csv(out / "termos.csv", rows)
    tids = sorted(per_topic, key=int)
    matrix = []
    for k in [r["termo"] for r in rows]:
        row = {"termo": k, "rotulo": vocab[k]["label"]}
        for t in tids:
            ws = per_topic[t]
            row[f"T{int(t):02d}"] = round(100 * sum(1 for w in ws if k in occ[w]) / len(ws), 1)
        matrix.append(row)
    write_csv(out / "termos_por_topico.csv", matrix)
    trow = []
    for t in tids:
        ws = per_topic[t]
        lift = []
        for k in df:
            n_in = sum(1 for w in ws if k in occ[w])
            if n_in >= 3:
                lift.append(((n_in / len(ws)) / (df[k] / N), k))
        trow.append({"topico": f"T{int(t):02d}", "nome": notes["topics"][t]["label"], "n_textos": len(ws),
                     "parcela": round(100 * len(ws) / N, 1),
                     "termos_caracteristicos": "; ".join(f"{vocab[k]['label']} (×{l:.1f})"
                                                          for l, k in sorted(lift, reverse=True)[:8])})
    write_csv(out / "topicos.csv", trow)
    write_csv(out / "ocorrencias.csv", [{"work_id": w, "termo": k, "n": n} for w, c in occ.items() for k, n in c.items()],
              ["work_id", "termo", "n"])

    # glossary and topic notes: coverage in this set
    for k, v in vocab.items():
        p = ROOT / f"{v['note']}.md"
        if p.exists():
            p.write_text(set_front(p.read_text(), {f"cobertura_{tag}": round(100 * df[k] / N, 2),
                                                    f"textos_{tag}": df[k]}))
    for t, v in notes["topics"].items():
        p = ROOT / f"{v['note']}.md"
        if p.exists():
            p.write_text(set_front(p.read_text(), {f"artigos_{tag}": len(per_topic.get(t, []))}))

    if args.conjunto in SCOPES:
        scope_notes(args.conjunto, chosen, occ, per_topic, rows, trow, notes, theme, N)

    linked = sum(1 for c in occ.values() if c)
    print(f"{args.conjunto}: {N} articles, {linked} with terms linked, {sum(len(c) for c in occ.values()) / max(N, 1):.1f} "
          f"distinct terms per article; {len(df)} of {len(vocab)} glossary terms found -> data/termos/{args.conjunto}/")
    for r in rows[:12]:
        print(f"  {r['rotulo']:<34} {r['n_textos']:4d} textos  {r['cobertura']:5.1f}%  prevalência {r['prevalencia']:5.1f}/10k")


if __name__ == "__main__":
    main()
