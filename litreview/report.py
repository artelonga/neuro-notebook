"""Render RELATORIO.md (pt-BR) from the data/ outputs (no network).

    python3 -m litreview.report
"""
from __future__ import annotations

import csv
import json
from collections import Counter

from .common import DATA, ROOT
from .literature import SOURCES
from .trials import REGISTRIES, TRIAL_TERMS

LICENSED = [
    ("Scopus", "API Elsevier (chave institucional)",
     'TITLE-ABS-KEY(optogenet* OR "opto-genet*" OR optigenet*) AND TITLE-ABS-KEY(alzheimer* OR parkinson*)'),
    ("Web of Science Core Collection", "API WoS Starter/Expanded (chave Clarivate)",
     'TS=(optogenet* OR "opto-genet*" OR optigenet*) AND TS=(alzheimer* OR parkinson*)'),
    ("Embase", "Ovid/Elsevier (licença; sem API aberta)",
     "(optogenet* OR 'opto-genet*' OR optigenet*):ti,ab,kw AND (alzheimer* OR parkinson*):ti,ab,kw"),
    ("LILACS / BVS (pt/es)", "Só web (bloqueio a robôs; exportar CSV)",
     "(tw:(optogenet* OR optogenétic* OR optogenétic*)) AND (tw:(alzheimer* OR parkinson*))"),
    ("CNKI (zh)", "Só web (licença)", "SU=('光遗传'+'光遺傳') AND SU=('阿尔茨海默'+'帕金森')"),
    ("CiNii / J-STAGE (ja)", "API OpenSearch do CiNii (gratuita)", "光遺伝 OR オプトジェネティクス AND (アルツハイマー OR パーキンソン)"),
]

# Display labels for values stored in English in the data/ files.
CATEGORY_PT = {
    "false positive": "falso positivo",
    "interventional: optogenetic gene therapy": "tratamento: terapia gênica optogenética",
    "interventional follow-up: optogenetic gene therapy (long-term safety)":
        "seguimento de tratamento: terapia gênica optogenética (segurança de longo prazo)",
    "observational: optogenetics-enabling (candidate selection)":
        "observacional: preparação para optogenética (seleção de candidatos)",
}
SENSITIVITY_PT = {
    "MeSH-only query": "busca só com MeSH",
    "all fields incl. full text": "todos os campos, incluindo texto completo",
}
STATUS_PT = {"ok": "ok", "failed": "falhou"}


def num(n):
    """Integer with pt-BR thousands separator (2167 -> 2.167); blanks pass through."""
    if n in ("", None):
        return ""
    return f"{int(n):,}".replace(",", ".")


def pct(s):
    """Percentage string with pt-BR decimal comma (59.6% -> 59,6%)."""
    return str(s).replace(".", ",")


