"""PRISMA 2020 flow: the n at every step, the final selection and the diagram.

    python3 -m litreview.prisma

Follows the PRISMA 2020 flow diagram for new systematic reviews that include
searches of databases, registers and other sources (Page et al., BMJ
2021;372:n71). Unit of counting: a *record* before deduplication, a *work*
(= study; its preprint/journal versions are its *reports*) after it.

  Identification  records per database (search_log.json); removed before
                  screening: duplicates, automated keyword re-check failures
                  (rejected), no abstract anywhere (unverifiable)
  Screening       confirmed works; title/abstract and full-text decisions are
                  read from the reviewers' fields in articles/*.md front matter
  Eligibility     year >= MIN_YEAR, then peer_reviewed (common.eligibility),
                  then the reviewers' full-text exclusions; one reason per work
  Included        the rest

Trial registries are a separate question (any optogenetic use, CA-4) and get
their own flow (data/prisma.json "registers").

Writes data/prisma.json (every n), data/prisma_works.csv (one row per unique
work with the step where it left the flow), data/included.csv (final selection)
and data/prisma_flow.svg / data/prisma_flow.en.svg; moves article files so
that articles/selected/ holds exactly the included works.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from html import escape

from .common import DATA, MIN_YEAR, ROOT
from .export import classify, load_records, study_type
from .literature import SOURCES

STUDY_TYPES = ["original-research", "review", "systematic-review", "meta-analysis", "methodology", "other"]
SCREEN_FIELDS = ("title_abstract", "title_abstract_reason", "full_text", "full_text_reason")
MANUAL_DBS = "Scopus, Web of Science, Embase, LILACS/BVS, CNKI, CiNii"


def screening(path):
    """Reviewer decisions from one article's front matter (JSON-quoted YAML scalars)."""
    text = path.read_text().split("\n---", 1)[0]
    out = {}
    for f in SCREEN_FIELDS:
        m = re.search(rf"^\s+{f}: (.*)$", text, re.M)
        out[f] = json.loads(m.group(1)) if m else None
    return out


