#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="full"
THRESHOLD_SECONDS="${PHYSLAB_COLD_START_THRESHOLD:-}"
EVIDENCE_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick)
      MODE="quick"
      shift
      ;;
    --threshold)
      THRESHOLD_SECONDS="$2"
      shift 2
      ;;
    --evidence)
      EVIDENCE_PATH="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

cd "$ROOT"
if [[ -z "$EVIDENCE_PATH" ]]; then
  SAFE_HOST="$(hostname | tr -cs 'A-Za-z0-9_.-' '_')"
  EVIDENCE_PATH=".sisyphus/evidence/cold_start_${SAFE_HOST}.txt"
fi
mkdir -p "$(dirname "$EVIDENCE_PATH")"

SECONDS=0
if [[ "$MODE" == "full" ]]; then
  rm -rf .venv mcp-server/node_modules
  uv venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  uv pip install -e .
  (cd mcp-server && bun install)
  python examples/hello_cartpole.py --headless --steps 10 --seed 42
else
  uv run python examples/hello_cartpole.py --headless --steps 10 --seed 42
fi
TOTAL_SECONDS="$SECONDS"

{
  echo "mode=$MODE"
  echo "host=$(hostname)"
  echo "cpu=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || uname -m)"
  echo "total_seconds=$TOTAL_SECONDS"
  echo "threshold_seconds=${THRESHOLD_SECONDS:-none}"
  echo "result=ok"
} | tee "$EVIDENCE_PATH"

if [[ -n "$THRESHOLD_SECONDS" && "$TOTAL_SECONDS" -gt "$THRESHOLD_SECONDS" ]]; then
  sed -i.bak 's/result=ok/result=fail/' "$EVIDENCE_PATH"
  rm -f "$EVIDENCE_PATH.bak"
  echo "cold start exceeded threshold: ${TOTAL_SECONDS}s > ${THRESHOLD_SECONDS}s" >&2
  exit 1
fi
