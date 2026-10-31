"""Render RELATORIO.md (pt-BR) from the data/ outputs (no network).

    python3 -m litreview.report
"""
from __future__ import annotations

import csv
import json
from collections import Counter

from .common import DATA, MIN_YEAR, ROOT
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


def topics_section():
    """Topic model (topicos/, BERTopic) summary, when its outputs exist."""
    base = DATA / "topicos"
    if not (base / "topics.csv").exists() or not (base / "viz" / "insights.json").exists():
        return []
    model = json.loads((base / "model.json").read_text())
    ins = {t["topic"]: t for t in json.loads((base / "viz" / "insights.json").read_text())["topics"]}
    topics = list(csv.DictReader((base / "topics.csv").open()))
    emb = {"specter": "SPECTER", "minilm": "all-MiniLM-L6-v2", "bge": "bge-small-en-v1.5",
           "e5-multi": "multilingual-e5-small"}.get(model["embedding"], model["embedding"])
    L = ["## Tópicos (BERTopic)\n",
         f"Gerado por `topicos/` (ver `topicos/README.md`): {num(model['n_topics'])} tópicos nos "
         f"{num(model['n_docs'])} trabalhos de `articles/`, com embeddings {emb}, redução {model['reducer'].upper()} e "
         f"agrupamento {model['clusterer']} ({model['params']}), escolhidos num benchmark de 4 embeddings × 4 "
         f"redutores × 6 agrupadores, mais LDA e NMF. Coerência NPMI média {pct(round(model['npmi'], 2))}, "
         f"diversidade {pct(round(model['diversity'], 2))}. Nomes dos tópicos: modelo de linguagem local "
         "(Ollama), com revisão à mão onde indicado.\n"]
    rows = []
    for t in topics:
        i = ins[int(t["topic"])]
        g = i["growth"]
        rows.append({"t": f"T{int(t['topic']):02d}", "nome": (t.get("llm_label") or t["label"])
                     + (" (revisado)" if t.get("label_source") == "revisado" else ""),
                     "n": num(t["n_docs"]), "ad": f"{round(i['alzheimer'] * 100)}%", "pd": f"{round(i['parkinson'] * 100)}%",
                     "g": pct(f"×{g:.1f}") if g is not None else "", "sel": f"{round(i['included'] * 100)}%"})
    L.append(table(rows, ["t", "nome", "n", "ad", "pd", "g", "sel"],
                   ["Tópico", "Nome", "Trabalhos", "Citam Alzheimer", "Citam Parkinson", "2021–26 vs 2016–20",
                    "Na seleção final"]))
    L.append("\n*Citam Alzheimer/Parkinson* = o título ou o resumo menciona a doença (um trabalho pode citar as duas). "
             "*2021–26 vs 2016–20* = razão entre a parcela de trabalhos do tópico nos dois períodos.\n")
    for name, title in [("over_time_facets", "Tópicos por ano"), ("disease", "Tópicos por doença citada"),
                        ("hierarchy", "Hierarquia de tópicos"), ("selection", "Tópicos dentro e fora da seleção final")]:
        if (base / "viz" / f"{name}.png").exists():
            L.append(f"![{title}](data/topicos/viz/{name}.png)\n")
    L.append("Versões interativas em `data/topicos/viz/*.html`; rede de termos no Obsidian em `grafo/Mapa.md`.\n")
    sel, fora = DATA / "termos" / "selecionados" / "termos.csv", DATA / "termos" / "nao-selecionados" / "termos.csv"
    if sel.exists() and fora.exists():
        s_rows = list(csv.DictReader(sel.open()))
        f_cov = {r["termo"]: r["cobertura"] for r in csv.DictReader(fora.open())}
        n_sel = len(list((ROOT / "articles" / "selected").glob("*.md")))
        L.append("### Termos do glossário\n")
        L.append(f"`python3 -m litreview.vincular` liga cada artigo ao seu tópico e aos termos do glossário "
                 f"(`grafo/termos/`, {num(len(json.loads((base / 'notes_index.json').read_text())['terms']))} verbetes) "
                 f"e mede cada termo. *Cobertura* = % dos textos em que o termo aparece; *prevalência* = ocorrências "
                 f"por 10 mil palavras dos resumos. Denominador: os {num(n_sel)} artigos da seleção final; a última "
                 "coluna repete a cobertura entre os artigos fora da seleção. Tabelas completas em `data/termos/`.\n")
        L.append(table([{"t": r["rotulo"], "n": num(r["n_textos"]), "c": pct(f"{float(r['cobertura']):.1f}%"),
                         "p": pct(r["prevalencia"]), "f": pct(f"{float(f_cov.get(r['termo'], 0)):.1f}%")}
                        for r in s_rows[:15]],
                       ["t", "n", "c", "p", "f"], ["Termo", "Textos", "Cobertura", "Prevalência (/10 mil)",
                                                   "Cobertura fora da seleção"]))
        L.append("")
    return L


