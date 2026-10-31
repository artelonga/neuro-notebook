"""Translate non-English titles + abstracts to English with an LLM (llm.py: Haiku or Ollama), cached.

    uv run python translate.py

SPECTER (and the c-TF-IDF vocabulary) read English only: works written in
French, Japanese, Chinese or Russian otherwise form a language cluster instead
of joining their subject's topic. A text counts as non-English when it reads
as French (common.is_french) or when over 20% of its letters are not Latin.
Translations are cached in data/topicos/translations.json by a hash of the
source text and the model that translated it; a cached translation is reused
whatever backend runs now, and redone only when the source text changes.
common.load_corpus uses them (flag "translated").
"""
from __future__ import annotations

import hashlib
import json
import re

import llm
from common import OUT, load_corpus, is_french

CACHE = OUT / "translations.json"
PROMPT = ("Translate this scientific title and abstract into English. Keep technical terms, gene and protein "
          "names, and abbreviations. Output only the translation, with the title on the first line.\n\n")


def non_english(text):
    letters = re.findall(r"[^\W\d_]", text)
    non_latin = sum(1 for c in letters if ord(c) > 0x24F)
    return is_french(text) or (letters and non_latin / len(letters) > 0.2)


def source_hash(model, text):
    return hashlib.sha1(f"{model}\n{text}".encode()).hexdigest()[:16]


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = [d for d in load_corpus(translated=False) if non_english(d["text"])]
    print(f"{len(todo)} non-English texts")
    for d in todo:
        old = cache.get(d["work_id"])
        if old and old["hash"] == source_hash(old["model"], d["text"]):
            continue
        en = llm.chat_text(PROMPT + d["text"], max_tokens=8000)
        cache[d["work_id"]] = {"hash": source_hash(llm.MODEL, d["text"]), "model": llm.MODEL, "text": en}
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")
        print(f"  {d['work_id']}: {en.splitlines()[0][:90]}")
    llm.unload()


if __name__ == "__main__":
    main()
