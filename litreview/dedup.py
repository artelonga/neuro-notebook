"""AC-3: merge records across databases, classify, and count overlaps.

    python3 -m litreview.dedup

Two records are the same work if they share any of: DOI, PMID, PMCID, arXiv id,
or normalised title (>=25 alphanumerics). Matching is transitive (union-find).

Each work gets a screening status from the local keyword re-check
(title + abstract + author keywords, diacritics folded):
  confirmed     both concepts found in at least one record of the work
  rejected      an abstract was available but a concept is missing
                (API matched on MeSH, stemming, CJK tokenisation, etc.)
  unverifiable  no abstract available anywhere; title alone does not confirm

Outputs (data/):
  works.csv           one row per unique work, a 0/1 column per database
  counts.csv          per-database hits, retrieved, confirmed, unique-to-database
  overlap_matrix.csv  pairwise overlap of confirmed works
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict

from .common import DATA, norm_title
from .literature import RAW, SOURCES


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def load():
    recs = []
    for key in SOURCES:
        f = RAW / f"{key}.jsonl"
        if f.exists():
            recs += [json.loads(line) for line in f.open()]
    return recs


def cluster(recs):
    dsu, first = DSU(len(recs)), {}
    for i, r in enumerate(recs):
        keys = [("doi", r["doi"]), ("pmid", r["pmid"]), ("pmcid", r["pmcid"]),
                ("arxiv", r["arxiv"]), ("title", norm_title(r["title"]))]
        for k in keys:
            if not k[1]:
                continue
            if k in first:
                dsu.union(i, first[k])
            else:
                first[k] = i
    groups = defaultdict(list)
    for i in range(len(recs)):
        groups[dsu.find(i)].append(recs[i])
    return list(groups.values())


def status(group):
    if any(r["verified"] for r in group):
        return "confirmed"
    if any(r["has_abstract"] for r in group):
        return "rejected"
    return "unverifiable"


def pick(group, field):
    # Prefer curated sources for display metadata.
    order = {k: i for i, k in enumerate(SOURCES)}
    for r in sorted(group, key=lambda r: order.get(r["source"], 99)):
        if r.get(field):
            return r[field]
    return ""


def main():
    recs = load()
    groups = cluster(recs)
    dbs = [k for k in SOURCES if (RAW / f"{k}.jsonl").exists()]
    log = json.loads((DATA / "search_log.json").read_text())

    works = []
    for g in groups:
        srcs = {r["source"] for r in g}
        works.append({
            "title": pick(g, "title"), "year": pick(g, "year"), "doi": pick(g, "doi"),
            "pmid": pick(g, "pmid"), "pmcid": pick(g, "pmcid"), "journal": pick(g, "journal"),
            "pubtype": pick(g, "pubtype"), "status": status(g), "n_databases": len(srcs),
            # >1 when a preprint and its journal version were merged into one work
            "n_versions": len({r["doi"] for r in g if r["doi"]}) or 1,
            **{f"in_{d}": int(d in srcs) for d in dbs},
            "source_ids": " | ".join(sorted(f"{r['source']}:{r['source_id']}" for r in g)),
        })
    works.sort(key=lambda w: (w["status"], -(w["year"] or 0), w["title"].lower()))
    for i, w in enumerate(works, 1):
        w["work_id"] = f"W{i:04d}"
    cols = ["work_id", "status", "n_databases", "n_versions"] + [f"in_{d}" for d in dbs] + \
           ["year", "title", "journal", "doi", "pmid", "pmcid", "pubtype", "source_ids"]
    with open(DATA / "works.csv", "w", newline="") as f:
        w_ = csv.DictWriter(f, fieldnames=cols)
        w_.writeheader()
        w_.writerows(works)

    conf = [w for w in works if w["status"] == "confirmed"]
    rows = []
    for d in dbs:
        mine = [w for w in works if w[f"in_{d}"]]
        mine_c = [w for w in mine if w["status"] == "confirmed"]
        st = Counter(w["status"] for w in mine)
        rows.append({
            "database": SOURCES[d][0], "key": d, "api_hits": log[d]["hits"],
            "retrieved": log[d]["retrieved"], "works": len(mine),
            "confirmed": st["confirmed"], "unverifiable": st["unverifiable"], "rejected": st["rejected"],
            "unique_confirmed": sum(1 for w in mine_c if w["n_databases"] == 1),
            "share_of_total_confirmed": f"{len(mine_c) / max(len(conf), 1):.1%}",
        })
    tot = Counter(w["status"] for w in works)
    rows.append({"database": "TOTAL (deduplicated)", "key": "total", "api_hits": sum(r["api_hits"] for r in rows),
                 "retrieved": len(recs), "works": len(works), "confirmed": tot["confirmed"],
                 "unverifiable": tot["unverifiable"], "rejected": tot["rejected"],
                 "unique_confirmed": "", "share_of_total_confirmed": "100.0%"})
    with open(DATA / "counts.csv", "w", newline="") as f:
        w_ = csv.DictWriter(f, fieldnames=list(rows[0]))
        w_.writeheader()
        w_.writerows(rows)

    with open(DATA / "overlap_matrix.csv", "w", newline="") as f:
        w_ = csv.writer(f)
        w_.writerow(["confirmed works"] + dbs)
        for a in dbs:
            w_.writerow([a] + [sum(1 for w in conf if w[f"in_{a}"] and w[f"in_{b}"]) for b in dbs])

    print(f"{len(recs)} records -> {len(works)} unique works "
          f"({tot['confirmed']} confirmed, {tot['unverifiable']} unverifiable, {tot['rejected']} rejected)")
    for r in rows:
        print(f"  {r['database']:<32} hits={r['api_hits']:<5} confirmed={r['confirmed']:<5} "
              f"unique={r['unique_confirmed']}")


if __name__ == "__main__":
    main()