def flow():
    log = json.loads((DATA / "search_log.json").read_text())
    works = list(csv.DictReader((DATA / "works.csv").open()))
    idx = {r["work_id"]: r for r in csv.DictReader((DATA / "articles_index.csv").open())}
    recs = load_records()

    rows = []
    for w in works:
        i = idx.get(w["work_id"])
        if i:
            stype, scr = i["study_type"], screening(ROOT / "articles" / i["file"])
        else:  # not exported (rejected / unverifiable): classify offline for the breakdown
            group = [recs[s] for s in w["source_ids"].split(" | ") if s in recs]
            stype, scr = study_type(classify(group)[0], group), dict.fromkeys(SCREEN_FIELDS)
        row = {"work_id": w["work_id"], "status": w["status"], "year": w["year"], "title": w["title"],
               "journal": w["journal"], "doi": w["doi"], "pmid": w["pmid"], "study_type": stype,
               "document_type": i["document_type"] if i else "", "peer_reviewed": i["peer_reviewed"] if i else "",
               "n_versions": w["n_versions"], "n_databases": w["n_databases"],
               "databases": " ".join(d for d in SOURCES if w.get(f"in_{d}") == "1"),
               "title_abstract": scr["title_abstract"] or "", "full_text": scr["full_text"] or "",
               "file": i["file"] if i else ""}
        # The first step the work fails decides where it leaves the flow.
        ta, ft = scr["title_abstract"], scr["full_text"]
        if w["status"] == "rejected":
            step, reason = "removed_before_screening", "automation: keyword re-check failed"
        elif w["status"] == "unverifiable":
            step, reason = "removed_before_screening", "other: no abstract in any source"
        elif ta == "exclude":
            step, reason = "title_abstract", scr["title_abstract_reason"] or "unspecified"
        elif ft == "not_retrieved":
            step, reason = "retrieval", "not retrieved"
        elif i["eligible"] != "1":
            step = "eligibility"
            reason = ("before_min_year" if w["year"] and int(w["year"]) < MIN_YEAR else
                      "year_unknown" if not w["year"] else "not_peer_reviewed")
        elif ft == "exclude":
            step, reason = "eligibility", scr["full_text_reason"] or "unspecified"
        else:
            step, reason = "included", ""
        row.update(excluded_at=step if step != "included" else "", reason=reason, included=int(step == "included"))
        rows.append(row)

    db = [{"key": k, "database": v["database"], "n": v["retrieved"]} for k, v in log.items()]
    n_records = sum(d["n"] for d in db)
    conf = [r for r in rows if r["status"] == "confirmed"]
    step = Counter(r["excluded_at"] for r in rows)
    reasons = lambda s: dict(Counter(r["reason"] for r in rows if r["excluded_at"] == s).most_common())
    inc = [r for r in rows if r["included"]]
    st = Counter(r["status"] for r in rows)
    n_sought = len(conf) - step["title_abstract"]
    n_assessed = n_sought - step["retrieval"]
    order = ["before_min_year", "year_unknown", "not_peer_reviewed"]
    elig = dict(sorted(reasons("eligibility").items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else 9))
    # Both automatic reasons at once (reported for transparency; counted once above).
    both = sum(1 for r in conf if r["year"] and int(r["year"]) < MIN_YEAR and r["peer_reviewed"] == "0")

    tl = json.loads((DATA / "trials_log.json").read_text())
    trials = list(csv.DictReader((DATA / "trials.csv").open()))
    t_inc = [t for t in trials if t["decision"] == "include"]
    t_unique = [t for t in t_inc if not t["same_trial_as"]]

    out = {
        "standard": "PRISMA 2020 (Page et al., BMJ 2021;372:n71); search reporting per PRISMA-S",
        "search_date": min(v["run_at"] for v in log.values())[:10],
        "eligibility_criteria": [f"published in {MIN_YEAR} or later", "peer reviewed (journal article or review)"],
        "identification": {
            "databases": db, "records": n_records,
            "databases_not_searched": {"manual (queries ready in RELATORIO.md)": MANUAL_DBS,
                                       "in the template, not used": "Google Scholar, ScienceDirect"},
            "registers_records": sum(v.get("records", 0) for v in tl.values()),
            "unique_works": len(rows),
            "unique_works_by_study_type": {t: sum(1 for r in rows if r["study_type"] == t) for t in STUDY_TYPES},
        },
        "removed_before_screening": {
            "duplicates": n_records - len(rows), "automation_ineligible": st["rejected"],
            "other_reasons_no_abstract": st["unverifiable"],
        },
        "screening": {
            "records_screened": len(conf), "records_excluded": step["title_abstract"],
            "records_excluded_reasons": reasons("title_abstract"),
            "title_abstract_pending": sum(1 for r in conf if r["title_abstract"] in ("", "pending")),
            "reports_sought": n_sought, "reports_not_retrieved": step["retrieval"],
            "reports_assessed": n_assessed, "reports_excluded": step["eligibility"],
            "reports_excluded_reasons": elig, "excluded_for_both_year_and_peer_review": both,
            "full_text_pending": sum(1 for r in inc if r["full_text"] in ("", "pending")),
        },
        "included": {
            "studies": len(inc), "reports": sum(int(r["n_versions"]) for r in inc),
            "by_study_type": {t: sum(1 for r in inc if r["study_type"] == t) for t in STUDY_TYPES},
            "by_year": dict(sorted(Counter(r["year"] for r in inc).items())),
            "in_meta_analysis": None,
        },
        "other_methods": {"websites": 0, "organisations": 0, "citation_searching": 0,
                          "note": "not yet performed (PROTOCOLO.md §7)"},
        "registers": {
            "records": sum(v.get("records", 0) for v in tl.values()),
            "by_registry": {v["registry"]: v.get("records", 0) for v in tl.values()},
            "screened": len(trials), "excluded": len(trials) - len(t_inc),
            "included_records": len(t_inc), "same_trial_duplicates": len(t_inc) - len(t_unique),
            "included_trials": len(t_unique),
            "included_trials_ad_pd": sum(1 for t in t_unique if t["ad_pd_flag"] == "1"),
        },
    }
    assert n_records - out["removed_before_screening"]["duplicates"] - st["rejected"] - st["unverifiable"] == len(conf)
    assert n_assessed - step["eligibility"] == len(inc)
    return out, rows