def table(rows, cols, header=None):
    out = ["| " + " | ".join(header or cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
    return "\n".join(out)


def main():
    log = json.loads((DATA / "search_log.json").read_text())
    counts = list(csv.DictReader((DATA / "counts.csv").open()))
    overlap = list(csv.reader((DATA / "overlap_matrix.csv").open()))
    works = list(csv.DictReader((DATA / "works.csv").open()))
    tlog = json.loads((DATA / "trials_log.json").read_text())
    trials = list(csv.DictReader((DATA / "trials.csv").open()))

    tot = counts[-1]
    n_rec, n_works = int(tot["retrieved"]), int(tot["works"])
    conf = [w for w in works if w["status"] == "confirmed"]
    multi = sum(1 for w in conf if int(w["n_versions"]) > 1)
    runs = sorted(v["run_at"] for v in log.values() if "run_at" in v)
    L = []
    L.append("# Optogenética × Alzheimer/Parkinson: relatório da busca\n")
    L.append(f"_Gerado por `python3 -m litreview.report`. Buscas executadas em {runs[0][:10]} "
             f"(última em {runs[-1]}). Protocolo: [PROTOCOLO.md](PROTOCOLO.md)._\n")

    # --- headline -------------------------------------------------------
    L.append("## Números principais\n")
    L.append(f"- **{num(n_rec)}** registros coletados em **{len(log)}** bases consultadas por código")
    L.append(f"- **{num(n_works)}** trabalhos únicos depois da deduplicação entre bases "
             f"({num(n_rec - n_works)} registros duplicados removidos)")
    L.append(f"- **{num(tot['confirmed'])} trabalhos únicos atendem à regra de inclusão** (palavras-chave "
             f"reconferidas no título, resumo e palavras-chave); {num(tot['unverifiable'])} não verificáveis "
             f"(sem resumo) e {num(tot['rejected'])} rejeitados como falsos positivos dos buscadores")
    inc = [t for t in trials if t["decision"] == "include"]
    inc_unique = [t for t in inc if not t["same_trial_as"]]
    inc_int = [t for t in inc_unique if t["category"].startswith("interventional:")]
    L.append(f"- Registros de ensaios clínicos: **{num(len(trials))}** registros → **{num(len(inc))}** sobre "
             f"optogenética → **{num(len(inc_int))} ensaios optogenéticos de tratamento distintos**, "
             f"**{num(sum(int(t['ad_pd_flag']) for t in inc))} em Alzheimer ou Parkinson**\n")

    # --- AC -------------------------------------------------------------
    L.append("## Critérios de aceitação\n")
    ok_dbs = [k for k, v in log.items() if v.get("status") == "ok"]
    L.append(table([
        {"ac": "CA-1", "what": "Lista de bases pesquisáveis, consultadas por código sempre que possível",
         "st": f"✅ {len(ok_dbs)} bases de literatura e {len(REGISTRIES)} registros de ensaios consultados por API; "
               f"{len(LICENSED)} bases licenciadas ou só web documentadas com buscas prontas"},
        {"ac": "CA-2", "what": "Busca quantitativa, com método explicado (optogenética E (alzheimer OU parkinson), "
                               "em vários idiomas)",
         "st": "✅ busca exata e número de resultados por base abaixo e em `data/search_log.json`"},
        {"ac": "CA-3", "what": "Contagem por base, exclusivos de cada base, total sem repetição, fácil de somar",
         "st": "✅ `data/counts.csv`, `data/overlap_matrix.csv`, `data/works.csv` (coluna 0/1 por base)"},
        {"ac": "CA-4", "what": "Busca sistemática em registros de ensaios clínicos para qualquer uso de optogenética",
         "st": ("✅ " if all(isinstance(n, int) for v in tlog.values() for n in v["terms"].values())
                else "⚠️ parcial: um registro falhou na execução (ver tabela; o WHO ICTRP cobre ChiCTR, JPRN, "
                     "ANZCTR, ReBEC, CTRI e DRKS); precisa ser refeito ou exportado manualmente. ")
               + "Decisões de triagem em `data/trials.csv`"},
    ], ["ac", "what", "st"], ["CA", "Critério", "Situação"]))
    L.append("")

    # --- AC-2/3 results --------------------------------------------------
    L.append("## Literatura: resultados por base\n")
    L.append("*Resultados* (`api_hits`) = número informado pela API da base; *Confirmados* (`confirmed`) = "
             "trabalhos cujo título/resumo/palavras-chave de fato contêm os dois conceitos; *Exclusivos* "
             "(`unique_confirmed`) = trabalhos confirmados encontrados **só** naquela base; *Participação* "
             "(`share_of_total_confirmed`) = fração de todos os trabalhos únicos confirmados coberta pela base.\n")
    count_rows = []
    for c in counts:
        r = {k: num(c[k]) for k in ("api_hits", "retrieved", "confirmed", "unverifiable", "rejected",
                                     "unique_confirmed")}
        r["database"] = "TOTAL (sem repetição)" if c["key"] == "total" else c["database"]
        r["share_of_total_confirmed"] = pct(c["share_of_total_confirmed"])
        count_rows.append(r)
    L.append(table(count_rows, ["database", "api_hits", "retrieved", "confirmed", "unverifiable", "rejected",
                                "unique_confirmed", "share_of_total_confirmed"],
                   ["Base", "Resultados", "Coletados", "Confirmados", "Não verificáveis", "Rejeitados",
                    "Exclusivos", "Participação"]))
    L.append(f"\nAs versões preprint e de periódico do mesmo estudo contam como um só trabalho "
             f"({num(multi)} trabalhos confirmados unem mais de 1 DOI; ver `n_versions`).\n")
    L.append("### Matriz de sobreposição (trabalhos confirmados presentes nas duas bases)\n")
    hdr = overlap[0]
    L.append(table([dict(zip(hdr, [r[0]] + [num(x) for x in r[1:]])) for r in overlap[1:]], hdr, [""] + hdr[1:]))
    L.append("")
    L.append("### Fluxo (PRISMA 2020, etapa de identificação)\n")
    L.append("```")
    L.append(f"Registros identificados nas bases                n = {num(n_rec)}")
    for c in counts[:-1]:
        L.append(f"  {c['database']:<46} n = {num(c['retrieved'])}")
    L.append(f"Registros duplicados removidos                   n = {num(n_rec - n_works)}")
    L.append(f"Trabalhos únicos triados (palavras-chave)        n = {num(n_works)}")
    L.append(f"  excluídos: conceito ausente em TI/AB/KW        n = {num(tot['rejected'])}")
    L.append(f"  aguardando conferência manual: sem resumo      n = {num(tot['unverifiable'])}")
    L.append(f"Trabalhos que atendem à regra de inclusão        n = {num(tot['confirmed'])}")
    L.append("```\n")
    yrs = Counter(w["year"] for w in conf if w["year"])
    L.append("Trabalhos confirmados por ano: " + ", ".join(f"{y}: {num(yrs[y])}" for y in sorted(yrs)) + "\n")

    L.append("### Buscas executadas (texto exato)\n")
    for k, v in log.items():
        st = STATUS_PT.get(v.get("status"), v.get("status"))
        L.append(f"**{v['database']}** — {st}, executada em {v.get('run_at')}\n")
        L.append(f"```\n{v.get('query', v.get('error'))}\n```")
        for name, s in (v.get("sensitivity") or {}).items():
            if isinstance(s, dict) and "hits" in s:
                L.append(f"- sensibilidade — {SENSITIVITY_PT.get(name, name)}: `{s['query']}` → "
                         f"{num(s['hits'])} resultados")
        L.append("")
    L.append("### Bases não consultadas por código (licença / bloqueio a robôs)\n")
    L.append("Faça estas buscas manualmente, exporte os resultados em RIS/CSV para `data/manual/` e "
             "inclua-os na deduplicação (ver README).\n")
    L.append(table([{"db": a, "acc": b, "q": f"`{c}`"} for a, b, c in LICENSED], ["db", "acc", "q"],
                   ["Base", "Acesso", "Busca"]))
    L.append("")

    # --- article database & peer review ---------------------------------
    idx_path = DATA / "articles_index.csv"
    if idx_path.exists():
        idx = list(csv.DictReader(idx_path.open()))
        n, pr = len(idx), sum(int(r["peer_reviewed"]) for r in idx)
        L.append("## Base de artigos e revisão por pares\n")
        L.append(f"`articles/` tem um arquivo Markdown para cada trabalho confirmado ({num(n)}): cabeçalho YAML "
                 f"(título, DOI, autores, identificadores, trilha de identificação PRISMA e campos de triagem "
                 f"ainda vazios) e o resumo como corpo. Os trabalhos com revisão por pares ficam em "
                 f"`articles/peer_reviewed/`; os demais ficam direto em `articles/`. Índice: "
                 f"`data/articles_index.csv`. {num(sum(int(r['has_abstract']) for r in idx))} têm resumo e "
                 f"{num(sum(1 for r in idx if r['doi']))} têm DOI.\n")
        L.append(f"**{num(pr)} dos {num(n)} trabalhos ({pr / n:.0%}) passaram por revisão por pares** "
                 f"(`peer_reviewed: true`).\n")
        pr_types = {"journal-article", "review"}
        labels = {"journal-article": "Artigo de periódico", "review": "Revisão", "preprint": "Preprint",
                  "thesis": "Tese / dissertação",
                  "conference-abstract": "Resumo de congresso (suplemento de periódico)",
                  "conference-paper": "Trabalho completo de congresso", "unknown": "Tipo desconhecido",
                  "editorial-or-news": "Editorial / notícia / comentário", "book": "Livro ou capítulo",
                  "other": "Outros (dataset, relatório)"}
        L.append(table([{"t": labels.get(k, k), "n": num(v), "p": str(k in pr_types).lower()}
                        for k, v in Counter(r["document_type"] for r in idx).most_common()],
                       ["t", "n", "p"], ["Tipo de documento", "Trabalhos", "`peer_reviewed`"]))
        L.append("")
        L.append("Como é decidido: nenhuma base informa diretamente se houve revisão por pares, então isso é "
                 "inferido do tipo de publicação e do veículo.\n")
        L.append("- A ordem de confiança é PubMed > Europe PMC > DOAJ (só lista periódicos com revisão por pares) "
                 "> OpenAlex (consultado pelo DOI) > Semantic Scholar. A evidência usada para cada trabalho "
                 "fica no campo `peer_review_basis`.")
        L.append("- O trabalho conta como revisado se qualquer versão dele saiu em periódico como artigo ou "
                 "revisão. Um preprint unido à versão publicada é, portanto, `true`.")
        L.append("- Preprints são reconhecidos pelo prefixo do DOI ou pelo nome do servidor (bioRxiv, incluindo "
                 "`10.64898`, medRxiv, Research Square, SSRN etc.).")
        L.append("- Resumos de congresso são reconhecidos por DOIs de suplemento e títulos numerados como "
                 "\"P1‐172: …\", porque o OpenAlex e o Semantic Scholar costumam classificá-los como artigos.\n")
        L.append("Ressalvas:\n")
        L.append("- `true` não é juízo de qualidade; alguns veículos são questionáveis.")
        L.append("- Trabalhos completos de anais IEEE/EMBC costumam ter revisão, mas aqui são marcados `false`, "
                 "por cautela.")
        L.append("- Os trabalhos `unknown` (em geral teses ou itens em outros idiomas sem DOI) ficam `false`.")
        L.append("- A deduplicação por título pode falhar com títulos corrompidos, por exemplo \"Aβ\" escrito "
                 "como \"Ab\" ou \"A b\". Vale conferir isso na triagem.\n")

    # --- AC-4 ------------------------------------------------------------
    L.append("## Registros de ensaios clínicos: qualquer uso de optogenética\n")
    L.append("Termos de busca (cada um buscado separadamente, resultados unidos): "
             + ", ".join(f"`{t}`" for t in TRIAL_TERMS) + "\n")
    rows = []
    for k, v in tlog.items():
        ok = {t: n for t, n in v["terms"].items() if isinstance(n, int)}
        failed = [t for t, n in v["terms"].items() if not isinstance(n, int)]
        status = v["terms"][failed[0]][:60].replace("failed:", "falhou:", 1) if failed else "ok"
        rows.append({"r": v["registry"], "h": ", ".join(f"{t}: {num(n)}" for t, n in ok.items() if n) or "0",
                     "n": num(v.get("records", "")),
                     "i": num(sum(1 for t in trials
                                  if t["decision"] == "include" and t["registry"].split()[0] in v["registry"])),
                     "s": status})
    L.append(table(rows, ["r", "h", "n", "i", "s"],
                   ["Registro", "Termos com resultados", "Registros", "Incluídos", "Situação"]))
    L.append("")
    cat = Counter(t["category"] for t in trials)
    L.append("Resultado da triagem (todos os registros de ensaios): "
             + ", ".join(f"{CATEGORY_PT.get(k, k)}: {num(v)}" for k, v in cat.most_common()) + "\n")
    L.append("### Ensaios incluídos\n")
    inc_rows = [dict(t, category=CATEGORY_PT.get(t["category"], t["category"])) for t in inc]
    L.append(table(inc_rows, ["trial_id", "registry", "category", "phase", "status", "start", "sponsor", "conditions",
                              "same_trial_as", "reason"],
                   ["ID", "Registro", "Categoria", "Fase", "Situação", "Início", "Patrocinador", "Condição",
                    "Duplicata de", "Observações"]))
    L.append("")
    adpd = [t for t in inc if t["ad_pd_flag"] == "1"]
    L.append(f"**Alzheimer / Parkinson:** {num(len(adpd))} ensaios optogenéticos registrados. "
             "Todas as intervenções optogenéticas registradas até hoje tratam doenças da retina "
             "(retinose pigmentar, doença de Stargardt, atrofia geográfica). Para a revisão, isso significa "
             "que a evidência em DA/DP é inteiramente pré-clínica.\n")
    (ROOT / "RELATORIO.md").write_text("\n".join(L))
    print("wrote RELATORIO.md")


if __name__ == "__main__":
    main()
