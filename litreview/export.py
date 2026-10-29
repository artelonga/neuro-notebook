"""Export confirmed works as a Markdown + YAML-front-matter database.

    python3 -m litreview.export

One file per confirmed work, named "<title>.md": the works that meet the
eligibility criteria (common.eligibility) in articles/selected/, all others
directly in articles/ (litreview.prisma keeps selected/ in sync with the
reviewers' decisions). The YAML front
matter holds bibliographic metadata, the PRISMA identification trail and empty
screening fields for the reviewers; the body is the abstract.

Authors missing from every source record, and the publication type of works
with no PubMed/Europe PMC/DOAJ record, are looked up on OpenAlex by DOI
(enrichment only; it does not change the search results or counts).
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import unicodedata

from .common import DATA, MIN_YEAR, ROOT, eligibility, get_json, qs
from .literature import RAW, SOURCES

OUT = ROOT / "articles"
# Preference order when sources disagree: curated indexes first.
ORDER = ["pubmed", "epmc", "doaj", "arxiv", "openalex", "s2"]
SEARCH_RULE = ("(optogenet* OR opto-genet* OR optigenet* + non-Latin forms) AND "
               "(alzheimer* OR parkinson* + non-Latin forms) in title/abstract/keywords")


def load_records():
    recs = {}
    for key in SOURCES:
        f = RAW / f"{key}.jsonl"
        if f.exists():
            for line in f.open():
                r = json.loads(line)
                recs[f"{r['source']}:{r['source_id']}"] = r
    return recs


def first(group, field):
    for r in sorted(group, key=lambda r: ORDER.index(r["source"])):
        if r.get(field):
            return r[field]
    return None


def enrich_authors(works):
    """Batch OpenAlex lookups by DOI for works without authors in any source."""
    need = [w for w in works if not w["authors"] and w["doi"]]
    found = {}
    for i in range(0, len(need), 50):
        dois = "|".join(w["doi"] for w in need[i:i + 50])
        r = get_json(f"https://api.openalex.org/works?{qs({'filter': f'doi:{dois}', 'per-page': 50, 'select': 'doi,authorships'})}",
                     pause=1.0)
        for it in r["results"]:
            doi = (it.get("doi") or "").lower().replace("https://doi.org/", "")
            found[doi] = [a["author"]["display_name"] for a in it.get("authorships") or []
                          if (a.get("author") or {}).get("display_name")]
    for w in need:
        if found.get(w["doi"]):
            w["authors"], w["authors_source"] = found[w["doi"]], "openalex (DOI lookup)"
    return len(need), sum(1 for w in need if w["authors"])


# --- peer-review classification -------------------------------------------
# No database states "peer reviewed"; it is inferred from publication type and
# venue. peer_reviewed = the work was published as a journal article or review
# (any version of it); preprints, theses, books, conference outputs, editorials,
# news, letters and works of unknown type are False.
PREPRINT_DOI = ("10.1101/", "10.64898/", "10.21203/", "10.2139/", "10.20944/", "10.48550/",
                "10.31219/", "10.31234/", "10.31235/", "10.36227/", "10.22541/", "10.26434/")
PREPRINT_VENUE = re.compile(r"rxiv|research square|preprints\.org|ssrn|authorea|figshare|zenodo", re.I)
# Meeting abstracts printed in journal supplements (AAIC in Alzheimer's & Dementia, FASEB J).
ABSTRACT_DOI = re.compile(r"^10\.1002/alz(\.0\d{5}$|\d+_)|\.s\d+\.|_supplement\.")
ABSTRACT_TITLE = re.compile(r"^[A-Z]{0,3}\d{1,4}(?:[-‐–]\d{1,4})*[:.]\s")
CONFERENCE_VENUE = re.compile(r"conference|congress|symposium|\bmeeting\b", re.I)
BOOK_VENUE = re.compile(r"ebooks?\b|handbook", re.I)
NON_RESEARCH = re.compile(r"\b(news|editorial|comment|letter|published erratum|retraction|"
                          r"article-commentary|paratext|peer-review|lettersandcomments)\b", re.I)
SOURCE_RANK = ["pubmed", "epmc", "doaj", "openalex-doi", "openalex", "s2", "arxiv"]


def record_kind(r):
    """(kind, basis) for one source record; kind None = no usable evidence."""
    doi, venue, pt, src = r.get("doi") or "", r.get("journal") or "", r.get("pubtype") or "", r["source"]
    if doi.startswith(PREPRINT_DOI) or PREPRINT_VENUE.search(venue) or "preprint" in pt.lower() \
            or src == "arxiv" or pt.startswith("[PPR]"):
        return "preprint", f"{src}: preprint ({venue or doi or pt})"
    if ABSTRACT_DOI.search(doi) or pt.startswith("[PMC] Abstract") or "conference-abstract" in pt:
        return "conference-abstract", f"{src}: meeting abstract ({doi or pt})"
    if pt.startswith("[ETH]") or pt == "dissertation":
        return "thesis", f"{src}: {pt}"
    if pt in ("book-chapter", "book") or "Book" in pt.split("; ") or BOOK_VENUE.search(venue):
        return "book", f"{src}: {pt or venue}"
    if pt == "conference-paper" or pt.split("; ") == ["Conference"] or CONFERENCE_VENUE.search(venue):
        return "conference-paper", f"{src}: {pt or venue}"
    if src in ("pubmed", "epmc"):
        if NON_RESEARCH.search(pt) and "Review" not in pt and "research-article" not in pt:
            return "editorial-or-news", f"{src}: {pt}"
        if "Journal Article" in pt or "Review" in pt or pt.startswith("[MED]"):
            return ("review" if "Review" in pt else "journal-article"), f"{src}: {pt}"
    if src == "doaj":
        return "journal-article", f"doaj: article in DOAJ-listed journal ({venue})"
    if src in ("openalex", "openalex-doi"):
        if pt in ("editorial", "paratext", "peer-review", "letter", "erratum"):
            return "editorial-or-news", f"{src}: {pt}"
        if pt in ("article", "review") and venue:
            return ("review" if pt == "review" else "journal-article"), f"{src}: {pt} in {venue}"
        if pt in ("dataset", "other", "report"):
            return "other", f"{src}: {pt}"
    if src == "s2" and pt:
        types = set(pt.split("; "))
        if types <= {"Editorial", "News", "LettersAndComments"}:
            return "editorial-or-news", f"s2: {pt}"
        if types & {"JournalArticle", "Review", "Study", "CaseReport"} and venue:
            return ("review" if "Review" in types else "journal-article"), f"s2: {pt} in {venue}"
    return None, None


def openalex_types(dois):
    """DOI -> pseudo-record with OpenAlex's type and venue (for works without curated sources)."""
    out = {}
    for i in range(0, len(dois), 50):
        q = {"filter": "doi:" + "|".join(dois[i:i + 50]), "per-page": 50, "select": "doi,type,primary_location"}
        for it in get_json(f"https://api.openalex.org/works?{qs(q)}", pause=1.0)["results"]:
            src = ((it.get("primary_location") or {}).get("source") or {})
            stype = src.get("type") or ""
            t = it.get("type") or ""
            if stype == "repository" and t == "article":
                t = "preprint"
            elif stype == "conference" and t == "article":
                t = "conference-paper"
            doi = (it.get("doi") or "").lower().replace("https://doi.org/", "")
            out[doi] = {"source": "openalex-doi", "doi": doi, "pubtype": t,
                        "journal": src.get("display_name") or ""}
    return out