# --- diagram ---------------------------------------------------------------
L10N = {
    "pt": {
        "num": lambda n: "NA" if n is None else f"{n:,}".replace(",", "."),
        "head_db": "Identificação de novos estudos via bases de dados e registros",
        "head_other": "Identificação de novos estudos via outros métodos",
        "phases": ["Identificação", "Triagem", "Incluídos"],
        "identified": "Registros identificados em:", "databases": "Bases de dados", "manual": "Bases manuais¹",
        "pending": "pendentes", "registers": "Registros de ensaios²", "by_type": "Trabalhos únicos por tipo",
        "types": {"original-research": "Pesquisa original", "review": "Artigos de revisão",
                  "systematic-review": "Revisões sistemáticas", "meta-analysis": "Meta-análises",
                  "methodology": "Artigos de metodologia", "other": "Outros (editorial, livro, …)"},
        "removed": "Registros removidos antes da triagem:", "dup": "Registros duplicados",
        "auto": "Inelegíveis por ferramenta de automação³", "other_r": "Removidos por outros motivos (sem resumo)",
        "screened": "Registros triados", "excluded": "Registros excluídos",
        "ta_pending": "triagem de título/resumo pendente", "sought": "Relatos buscados para recuperação",
        "not_retr": "Relatos não recuperados", "assessed": "Relatos avaliados quanto à elegibilidade",
        "rep_excl": "Relatos excluídos:",
        "reasons": {"before_min_year": f"Publicados antes de {MIN_YEAR}", "year_unknown": "Ano desconhecido",
                    "not_peer_reviewed": "Sem revisão por pares"},
        "o_ident": ["Sites", "Organizações", "Busca por citações"],
        "included": "Novos estudos incluídos na revisão", "reports": "Relatos dos novos estudos incluídos",
        "ft_pending": "texto completo pendente", "meta": "Total de estudos incluídos na meta-análise",
        "meta_rep": "Relatos do total de estudos incluídos na meta-análise",
        "notes": [f"¹ {MANUAL_DBS}: buscas prontas no RELATORIO.md, ainda não executadas.",
                  "  Google Scholar e ScienceDirect não foram buscados (o Scopus cobre o ScienceDirect).",
                  "² Qualquer uso de optogenética (CA-4); seguem fluxo próprio: ver data/prisma.json → registers.",
                  "³ Reverificação local das palavras-chave no título/resumo/palavras-chave (common.matches).",
                  "Estudo = trabalho único; relatos = suas versões (preprint e periódico)."],
    },
    "en": {
        "num": lambda n: "NA" if n is None else f"{n:,}",
        "head_db": "Identification of new studies via databases and registers",
        "head_other": "Identification of new studies via other methods",
        "phases": ["Identification", "Screening", "Included"],
        "identified": "Records identified from:", "databases": "Databases", "manual": "Manual databases¹",
        "pending": "pending", "registers": "Trial registers²", "by_type": "Unique works by type",
        "types": {"original-research": "Original Research", "review": "Review Articles",
                  "systematic-review": "Systematic Reviews", "meta-analysis": "Meta-Analyses",
                  "methodology": "Methodology Articles", "other": "Other (editorial, book, …)"},
        "removed": "Records removed before screening:", "dup": "Duplicate records",
        "auto": "Records marked as ineligible by automation tools³",
        "other_r": "Records removed for other reasons (no abstract)",
        "screened": "Records screened", "excluded": "Records excluded",
        "ta_pending": "title/abstract screening pending", "sought": "Reports sought for retrieval",
        "not_retr": "Reports not retrieved", "assessed": "Reports assessed for eligibility",
        "rep_excl": "Reports excluded:",
        "reasons": {"before_min_year": f"Published before {MIN_YEAR}", "year_unknown": "Year unknown",
                    "not_peer_reviewed": "Not peer-reviewed"},
        "o_ident": ["Websites", "Organisations", "Citation searching"],
        "included": "New studies included in review", "reports": "Reports of new included studies",
        "ft_pending": "full-text review pending", "meta": "Total studies included in meta-analysis",
        "meta_rep": "Reports of total included studies in meta-analysis",
        "notes": [f"¹ {MANUAL_DBS}: queries ready in RELATORIO.md, not yet run.",
                  "  Google Scholar and ScienceDirect were not searched (Scopus covers ScienceDirect).",
                  "² Any optogenetic use (CA-4); reported in a separate flow: see data/prisma.json → registers.",
                  "³ Local keyword re-check on title/abstract/keywords (common.matches).",
                  "Study = unique work; reports = its versions (preprint and journal)."],
    },
}
LINE, PAD, GAP = 15, 8, 26
COLORS = {"orange": "#f6b13a", "grey": "#d9d9d9", "phase": "#a9c4e8", "ink": "#111111", "box": "#ffffff"}


