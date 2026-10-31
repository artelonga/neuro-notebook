#!/usr/bin/env bash
# Topic modeling + term network + Obsidian notes. Needs: uv sync (see README.md).
set -euo pipefail
cd "$(dirname "$0")"
uv run python embed.py
uv run python benchmark.py
uv run python model.py
uv run python labels.py
uv run python visuals.py
uv run python graph.py
uv run python obsidian.py
cd ..
for c in todos selecionados nao-selecionados; do python3 -m litreview.vincular --conjunto "$c"; done
python3 -m litreview.report