def prisma_section(p):
    """PRISMA 2020 flow (data/prisma.json, written by litreview.prisma)."""
    idn, rm, sc, inc, rg = (p["identification"], p["removed_before_screening"], p["screening"],
                            p["included"], p["registers"])
    reasons = {"before_min_year": f"publicados antes de {MIN_YEAR}",
               "year_unknown": "ano desconhecido", "not_peer_reviewed": "sem revisão por pares"}
    types = {"original-research": "pesquisa original", "review": "revisão", "systematic-review": "revisão sistemática",
             "meta-analysis": "meta-análise", "methodology": "metodologia", "other": "outros"}
    L = ["## Fluxo PRISMA 2020 e seleção final\n",
         "Gerado por `python3 -m litreview.prisma`, que segue o modelo do PRISMA 2020 para revisões novas com bases, "
         "registros e outras fontes. Diagrama: `data/prisma_flow.svg` (inglês: `data/prisma_flow.en.svg`); "
         "todos os n: `data/prisma.json`; etapa em que cada trabalho saiu do fluxo: `data/prisma_works.csv`; "
         "**seleção final: `data/included.csv`**.\n",
         "![Fluxo PRISMA 2020](data/prisma_flow.svg)\n"]
    steps = [
        ("Identificação", "Registros identificados nas bases", idn["records"]),
        ("", "Duplicados removidos", rm["duplicates"]),
        ("", "Inelegíveis pela reverificação automática de palavras-chave", rm["automation_ineligible"]),
        ("", "Removidos por outros motivos (sem resumo em nenhuma fonte)", rm["other_reasons_no_abstract"]),
        ("Triagem", "Registros triados (título/resumo)", sc["records_screened"]),
        ("", "Excluídos na triagem de título/resumo", sc["records_excluded"]),
        ("", "Relatos buscados para recuperação", sc["reports_sought"]),
        ("", "Relatos não recuperados", sc["reports_not_retrieved"]),
        ("Elegibilidade", "Relatos avaliados quanto à elegibilidade", sc["reports_assessed"]),
    ] + [("", f"Excluídos: {reasons.get(k, k)}", v) for k, v in sc["reports_excluded_reasons"].items()] + [
        ("Incluídos", "**Novos estudos incluídos na revisão**", inc["studies"]),
        ("", "Relatos (versões) desses estudos", inc["reports"]),
    ]
    L.append(table([{"e": a, "s": b, "n": f"**{num(c)}**" if a == "Incluídos" and "**" in b else num(c)}
                    for a, b, c in steps], ["e", "s", "n"], ["Etapa", "Passo", "n"]))
    L.append("")
    L.append(f"Critérios de elegibilidade, aplicados nesta ordem (cada trabalho é contado uma vez, pelo primeiro "
             f"critério que não cumpre): (1) publicado em {MIN_YEAR} ou depois; (2) com revisão por pares "
             f"(`peer_reviewed: true`, artigo de periódico ou revisão). "
             f"{num(sc['excluded_for_both_year_and_peer_review'])} trabalhos falham nos dois.\n")
    L.append("Seleção final por tipo de estudo: " + ", ".join(
        f"{types[k]}: {num(v)}" for k, v in inc["by_study_type"].items() if v) + ". Por ano: " + ", ".join(
        f"{y}: {num(v)}" for y, v in inc["by_year"].items()) + ".\n")
    L.append(f"**Atenção:** a triagem humana ainda não começou ({num(sc['title_abstract_pending'])} pendentes na "
             f"triagem de título/resumo, {num(sc['full_text_pending'])} na leitura do texto completo). Os "
             f"{num(inc['studies'])} incluídos são os que passam nos critérios automáticos. As decisões dos "
             "revisores são lidas dos campos `prisma.screening` de `articles/*.md` e atualizam o fluxo na próxima "
             "execução.\n")
    L.append("Diferenças em relação ao modelo: Google Scholar e ScienceDirect não foram buscados (o Google Scholar "
             "não é reprodutível e o ScienceDirect é coberto pelo Scopus); as bases manuais "
             f"({idn['databases_not_searched']['manual (queries ready in RELATORIO.md)']}) e a busca por citações "
             "ainda não foram feitas (n = 0 em \"outros métodos\"). A classificação por tipo de estudo é "
             "heurística (tipos de publicação do PubMed/Europe PMC, título e veículo; `study_type` no cabeçalho "
             "de cada artigo).\n")
    L.append(f"Registros de ensaios (fluxo próprio, qualquer uso de optogenética): {num(rg['records'])} registros "
             f"triados → {num(rg['excluded'])} excluídos → {num(rg['included_records'])} incluídos → "
             f"{num(rg['same_trial_duplicates'])} registros duplicados do mesmo ensaio → "
             f"**{num(rg['included_trials'])} ensaios distintos**, {num(rg['included_trials_ad_pd'])} em DA/DP.\n")
    return L


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
    pr_path = DATA / "prisma.json"
    if pr_path.exists():
        L += prisma_section(json.loads(pr_path.read_text()))
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
                 f"ainda vazios) e o resumo como corpo. A seleção final do fluxo PRISMA fica em "
                 f"`articles/selected/`; os demais ficam direto em `articles/`. Índice: "
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

    L += topics_section()

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