def svg(p, lang):
    t, n = L10N[lang], L10N[lang]["num"]
    idn, rm, sc, inc = p["identification"], p["removed_before_screening"], p["screening"], p["included"]
    ax, aw, bx, bw, cx, cw, dx, dw = 60, 360, 452, 330, 818, 280, 1130, 230
    W = dx + dw + 10
    el, y = [], 54

    def box(x, w, y, lines, fill=COLORS["box"], stroke=True):
        h = PAD * 2 + LINE * len(lines)
        el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
                  + (f' stroke="{COLORS["ink"]}"' if stroke else "") + "/>")
        for k, s in enumerate(lines):
            el.append(f'<text x="{x + w / 2}" y="{y + PAD + LINE * k + 11.5}" text-anchor="middle">{escape(s)}</text>')
        return (x, y, w, h)

    def arrow(x1, y1, x2, y2, mid=None):
        pts = [(x1, y1)] + ([mid] if mid else []) + [(x2, y2)]
        el.append('<polyline fill="none" stroke="#111" marker-end="url(#a)" points="'
                  + " ".join(f"{a},{b}" for a, b in pts) + '"/>')

    def row(left, right, rx=bx, rw=bw, fill=COLORS["box"], lx=ax, lw=aw):
        """Left box with an exclusion box to its right, vertically centred."""
        hl, hr = PAD * 2 + LINE * len(left), PAD * 2 + LINE * len(right)
        top = y + max(0, (hr - hl) / 2)
        L_ = box(lx, lw, top, left, fill)
        R_ = box(rx, rw, top + (hl - hr) / 2, right, fill)
        arrow(lx + lw, top + hl / 2, rx - 2, top + hl / 2)
        return L_, R_, max(hl, hr)

    el.append(f'<rect x="{ax}" y="10" width="{bx + bw - ax}" height="30" rx="8" fill="{COLORS["orange"]}"/>')
    el.append(f'<text x="{(ax + bx + bw) / 2}" y="30" text-anchor="middle">{escape(t["head_db"])}</text>')
    el.append(f'<rect x="{cx}" y="10" width="{dx + dw - cx}" height="30" rx="8" fill="{COLORS["grey"]}"/>')
    el.append(f'<text x="{(cx + dx + dw) / 2}" y="30" text-anchor="middle">{escape(t["head_other"])}</text>')

    # Identification
    ident = [t["identified"], f'{t["databases"]} (n = {n(idn["records"])}):']
    ident += [f'{d["database"]} (n = {n(d["n"])})' for d in idn["databases"]]
    ident += [f'{t["manual"]} (n = NA, {t["pending"]})', f'{t["registers"]} (n = {n(idn["registers_records"])})',
              "", f'{t["by_type"]} (n = {n(idn["unique_works"])}):']
    ident += [f'{t["types"][k]} (n = {n(v)})' for k, v in idn["unique_works_by_study_type"].items()]
    removed = [t["removed"], f'{t["dup"]} (n = {n(rm["duplicates"])})',
               f'{t["auto"]} (n = {n(rm["automation_ineligible"])})',
               f'{t["other_r"]} (n = {n(rm["other_reasons_no_abstract"])})']
    p0 = y
    A1, _, h = row(ident, removed)
    C1 = box(cx, cw, A1[1] + 40, [t["identified"]] + [f"{s} (n = 0)" for s in t["o_ident"]], COLORS["grey"], False)
    phase_ends = [y + h]
    y += h + GAP

    # Screening
    ta_note = [f'({t["ta_pending"]}: n = {n(sc["title_abstract_pending"])})'] if sc["title_abstract_pending"] else []
    A2, _, h = row([t["screened"], f'(n = {n(sc["records_screened"])})'],
                   [t["excluded"], f'(n = {n(sc["records_excluded"])})'] + ta_note
                   + [f"{k} (n = {n(v)})" for k, v in sc["records_excluded_reasons"].items()])
    arrow(ax + aw / 2, A1[1] + A1[3], ax + aw / 2, A2[1] - 2)
    p1 = y - GAP / 2
    y += h + GAP
    A3, _, h = row([t["sought"], f'(n = {n(sc["reports_sought"])})'],
                   [t["not_retr"], f'(n = {n(sc["reports_not_retrieved"])})'])
    arrow(ax + aw / 2, A2[1] + A2[3], ax + aw / 2, A3[1] - 2)
    C3, _, _ = row([t["sought"], "(n = 0)"], [t["not_retr"], "(n = 0)"], dx, dw, COLORS["grey"], cx, cw)
    arrow(cx + cw / 2, C1[1] + C1[3], cx + cw / 2, C3[1] - 2)
    y += h + GAP
    excl = [t["rep_excl"]] + [f'{t["reasons"].get(k, k)} (n = {n(v)})' for k, v in sc["reports_excluded_reasons"].items()]
    A4, _, h = row([t["assessed"], f'(n = {n(sc["reports_assessed"])})'], excl)
    arrow(ax + aw / 2, A3[1] + A3[3], ax + aw / 2, A4[1] - 2)
    C4, _, _ = row([t["assessed"], "(n = 0)"], [t["rep_excl"], "(n = 0)"], dx, dw, COLORS["grey"], cx, cw)
    arrow(cx + cw / 2, C3[1] + C3[3], cx + cw / 2, C4[1] - 2)
    phase_ends.append(y + h)
    y += h + GAP + 10

    # Included
    p2 = y - GAP / 2
    inc_lines = [t["included"], f'(n = {n(inc["studies"])})', t["reports"], f'(n = {n(inc["reports"])})']
    if sc["full_text_pending"]:
        inc_lines.append(f'({t["ft_pending"]}: n = {n(sc["full_text_pending"])})')
    inc_lines += [""] + [f'{t["types"][k]} (n = {n(v)})' for k, v in inc["by_study_type"].items() if v]
    A5 = box(ax, aw, y, inc_lines)
    arrow(ax + aw / 2, A4[1] + A4[3], ax + aw / 2, y - 2)
    arrow(cx + cw / 2, C4[1] + C4[3], ax + aw + 2, y + 30, mid=(cx + cw / 2, y + 30))
    y += A5[3] + GAP
    A6 = box(ax, aw, y, [t["meta"], "(n = NA)", t["meta_rep"], "(n = NA)"])
    arrow(ax + aw / 2, A5[1] + A5[3], ax + aw / 2, y - 2)
    y += A6[3]
    phase_ends.append(y)

    for (top, bot), label in zip([(p0, phase_ends[0]), (p1, phase_ends[1]), (p2, phase_ends[2])], t["phases"]):
        cy = (top + bot) / 2
        el.append(f'<rect x="10" y="{top}" width="30" height="{bot - top}" rx="10" fill="{COLORS["phase"]}"/>')
        el.append(f'<text transform="translate(29,{cy}) rotate(-90)" text-anchor="middle">{escape(label)}</text>')

    y += 24
    for k, s in enumerate(t["notes"] + [f"PRISMA 2020 · {p['search_date']}"]):
        el.append(f'<text x="10" y="{y + k * 15}" font-size="11" fill="#444" xml:space="preserve">{escape(s)}</text>')
    H = y + len(t["notes"]) * 15 + 10
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="Helvetica, Arial, sans-serif" font-size="12" fill="{COLORS["ink"]}">\n'
            '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111"/></marker></defs>\n'
            f'<rect width="{W}" height="{H}" fill="#fff"/>\n' + "\n".join(el) + "\n</svg>\n")


