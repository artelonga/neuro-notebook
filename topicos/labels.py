"""Name each topic with an LLM (Claude Haiku or local Ollama, see llm.py), cached.

    uv run python labels.py            # LLM=haiku / LLM=ollama (MODEL=qwen2.5:7b) to force a backend

For each topic the model gets its key phrases (KeyBERTInspired + MMR), its
c-TF-IDF words and the titles of its 5 most representative works, and returns
a Portuguese name, an English name and a one-sentence description (JSON schema,
structured output). Answers are cached in data/topicos/llm_labels.json by a
hash of the input and the model, so reruns cost nothing; a local model is
unloaded at the end. If the backend fails, cached labels are kept and uncached
topics fall back to their first two phrases.

Human review: topicos/rotulos_revisados.csv (topic, guard, rotulo, label_en,
motivo) replaces a model label. The guard is the topic's first three c-TF-IDF
words; when a refit changes them the override is skipped with a warning, so a
reviewed name never lands on a different topic. Column label_source says which
labels are reviewed.

BERTopic can also call an LLM itself (bertopic.representation.OpenAI pointed at
Ollama's OpenAI-compatible endpoint); a separate cached step keeps the topic
model deterministic and the labels reviewable.
"""
from __future__ import annotations

import hashlib
import json

import pandas as pd

import llm
from common import OUT, ROOT, load_corpus

MODEL = llm.MODEL
CACHE = OUT / "llm_labels.json"
REVIEWED = ROOT / "topicos" / "rotulos_revisados.csv"
SYSTEM = ("Você é especialista em neurociência e nomeia tópicos de uma revisão sistemática sobre optogenética "
          "nas doenças de Alzheimer e Parkinson. Todos os trabalhos já tratam de optogenética e de Alzheimer ou "
          "Parkinson: o nome deve dizer o que distingue ESTE tópico dos outros. As palavras mais distintivas "
          "(c-TF-IDF) e os títulos pesam mais que as frases-chave. Use a terminologia médica do português do "
          "Brasil. Responda só com JSON.")
SCHEMA = {"type": "object", "required": ["nome_do_topico", "topic_name", "descricao"],
          "properties": {"nome_do_topico": {"type": "string"}, "topic_name": {"type": "string"},
                         "descricao": {"type": "string"}}}


def main():
    topics = pd.read_csv(OUT / "topics.csv")
    titles = {d["work_id"]: d["title"] for d in load_corpus()}
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    used_llm = False
    out = []
    for r in topics.itertuples():
        reps = [titles[w] for w in r.representative.split()]
        prompt = (f"Frases-chave do tópico: {r.top_words}.\nPalavras mais distintivas: {r.ctfidf_words}.\n"
                  "Títulos representativos:\n" + "\n".join(f"- {t}" for t in reps) +
                  "\n\nDevolva: nome_do_topico (português, 2 a 6 palavras, sem as palavras optogenética, Alzheimer "
                  "ou Parkinson), topic_name (o mesmo em inglês) e descricao (uma frase em português sobre o que os "
                  "trabalhos estudam).")
        key = hashlib.sha1(f"{MODEL}\n{SYSTEM}\n{prompt}".encode()).hexdigest()[:16]
        hit = cache.get(str(r.topic))
        if not (hit and hit["key"] == key):
            try:
                ans = llm.chat_json(SYSTEM, prompt, SCHEMA)
                used_llm = True
                hit = {"key": key, "model": MODEL, **ans}
                cache[str(r.topic)] = hit
                print(f"  T{r.topic:02d} {ans['nome_do_topico']}")
            except Exception as e:  # network, auth, refusal: keep going with the cache
                print(f"  T{r.topic:02d} {llm.BACKEND} falhou ({e}); usando {'cache antigo' if hit else 'as frases'}")
        out.append(hit or {"nome_do_topico": ", ".join(r.top_words.split("; ")[:2]),
                           "topic_name": "", "descricao": "", "model": None})
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")
    topics["llm_label"] = [o["nome_do_topico"].strip().rstrip(".") for o in out]
    topics["llm_label_en"] = [o["topic_name"].strip().rstrip(".") for o in out]
    topics["llm_description"] = [o["descricao"].strip() for o in out]
    topics["llm_model"] = [o.get("model") for o in out]
    topics["label_source"] = "llm"
    if REVIEWED.exists():
        for rv in pd.read_csv(REVIEWED).itertuples():
            i = topics.index[topics["topic"] == rv.topic]
            guard = "; ".join(str(topics.loc[i[0], "ctfidf_words"]).split("; ")[:3]) if len(i) else None
            if guard != rv.guard:
                print(f"  revisão de T{rv.topic:02d} ignorada: o tópico mudou ({guard!r} != {rv.guard!r})")
                continue
            topics.loc[i, ["llm_label", "llm_label_en", "label_source"]] = [rv.rotulo, rv.label_en, "revisado"]
    topics.to_csv(OUT / "topics.csv", index=False)
    if used_llm:
        llm.unload()
    for r in topics.itertuples():
        print(f"T{r.topic:02d} [{r.label_source}] {r.llm_label} | {r.llm_label_en} | c-TF-IDF: {r.ctfidf_words[:60]}")


if __name__ == "__main__":
    main()