def classify(group, extra=None):
    """Work-level decision: the best-ranked source with evidence wins, but a
    published (journal) version beats a preprint of the same work."""
    kinds = [(SOURCE_RANK.index(r["source"]),) + record_kind(r) for r in group + ([extra] if extra else [])]
    kinds = sorted(k for k in kinds if k[1])
    # Meeting abstracts are often typed "article" by OpenAlex/S2: an abstract
    # signal (supplement DOI, or a numbered title like "P1-172:" / "558.") wins
    # unless PubMed or Europe PMC holds it as a journal article.
    curated = any(k[0] <= 1 and k[1] in ("journal-article", "review") for k in kinds)
    numbered = next((r["title"] for r in group if ABSTRACT_TITLE.match(r.get("title") or "")), None)
    if not curated and (numbered or any(k[1] == "conference-abstract" for k in kinds)):
        basis = next((k[2] for k in kinds if k[1] == "conference-abstract"),
                     f"numbered meeting-abstract title ({(numbered or '')[:30]}…)")
        return "conference-abstract", False, basis
    if not kinds:
        return "unknown", False, "no publication-type evidence in any source"
    non_pre = [k for k in kinds if k[1] != "preprint"]
    rank, kind, basis = (non_pre or kinds)[0]
    if kind == "journal-article" and any(k[1] == "review" for k in non_pre if k[0] <= 2):
        kind = "review"
    return kind, kind in ("journal-article", "review"), basis


