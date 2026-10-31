"""Embed the corpus with several sentence-embedding models (cached as .npy).

    uv run python embed.py

Models compared (all small enough to run locally on the M4 / MPS):
  minilm      sentence-transformers/all-MiniLM-L6-v2   general English baseline (BERTopic's default)
  bge         BAAI/bge-small-en-v1.5                   strong small English retrieval model
  specter     sentence-transformers/allenai-specter    trained on scientific citations
  e5-multi    intfloat/multilingual-e5-small           multilingual (fr/ja/zh/ru works in the base)
"""
from __future__ import annotations

import json
import time

import numpy as np
from sentence_transformers import SentenceTransformer

from common import OUT, load_corpus

MODELS = {
    "minilm": ("sentence-transformers/all-MiniLM-L6-v2", ""),
    "bge": ("BAAI/bge-small-en-v1.5", ""),
    "specter": ("sentence-transformers/allenai-specter", ""),
    "e5-multi": ("intfloat/multilingual-e5-small", "passage: "),
}


def main():
    docs = load_corpus()
    texts = [d["text"] for d in docs]
    (OUT / "corpus_ids.json").write_text(json.dumps([d["work_id"] for d in docs]))
    for key, (name, prefix) in MODELS.items():
        path = OUT / f"emb_{key}.npy"
        if path.exists():
            print(f"{key}: cached")
            continue
        t = time.time()
        model = SentenceTransformer(name, device="mps")
        emb = model.encode([prefix + x for x in texts], batch_size=32, normalize_embeddings=True,
                           show_progress_bar=False)
        np.save(path, emb.astype(np.float32))
        print(f"{key}: {emb.shape} in {time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
