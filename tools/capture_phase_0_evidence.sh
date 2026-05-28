#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
fi

mkdir -p .sisyphus/evidence

happy_tmp="$(mktemp)"
bad_tmp="$(mktemp)"
bad_out="$(mktemp)"
trap 'rm -f "$happy_tmp" "$bad_tmp" "$bad_out"' EXIT

{
  printf '$ python tools/validate_phase_0.py\n'
  python tools/validate_phase_0.py 2>&1
  printf 'exit_code=0\n'
} > "$happy_tmp"
mv "$happy_tmp" .sisyphus/evidence/task-1-phase0-happy.txt

cat > "$bad_tmp" <<'BAD_ASSESSMENT'
# Phase 0 Assessment

## Fluency Scores

MuJoCo Python: 2
MCP server building: 2
IsaacLab internals: 2
OSS framework launch experience: 2
Robotics control fundamentals: 2

## Ship Name

isaac-clone

## First User

The first user is a local Apple Silicon robotics researcher. They want fast local iteration without CUDA. They are comfortable with Python tooling and need reproducible examples.

## Success Metric

The v0.1 success metric is Franka pick-place >=70% success within 30 minutes for seed 42.

## Kill-Switch

Week 6: pivot if benchmark evidence shows the anchor demo cannot exceed 50% success within 30 minutes.

## Scope Adjustments

MuJoCo: no cut. MCP: no cut. IsaacLab: no cut. OSS: no cut.
BAD_ASSESSMENT

{
  printf '$ python tools/validate_phase_0.py --file=%s\n' "$bad_tmp"
  set +e
  python tools/validate_phase_0.py --file="$bad_tmp" > "$bad_out" 2>&1
  code=$?
  set -e
  cat "$bad_out"
  printf 'exit_code=%s\n' "$code"
  if [[ "$code" -eq 0 ]]; then
    printf 'ASSERTION FAILED: expected non-zero exit for forbidden ship name\n'
    exit 1
  fi
} > .sisyphus/evidence/task-1-phase0-bad-name.txt