# --- study type (PRISMA identification breakdown) --------------------------
# Heuristic on publication types, titles and venues of every record of the work.
META = re.compile(r"meta-?analy[sz]", re.I)
SYSTEMATIC = re.compile(r"systematic (literature )?review|scoping review|umbrella review|revis[aã]o sistem", re.I)
# "Methods in Enzymology" is a series of review chapters, not a methods venue.
METHODS_VENUE = re.compile(r"\bmethods?\b(?! in enzymology)|protocols?\b|visualized experiments|\bjove\b", re.I)
METHODS_TITLE = re.compile(r"\b(methodolog\w*|step-by-step|(a|new|novel) (method|technique|tool|approach) "
                           r"(for|to))\b|^(a )?protocol\b", re.I)
NON_STUDY = ("editorial-or-news", "book", "other", "unknown")


def study_type(doc_type, group):
    """meta-analysis | systematic-review | review | methodology | original-research | other."""
    pts = " ; ".join(r.get("pubtype") or "" for r in group)
    titles = " ".join(r.get("title") or "" for r in group)
    venues = " ".join(r.get("journal") or "" for r in group)
    if "Meta-Analysis" in pts or META.search(titles):
        return "meta-analysis"
    if "Systematic Review" in pts or SYSTEMATIC.search(titles):
        return "systematic-review"
    if doc_type == "review":
        return "review"
    if doc_type in NON_STUDY:
        return "other"
    if "methods-article" in pts or METHODS_VENUE.search(venues) or METHODS_TITLE.search(titles):
        return "methodology"
    return "original-research"


def filename(title, taken, work_id):
    name = unicodedata.normalize("NFC", re.sub(r"<[^>]+>", "", title or work_id))
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "-", name)
    name = re.sub(r"\s+", " ", name).strip(" .-") or work_id
    while len(name.encode()) > 180:  # stay well under the 255-byte filename limit
        name = name[:-1]
    name = name.rstrip(" .-")
    if name.lower() in taken:  # case-insensitive filesystems (macOS)
        name = f"{name} ({work_id})"
    taken.add(name.lower())
    return name + ".md"


def y(v, indent=0):
    """Minimal YAML emitter: JSON scalars are valid YAML, so strings are JSON-quoted."""
    pad = "  " * indent
    if isinstance(v, dict):
        out = []
        for k, val in v.items():
            if isinstance(val, dict) and val:
                out.append(f"{pad}{k}:\n{y(val, indent + 1)}")
            elif isinstance(val, list) and val:
                out.append(f"{pad}{k}:\n" + "\n".join(f"{pad}  - {json.dumps(i, ensure_ascii=False)}" for i in val))
            else:
                out.append(f"{pad}{k}: {json.dumps(val, ensure_ascii=False) if val != [] else '[]'}")
        return "\n".join(out)
    return json.dumps(v, ensure_ascii=False)


