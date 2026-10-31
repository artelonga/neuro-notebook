"""Shared pieces: corpus from articles/, vocabulary, topic-quality metrics.

The corpus is the review base (articles/, one work per file): title + abstract.
Keywords are kept apart (they feed the term network, not the embeddings),
because a third of them are machine-assigned by OpenAlex.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "topicos"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT))
from litreview.keywords import OPTO, front_matter, kw_key  # noqa: E402

NO_ABSTRACT = "_Abstract not available in any source database._"
# The two search concepts are in every document by construction, and these
# words are generic scientific prose: neither separates topics.
DOMAIN_STOP = {
    "optogenetic", "optogenetics", "optogenetically", "alzheimer", "alzheimers", "parkinson",
    "parkinsons", "disease", "diseases", "ad", "pd", "study", "studies", "result", "results",
    "using", "used", "use", "showed", "shown", "show", "shows", "suggest", "suggests", "found",
    "findings", "role", "including", "demonstrate", "demonstrated", "reveal", "revealed", "data",
    "however", "potential", "approach", "approaches", "new", "novel", "recent", "recently",
    "review", "important", "understanding", "provide", "provides", "present", "investigated",
    "effect", "effects", "significantly", "increased", "decreased", "induced", "related",
    "associated", "et", "al", "mouse", "mice",
}
STOP = sorted(ENGLISH_STOP_WORDS | DOMAIN_STOP)
TOKEN = r"(?u)\b[a-zA-Z][a-zA-Z0-9-]{2,}\b"


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"^\s*(abstract|summary)[:.\s]+", "", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


# Bilingual theses (theses.fr) carry a French and an English abstract. SPECTER is
# English-only, so French sentences pull those works into a language cluster
# instead of a subject one. Sentences that read as French are dropped when the
# text has other sentences; fully French texts are kept as they are.
FR_WORDS = set("les des dans une est que pour sur avec par nous cette aux ces sont qui du le la et au chez "
               "leur leurs ont été entre ainsi".split())


def is_french(sentence):
    toks = re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", sentence.lower())
    return len(toks) >= 4 and sum(t in FR_WORDS for t in toks) / len(toks) > 0.12


def drop_french(text):
    sents = re.split(r"(?<=[.!?])\s+", text)
    kept = [x for x in sents if not is_french(x)]
    return " ".join(kept) if kept else text


# litreview/vincular.py writes links and a block into the article bodies; the corpus
# must read the abstract as it was exported, or the links feed back into the model.
LINKS_BLOCK = re.compile(r"\n*<!-- vinculos:inicio -->.*?<!-- vinculos:fim -->\n*", re.S)
WIKILINK = re.compile(r"\[\[grafo/[^\]|]+\|([^\]]+)\]\]")


def load_corpus(translated=True):
    """One dict per work in articles/: work_id, title, text, keywords, metadata.

    translated=True replaces non-English texts by their cached English
    translation (translate.py) when it matches the current source text.
    """
    tr = json.loads((OUT / "translations.json").read_text()) if translated and (OUT / "translations.json").exists() else {}
    docs = []
    for r in csv.DictReader((DATA / "prisma_works.csv").open()):
        if not r["file"]:
            continue
        path = ROOT / "articles" / r["file"]
        fm = front_matter(path)
        body = WIKILINK.sub(r"\1", LINKS_BLOCK.sub("\n", path.read_text().split("\n---", 2)[-1])).strip()
        abstract = "" if body == NO_ABSTRACT else drop_french(clean(body))
        title = clean(r["title"])
        docs.append({
            "work_id": r["work_id"], "file": r["file"], "title": title, "abstract": abstract, "doi": r["doi"],
            "text": f"{title.rstrip('.')}. {abstract}".strip(), "keywords": fm["keywords"],
            "opto_keyword": any(OPTO.search(k) for k in fm["keywords"]),
            "year": r["year"], "journal": fm["journal"], "document_type": fm["document_type"],
            "study_type": fm["study_type"], "language": fm["language"], "included": r["included"] == "1",
            "translated": False,
        })
    if tr:
        import hashlib
        for d in docs:
            t = tr.get(d["work_id"])
            if t and t["hash"] == hashlib.sha1(f"{t['model']}\n{d['text']}".encode()).hexdigest()[:16]:
                d.update(text=t["text"], translated=True)
    return docs


def vectorizer(min_df=3, ngram=(1, 2)):
    return CountVectorizer(stop_words=STOP, token_pattern=TOKEN, ngram_range=ngram, min_df=min_df,
                           max_df=0.5, lowercase=True)


# Phrases for labels and keyphrases: n-grams never cross a stopword or punctuation,
# so "nucleus (STN)" or "neurons of the motor cortex" do not become "nucleus stn" or
# "neurons motor". Extra stopwords: boilerplate and the French abstracts' function words.
PHRASE_STOP = set(STOP) | {
    "topic", "research", "editorial", "maladie", "maladies", "les", "des", "une", "dans", "par", "pour",
    "sur", "est", "sont", "avec", "qui", "que", "aux", "ces", "nous", "cette", "plus", "chez",
}
SPLIT = re.compile(r"[.,;:!?()\[\]{}\"“”'’/]+")
WORD = re.compile(r"[a-z][a-z0-9-]*")


def phrases(text, ngram=(1, 3)):
    out = []
    for chunk in SPLIT.split((text or "").lower()):
        run = []
        for tok in WORD.findall(chunk) + [None]:
            if tok is None or tok in PHRASE_STOP or len(tok) < 3:
                for n in range(ngram[0], ngram[1] + 1):
                    out += [" ".join(run[i:i + n]) for i in range(len(run) - n + 1)]
                run = []
            else:
                run.append(tok)
    return out


def phrase_vectorizer(min_df=3, ngram=(1, 3)):
    return CountVectorizer(analyzer=lambda t: phrases(t, ngram), min_df=min_df, max_df=0.5)


def ctfidf_top_words(texts, labels, n=10, cv=None):
    """Class-based TF-IDF (BERTopic's formula) -> {label: [top words]}; label -1 = noise, skipped."""
    cv = cv or vectorizer()
    X = cv.fit_transform(texts)
    vocab = np.array(cv.get_feature_names_out())
    labels = np.asarray(labels)
    classes = [c for c in sorted(set(labels)) if c != -1]
    if not classes:
        return {}
    tf = np.vstack([np.asarray(X[labels == c].sum(axis=0)).ravel() for c in classes])
    avg = tf.sum() / len(classes)
    idf = np.log(1 + avg / np.maximum(tf.sum(axis=0), 1))
    w = (tf / np.maximum(tf.sum(axis=1, keepdims=True), 1)) * idf
    return {c: list(vocab[np.argsort(-w[i])[:n]]) for i, c in enumerate(classes)}


class Coherence:
    """Document-level NPMI over the corpus vocabulary (unigrams + bigrams)."""

    def __init__(self, texts):
        self.cv = vectorizer(min_df=2)
        X = (self.cv.fit_transform(texts) > 0).astype(np.int32).tocsc()
        self.X, self.n = X, X.shape[0]
        self.idx = {w: i for i, w in enumerate(self.cv.get_feature_names_out())}
        self.df = np.asarray(X.sum(axis=0)).ravel()

    def npmi(self, a, b):
        i, j = self.idx.get(a), self.idx.get(b)
        if i is None or j is None:
            return 0.0
        co = self.X[:, i].multiply(self.X[:, j]).sum()
        if co == 0:
            return -1.0
        p_ab, p_a, p_b = co / self.n, self.df[i] / self.n, self.df[j] / self.n
        if p_ab == 1:
            return 1.0
        return float(np.log(p_ab / (p_a * p_b)) / -np.log(p_ab))

    def topic(self, words):
        pairs = list(combinations(words, 2))
        return float(np.mean([self.npmi(a, b) for a, b in pairs])) if pairs else 0.0

    def model(self, topics):
        return float(np.mean([self.topic(w) for w in topics.values()])) if topics else float("nan")


def diversity(topics):
    words = [w for ws in topics.values() for w in ws]
    return len(set(words)) / len(words) if words else float("nan")


def save_json(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=float) + "\n")


__all__ = ["ROOT", "DATA", "OUT", "STOP", "load_corpus", "vectorizer", "phrase_vectorizer", "phrases", "ctfidf_top_words", "Coherence",
           "diversity", "save_json", "kw_key", "OPTO"]
