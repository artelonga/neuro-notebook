"""Keyword profile of the article database (no network).

    python3 -m litreview.keywords

Two groups of works in articles/ (the 801 screened works):
  with_keywords   at least one keyword in the front matter (any source)
  opto_keyword    at least one keyword containing an optogenetics term
                  (a subset of with_keywords)
For each: language, other keywords (prevalence), year, journal, and the three
type fields (document_type, study_type, publication_type). Also where the
keywords come from: author keywords (PubMed [ot], Europe PMC KW, DOAJ) or
OpenAlex's machine-assigned keywords.

Writes data/keywords_profile.json and data/keywords_prevalence.csv.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter

from .common import DATA, ROOT
from .export import load_records

OPTO = re.compile(r"optogenet|opto-genet|optigenet|оптогенет|光遗传|光遺傳|光遺伝|オプトジェネティクス|광유전", re.I)
FIELDS = ("language", "publication_type", "journal", "document_type", "study_type")
LANG = {"eng": "en", "en": "en", "fre": "fr", "fr": "fr", "es": "es", "spa": "es", "rus": "ru", "ja": "ja",
        "jpn": "ja", "zh": "zh", "中文": "zh", "chi": "zh", "tr": "tr", "it": "it", "ita": "it", "fa": "fa",
        "en,zh": "en+zh", "por": "pt", "pt": "pt", "ger": "de", "de": "de", "ko": "ko"}
# Funding labels in PubMed publication types say nothing about the kind of document.
FUNDING = re.compile(r"^Research Support|^\[MED\] Research Support")
AUTHOR_KW_SOURCES = ("pubmed", "epmc", "doaj")


def front_matter(path):
    text = path.read_text().split("\n---", 1)[0]
    d = {}
    for f in FIELDS:
        m = re.search(rf"^{f}: (.*)$", text, re.M)
        d[f] = json.loads(m.group(1)) if m else None
    m = re.search(r"^keywords:(.*?)(?=^\S)", text, re.M | re.S)
    body = m.group(1).strip() if m else "[]"
    d["keywords"] = [] if body == "[]" else [json.loads(line.strip()[2:]) for line in body.splitlines()
                                             if line.strip().startswith("- ")]
    return d


def kw_key(k):
    """Merge spelling variants: case, curly quotes, possessive, parenthetical acronym, plural."""
    k = k.lower().replace("’", "'").replace("‐", "-")
    k = re.sub(r"\s*\([^)]*\)", "", k)
    k = re.sub(r"'s\b|'", "", k)
    k = re.sub(r"[\s_]+", " ", k).strip(" .;,")
    k = {"pd": "parkinson disease", "ad": "alzheimer disease", "6-ohda": "6-hydroxydopamine",
         "dbs": "deep brain stimulation", "chr2": "channelrhodopsin-2", "stn": "subthalamic nucleus"}.get(k, k)
    words = k.split(" ")
    if len(words[-1]) > 4 and words[-1].endswith("s") and not words[-1].endswith("ss"):
        words[-1] = words[-1][:-1]
    return " ".join(words)


def dist(values, top=None):
    c = Counter(v if v not in (None, "") else "unknown" for v in values)
    return dict(c.most_common(top))


def profile(works, n_top_kw=20, n_top_journal=12):
    n = len(works)
    other = Counter()
    label = {}
    for w in works:
        keys = {kw_key(k) for k in w["keywords"] if not OPTO.search(k)}
        for k in w["keywords"]:
            if not OPTO.search(k):
                label.setdefault(kw_key(k), Counter())[k] += 1
        other.update(keys)
    journals = Counter()
    jlabel = {}
    for w in works:
        j = (w["journal"] or "").split(" : ")[0].strip()  # drop subtitles ("bioRxiv : the preprint server…")
        if j:
            journals[j.lower()] += 1
            jlabel.setdefault(j.lower(), Counter())[j] += 1
    pub_tokens = Counter()
    for w in works:
        toks = [t.replace("[MED] ", "").replace("[PPR] ", "").strip() for t in (w["publication_type"] or "").split("; ")]
        toks = {t for t in toks if t and not FUNDING.match(t)} or {"unknown"}
        pub_tokens.update(toks)
    return {
        "n": n,
        "language": dist(LANG.get((w["language"] or "").lower(), w["language"]) for w in works),
        "other_keywords": [{"keyword": label[k].most_common(1)[0][0], "key": k, "works": v,
                            "prevalence": round(v / n, 3)} for k, v in other.most_common(n_top_kw)],
        "distinct_other_keywords": len(other),
        "year": dict(sorted(Counter(w["year"] for w in works if w["year"]).items())),
        "journal": [{"journal": jlabel[j].most_common(1)[0][0], "works": v} for j, v in journals.most_common(n_top_journal)],
        "no_journal": sum(1 for w in works if not (w["journal"] or "").strip()),
        "distinct_journals": len(journals),
        "document_type": dist(w["document_type"] for w in works),
        "study_type": dist(w["study_type"] for w in works),
        "publication_type_tokens": dict(pub_tokens.most_common(15)),
        "selected": sum(1 for w in works if w["included"] == "1"),
        "keyword_source": dict(Counter(w["kw_source"] for w in works).most_common()),
    }


def main():
    recs = load_records()
    works = []
    wsrc = {w["work_id"]: w["source_ids"] for w in csv.DictReader((DATA / "works.csv").open())}
    for r in csv.DictReader((DATA / "prisma_works.csv").open()):
        if not r["file"]:
            continue
        d = front_matter(ROOT / "articles" / r["file"])
        group = [recs[s] for s in wsrc[r["work_id"]].split(" | ") if s in recs]
        with_kw = {g["source"] for g in group if (g.get("keywords") or "").strip()}
        d["kw_source"] = ("author" if with_kw & set(AUTHOR_KW_SOURCES) else
                          "openalex-only" if with_kw else "none")
        d.update(work_id=r["work_id"], year=r["year"], included=r["included"])
        works.append(d)
    g_kw = [w for w in works if w["keywords"]]
    g_opto = [w for w in g_kw if any(OPTO.search(k) for k in w["keywords"])]
    out = {
        "base": "articles/ (screened works)", "n_works": len(works),
        "groups": {"with_keywords": profile(g_kw), "opto_keyword": profile(g_opto),
                   "keywords_without_opto": profile([w for w in g_kw if w not in g_opto]),
                   "no_keywords": profile([w for w in works if not w["keywords"]])},
        "opto_keyword_forms": dict(Counter(k for w in g_opto for k in w["keywords"] if OPTO.search(k)).most_common(12)),
    }
    (DATA / "keywords_profile.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    rows = []
    for gname in ("with_keywords", "opto_keyword"):
        for k in profile(g_kw if gname == "with_keywords" else g_opto, n_top_kw=100)["other_keywords"]:
            rows.append({"group": gname, **k})
    with open(DATA / "keywords_prevalence.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(works)} works: {len(g_kw)} with keywords, {len(g_opto)} with an optogenetics keyword")


if __name__ == "__main__":
    main()