def main():
    recs = load_records()
    rows = [w for w in csv.DictReader((DATA / "works.csv").open()) if w["status"] == "confirmed"]
    run_date = json.loads((DATA / "search_log.json").read_text())["pubmed"]["run_at"][:10]
    works = []
    for row in rows:
        group = [recs[s] for s in row["source_ids"].split(" | ") if s in recs]
        dbs = [d for d in ORDER if row.get(f"in_{d}") == "1"]
        doi = first(group, "doi")
        abstract_src = next((r for r in sorted(group, key=lambda r: ORDER.index(r["source"])) if r["abstract"]), None)
        author_src = next((r for r in sorted(group, key=lambda r: ORDER.index(r["source"])) if r["authors"]), None)
        kws = []
        for r in group:
            for k in (r.get("keywords") or "").split(";"):
                k = k.strip()
                if k and k.lower() not in {x.lower() for x in kws}:
                    kws.append(k)
        works.append({
            "work_id": row["work_id"], "title": first(group, "title") or row["title"], "doi": doi,
            "other_dois": sorted({r["doi"] for r in group if r["doi"] and r["doi"] != doi}),
            "authors": author_src["authors"] if author_src else [],
            "authors_source": author_src["source"] if author_src else None,
            "year": first(group, "year"), "journal": first(group, "journal"),
            "pubtype": first(group, "pubtype"), "lang": first(group, "lang"), "keywords": kws,
            "pmid": first(group, "pmid"), "pmcid": first(group, "pmcid"), "arxiv": first(group, "arxiv"),
            "openalex": next((r["source_id"] for r in group if r["source"] == "openalex"), None),
            "abstract": abstract_src["abstract"] if abstract_src else "",
            "abstract_source": abstract_src["source"] if abstract_src else None,
            "dbs": dbs, "sources": sorted(f"{r['source']}:{r['source_id']}" for r in group),
            "_group": group,
        })
    n_need, n_fixed = enrich_authors(works)
    # OpenAlex type lookup for works with no curated (PubMed/Europe PMC/DOAJ) record.
    lookup = sorted({w["doi"] for w in works if w["doi"] and
                     not any(r["source"] in ("pubmed", "epmc", "doaj") for r in w["_group"])})
    oa = openalex_types(lookup)
    for w in works:
        w["doc_type"], w["peer_reviewed"], w["pr_basis"] = classify(w["_group"], oa.get(w["doi"]))
        w["study_type"] = study_type(w["doc_type"], w["_group"])
        w["elig"] = eligibility(w["year"], w["peer_reviewed"])

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "selected").mkdir(parents=True)
    taken, index = set(), []
    for w in works:
        fname = filename(w["title"], taken, w["work_id"])
        meta = {
            "title": w["title"], "doi": w["doi"], "work_id": w["work_id"],
            "authors": w["authors"], "year": w["year"], "journal": w["journal"],
            "peer_reviewed": w["peer_reviewed"], "document_type": w["doc_type"],
            "peer_review_basis": w["pr_basis"], "study_type": w["study_type"],
            "publication_type": w["pubtype"], "language": w["lang"], "keywords": w["keywords"],
            "identifiers": {"pmid": w["pmid"], "pmcid": w["pmcid"], "arxiv": w["arxiv"], "openalex": w["openalex"]},
            "other_dois": w["other_dois"],
            "abstract_source": w["abstract_source"], "authors_source": w["authors_source"],
            "prisma": {
                "identification": {
                    "search_date": run_date, "search_rule": SEARCH_RULE,
                    "databases": w["dbs"], "n_databases": len(w["dbs"]),
                    "source_records": w["sources"], "keyword_check": "confirmed",
                    "duplicates_merged": len(w["sources"]) - 1,
                },
                # automatic criteria; litreview.prisma combines them with the reviewers' decisions
                "eligibility": {
                    "criteria": f"year >= {MIN_YEAR} AND peer_reviewed",
                    "eligible": w["elig"] is None, "reason": w["elig"],
                },
                "screening": {
                    "title_abstract": "pending", "title_abstract_reason": None,
                    "full_text": "pending", "full_text_reason": None,
                    "reviewers": [], "notes": "",
                },
                "included": None,
            },
        }
        body = w["abstract"] or "_Abstract not available in any source database._"
        rel = f"selected/{fname}" if w["elig"] is None else fname
        (OUT / rel).write_text(f"---\n{y(meta)}\n---\n\n{body}\n")
        index.append({"work_id": w["work_id"], "file": rel, "doi": w["doi"] or "", "year": w["year"] or "",
                      "has_abstract": int(bool(w["abstract"])), "n_authors": len(w["authors"]),
                      "peer_reviewed": int(w["peer_reviewed"]), "document_type": w["doc_type"],
                      "study_type": w["study_type"], "eligible": int(w["elig"] is None)})
    with open(DATA / "articles_index.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(index[0]))
        wr.writeheader()
        wr.writerows(index)
    print(f"wrote {len(works)} files to {OUT.relative_to(ROOT)}/ "
          f"({sum(i['has_abstract'] for i in index)} with abstract, "
          f"{sum(1 for w in works if w['doi'])} with DOI, "
          f"{sum(1 for w in works if w['authors'])} with authors; "
          f"OpenAlex author lookup filled {n_fixed}/{n_need})")
    from collections import Counter
    print(f"peer_reviewed: {sum(w['peer_reviewed'] for w in works)} true / "
          f"{sum(not w['peer_reviewed'] for w in works)} false")
    for k, n in Counter(w["doc_type"] for w in works).most_common():
        print(f"  {k:<20} {n}")


if __name__ == "__main__":
    main()
