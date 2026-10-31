"""One small LLM interface for labels.py and translate.py: Claude Haiku or local Ollama.

Backend choice (LLM env var): "haiku" (Anthropic API, claude-haiku-5-5),
"ollama" (local, MODEL env var, default qwen3.8:27b), or unset = haiku when
Anthropic credentials are available (ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN or
an `ant auth login` profile), else ollama.

Haiku: structured JSON via output_config.format, effort "low" (naming and
translating need no deep reasoning). Ollama: JSON schema via "format",
temperature 0, thinking off, model unloaded by unload().
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

HAIKU = "claude-haiku-5-5"
OLLAMA_MODEL = os.environ.get("MODEL", "qwen3.8:27b")
OLLAMA = "http://127.0.0.1:11434"


def _has_anthropic_credentials():
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
                or (Path.home() / ".config" / "anthropic").exists())


BACKEND = os.environ.get("LLM") or ("haiku" if _has_anthropic_credentials() else "ollama")
MODEL = HAIKU if BACKEND == "haiku" else OLLAMA_MODEL
_client = None


def _anthropic():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def _ollama(messages, fmt=None):
    body = {"model": OLLAMA_MODEL, "stream": False, "think": False, "keep_alive": "2m", "messages": messages,
            "options": {"temperature": 0, "seed": 0, "num_ctx": 8192}}
    if fmt:
        body["format"] = fmt
    req = urllib.request.Request(f"{OLLAMA}/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())["message"]["content"].strip()


def _haiku(system, prompt, schema=None, max_tokens=4000):
    output_config = {"effort": "low"}
    if schema:
        output_config["format"] = {"type": "json_schema", "schema": {**schema, "additionalProperties": False}}
    kwargs = {"system": system} if system else {}
    response = _anthropic().messages.create(
        model=HAIKU, max_tokens=max_tokens, output_config=output_config,
        messages=[{"role": "user", "content": prompt}], **kwargs)
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Haiku refused: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Haiku hit max_tokens; raise it for this call")
    return next(b.text for b in response.content if b.type == "text").strip()


def chat_json(system, prompt, schema):
    if BACKEND == "haiku":
        return json.loads(_haiku(system, prompt, schema))
    return json.loads(_ollama([{"role": "system", "content": system}, {"role": "user", "content": prompt}], schema))


def chat_text(prompt, max_tokens=4000):
    if BACKEND == "haiku":
        return _haiku(None, prompt, max_tokens=max_tokens)
    return _ollama([{"role": "user", "content": prompt}])


def unload():
    """Free the local model's memory (no-op for Haiku)."""
    if BACKEND != "ollama":
        return
    try:
        urllib.request.urlopen(urllib.request.Request(
            f"{OLLAMA}/api/generate", json.dumps({"model": OLLAMA_MODEL, "keep_alive": 0}).encode(),
            {"Content-Type": "application/json"}), timeout=30)
    except OSError:
        pass