def sync_selected(rows):
    """Keep articles/selected/ equal to the final selection (reviewer exclusions move files out)."""
    idx_path = DATA / "articles_index.csv"
    idx = list(csv.DictReader(idx_path.open()))
    moved = {}
    for r in rows:
        if not r["file"]:
            continue
        name = r["file"].split("/")[-1]
        want = f"selected/{name}" if r["included"] else name
        if want != r["file"]:
            (ROOT / "articles" / r["file"]).rename(ROOT / "articles" / want)
            moved[r["work_id"]] = r["file"] = want
    if moved:
        for i in idx:
            i["file"] = moved.get(i["work_id"], i["file"])
        with open(idx_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(idx[0]))
            w.writeheader()
            w.writerows(idx)
    return len(moved)


def main():
    p, rows = flow()
    n_moved = sync_selected(rows)
    (DATA / "prisma.json").write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n")
    cols = list(rows[0])
    for name, subset in (("prisma_works.csv", rows), ("included.csv", [r for r in rows if r["included"]])):
        with open(DATA / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(subset)
    for lang, suffix in (("pt", ""), ("en", ".en")):
        (DATA / f"prisma_flow{suffix}.svg").write_text(svg(p, lang))
    sc = p["screening"]
    print(f"articles/selected/: {p['included']['studies']} files ({n_moved} moved this run)")
    print(f"identified {p['identification']['records']} records -> {p['identification']['unique_works']} works -> "
          f"screened {sc['records_screened']} -> assessed {sc['reports_assessed']} -> "
          f"included {p['included']['studies']} ({p['included']['reports']} reports)")
    for k, v in sc["reports_excluded_reasons"].items():
        print(f"  excluded at eligibility: {k} = {v}")


if __name__ == "__main__":
    main()
