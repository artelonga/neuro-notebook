"""AC-2: run the bibliographic search in every programmatic database.

    python3 -m litreview.literature [--refresh] [--only pubmed,epmc,...]

Writes data/raw/<source>.jsonl (one normalised record per line) and
data/search_log.json (exact query, API hit count, records retrieved, timestamp).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import quote

from .common import DATA, DISEASE_STEMS, OPTO_STEMS, OPTO_WORDS, fetch, get_json, qs, record

RAW = DATA / "raw"


# ---------------------------------------------------------------------------
# PubMed (NCBI E-utilities)
# ---------------------------------------------------------------------------
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _pubmed_ids(term: str, refresh: bool) -> tuple[int, list]:
    p = {"db": "pubmed", "term": term, "retmode": "json", "retmax": 9999}
    if os.environ.get("NCBI_API_KEY"):
        p["api_key"] = os.environ["NCBI_API_KEY"]
    r = get_json(f"{EUTILS}/esearch.fcgi?{qs(p)}", refresh=refresh)["esearchresult"]
    return int(r["count"]), r["idlist"]


def pubmed_query() -> str:
    def block(stems, tags=("tiab", "ot")):
        return " OR ".join(f"{s}*[{t}]" for s in stems for t in tags)
    return f"({block(OPTO_STEMS)}) AND ({block(DISEASE_STEMS)})"


def pubmed(refresh=False):
    q = pubmed_query()
    count, ids = _pubmed_ids(q, refresh)
    recs = []
    for i in range(0, len(ids), 200):
        xml = fetch(f"{EUTILS}/efetch.fcgi?{qs({'db': 'pubmed', 'id': ','.join(ids[i:i+200]), 'retmode': 'xml'})}",
                    refresh=refresh)
        for art in ET.fromstring(xml).iter("PubmedArticle"):
            pmid = art.findtext(".//MedlineCitation/PMID")
            title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
            abstract = " ".join((f"{a.get('Label')}: " if a.get("Label") else "") + "".join(a.itertext())
                                for a in art.iter("AbstractText"))
            authors = [au.findtext("CollectiveName") or
                       " ".join(x for x in (au.findtext("ForeName"), au.findtext("LastName")) if x)
                       for au in art.findall(".//AuthorList/Author")]
            kws = "; ".join("".join(k.itertext()) for k in art.iter("Keyword"))
            # Only the article's own ids; ReferenceList also contains <ArticleId>s.
            ids_ = {a.get("IdType"): a.text for a in art.findall("PubmedData/ArticleIdList/ArticleId")}
            year = art.findtext(".//JournalIssue/PubDate/Year") or (art.findtext(".//JournalIssue/PubDate/MedlineDate") or "")[:4]
            ptypes = "; ".join(p.text or "" for p in art.iter("PublicationType"))
            recs.append(record("pubmed", pmid, title=title, abstract=abstract, keywords=kws, year=year,
                               doi=ids_.get("doi"), pmid=pmid, pmcid=ids_.get("pmc"),
                               journal=art.findtext(".//Journal/Title") or "", pubtype=ptypes,
                               lang=art.findtext(".//Language") or "", authors=authors))
    # Sensitivity check (count only): controlled vocabulary instead of keywords.
    mesh_q = ('"Optogenetics"[Mesh] AND ("Alzheimer Disease"[Mesh] OR "Parkinson Disease"[Mesh] '
              'OR "Parkinsonian Disorders"[Mesh])')
    mesh_n, _ = _pubmed_ids(mesh_q, refresh)
    return {"query": q, "hits": count, "records": recs,
            "sensitivity": {"MeSH-only query": {"query": mesh_q, "hits": mesh_n}}}


# ---------------------------------------------------------------------------
# Europe PMC (includes PubMed, PMC, Agricola, patents excluded, + preprints)
# ---------------------------------------------------------------------------
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def epmc_query() -> str:
    def block(stems):
        return " OR ".join(f'{f}:"{s}*"' if "-" in s else f"{f}:{s}*"
                           for s in stems for f in ("TITLE_ABS", "KW"))
    return f"({block(OPTO_STEMS)}) AND ({block(DISEASE_STEMS)})"


def epmc(refresh=False):
    q = epmc_query()
    recs, cursor, hits = [], "*", 0
    while True:
        r = get_json(f"{EPMC}?{qs({'query': q, 'format': 'json', 'resultType': 'core', 'pageSize': 250, 'cursorMark': cursor})}",
                     refresh=refresh)
        hits = r["hitCount"]
        for it in r["resultList"]["result"]:
            kws = "; ".join((it.get("keywordList") or {}).get("keyword", []))
            ptypes = "; ".join((it.get("pubTypeList") or {}).get("pubType", []))
            recs.append(record("epmc", f"{it.get('source')}:{it.get('id')}", title=it.get("title", ""),
                               abstract=it.get("abstractText", ""), keywords=kws, year=it.get("pubYear"),
                               doi=it.get("doi"), pmid=it.get("pmid"), pmcid=it.get("pmcid"),
                               journal=(it.get("journalInfo") or {}).get("journal", {}).get("title", "")
                               or it.get("bookOrReportDetails", {}).get("publisher", ""),
                               pubtype=f"[{it.get('source')}] {ptypes}", lang=it.get("language", ""),
                               authors=[a.strip() for a in (it.get("authorString") or "").rstrip(".").split(",")]))
        nxt = r.get("nextCursorMark")
        if not r["resultList"]["result"] or nxt == cursor:
            break
        cursor = nxt
    full_q = "(optogenet* OR \"opto-genet*\" OR optigenet*) AND (alzheimer* OR parkinson*)"
    full_n = get_json(f"{EPMC}?{qs({'query': full_q, 'format': 'json', 'pageSize': 1})}", refresh=refresh)["hitCount"]
    return {"query": q, "hits": hits, "records": recs,
            "sensitivity": {"all fields incl. full text": {"query": full_q, "hits": full_n}}}


# ---------------------------------------------------------------------------
# OpenAlex (title_and_abstract.search: stemmed, no wildcards -> enumerate forms)
# ---------------------------------------------------------------------------

def _oa_or(terms):
    return "(" + " OR ".join(f'"{t}"' if "-" in t else t for t in terms) + ")"


OA_DISEASE_LATIN = ["alzheimer", "parkinson", "parkinsonism", "parkinsonian"]
# Non-Latin scripts are paired within the same language (opto terms, disease terms).
OA_NONLATIN = [
    (["光遗传", "光遺傳"], ["阿尔茨海默", "阿茲海默", "阿兹海默", "帕金森"]),  # zh
    (["光遺伝", "オプトジェネティクス"], ["アルツハイマー", "パーキンソン"]),  # ja
    (["оптогенетика", "оптогенетический"], ["альцгеймер", "паркинсон"]),  # ru
    (["광유전"], ["알츠하이머", "파킨슨"]),  # ko
]


def openalex_subqueries() -> list:
    """OpenAlex throttles searches with >5 boolean operators, so the logical
    query (any opto form) AND (any disease form) is split into sub-queries of
    <=5 operators each; results are unioned on the OpenAlex work id."""
    subs = []
    for i in range(0, len(OPTO_WORDS), 2):
        subs.append(f"{_oa_or(OPTO_WORDS[i:i+2])} AND {_oa_or(OA_DISEASE_LATIN)}")
    for opto, dis in OA_NONLATIN:
        subs.append(f"{_oa_or(opto)} AND {_oa_or(dis)}")
        subs.append(f"{_oa_or(opto)} AND {_oa_or(OA_DISEASE_LATIN)}")
    return subs


def openalex_query() -> str:
    return " ∪ ".join(f"[{s}]" for s in openalex_subqueries())


def _oa_abstract(inv):
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


def openalex(refresh=False):
    sel = "id,doi,title,publication_year,ids,abstract_inverted_index,primary_location,type,language,keywords"
    seen, recs, per_sub = set(), [], {}
    for sub in openalex_subqueries():
        base = {"filter": f"title_and_abstract.search:{sub}", "per-page": 200, "select": sel}
        if os.environ.get("OPENALEX_API_KEY"):
            base["api_key"] = os.environ["OPENALEX_API_KEY"]
        recs_sub = _openalex_pages(base, refresh)
        per_sub[sub] = len(recs_sub)
        for w in recs_sub:
            if w["id"] in seen:
                continue
            seen.add(w["id"])
            recs.append(w)
    out = []
    for w in recs:
        ids = w.get("ids") or {}
        pmid = (ids.get("pmid") or "").rsplit("/", 1)[-1] or None
        pmcid = (ids.get("pmcid") or "").rsplit("/", 1)[-1] or None
        src = ((w.get("primary_location") or {}).get("source") or {})
        kws = "; ".join(k.get("display_name", "") for k in w.get("keywords") or [])
        out.append(record("openalex", w["id"].rsplit("/", 1)[-1], title=w.get("title") or "",
                          abstract=_oa_abstract(w.get("abstract_inverted_index")), keywords=kws,
                          year=w.get("publication_year"), doi=w.get("doi"), pmid=pmid, pmcid=pmcid,
                          journal=src.get("display_name") or "", pubtype=w.get("type") or "",
                          lang=w.get("language") or ""))
    return {"query": "title_and_abstract.search, union of: " + openalex_query(), "hits": len(out),
            "records": out, "sensitivity": {"hits per sub-query": per_sub}}


def _openalex_pages(base, refresh):
    # Basic page= paging (cursor paging needs an API key; page= is fine <10k hits).
    works, page = [], 1
    while True:
        r = get_json(f"https://api.openalex.org/works?{qs({**base, 'page': page})}", refresh=refresh, pause=1.0)
        works.extend(r["results"])
        if not r["results"] or len(works) >= r["meta"]["count"]:
            return works
        page += 1


# ---------------------------------------------------------------------------
# Semantic Scholar (bulk search: title + abstract, supports prefix* and |)
# ---------------------------------------------------------------------------

def s2_query() -> str:
    opto = " | ".join(f'"{s}*"' if "-" in s else f"{s}*" for s in OPTO_STEMS)
    dis = " | ".join(f"{s}*" for s in DISEASE_STEMS)
    return f"({opto}) + ({dis})"


def semanticscholar(refresh=False):
    q = s2_query()
    hdr = {"x-api-key": os.environ["S2_API_KEY"]} if os.environ.get("S2_API_KEY") else {}
    fields = "title,abstract,year,externalIds,venue,publicationTypes"
    recs, token, hits = [], None, 0
    while True:
        p = {"query": q, "fields": fields}
        if token:
            p["token"] = token
        r = get_json(f"https://api.semanticscholar.org/graph/v1/paper/search/bulk?{qs(p)}",
                     headers=hdr, refresh=refresh, retries=9, pause=1.5)
        hits = r.get("total", hits)
        for it in r.get("data") or []:
            ex = it.get("externalIds") or {}
            recs.append(record("s2", it["paperId"], title=it.get("title") or "", abstract=it.get("abstract") or "",
                               year=it.get("year"), doi=ex.get("DOI"), pmid=ex.get("PubMed"),
                               pmcid=("PMC" + str(ex["PubMedCentral"])) if ex.get("PubMedCentral") else None,
                               arxiv=ex.get("ArXiv"), journal=it.get("venue") or "",
                               pubtype="; ".join(it.get("publicationTypes") or [])))
        token = r.get("token")
        if not token:
            break
    return {"query": q, "hits": hits, "records": recs}


# ---------------------------------------------------------------------------
# arXiv (q-bio.NC etc.; ti/abs fields, trailing wildcard)
# ---------------------------------------------------------------------------
ATOM = {"a": "http://www.w3.org/2005/Atom"}


def arxiv_query() -> str:
    opto = " OR ".join(f"{f}:{s}*" for s in ("optogenet", "optigenet") for f in ("ti", "abs"))
    dis = " OR ".join(f"{f}:{s}*" for s in DISEASE_STEMS for f in ("ti", "abs"))
    return f"({opto}) AND ({dis})"


def arxiv(refresh=False):
    q = arxiv_query()
    recs, start = [], 0
    while True:
        xml = fetch(f"https://export.arxiv.org/api/query?{qs({'search_query': q, 'start': start, 'max_results': 200})}",
                    refresh=refresh, pause=3.0)
        entries = ET.fromstring(xml).findall("a:entry", ATOM)
        for e in entries:
            aid = re.sub(r"v\d+$", "", e.findtext("a:id", "", ATOM).rsplit("/abs/", 1)[-1])
            doi = e.findtext("{http://arxiv.org/schemas/atom}doi")
            recs.append(record("arxiv", aid, title=e.findtext("a:title", "", ATOM),
                               abstract=e.findtext("a:summary", "", ATOM),
                               year=e.findtext("a:published", "", ATOM)[:4], doi=doi or f"10.48550/arxiv.{aid}",
                               arxiv=aid, journal="arXiv", pubtype="preprint",
                               authors=[a.findtext("a:name", "", ATOM) for a in e.findall("a:author", ATOM)]))
        if len(entries) < 200:
            break
        start += 200
    # arXiv's opensearch:totalResults is unreliable; hits = records retrieved.
    return {"query": q, "hits": len(recs), "records": recs}


# ---------------------------------------------------------------------------
# DOAJ (open-access journals; Lucene without wildcards)
# ---------------------------------------------------------------------------

def doaj_query() -> str:
    opto = " OR ".join(f'"{t}"' if "-" in t else t for t in OPTO_WORDS)
    dis = " OR ".join(DISEASE_STEMS + ["alzheimers", "parkinsons", "parkinsonism", "parkinsonian"])
    fields = ("bibjson.title", "bibjson.abstract", "bibjson.keywords")
    a = " OR ".join(f"{f}:({opto})" for f in fields)
    b = " OR ".join(f"{f}:({dis})" for f in fields)
    return f"({a}) AND ({b})"


def doaj(refresh=False):
    q = doaj_query()
    recs, page, hits = [], 1, 0
    while True:
        r = get_json(f"https://doaj.org/api/search/articles/{quote(q, safe='')}?{qs({'page': page, 'pageSize': 100})}",
                     refresh=refresh)
        hits = r["total"]
        for it in r["results"]:
            b = it["bibjson"]
            ids = {i.get("type"): i.get("id") for i in b.get("identifier", [])}
            recs.append(record("doaj", it["id"], title=b.get("title", ""), abstract=b.get("abstract", ""),
                               keywords="; ".join(b.get("keywords", [])), year=b.get("year"), doi=ids.get("doi"),
                               journal=(b.get("journal") or {}).get("title", ""), pubtype="article",
                               lang=",".join((b.get("journal") or {}).get("language", [])),
                               authors=[a.get("name", "") for a in b.get("author", [])]))
        if page * 100 >= hits:
            break
        page += 1
    return {"query": q, "hits": hits, "records": recs}


SOURCES = {
    "pubmed": ("PubMed / MEDLINE", pubmed),
    "epmc": ("Europe PMC (incl. preprints)", epmc),
    "openalex": ("OpenAlex", openalex),
    "s2": ("Semantic Scholar", semanticscholar),
    "doaj": ("DOAJ", doaj),
    "arxiv": ("arXiv", arxiv),
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true", help="ignore HTTP cache")
    ap.add_argument("--only", help="comma-separated subset of: " + ",".join(SOURCES))
    a = ap.parse_args(argv)
    RAW.mkdir(parents=True, exist_ok=True)
    log_path = DATA / "search_log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {}
    for key, (label, fn) in SOURCES.items():
        if a.only and key not in a.only.split(","):
            continue
        print(f"-> {label} ...", file=sys.stderr, flush=True)
        try:
            res = fn(refresh=a.refresh)
        except Exception as e:  # keep going; failure is logged and reported
            print(f"   FAILED: {e!r}", file=sys.stderr)
            log[key] = {"database": label, "status": "failed", "error": repr(e),
                        "run_at": dt.datetime.now().isoformat(timespec="seconds")}
            continue
        with open(RAW / f"{key}.jsonl", "w") as f:
            for r in res["records"]:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        log[key] = {"database": label, "status": "ok", "query": res["query"], "hits": res["hits"],
                    "retrieved": len(res["records"]),
                    "verified": sum(r["verified"] for r in res["records"]),
                    "sensitivity": res.get("sensitivity", {}),
                    "run_at": dt.datetime.now().isoformat(timespec="seconds")}
        print(f"   hits={res['hits']} retrieved={len(res['records'])} "
              f"verified={log[key]['verified']}", file=sys.stderr)
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
