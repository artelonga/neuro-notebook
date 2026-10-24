"""AC-4: systematic search of clinical-trial registries for ANY use of optogenetics.

    python3 -m litreview.trials [--refresh]

Unlike the literature search this is not restricted to Alzheimer/Parkinson:
every registered trial that mentions optogenetics (or an optogenetic product /
opsin) is retrieved, then screened (data/trials_screening.csv, human decisions)
and flagged for AD/PD relevance.

Writes data/trials_raw.csv (one row per registry record, union over terms),
data/trials_log.json (per registry x term hit counts) and
data/trials.csv (records joined with screening decisions).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import quote

from .common import DATA, fetch, get_json, qs

# Generic concept terms + named opsins + every optogenetic product known to have
# reached the clinic (registries index product codes, not always "optogenetic").
TRIAL_TERMS = [
    "optogenetic", "optogenetics", "optogenetically", "opto-genetic", "optogenética", "optogénétique",
    "channelrhodopsin", "ChrimsonR", "halorhodopsin", "ChR2", "multi-characteristic opsin", "light-sensitive opsin",
    "GS030", "RST-001", "MCO-010", "sonpiretigene isteparvovec", "BS01", "Bionic Sight",
]
AD_PD = re.compile(r"alzheimer|parkinson|dementia|cognitive impairment", re.I)
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def ctgov(term, refresh):
    out, token = [], None
    while True:
        p = {"query.term": term, "pageSize": 100, "countTotal": "true", "format": "json"}
        if token:
            p["pageToken"] = token
        r = get_json(f"https://clinicaltrials.gov/api/v2/studies?{qs(p)}", refresh=refresh)
        for s in r.get("studies", []):
            ps = s["protocolSection"]
            idm, st = ps["identificationModule"], ps.get("statusModule", {})
            design = ps.get("designModule", {})
            arms = ps.get("armsInterventionsModule", {})
            out.append({
                "registry": "ClinicalTrials.gov", "trial_id": idm["nctId"],
                "title": idm.get("officialTitle") or idm.get("briefTitle", ""),
                "conditions": "; ".join(ps.get("conditionsModule", {}).get("conditions", [])),
                "interventions": "; ".join(f"{i.get('type', '')}: {i.get('name', '')}"
                                           for i in arms.get("interventions", [])),
                "phase": ", ".join(design.get("phases", [])), "study_type": design.get("studyType", ""),
                "status": st.get("overallStatus", ""),
                "start": (st.get("startDateStruct") or {}).get("date", ""),
                "sponsor": ps.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", ""),
                "enrollment": (design.get("enrollmentInfo") or {}).get("count", ""),
                "summary": re.sub(r"\s+", " ", ps.get("descriptionModule", {}).get("briefSummary", ""))[:600],
                "url": f"https://clinicaltrials.gov/study/{idm['nctId']}",
            })
        token = r.get("nextPageToken")
        if not token:
            return r.get("totalCount", len(out)), out


def isrctn(term, refresh):
    xml = fetch(f"https://www.isrctn.com/api/query/format/default?{qs({'q': term, 'limit': 100})}", refresh=refresh)
    root = ET.fromstring(xml)
    ns = {"i": "http://www.67bricks.com/isrctn"}
    out = []
    for t in root.findall("i:fullTrial", ns):
        tid = "ISRCTN" + (t.findtext(".//i:isrctn", "", ns) or "")
        out.append({"registry": "ISRCTN", "trial_id": tid,
                    "title": t.findtext(".//i:scientificTitle", "", ns) or t.findtext(".//i:title", "", ns),
                    "conditions": t.findtext(".//i:condition/i:description", "", ns),
                    "interventions": t.findtext(".//i:intervention/i:description", "", ns)[:300],
                    "phase": t.findtext(".//i:phase", "", ns), "status": t.findtext(".//i:overallStatusOverride", "", ns),
                    "url": f"https://www.isrctn.com/{tid}"})
    return int(root.get("totalCount", len(out))), out


def ctis(term, refresh):
    body = json.dumps({"pagination": {"page": 1, "size": 100},
                       "sort": {"property": "decisionDate", "direction": "DESC"},
                       "searchCriteria": {"containAll": term, "containAny": None, "containNot": None}}).encode()
    r = json.loads(fetch("https://euclinicaltrials.eu/ctis-public-api/search", data=body, refresh=refresh,
                         headers={"Content-Type": "application/json", "User-Agent": BROWSER_UA}))
    out = [{"registry": "EU CTIS", "trial_id": d.get("ctNumber", ""), "title": d.get("ctTitle", ""),
            "conditions": d.get("conditions", ""), "phase": d.get("trialPhase", ""),
            "status": d.get("ctStatus", ""), "sponsor": d.get("sponsor", ""),
            "url": f"https://euclinicaltrials.eu/search-for-clinical-trials/?lang=en&EUCT={d.get('ctNumber', '')}"}
           for d in r.get("data", [])]
    return r["pagination"]["totalRecords"], out


def euctr(term, refresh):
    html = fetch(f"https://www.clinicaltrialsregister.eu/ctr-search/search?query={quote(term)}",
                 refresh=refresh, headers={"User-Agent": BROWSER_UA})
    if "Request Rejected" in html:
        raise RuntimeError("EUCTR rejected the request")
    text = re.sub(r"<[^>]+>", " ", html)
    m = re.search(r"(\d+)\s+result\(s\)\s+found", text)
    ids = sorted(set(re.findall(r"EudraCT Number:\s*(\d{4}-\d{6}-\d{2})", text)))
    out = []
    for tid in ids:
        seg = text[text.index(tid):][:1500]
        title = re.search(r"Full Title:\s*(.+?)\s{2,}", seg)
        cond = re.search(r"Medical condition:\s*(.+?)\s{2,}", seg)
        out.append({"registry": "EUCTR", "trial_id": tid, "title": title.group(1) if title else "",
                    "conditions": cond.group(1) if cond else "",
                    "url": f"https://www.clinicaltrialsregister.eu/ctr-search/search?query={tid}"})
    return int(m.group(1)) if m else 0, out


def ictrp(term, refresh):
    # WHO ICTRP has no public API; the portal's search page is attempted and the
    # registry is reported as "manual" when it is unavailable (see PROTOCOLO.md).
    html = fetch(f"https://trialsearch.who.int/?SearchAll={quote(term)}", refresh=refresh,
                 headers={"User-Agent": BROWSER_UA}, retries=2)
    m = re.search(r"(\d+)\s+records?\s+for", html)
    if not m:
        raise RuntimeError("ICTRP returned no parseable result count")
    return int(m.group(1)), []


REGISTRIES = {
    "ctgov": ("ClinicalTrials.gov (API v2)", ctgov),
    "ctis": ("EU CTIS (EU Clinical Trials Regulation, 2023-)", ctis),
    "euctr": ("EU Clinical Trials Register (EudraCT, legacy)", euctr),
    "isrctn": ("ISRCTN registry", isrctn),
    "ictrp": ("WHO ICTRP (meta-registry: ChiCTR, JPRN, ANZCTR, ReBEC, CTRI, DRKS, ...)", ictrp),
}

COLS = ["registry", "trial_id", "title", "conditions", "interventions", "phase", "study_type", "status",
        "start", "sponsor", "enrollment", "matched_terms", "ad_pd_flag", "summary", "url"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args(argv)
    log, found = {}, {}
    for key, (label, fn) in REGISTRIES.items():
        log[key] = {"registry": label, "terms": {}, "run_at": dt.datetime.now().isoformat(timespec="seconds")}
        print(f"-> {label}", file=sys.stderr, flush=True)
        for term in TRIAL_TERMS:
            try:
                n, recs = fn(term, a.refresh)
            except Exception as e:
                log[key]["terms"][term] = f"failed: {e!r}"
                print(f"   {term}: FAILED {e!r}", file=sys.stderr)
                if key == "ictrp":
                    break  # portal is down; don't hammer it for every term
                continue
            log[key]["terms"][term] = n
            for r in recs:
                k = (r["registry"], r["trial_id"])
                found.setdefault(k, {**{c: "" for c in COLS}, **r, "matched_terms": []})
                found[k]["matched_terms"].append(term)
        hits = {t: n for t, n in log[key]["terms"].items() if isinstance(n, int) and n}
        print(f"   non-zero terms: {hits}", file=sys.stderr)

    rows = []
    for r in found.values():
        r["matched_terms"] = "; ".join(r["matched_terms"])
        r["ad_pd_flag"] = int(bool(AD_PD.search(" ".join(str(r[c]) for c in ("title", "conditions", "summary")))))
        rows.append(r)
    rows.sort(key=lambda r: (r["registry"], r["trial_id"]))
    with open(DATA / "trials_raw.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    # Join with human screening decisions; unseen records are left PENDING.
    scr_path = DATA / "trials_screening.csv"
    decisions = {}
    if scr_path.exists():
        decisions = {(d["registry"], d["trial_id"]): d for d in csv.DictReader(scr_path.open())}
    joined = []
    for r in rows:
        d = decisions.get((r["registry"], r["trial_id"]), {})
        joined.append({**r, "decision": d.get("decision", "PENDING"), "category": d.get("category", ""),
                       "same_trial_as": d.get("same_trial_as", ""), "reason": d.get("reason", "")})
    with open(DATA / "trials.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS + ["decision", "category", "same_trial_as", "reason"])
        w.writeheader()
        w.writerows(joined)
    for key in log:
        log[key]["records"] = sum(1 for r in rows if r["registry"].split()[0] in log[key]["registry"])
    (DATA / "trials_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))
    print(f"{len(rows)} registry records; pending screening: "
          f"{sum(1 for j in joined if j['decision'] == 'PENDING')}", file=sys.stderr)


if __name__ == "__main__":
    main()
