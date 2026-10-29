#!/usr/bin/env bash
# Full pipeline: literature search -> dedup -> trial registries -> PRISMA flow -> RELATORIO.md
# Pass --refresh to bypass the HTTP cache (data/cache/).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m litreview.literature "$@"
python3 -m litreview.dedup
python3 -m litreview.export
python3 -m litreview.trials "$@"
python3 -m litreview.prisma
python3 -m litreview.report
