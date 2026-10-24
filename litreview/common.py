"""Shared pieces: search vocabulary, HTTP with cache/backoff, normalisation.

Everything here is stdlib-only so the pipeline runs on the system Python 3.9.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = DATA / "cache"
CONTACT = os.environ.get("LITREVIEW_MAILTO", "yuri@artelonga.com.br")
UA = f"neuro-notebook-litreview/1.0 (mailto:{CONTACT})"

# ---------------------------------------------------------------------------
# Search vocabulary (see PROTOCOL.md §2 for the rationale of every term)
# ---------------------------------------------------------------------------

# Concept A: optogenetics. Truncated stem "optogenet*" covers EN optogenetic(s),
# optogenetically; PT/ES optogenética/o; IT optogenetica; FR optogénétique
# (diacritics folded); DE Optogenetik/optogenetisch. Hyphenated and the
# "optigenet*" misspelling are added for sensitivity.
OPTO_STEMS = ["optogenet", "opto-genet", "optigenet"]
# Full word forms for engines without truncation (OpenAlex, DOAJ).
OPTO_WORDS = [
    "optogenetic", "optogenetics", "optogenetically", "opto-genetic", "opto-genetics",
    "optigenetic", "optigenetics",
    "optogenética", "optogenético", "optogenetica", "optogenetico",  # pt / es / it
    "optogénétique", "optogenetique",  # fr
    "optogenetik", "optogenetisch",  # de
]
OPTO_NONLATIN = ["оптогенетика", "оптогенетический", "光遗传", "光遺伝", "光遺傳",
                 "オプトジェネティクス", "광유전"]

# Concept B: disease. "alzheimer*" / "parkinson*" are spelled identically in all
# Latin-script languages; truncation covers Alzheimer's, parkinsonism, parkinsonian.
DISEASE_STEMS = ["alzheimer", "parkinson"]
DISEASE_NONLATIN = ["альцгеймер", "паркинсон", "阿尔茨海默", "阿茲海默", "阿兹海默",
                    "帕金森", "アルツハイマー", "パーキンソン", "알츠하이머", "파킨슨"]

_OPTO_RE = re.compile(r"opt[oi]\W?genet|" + "|".join(map(re.escape, OPTO_NONLATIN)), re.I)
_DIS_RE = re.compile(r"alzheimer|parkinson|" + "|".join(map(re.escape, DISEASE_NONLATIN)), re.I)


def fold(text: str) -> str:
    """Lower-case and strip diacritics (optogénétique -> optogenetique)."""
    text = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def matches(title: str, abstract: str, keywords: str = "") -> dict:
    """Local re-check of the inclusion rule on title + abstract + keywords."""
    blob = fold(" ".join([title or "", abstract or "", keywords or ""]))
    return {"opto": bool(_OPTO_RE.search(blob)), "disease": bool(_DIS_RE.search(blob))}


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def fetch(url: str, *, data: bytes | None = None, headers: dict | None = None,
          refresh: bool = False, retries: int = 6, pause: float = 0.4,
          retry_codes=(429, 500, 502, 503, 504)) -> str:
    """GET/POST with on-disk cache and exponential backoff on 429/5xx."""
    key = hashlib.sha256((url + (data or b"").decode("utf-8", "ignore")).encode()).hexdigest()[:24]
    path = CACHE / f"{key}.txt"
    if path.exists() and not refresh:
        return path.read_text()
    hdrs = {"User-Agent": UA, "Accept": "*/*"}
    hdrs.update(headers or {})
    delay = 2.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs)
            with urllib.request.urlopen(req, timeout=90) as resp:
                body = resp.read().decode("utf-8", "replace")
            CACHE.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
            time.sleep(pause)
            return body
        except urllib.error.HTTPError as e:
            if e.code in retry_codes and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise RuntimeError("unreachable")


def get_json(url: str, **kw):
    return json.loads(fetch(url, **kw))


def qs(params: dict) -> str:
    return urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


# ---------------------------------------------------------------------------
# Record normalisation
# ---------------------------------------------------------------------------

def norm_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip().lower()
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi or None


def norm_title(title: str | None) -> str | None:
    t = re.sub(r"[^a-z0-9]+", "", fold(re.sub(r"<[^>]+>", "", title or "")))
    return t if len(t) >= 25 else None


def record(source: str, source_id: str, *, title: str = "", abstract: str = "",
           keywords: str = "", year=None, doi=None, pmid=None, pmcid=None,
           arxiv=None, journal: str = "", pubtype: str = "", lang: str = "",
           authors=None) -> dict:
    m = matches(title, abstract, keywords)
    abstract = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", abstract or "")).strip()
    return {
        "source": source, "source_id": str(source_id),
        "doi": norm_doi(doi), "pmid": str(pmid) if pmid else None,
        "pmcid": (pmcid or "").upper() or None, "arxiv": arxiv or None,
        "title": re.sub(r"\s+", " ", title or "").strip(),
        "year": int(year) if str(year or "").isdigit() else None,
        "journal": journal or "", "pubtype": pubtype or "", "lang": lang or "",
        "has_abstract": bool(abstract),
        "abstract": abstract, "keywords": (keywords or "").strip(),
        "authors": [a for a in (authors or []) if a],
        "verified": m["opto"] and m["disease"],
    }
