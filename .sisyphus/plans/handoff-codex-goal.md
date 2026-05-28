# Mac Physical AI Lab v0.1 — Codex Goal Handoff

## Goal
Ship a Mac-native, MIT-licensed OSS framework v0.1 in 12 weeks demonstrating Isaac-Sim-equivalent **agentic physical AI** on Apple Silicon.

**Anchor success**: `python examples/eureka_franka.py --seed=42` on M5 Pro achieves Franka pick-place ≥70% success in ≤30min wall-clock. LLM-driven Eureka-style reward learning, fully local (no CUDA).

## Source of Truth (READ FIRST)
`.sisyphus/plans/mac-physical-ai-lab.md` — 43 TODOs across 4 waves + Final Verification. Each task documents What to do / Must NOT do / Agent profile / Parallelization / Acceptance / QA Scenarios / Evidence / Commit. **All execution details live there; this is only a directive.**

Run waves in declared order. Within a wave, fan out PARALLEL-tagged tasks concurrently. Mark `[x]` only after acceptance + QA verified with evidence captured.

## Stack (fixed)
- Sim backend: **MuJoCo** (Apache-2.0) only. No Drake, Taichi, or MPS-as-sim.
- Agent: **opencode** canonical. Other LLMs = design intent only.
- MCP tools min: `sim.make/reset/step/observe`, `task.list`.
- Python ≥3.11 (uv + ruff + mypy strict), Node ≥20 (bun + biome).
- Ship exactly 3 tasks: Franka pick-place + Locomotion + Manipulation variant.

## Forbidden in v0.1 (BLOCKING)
Drake, Taichi, VLA serving, full USD, IsaacLab compat (case-study at most), plug-in machinery (extension-points doc only), multi-LLM adapters, Omniverse/Replicator/Cosmos clones, 4096-env claims, MPS bit-exact, Windows, >5 tasks, breaking API after W8, RoboGen env generator, autonomous reward designer beyond anchor demo, `isaac/omniverse/nvidia` in ship name, marketing copy in place of CI tests, abstractions for <3 instances.

## Verification (strict)
- **TDD**: failing test → minimal impl → refactor, same task. No "tests later".
- **Agent QA**: every task ships tmux/Bash/Playwright scenarios. Evidence → `.sisyphus/evidence/task-{N}-{slug}.{ext}`.
- **Determinism**: CPU = seed bit-exact. MPS = ε≤1e-4 documented. LLM calls cached for CI.
- **CI matrix**: macOS-14 + macOS-15 + ubuntu-22.04 all green.
- **License audit**: pip-licenses + license-checker reject GPL/AGPL/LGPL/proprietary.
- **Cold start**: clone → first episode ≤120s on M5 Pro, ≤300s on macOS-15 runner.

## 7 Freedom CI Tests (as code)
License / API-Backend (3-impl contract) / Workflow (headless) / Extension (50-line explicit-register example) / Agent-LLM (MCP compliance) / Hardware (3-OS matrix) / Research (cold-start ≤120s).

## Execution Sequence
1. **Phase 0 (T1) — GATE**: 0-3 fluency (MuJoCo/MCP/IsaacLab/OSS-launch/robotics), ship name (`^[a-z][a-z0-9-]*$`, no forbidden tokens), first-user persona, single success metric, kill-switch (week+evidence), scope cuts per fluency rules. `python tools/validate_phase_0.py` exits 0. **Honest scores — this gate prevents burnout.**
2. **Wave 1 (W1-3) Vertical Slice**: scaffold → CI/license/types → MuJoCo+Mock+MCP → env API → cartpole + MCP sim tools → vertical slice test (W1F).
3. **Wave 2 (W4-6) ANCHOR DEMO**: Franka + PPO + opencode client → orchestrator → reward gen + sandbox → iteration controller → demo → **T21 FEASIBILITY GATE (oracle, BLOCKING)** → polish.
4. **Wave 3 (W7-9) Stabilization**: 7 freedom CI tests (peak 7-wide) → 2 extra tasks → docs.
5. **Wave 4 (W10-12) Release**: extension-points doc → plugin example + PyPI + npm → release automation → v0.1.0 → demo site + IsaacLab decision + governance.
6. **Final**: F1 oracle plan-compliance, F2/F3 manual QA, F4 deep scope-fidelity → present → user okay → done.

## When Stuck
- Re-read the relevant TODO; `Must NOT do` + `References + WHY` answer most questions.
- 3 consecutive failures on a task: stop, revert to last green, document attempts, consult oracle with full context.
- Never delete failing tests, never `--no-verify`, never invent a forbidden ship name, never mark `[x]` without evidence.

## Done When
All 43 TODOs `[x]`, F1-F4 APPROVE, user explicit okay. v0.1.0 signed tag + PyPI + npm + GitHub release.
