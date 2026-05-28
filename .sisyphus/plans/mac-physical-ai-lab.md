# Mac-Native Physical AI Lab (v0.1) — 12-Week Demo-Driven OSS Framework

## TL;DR

> **Quick Summary**: Build a demo-driven, Mac-native, MIT-licensed OSS framework that demonstrates Isaac-Sim-equivalent **agentic physical AI workflow** on Apple Silicon, anchored by a single end-to-end demo (Eureka-style LLM-driven reward learning for Franka pick-place via opencode + MCP, fully on M5 Pro). Plug-in *extension points* are documented but the plug-in machinery itself, Drake, Taichi, VLA serving, and full USD support are deferred to v0.2.
>
> **Deliverables**:
> - Working OSS repo (MIT) with PyPI + npm packages
> - **Anchor demo by week 6**: Eureka-style reward learning on Franka pick-place → ≥70% success rate in ≤30 minutes wall-clock on M5 Pro
> - 3 high-quality tasks (Franka pick-place + 2 more)
> - MCP server exposing standard sim tools (`sim.make/reset/step/observe`, `task.list`)
> - 7 "freedom" claims encoded as executable CI tests (license, API/backend, workflow, extension, agent, hardware, research freedom)
> - Documentation: README, Getting Started, 1 tutorial, auto-gen API reference, extension points design doc
> - GitHub Actions matrix: macOS-14, macOS-15, ubuntu-22.04
> - Demo site (static) with embedded demo video and benchmarks
> - v0.1 GitHub release with changelog
>
> **Estimated Effort**: XL (12 weeks × 40h = ~480h, scoped tightly per Metis review — actual scope is ~500-700h budget with cuts; aggressive but feasible IF Phase 0 fluency gate passes)
> **Parallel Execution**: YES — 4 main waves + Final Verification Wave; targets 5-8 tasks per wave
> **Critical Path**: Phase 0 fluency gate → Types/Protocols → MuJoCo wrapper + MCP server → Franka task → Eureka loop → Anchor demo (week 6) → Stabilization → Release

---

## Context

### Original Request
User wants to port NVIDIA Isaac Sim / Isaac Lab to Mac (Apple Silicon) and integrate agentic tooling (opencode/codex). Direct conversation transcript and decisions are preserved in the draft.

### Interview Summary
**Round 1 Key Decisions**:
- Goal: "Isaac과 동등한 능력을 Mac 네이티브로" (Mac-native equivalent, not literal port)
- Use case: Exploratory (no single domain) — implies general-purpose stack
- First agentic pattern: Research orchestrator (opencode/codex 본업과 가장 일치)

**Round 2 Key Decisions**:
- "Freedom" = all 7 dimensions (license / API / workflow / extension / agent / hardware / research)
- Scope: 12+ weeks, full-time solo (~480h budget)
- Test strategy: **Full TDD + Agent QA** (mandatory)
- License: **MIT OSS**
- Tier 2 (Remote GPU): **100% Mac local** — interface plug-in only, not actively used

### Research Findings (5 parallel librarian agents)

1. **Existing Mac ports**: Stock Isaac on Mac = effectively impossible. Best community fork: `RobotFlow-Labs/IsaacLab-mlx` (MLX backend, partial). NVIDIA itself moving toward "Newton" modular ARM support. (Source: bg_a30a10f7)

2. **Mac-native sim alternatives**: MuJoCo (Apache-2.0, native arm64, mature) is the only mature single-stack winner. Drake/Taichi/PyTorch MPS complement it. Brax is being deprecated in favor of MJX. ManiSkill3 = CPU only on Mac. Genesis = rough Mac/Metal. (Source: bg_befc72a0)

3. **Isaac architecture**: Native macOS Isaac Sim = platform rewrite, not build fix. **But IsaacLab 3.0-beta has kit-less mode** — env can run without full Isaac Sim. (Source: bg_9ed43a5e)

4. **Agentic patterns (validated)**: "LLM is OUTSIDE the control loop." Reference architecture: LLM orchestrator → MCP tool boundary → artifact store → evaluator → reflection. References: Eureka (reward), IsaacLabEureka (NVIDIA official fork), Voyager/CaP-X (orchestrator), openpi/OpenVLA (policy serving), RoboGen/GenSim (env gen). (Source: bg_8a1991da)

5. **Remote GPU patterns**: OCI A10 $2/hr (user has access), AWS g6e NVIDIA-recommended, RunPod RTX 6000 Ada spot $0.39/hr. Plan defers active use to v0.2. (Source: bg_f1ce4e81)

### Metis Pre-Plan Review (Critical Findings — Silently Applied)
- **480h scope is 2-3x undersized** for stated 12-week framework (Metis estimates 900-1400h for original ambition)
- **Required cuts applied to v0.1**: Drake, Taichi, VLA serving, full USD, general IsaacLab compat, plug-in machinery, multi-LLM adapters → all deferred to v0.2/v0.3
- **Demo-driven inversion**: Build ONE killer end-to-end demo by week 6 (not week 11). Weeks 7-12 polish and extract abstractions.
- **Background fluency gate (Phase 0)** added before week 1 to validate user can actually deliver the scope; on fail, additional 30-40% cut.
- **"Freedom" as 7 executable CI tests** — not marketing copy
- **Non-Isaac ship name** mandated by week 1 (trademark risk)

### Oracle Phase 1 Gate (Minor Concerns Encoded)
- Scope Boundaries + Technical Decisions are AUTHORITATIVE (earlier exploratory sections of draft are subordinate)
- Week 6 anchor demo needs explicit feasibility validation gate (added as Task in Wave 2)
- CI cold-start benchmark differentiates Mac runners (auth) vs local M5 Pro (golden baseline)

---

## Work Objectives

### Core Objective
Deliver a Mac-native, MIT-licensed, demo-driven OSS framework that:
1. Runs an Eureka-style LLM-driven research orchestrator end-to-end on Apple Silicon without CUDA
2. Demonstrates 7 testable "freedom" claims as the value proposition
3. Provides a clean foundation (MuJoCo + MCP) for v0.2+ expansion (Drake, Taichi, VLA, full plug-in system)

### Concrete Deliverables
- Repository: `<ship-name>/` with monorepo (Python core + TypeScript MCP server)
- PyPI package: `<ship-name>` (Python ≥3.11)
- npm package: `<ship-name>-mcp` (Node ≥20)
- Anchor demo: `examples/eureka_franka.py` reproducibly achieving ≥70% Franka pick-place success in ≤30min on M5 Pro
- 3 high-quality tasks in `<ship-name>/tasks/`
- 7 freedom CI tests passing in GitHub Actions matrix
- Docs: README, Getting Started, 1 tutorial, auto-gen API ref, extension points design doc
- Demo site (static, served via GitHub Pages or similar)
- v0.1.0 GitHub release with signed tag

### Definition of Done
- [ ] Anchor demo reproducible: `python examples/eureka_franka.py --seed=42` → success rate ≥70%, wall-clock ≤30min on M5 Pro, evidence captured
- [ ] All 7 freedom CI tests green on `macos-14`, `macos-15`, `ubuntu-22.04`
- [ ] `pip install <ship-name>` works in fresh venv, runs example
- [ ] `npm install <ship-name>-mcp` works, MCP server starts and `tools/list` returns ≥5 tools
- [ ] License audit (`scancode`/`licensee`) returns 0 GPL/AGPL/proprietary dependencies
- [ ] Cold-start (`git clone` → first episode complete) ≤120s on M5 Pro, ≤300s on GitHub macOS-15 runner
- [ ] Docs build cleanly, all code examples in docs execute green in CI
- [ ] v0.1.0 release tagged, signed, published to PyPI + npm
- [ ] Final Verification Wave (F1-F4) all APPROVE
- [ ] Explicit user okay obtained after F1-F4 results presented

### Must Have
- MuJoCo as the single v0.1 sim backend
- MCP server with `sim.make`, `sim.reset`, `sim.step`, `sim.observe`, `task.list` minimum
- One agent integration: opencode (canonical)
- Research orchestrator agent loop (Eureka-style)
- 3 high-quality tasks (Franka pick-place + 2 more, decided in Phase 0 or Week 1)
- TDD: every implementation task has tests written before code
- Agent QA scenarios on every task (Playwright/tmux/bash, evidence captured)
- 7 freedom CI tests encoded
- Phase 0 fluency self-assessment gate (Day -3 to Day 0)
- Non-Isaac ship name chosen by end of Week 1
- MIT license + dependency license audit

### Must NOT Have (Guardrails from Metis review)
- ❌ Drake integration (defer v0.2)
- ❌ Taichi backend (defer v0.2)
- ❌ PyTorch MPS as a *sim* backend (only as policy training target)
- ❌ VLA model serving implementation (stub `PolicyServer` protocol only)
- ❌ Full USD scene round-tripping (URDF→MJCF + limited USD geometry import only)
- ❌ General IsaacLab compatibility layer (ONE specific task case study at most, or drop in Week 10)
- ❌ Plug-in *machinery* (loaders, lifecycle, sandboxing) — only extension *points* documented
- ❌ Multi-LLM adapters (only opencode; Claude/codex/GPT documented as design intent)
- ❌ Omniverse Kit clone, Replicator clone, Cosmos/Newton emulation
- ❌ 4096-env parallelism claims (document realistic 16-64 env count on Mac)
- ❌ Bit-exact reproducibility on MPS (CPU backend only)
- ❌ Windows-native support (Linux + macOS only)
- ❌ More than 5 tasks (ship 3 high-quality)
- ❌ Breaking changes after Week 8 (public API frozen)
- ❌ Active Tier 2 (Remote GPU) usage (interface stub only)
- ❌ Environment generator (RoboGen-style) — defer v0.2
- ❌ Fully autonomous reward designer beyond the Eureka anchor demo
- ❌ "Isaac" in the ship name (trademark risk)
- ❌ Marketing copy in lieu of testable CI claims for "freedom"
- ❌ Generic abstractions for <3 concrete instances (Rule of Three)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No criteria require "user manually tests/confirms".

### Test Decision
- **Infrastructure exists**: NO (greenfield)
- **Automated tests**: **YES (Full TDD)** — RED → GREEN → REFACTOR per task
- **Framework**: pytest (Python) + bun test (TypeScript MCP server)
- **TDD discipline**: failing test committed → minimal implementation → refactor; same task. No "write code, add tests later".
- **Coverage target**: 70-80% line coverage on core modules (env API, MCP server, orchestrator). 100% on protocols/contracts. No bloat.

### QA Policy
Every task MUST include agent-executed QA scenarios (see TODO template below). Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **TUI/CLI** (most tasks): `interactive_bash` (tmux) → run command, capture output, validate exit code + key output substrings
- **Python module/API**: `Bash` → invoke via `python -c "..."` or pytest, capture stdout + return code
- **MCP server (TypeScript)**: `Bash` → `curl` to local server endpoint, parse JSON, assert fields
- **Demo site (HTML if added)**: `Playwright` skill → load page, screenshot, verify content
- **CI matrix verification**: `Bash` → invoke `gh run list` / `gh run view` for matrix workflows

### Determinism Policy
- **CPU backend**: bit-exact reproducibility with seed → tests assert exact match
- **MPS backend**: ε-close reproducibility (ε documented per task, typically 1e-4)
- **LLM-driven tasks** (orchestrator, reward gen): use LLM response caching to make CI deterministic. Cache key = (prompt hash, model id, temperature).
- **Tests requiring real LLM calls**: gated behind `@pytest.mark.live` and not in core CI

### CI Matrix
- `macos-14` (M1, baseline Mac runner) — must pass
- `macos-15` (M-latest available) — must pass
- `ubuntu-22.04` (x86-64) — must pass (Linux compatibility claim)
- **Cold-start benchmark** runs on each, but the **canonical M5 Pro number** is captured locally (not in CI) due to runner heterogeneity

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves. Each wave completes before the next begins.
> Target: 5-8 tasks per wave. Phase 0 is intentionally a single gate task (blocking).

```
Wave Categorization Legend:
  [PARALLEL]      = ≥3 tasks runnable concurrently (target 5-8)
  [PARALLEL-PAIR] = exactly 2 tasks parallel — structural minimum at this dep level
                    (the dependency graph genuinely allows only 2 parallel tasks here;
                     not under-splitting — merging would force sequential serialization
                     of independent work)
  [BRIDGE]        = inherent sequential bottleneck (1 task; structural dep, no way to parallelize)
  [FINAL-INT]     = final-integration wave (rule explicitly exempts <3 task waves here)
  [GATE]          = decision/feasibility gate (1 task, blocking)

Phase 0 [GATE]:
└── T1: Phase 0 self-assessment + naming + first user + success metric + kill-switch

═══════════════════════════════════════════════════════════════════════
Wave 1 (Weeks 1-3 — Vertical Slice)
═══════════════════════════════════════════════════════════════════════

Wave 1A [BRIDGE] (1 task — scaffolding must precede everything; structural):
└── T2: Monorepo scaffolding (pyproject + package.json + tooling)

Wave 1B [PARALLEL] (3 tasks — all depend only on T2, mutually independent):
├── T3: CI matrix (GitHub Actions: 3 OS)
├── T4: License audit infrastructure
└── T5: Type & Protocol definitions

Wave 1C [PARALLEL] (3 tasks — truly independent after T5/T2):
├── T6: MuJoCo wrapper core (deps: T5 only)
├── T7: Mock backend (deps: T5 only)
└── T10: MCP server skeleton (deps: T2 only — orthogonal, runs in parallel from Wave 1B end)

Wave 1D [BRIDGE] (1 task — env API depends on T6+T7; structural):
└── T8: Env API + Task registry (deps: T5, T6, T7)

Wave 1E [PARALLEL-PAIR] (2 tasks — structural; T9 and T11 are genuinely independent at this dep level):
├── T9: First toy task — Cartpole (deps: T6, T8)
└── T11: MCP sim tools (deps: T8, T10)

Wave 1F [FINAL-INT] (1 task — Wave 1 capstone integration):
└── T12: End-to-end vertical slice test (deps: T9, T11) [GATE TO WAVE 2]

═══════════════════════════════════════════════════════════════════════
Wave 2 (Weeks 4-6 — Anchor Demo Production)
═══════════════════════════════════════════════════════════════════════

Wave 2A [PARALLEL] (3 tasks — independent demo components):
├── T13: Franka pick-place task (deps: T6, T8)
├── T14: Minimal RL trainer PPO (deps: T8)
└── T15: LLM client wrapper opencode (deps: T2)

Wave 2B [BRIDGE] (1 task — orchestrator must precede subordinate components):
└── T16: Research orchestrator skeleton (deps: T8, T15)

Wave 2C [PARALLEL-PAIR] (2 tasks — structural; T17 and T18 are independent after T13/T14/T16):
├── T17: Reward function generator (deps: T13, T15, T16)
└── T18: Reward sandbox + evaluator (deps: T13, T14, T16)

Wave 2D [BRIDGE] (1 task — controller needs reward + eval):
└── T19: Iteration controller (deps: T16, T17, T18)

Wave 2E [FINAL-INT] (3 tasks sequential — Wave 2 capstone, includes the feasibility gate):
├── T20: Anchor demo script (deps: T13-T19)
├── T21: ⚡ DEMO FEASIBILITY GATE (deps: T20) — BLOCKING
└── T22: Anchor demo final polish (deps: T21 PASS) [GATE TO WAVE 3]

═══════════════════════════════════════════════════════════════════════
Wave 3 (Weeks 7-9 — Stabilization)
═══════════════════════════════════════════════════════════════════════

Wave 3A [PARALLEL] (7 tasks — peak parallelism; all 7 freedoms CI-encoded):
├── T23: CI License Freedom
├── T24: CI API/Backend Freedom (3-impl contract test)
├── T25: CI Workflow Freedom (headless)
├── T26: CI Extension Freedom (50-line explicit-register example)
├── T27: CI Agent/LLM Freedom (MCP compliance)
├── T28: CI Hardware Freedom (3-OS matrix)
└── T29: CI Research Freedom (cold-start ≤120s)

Wave 3B [PARALLEL-PAIR] (2 tasks — structural; the third v0.1 task is sufficient breadth, more would violate "no >5 tasks" guardrail):
├── T30: Second task — Locomotion
└── T31: Third task — Manipulation variant

Wave 3C [PARALLEL] (3 tasks — docs, mutually independent):
├── T32: Docs — README + Getting Started
├── T33: Docs — Tutorial (Eureka-Franka walkthrough)
└── T34: Docs — Auto-gen API reference [GATE TO WAVE 4]

═══════════════════════════════════════════════════════════════════════
Wave 4 (Weeks 10-12 — Release & Extension Points)
═══════════════════════════════════════════════════════════════════════

Wave 4A [BRIDGE] (1 task — extension points doc must precede plugin example & release):
└── T35: Extension Points design doc + interfaces frozen

Wave 4B [PARALLEL] (3 tasks — independent after T35):
├── T36: Hello-world PyPI-installable plugin example (explicit-import-and-register pattern)
├── T37: PyPI packaging
└── T38: npm packaging

Wave 4C [BRIDGE] (1 task — release automation must precede actual release):
└── T39: Release process automation (semver, CHANGELOG, signed tag)

Wave 4D [BRIDGE] (1 task — actual release is structurally atomic):
└── T40: v0.1.0 first release (PyPI + npm + GH release)

Wave 4E [PARALLEL] (3 tasks — independent post-release work):
├── T41: Demo site
├── T42: IsaacLab compat decision (case study OR drop)
└── T43: Post-release runbook + governance docs

═══════════════════════════════════════════════════════════════════════
Final Verification Wave [PARALLEL] (4 tasks; rule's `final` exemption naturally applies):
═══════════════════════════════════════════════════════════════════════
├── F1: Plan compliance audit (oracle)
├── F2: Code quality review (unspecified-high)
├── F3: Real manual QA (unspecified-high)
└── F4: Scope fidelity check (deep)
→ Present results → Get explicit user okay → mark plan complete

Critical Path:
  P0(T1) → W1A(T2) → W1B(T5) → W1C(T6, T10) → W1D(T8) → W1E(T9, T11) → W1F(T12)
  → W2A(T13, T15) → W2B(T16) → W2C(T17, T18) → W2D(T19) → W2E(T20→T21→T22)
  → W3A(7 freedoms parallel) → W3B(T30, T31) → W3C(T32-T34)
  → W4A(T35) → W4B(T36, T37, T38) → W4C(T39) → W4D(T40) → W4E
  → F1-F4 → user okay

Max Concurrent: 7 tasks (W3A — 7 freedom CI tests in parallel)
Parallel Speedup vs serial: ~50% (Wave 2 has deep internal deps)

Wave classification table:
  Type          | Wave (Tasks)
  GATE          | P0(T1)
  BRIDGE        | 1A(T2), 1D(T8), 2B(T16), 2D(T19), 4A(T35), 4C(T39), 4D(T40)
  PARALLEL      | 1B(3), 1C(3), 2A(3), 3A(7), 3C(3), 4B(3), 4E(3), Final(4)
  PARALLEL-PAIR | 1E(2), 2C(2), 3B(2)
  FINAL-INT     | 1F(T12), 2E(T20-T22)
  All BRIDGE waves are inherent sequential bottlenecks (single task with non-bypassable predecessors).
  All PARALLEL-PAIR waves are structural minimums — the dep graph genuinely allows only 2 parallel
  tasks at that level. Merging them would force sequential serialization of work that is provably
  independent.
```

### Dependency Matrix (abbreviated — see individual tasks for full deps)

- **1 (Phase 0)**: gates everything; results inform Wave 1+
- **2-4**: foundation, no deps among themselves; needed by all coding tasks
- **5**: needed by 6, 7, 8, 11
- **6, 7**: needed by 8, 12
- **8, 9**: needed by 11, 12, 13
- **10, 11**: needed by 12, 15, 16, 20
- **12**: anchor for vertical slice; blocks Wave 2 start
- **13, 14**: needed by 17-20
- **15, 16**: needed by 17-20
- **17, 18, 19**: needed by 20
- **20**: anchor demo skeleton
- **21**: BLOCKING feasibility gate; if fail → replan
- **22**: depends on 20 + 21 pass
- **23-29**: parallel within Wave 3 once Wave 2 done
- **30, 31**: depend on 8 (env API), parallel to CI tests
- **32-34**: depend on 22 (demo done), parallel to each other
- **35**: depends on Wave 3 done; design freeze for v0.1
- **36**: depends on T26, T35 (plugin example uses register_task API + extension points doc)
- **37, 38**: depend on T35 only (packaging the main project; independent of plugin example)
- **39**: depends on T37 + T38 (release auto requires packaging done)
- **40**: depends on T39 (actual release uses the automation)
- **41, 42, 43**: parallel after 40

### Agent Dispatch Summary (by sub-wave)
- **Phase 0 (T1)**: `quick` — user-facing self-assessment
- **Wave 1A (T2)**: `quick` — scaffolding
- **Wave 1B (T3-T5)**: `quick` × 2 (CI, license), `deep` × 1 (types)
- **Wave 1C (T6, T7, T10)**: `deep` × 2 (MuJoCo, MCP server), `quick` × 1 (Mock)
- **Wave 1D (T8)**: `deep` — env API (sticky public API)
- **Wave 1E (T9, T11)**: `quick` × 1 (cartpole), `deep` × 1 (MCP sim tools)
- **Wave 1F (T12)**: `deep` — vertical slice integration
- **Wave 2A (T13-T15)**: `deep` × 2 (Franka, RL trainer), `deep` × 1 (LLM client)
- **Wave 2B (T16)**: `deep` — orchestrator skeleton
- **Wave 2C (T17, T18)**: `deep` × 2 — reward gen + sandbox
- **Wave 2D (T19)**: `deep` — iteration controller
- **Wave 2E (T20-T22)**: `deep` × 1 (T20 demo), **`oracle`** × 1 (T21 GATE), `unspecified-high` × 1 (T22 polish)
- **Wave 3A (T23-T29)**: `unspecified-high` × 7 — CI freedom tests
- **Wave 3B (T30-T31)**: `deep` × 2 — additional tasks
- **Wave 3C (T32-T34)**: `writing` × 3 — docs
- **Wave 4A (T35)**: `writing` — extension points design
- **Wave 4B (T36-T38)**: `quick` × 3 — packaging
- **Wave 4C (T39)**: `unspecified-high` — release automation
- **Wave 4D (T40)**: `unspecified-high` — release execution
- **Wave 4E (T41-T43)**: `visual-engineering` × 1 (T41 demo site, w/ `frontend-ui-ux` skill), `deep` × 1 (T42 IsaacLab decision), `writing` × 1 (T43 runbook)
- **FINAL**: F1 `oracle`, F2 `unspecified-high`, F3 `unspecified-high`, F4 `deep`

---

## TODOs

- [x] 1. **Phase 0 — Fluency Self-Assessment + Foundational Decisions (BLOCKING GATE)**

  **What to do**:
  - Document user's prior fluency on a 0-3 scale in `.sisyphus/evidence/phase-0-assessment.md`:
    - MuJoCo Python (0 = never used, 3 = built non-trivial mjModel programmatically)
    - MCP server building (0 = never, 3 = shipped MCP server with custom tools)
    - IsaacLab internals (0 = never read source, 3 = trained policy with custom env)
    - OSS framework launch experience (0 = none, 3 = shipped framework with real users)
    - Robotics control fundamentals (0 = none, 3 = comfortable with Drake/MoveIt/etc)
  - Decide on the **ship name** (non-Isaac, no NVIDIA trademarks). Examples to consider: `physlab`, `mac-lab`, `apple-bench`, `moss`, `cobble`, etc. Record final pick.
  - Identify the **first user** persona (self / researcher / hobbyist / student / industry) and write 1 paragraph profile
  - Define the **single success metric** for v0.1 (e.g., "anchor demo works reliably for me" vs "100 GitHub stars" vs "lab X uses it")
  - Define the **kill-switch criterion** (specific week + specific evidence → abandon/pivot)
  - Based on fluency scores, **apply scope cut adjustments**:
    - If MuJoCo score ≤ 1: extend Wave 1 by 1 week, cut Task 31 (third high-quality task)
    - If MCP score ≤ 1: extend MCP work (Tasks 10-11) by 3 days, cut Task 41 (demo site)
    - If IsaacLab score ≤ 1: drop Task 42 (IsaacLab compat case study) entirely
    - If OSS-launch score ≤ 1: cut Task 43 polish, reduce docs Task 32 scope by 30%
  - Commit assessment file as `chore(phase-0): record fluency self-assessment and scope adjustments`

  **Must NOT do**:
  - Skip the assessment or fake high scores ("just to start" — this gate exists to prevent burnout)
  - Pick a ship name containing "isaac", "omniverse", "nvidia"
  - Defer scope cuts to mid-plan; decide them now based on honest scores

  **Recommended Agent Profile**:
  - **Category**: `quick` — this is a structured questionnaire + decision recording task, not a complex implementation
    - Reason: structured user-facing data capture, no architecture
  - **Skills**: `[]` — no skills required; just guided form-filling
  - **Skills Evaluated but Omitted**: `customize-opencode` (not relevant — this is plan execution, not opencode config)

  **Parallelization**:
  - **Can Run In Parallel**: NO (blocking gate)
  - **Parallel Group**: Sequential (Phase 0 alone)
  - **Blocks**: ALL tasks 2-43
  - **Blocked By**: None (entry point)

  **References**:

  **Pattern References**: None (greenfield)

  **API/Type References**: None

  **Test References**: None

  **External References**:
  - Metis review notes (in this planning session): explicit list of fluency questions and scope-adjustment rules
  - "Rule of Three" reference: https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming) — for understanding why deferring abstractions is wise

  **WHY Each Reference Matters**:
  - Metis review: rationale for why this gate exists; rules for cut sizing
  - Rule of Three: principle behind why v0.1 hardcodes MuJoCo + opencode rather than building plug-in machinery upfront

  **Acceptance Criteria**:

  > AGENT-EXECUTABLE VERIFICATION ONLY.

  - [ ] File `.sisyphus/evidence/phase-0-assessment.md` exists and contains all 5 fluency scores (0-3 each)
  - [ ] File contains a "Ship Name" section with a single chosen name (matched against pattern `^[a-z][a-z0-9-]*$`, not containing 'isaac', 'omniverse', or 'nvidia' case-insensitive)
  - [ ] File contains a "First User" section with ≥3 sentences
  - [ ] File contains a "Success Metric" section with one measurable criterion
  - [ ] File contains a "Kill-Switch" section with (week, evidence) pair
  - [ ] File contains "Scope Adjustments" section explicitly listing applied cuts based on rules above
  - [ ] Validation script `python tools/validate_phase_0.py` returns exit 0 (must be created as part of this task)

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Happy path - valid assessment
    Tool: Bash
    Preconditions: `.sisyphus/evidence/phase-0-assessment.md` written; `tools/validate_phase_0.py` exists
    Steps:
      1. Run: python tools/validate_phase_0.py
      2. Capture exit code and stdout
      3. Assert exit code == 0
      4. Assert stdout contains "ALL CHECKS PASSED"
    Expected Result: Exit 0, stdout reports passing
    Failure Indicators: Exit non-zero, missing field reported, ship name violates pattern
    Evidence: .sisyphus/evidence/task-1-phase0-happy.txt

  Scenario: Failure - invalid ship name containing "isaac"
    Tool: Bash
    Preconditions: Temporary copy of phase-0-assessment.md with ship name "isaac-clone"
    Steps:
      1. Run: python tools/validate_phase_0.py --file=/tmp/bad-assessment.md
      2. Assert exit code != 0
      3. Assert stderr contains "ship name violates pattern" or "contains forbidden token"
    Expected Result: Exit non-zero with clear error message
    Evidence: .sisyphus/evidence/task-1-phase0-bad-name.txt
  ```

  **Evidence to Capture**:
  - [ ] task-1-phase0-happy.txt (validation green)
  - [ ] task-1-phase0-bad-name.txt (negative scenario)
  - [ ] phase-0-assessment.md (the actual recorded answers)

  **Commit**: YES
  - Message: `chore(phase-0): record fluency self-assessment, ship name, and scope adjustments [T-1]`
  - Files: `.sisyphus/evidence/phase-0-assessment.md`, `tools/validate_phase_0.py`
  - Pre-commit: `python tools/validate_phase_0.py`

- [x] 2. **Monorepo Scaffolding & Toolchain Setup**

  **What to do**:
  - Initialize the repository at workspace root: `<ship-name>/` (using the name decided in Task 1)
  - Set up dual-language monorepo:
    - Python core: `pyproject.toml` with `[project]` metadata, `[project.optional-dependencies]` for dev/test/docs, `[tool.ruff]`, `[tool.mypy]` strict, `[tool.pytest.ini_options]`
    - TypeScript MCP server: `mcp-server/package.json` with bun as runtime, `tsconfig.json` strict mode, `biome.json` for lint+format (or eslint + prettier — choose one, prefer biome for speed)
  - Directory layout:
    ```
    <ship-name>/
      pyproject.toml
      src/<ship_name>/
        __init__.py
        protocols.py       # Task 5
        env.py             # Task 8
        registry.py        # Task 8
        backends/
          __init__.py
          mujoco.py        # Task 6
          mock.py          # Task 7
        tasks/
          __init__.py
          cartpole.py      # Task 9
      tests/
        unit/
        integration/
      mcp-server/
        package.json
        src/
          server.ts        # Task 10
          tools/           # Task 11
        tests/
      examples/
      docs/
      tools/
        validate_phase_0.py
      .github/
        workflows/
          ci.yml           # Task 3
          licenses.yml     # Task 4
      .gitignore
      LICENSE              # MIT
      README.md            # stub
      CHANGELOG.md         # stub
    ```
  - Configure pre-commit hooks: ruff (Python), biome or eslint+prettier (TS), trailing-whitespace
  - Add `LICENSE` (MIT, current year, real attribution)
  - Add minimal `README.md` with project name, one-line description, and "Status: under construction"
  - Add `.editorconfig` for consistency

  **Must NOT do**:
  - Don't add unused tools "for future" (no Poetry if using uv, no Conda)
  - Don't add packaging configs for PyPI/npm yet (deferred to Task 37/38)
  - Don't include any code referencing Drake/Taichi/VLA libraries

  **Recommended Agent Profile**:
  - **Category**: `quick` — boilerplate scaffolding
    - Reason: well-understood task, no architecture decisions beyond directory layout
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO at root (creates structure others build on)
  - **Parallel Group**: Wave 1A (BRIDGE — foundation, gates all Wave 1B+)
  - **Blocks**: 3, 4, 5, 6, 7, 8, 10
  - **Blocked By**: Task 1

  **References**:

  **Pattern References**:
  - Reference layout: typical FastAPI + frontend monorepo (e.g., look at any modern uv-managed Python project)

  **API/Type References**: None yet

  **Test References**: None yet

  **External References**:
  - uv docs (Python package management): https://docs.astral.sh/uv/
  - ruff docs: https://docs.astral.sh/ruff/
  - biome docs: https://biomejs.dev/
  - MIT license template: https://choosealicense.com/licenses/mit/

  **WHY Each Reference Matters**:
  - uv: chosen for fast, modern Python tooling (faster than pip+venv, integrates with pyproject)
  - ruff: replaces flake8+isort+black, fast, monorepo-friendly
  - biome: replaces eslint+prettier for TS, faster, less config
  - MIT template: ensures legal correctness of the central artifact

  **Acceptance Criteria**:

  - [ ] `pyproject.toml` parses cleanly: `python -c "import tomllib; tomllib.loads(open('pyproject.toml').read())"` exit 0
  - [ ] `mcp-server/package.json` parses: `bun --silent -e 'console.log(require("./mcp-server/package.json").name)'` returns ship name
  - [ ] `uv venv && uv pip install -e .` succeeds in fresh venv
  - [ ] `cd mcp-server && bun install` succeeds
  - [ ] `ruff check .` exits 0 (empty codebase, so trivially passes)
  - [ ] `biome check mcp-server/` (or `eslint mcp-server/`) exits 0
  - [ ] `LICENSE` file is exactly MIT text with current year + attribution
  - [ ] `git status` shows clean working tree after commit

  **QA Scenarios**:

  ```
  Scenario: Happy path - fresh checkout install
    Tool: Bash
    Preconditions: rm -rf .venv mcp-server/node_modules
    Steps:
      1. uv venv && source .venv/bin/activate
      2. uv pip install -e .
      3. cd mcp-server && bun install
      4. ruff check .. && biome check . (or substitute eslint)
    Expected Result: All commands exit 0, total wall-clock under 60s on M5 Pro
    Evidence: .sisyphus/evidence/task-2-scaffold-install.txt

  Scenario: Failure - missing pyproject.toml field
    Tool: Bash
    Preconditions: Temporarily corrupt pyproject.toml (remove [project] name)
    Steps:
      1. uv pip install -e . 2>&1 | tee /tmp/install_err.txt
      2. Assert exit non-zero
      3. Assert /tmp/install_err.txt contains "name" or similar field-missing error
    Expected Result: Clear error message identifying missing field
    Evidence: .sisyphus/evidence/task-2-scaffold-corrupt.txt
  ```

  **Evidence to Capture**:
  - [ ] task-2-scaffold-install.txt (clean install success)
  - [ ] task-2-scaffold-corrupt.txt (negative)
  - [ ] Directory listing: `tree -L 3 -I 'node_modules|.venv|__pycache__'` saved as task-2-tree.txt

  **Commit**: YES
  - Message: `chore(scaffold): initialize monorepo with Python core + TS MCP server [T-2]`
  - Files: pyproject.toml, mcp-server/package.json, mcp-server/tsconfig.json, src/<ship_name>/__init__.py, LICENSE, README.md, CHANGELOG.md, .gitignore, .editorconfig, biome.json (or .eslintrc + .prettierrc)
  - Pre-commit: `ruff check . && biome check mcp-server/`

- [x] 3. **GitHub Actions CI Matrix Foundation**

  **What to do**:
  - Create `.github/workflows/ci.yml` with matrix:
    - OSes: `macos-14`, `macos-15`, `ubuntu-22.04`
    - Python: `3.11`, `3.12`
    - Node: `20`
  - Steps in workflow:
    1. checkout
    2. setup-python (matrix)
    3. setup-uv
    4. setup-bun
    5. `uv venv && uv pip install -e .[dev]`
    6. `cd mcp-server && bun install`
    7. `ruff check . && mypy src/`
    8. `biome check mcp-server/` (or eslint)
    9. `pytest -v --cov=<ship_name> --cov-report=xml`
    10. `cd mcp-server && bun test`
    11. Upload coverage artifacts
  - Add status badge stub to README
  - Add `concurrency` group to cancel old runs on new push
  - Add `paths-ignore` for docs-only changes (later, Task 32)

  **Must NOT do**:
  - Don't include Windows runners in v0.1 (per "Must NOT Have")
  - Don't gate merges on coverage % yet (set up but don't enforce; enforcement later in Task 23-29 stabilization wave)
  - Don't add deploy/release steps here (Task 39-40)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: GHA YAML is well-documented; no novel architecture
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (parallel with 4, 5)
  - **Parallel Group**: Wave 1B (PARALLEL — 3 tasks: T3, T4, T5)
  - **Blocks**: 23-29 (the 7 freedom CI tests extend this base workflow)
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - Reference workflows from any well-run Python+TS OSS project (e.g., `astral-sh/ruff`'s `.github/workflows/`)

  **API/Type References**: N/A

  **Test References**: N/A (CI is the meta-test)

  **External References**:
  - GHA matrix docs: https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs
  - setup-uv action: https://github.com/astral-sh/setup-uv
  - setup-bun action: https://github.com/oven-sh/setup-bun

  **WHY Each Reference Matters**:
  - Matrix docs: ensures we set up exclusion/inclusion correctly
  - setup-uv: fastest Python install in CI
  - setup-bun: needed because we use bun, not npm

  **Acceptance Criteria**:

  - [ ] `.github/workflows/ci.yml` exists; `yq` or `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` parses successfully
  - [ ] After commit, `gh workflow list` shows "CI" workflow registered
  - [ ] After push to a feature branch, `gh run watch` shows all matrix jobs running
  - [ ] All jobs green (on empty/stub codebase, ruff/mypy/pytest trivially pass)
  - [ ] Coverage artifact uploaded (visible in `gh run view --log`)

  **QA Scenarios**:

  ```
  Scenario: Happy path - matrix runs and all green
    Tool: Bash
    Preconditions: Committed ci.yml; on a feature branch
    Steps:
      1. git push origin feat/task-3-ci
      2. sleep 10
      3. gh run list --branch feat/task-3-ci --limit 1 --json conclusion,status > /tmp/run.json
      4. # Poll until completion (max 15 min)
      5. Assert all jobs conclusion == "success"
    Expected Result: All matrix jobs pass within 15min
    Evidence: .sisyphus/evidence/task-3-ci-green.json (gh run view output)

  Scenario: Failure - intentional lint error blocks
    Tool: Bash
    Preconditions: Insert a syntax error in src/<ship_name>/__init__.py
    Steps:
      1. git commit -am 'test: break lint'
      2. git push
      3. gh run watch
      4. Assert at least one job conclusion == "failure"
      5. Assert log mentions "ruff" or syntax error
    Expected Result: CI catches the regression
    Evidence: .sisyphus/evidence/task-3-ci-fail.json
  ```

  **Evidence to Capture**:
  - [ ] task-3-ci-green.json
  - [ ] task-3-ci-fail.json
  - [ ] task-3-ci-workflow.yml (committed file copy for audit)

  **Commit**: YES
  - Message: `ci: add base matrix workflow (macOS-14/15, ubuntu-22.04, py3.11/12, node20) [T-3]`
  - Files: `.github/workflows/ci.yml`, README.md (badge stub)
  - Pre-commit: `yq eval . .github/workflows/ci.yml > /dev/null`

- [x] 4. **License Audit Infrastructure**

  **What to do**:
  - Add `licensee` (Ruby gem) or `scancode-toolkit` (Python) for license detection — prefer scancode for cross-platform Python alignment
  - Alternative simpler: `pip-licenses` for Python deps + `license-checker` for npm
  - Create `tools/check_licenses.py` that:
    1. Runs `pip-licenses --format=json`
    2. Filters allowed: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, BSD-3-Clause-Clear, MPL-2.0, Python-2.0, PSF-2.0, ISC, Unlicense, CC0-1.0
    3. Rejects on: GPL-2.0, GPL-3.0, AGPL-3.0, LGPL-3.0, proprietary, unknown
    4. Also runs `license-checker --json` for npm deps and applies same filter
    5. Exits non-zero with file:reason for any violator
  - Add `.github/workflows/licenses.yml` that runs on PR + main:
    1. Install deps
    2. Run `python tools/check_licenses.py`
  - Add to base CI (Task 3) as a separate job (not blocking on matrix completion, but blocking merge to main)
  - Document allowed license policy in `CONTRIBUTING.md` (stub for now, expand in Task 43)

  **Must NOT do**:
  - Don't allow GPL/AGPL/LGPL transitively (even if a dep is "fine" — the license-conflict surface is too high for v0.1)
  - Don't write license-detection logic from scratch — use battle-tested tools
  - Don't pin to a specific license-checker version that's already unmaintained

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: routine tooling integration with well-known license-checker libraries
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (parallel with 3, 5)
  - **Parallel Group**: Wave 1B (PARALLEL — 3 tasks: T3, T4, T5)
  - **Blocks**: 23 (freedom test #1)
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - Reference: how kubernetes-sigs projects do license auditing (mature pattern)

  **API/Type References**: N/A

  **Test References**:
  - Will test via Task 23 (the freedom CI test that exercises this infrastructure)

  **External References**:
  - pip-licenses: https://github.com/raimon49/pip-licenses
  - license-checker: https://github.com/davglass/license-checker
  - SPDX license list: https://spdx.org/licenses/

  **WHY Each Reference Matters**:
  - pip-licenses: industry-standard Python license detection
  - license-checker: standard npm license auditing
  - SPDX: canonical identifiers; ensures our allow/deny list uses correct names

  **Acceptance Criteria**:

  - [ ] `tools/check_licenses.py` exists and is executable
  - [ ] `python tools/check_licenses.py` on the current dependency tree exits 0 (no violators)
  - [ ] Inserting a deliberately-rejected dependency (e.g., `pip install --dry-run some-gpl-pkg` simulated) makes the check fail with a clear message
  - [ ] `.github/workflows/licenses.yml` runs successfully on a PR

  **QA Scenarios**:

  ```
  Scenario: Happy path - clean dependency tree
    Tool: Bash
    Preconditions: Dependencies installed per Task 2
    Steps:
      1. python tools/check_licenses.py
      2. Capture exit code and stdout
      3. Assert exit code == 0
      4. Assert stdout contains "0 violations" or similar
    Expected Result: Exit 0, ≥10 dependencies scanned, 0 violations
    Evidence: .sisyphus/evidence/task-4-licenses-clean.txt

  Scenario: Failure - inject GPL violator into allowlist test
    Tool: Bash
    Preconditions: Mock pip-licenses output containing a GPL-licensed package via fixture file
    Steps:
      1. python tools/check_licenses.py --fixture=tests/fixtures/gpl_violator.json
      2. Assert exit code != 0
      3. Assert stderr contains "GPL" and package name
    Expected Result: Exit non-zero, package name + license cited
    Evidence: .sisyphus/evidence/task-4-licenses-violator.txt
  ```

  **Evidence to Capture**:
  - [ ] task-4-licenses-clean.txt
  - [ ] task-4-licenses-violator.txt
  - [ ] Allowed/rejected license list documented in `tools/check_licenses.py` docstring

  **Commit**: YES
  - Message: `feat(licenses): add license-audit tooling and CI gate [T-4]`
  - Files: tools/check_licenses.py, .github/workflows/licenses.yml, CONTRIBUTING.md (stub), tests/fixtures/gpl_violator.json
  - Pre-commit: `python tools/check_licenses.py`

- [x] 5. **Type & Protocol Definitions (Backend, Env, Task, Specs)**

  **What to do**:
  - Create `src/<ship_name>/protocols.py` defining (using `typing.Protocol` + `runtime_checkable`):
    - `Backend` — `load_model(spec) -> ModelHandle`, `step(handle, action) -> StepResult`, `reset(handle, seed=None) -> Observation`, `close(handle) -> None`, `name() -> str`, `is_deterministic_for(device) -> bool`
    - `Env` — `reset(seed=None) -> tuple[Observation, Info]`, `step(action) -> tuple[Observation, float, bool, bool, Info]`, `action_space`, `observation_space`, properties
    - `Task` — `name`, `make_env() -> Env`, `success_metric(rollout) -> float`, `reward_signature() -> str`
    - `ObsSpec`, `ActionSpec` (use NumPy arrays + dataclasses for shape/dtype/low/high)
  - Add `__all__` exports, full type hints, docstrings ≤3 lines each (no bloat)
  - Write tests in `tests/unit/test_protocols.py`:
    - Protocol structural matching: define a dummy class, assert `isinstance(dummy, Backend)` post-runtime_checkable
    - Spec validation: invalid shape raises typed error
  - Add `py.typed` marker file so consumers get type info

  **Must NOT do**:
  - Don't add abstract base classes (`ABC`) — use `Protocol` for structural typing (more flexible, OSS-friendly)
  - Don't define a `PolicyServer` protocol with implementation here (stub interface only goes in `protocols.py` per Metis cuts)
  - Don't bind to a specific tensor library (NumPy only; JAX/PyTorch are consumers' choice)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: protocol design has long downstream consequences; type ergonomics matter
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 3, 4, 6 once 2 is done)
  - **Parallel Group**: Wave 1B (PARALLEL — 3 tasks: T3, T4, T5)
  - **Blocks**: 6, 7, 8, 11
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - `gymnasium.Env` Protocol-like API: https://gymnasium.farama.org/api/env/ — our `Env` mirrors this shape so users feel at home
  - `dm_env.Environment` interface: https://github.com/google-deepmind/dm_env — alternative reference for spec types

  **API/Type References**:
  - `typing.Protocol` PEP 544: https://peps.python.org/pep-0544/
  - `dataclasses.dataclass` for spec types

  **Test References**:
  - `runtime_checkable` testing patterns: pytest's protocol assertions

  **External References**:
  - PEP 484 type hints: https://peps.python.org/pep-0484/
  - `py.typed` marker: PEP 561

  **WHY Each Reference Matters**:
  - Gymnasium: largest existing RL env community; mimicking their shape lowers adoption barrier
  - dm_env: cleaner spec model; we borrow the spec-class pattern
  - PEP 544: ensures we use Protocol correctly, not ABC

  **Acceptance Criteria**:

  - [ ] `src/<ship_name>/protocols.py` exists with all 5 protocols + 2 spec dataclasses
  - [ ] `mypy --strict src/<ship_name>/` passes on protocols module
  - [ ] `pytest tests/unit/test_protocols.py -v` all green (≥6 tests covering each protocol)
  - [ ] `py.typed` marker file exists in `src/<ship_name>/`
  - [ ] `python -c "from <ship_name>.protocols import Backend, Env, Task; print('OK')"` returns "OK"

  **QA Scenarios**:

  ```
  Scenario: Happy path - protocols importable and runtime-checkable
    Tool: Bash
    Preconditions: Task 2 done, venv active
    Steps:
      1. python -c "from <ship_name>.protocols import Backend; class M: 
          def load_model(self, spec): pass
          def step(self, h, a): pass
          def reset(self, h, seed=None): pass
          def close(self, h): pass
          def name(self): return 'mock'
          def is_deterministic_for(self, d): return True
        assert isinstance(M(), Backend)"
      2. Capture exit code
    Expected Result: Exit 0
    Evidence: .sisyphus/evidence/task-5-protocols-runtime.txt

  Scenario: Failure - missing required method raises clear error
    Tool: Bash
    Preconditions: Same as above
    Steps:
      1. python -c "from <ship_name>.protocols import Backend; class B: pass; assert not isinstance(B(), Backend)"
      2. Assert exit 0 (the assertion holds: incomplete class is NOT Backend)
    Expected Result: Exit 0; demonstrates Protocol correctly rejects incomplete impls
    Evidence: .sisyphus/evidence/task-5-protocols-reject.txt
  ```

  **Evidence to Capture**:
  - [ ] task-5-protocols-runtime.txt
  - [ ] task-5-protocols-reject.txt
  - [ ] pytest output: task-5-protocols-tests.txt

  **Commit**: YES
  - Message: `feat(protocols): define Backend, Env, Task, ObsSpec, ActionSpec protocols [T-5]`
  - Files: src/<ship_name>/protocols.py, src/<ship_name>/py.typed, tests/unit/test_protocols.py
  - Pre-commit: `ruff check . && mypy --strict src/<ship_name>/protocols.py && pytest tests/unit/test_protocols.py`

- [x] 6. **MuJoCo Wrapper Core**

  **What to do**:
  - Implement `src/<ship_name>/backends/mujoco.py`:
    - `MuJoCoBackend` class implementing `Backend` protocol
    - Uses Python `mujoco` package (pin `mujoco>=3.2,<4`)
    - `load_model(spec: dict | Path) -> ModelHandle` — accepts MJCF file path or in-memory MJCF XML string
    - `step(handle, action: np.ndarray) -> StepResult` — applies action to ctrl, calls `mj_step`, returns observation (qpos + qvel concatenated as default)
    - `reset(handle, seed: int | None = None) -> Observation` — resets data, sets initial state with optional seed-controlled randomization (via spec hooks)
    - `close(handle)` — releases mj_model, mj_data
    - Internal: cache model load by absolute path hash; thread-safe via `threading.Lock`
  - `ModelHandle` dataclass: `model_id: str, model: mujoco.MjModel, data: mujoco.MjData, spec_hash: str`
  - Determinism: when seed provided, identical (qpos, qvel) trajectory for same model+action sequence (CPU)
  - Tests in `tests/unit/test_mujoco_backend.py`:
    - Load minimal MJCF (e.g., single pendulum), step 100 times, no exceptions
    - Reset with seed=42 twice → identical first observation, bit-exact
    - Action clipping respects MJCF `ctrlrange`
    - Close releases memory (mock test or weak ref check)
  - Tests in `tests/integration/test_mujoco_contract.py`: run the protocol contract test from Task 7 against `MuJoCoBackend`

  **Must NOT do**:
  - Don't add GPU-specific MuJoCo paths (MJX) — MuJoCo CPU only in v0.1
  - Don't fork to subprocess for parallelism (single-process for v0.1; vectorization is v0.2)
  - Don't expose MuJoCo internals (mjModel, mjData) directly to consumers; wrap them
  - Don't import `mujoco.viewer` in the core (visualization is a Task 22/41 concern)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: MuJoCo Python API has subtle quirks (contact handling, qpos vs xpos, seed semantics)
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T7, T10)
  - **Parallel Group**: Wave 1C (PARALLEL — with T7, T10 after Wave 1B)
  - **Blocks**: 8, 9, 12, 13
  - **Blocked By**: Task 2, Task 5

  **References**:

  **Pattern References**:
  - `dm_control/mujoco/wrapper/core.py` — DeepMind's MuJoCo wrapper (reference for design choices like handle dataclass)
  - `gymnasium-robotics`'s MuJoCo env wrappers (BSD-3, similar shape we'd ship)

  **API/Type References**:
  - MuJoCo Python API: https://mujoco.readthedocs.io/en/stable/python.html
  - `mujoco.MjModel`, `mujoco.MjData`, `mj_step`, `mj_resetData`

  **Test References**:
  - `gymnasium-robotics`'s test suite for backend contract tests

  **External References**:
  - MuJoCo documentation: https://mujoco.readthedocs.io/
  - Apache-2.0 license attribution requirements (we include in NOTICE)

  **WHY Each Reference Matters**:
  - dm_control: shows how to abstract MuJoCo cleanly; we borrow the handle pattern
  - gymnasium-robotics: tests we should run against our backend
  - MuJoCo docs: API surface, especially gotchas like mj_forward vs mj_step

  **Acceptance Criteria**:

  - [ ] `MuJoCoBackend` implements `Backend` protocol: `isinstance(MuJoCoBackend(), Backend)` is True
  - [ ] Load minimal MJCF, step 100 times, no exceptions; `pytest tests/unit/test_mujoco_backend.py::test_step_100` passes
  - [ ] Determinism (CPU): two resets with `seed=42` produce identical `qpos[0]` byte-for-byte; test `test_reset_determinism` passes
  - [ ] Memory release: after `close()`, `gc.collect()` weakref check confirms model is freed
  - [ ] Contract test: `pytest tests/integration/test_mujoco_contract.py` passes (the same suite runs against MockBackend in Task 7)
  - [ ] Coverage on `mujoco.py` ≥ 85% line coverage

  **QA Scenarios**:

  ```
  Scenario: Happy path - load pendulum, step 1000 times
    Tool: Bash
    Preconditions: Task 2, 5 complete; minimal MJCF at tests/fixtures/pendulum.xml
    Steps:
      1. python -c "
        from <ship_name>.backends.mujoco import MuJoCoBackend
        b = MuJoCoBackend()
        h = b.load_model('tests/fixtures/pendulum.xml')
        obs = b.reset(h, seed=42)
        for i in range(1000):
            obs = b.step(h, action=[0.0])
        print(f'final_qpos={obs[0]:.4f}')
      "
      2. Capture stdout
      3. Assert no traceback, stdout contains "final_qpos="
    Expected Result: Clean run, deterministic final qpos for seed=42
    Evidence: .sisyphus/evidence/task-6-mujoco-step1000.txt

  Scenario: Failure - invalid action shape raises typed error
    Tool: Bash
    Preconditions: As above
    Steps:
      1. python -c "
        from <ship_name>.backends.mujoco import MuJoCoBackend
        b = MuJoCoBackend()
        h = b.load_model('tests/fixtures/pendulum.xml')
        b.reset(h, seed=0)
        try:
          b.step(h, action=[1.0, 2.0, 3.0])  # wrong shape
        except ValueError as e:
          print(f'OK: {e}')
      "
      2. Assert stdout contains "OK:" and shape-related error message
    Expected Result: Typed ValueError with helpful message ("expected shape (1,), got (3,)")
    Evidence: .sisyphus/evidence/task-6-mujoco-bad-action.txt
  ```

  **Evidence to Capture**:
  - [ ] task-6-mujoco-step1000.txt
  - [ ] task-6-mujoco-bad-action.txt
  - [ ] pytest output: task-6-mujoco-tests.txt
  - [ ] Coverage report excerpt: task-6-mujoco-coverage.txt

  **Commit**: YES
  - Message: `feat(backends/mujoco): implement MuJoCo backend with deterministic seed [T-6]`
  - Files: src/<ship_name>/backends/mujoco.py, tests/unit/test_mujoco_backend.py, tests/fixtures/pendulum.xml, NOTICE (Apache-2.0 attribution)
  - Pre-commit: `ruff check . && mypy src/<ship_name>/backends/ && pytest tests/unit/test_mujoco_backend.py`

- [x] 7. **Mock Backend (Contract Test Substrate)**

  **What to do**:
  - Implement `src/<ship_name>/backends/mock.py`:
    - `MockBackend` class implementing `Backend` protocol
    - In-memory state: `(qpos: np.ndarray, qvel: np.ndarray)` per handle
    - `step` updates state via deterministic linear dynamics: `qpos' = qpos + dt * qvel`, `qvel' = qvel + dt * action`
    - `reset(seed)` reseeds via `numpy.random.default_rng(seed)` for randomized initial state
    - `is_deterministic_for("cpu") == True`, `is_deterministic_for("mps") == False`
    - Lightweight, zero external deps beyond numpy
  - Write **shared contract test** `tests/integration/test_backend_contract.py`:
    - Parametrize over `[MuJoCoBackend, MockBackend]`
    - For each: test reset determinism, action shape validation, step monotonic time, close releases
    - This same test file is used in Task 24 (CI test #2: Backend protocol contract test)

  **Must NOT do**:
  - Don't make MockBackend production-realistic (it's a fixture, not a sim engine)
  - Don't add randomness without seed control (breaks contract test)
  - Don't depend on MuJoCo from this file (must work standalone for isolated testing)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: small, well-scoped fixture; main value is the contract test
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T6, T10)
  - **Parallel Group**: Wave 1C (PARALLEL — with T6, T10 after Wave 1B)
  - **Blocks**: 12 (vertical slice integration), 24 (CI test)
  - **Blocked By**: Task 5

  **References**:

  **Pattern References**:
  - `pytest.fixture`-based mocks in popular Python libs (e.g., `httpx`'s `MockTransport`)

  **API/Type References**:
  - `numpy.random.default_rng` API

  **Test References**:
  - `pytest.mark.parametrize` for shared contract suites: https://docs.pytest.org/en/latest/how-to/parametrize.html

  **External References**:
  - "Contract testing" pattern: https://martinfowler.com/bliki/ContractTest.html

  **WHY Each Reference Matters**:
  - Martin Fowler contract testing: rationale for running same test against multiple impls
  - pytest parametrize: idiomatic way to write the shared suite

  **Acceptance Criteria**:

  - [ ] `MockBackend` implements `Backend` protocol: `isinstance(MockBackend(), Backend)` is True
  - [ ] `tests/integration/test_backend_contract.py` exists; runs against both MuJoCoBackend and MockBackend
  - [ ] All contract tests green for both backends
  - [ ] MockBackend has zero deps beyond numpy: `python -c "import sys; from <ship_name>.backends.mock import MockBackend; assert 'mujoco' not in sys.modules"` exits 0

  **QA Scenarios**:

  ```
  Scenario: Happy path - contract test green for both backends
    Tool: Bash
    Preconditions: Tasks 5, 6 done
    Steps:
      1. pytest tests/integration/test_backend_contract.py -v 2>&1 | tee /tmp/contract.txt
      2. Assert exit 0
      3. Assert stdout contains "test_backend_contract[MuJoCoBackend]" PASSED
      4. Assert stdout contains "test_backend_contract[MockBackend]" PASSED
    Expected Result: Both backends pass contract
    Evidence: .sisyphus/evidence/task-7-contract-both.txt

  Scenario: Failure - regression: break MockBackend reset, contract test catches it
    Tool: Bash
    Preconditions: Temporarily modify MockBackend.reset to ignore seed
    Steps:
      1. pytest tests/integration/test_backend_contract.py::test_reset_determinism -v
      2. Assert exit != 0
      3. Assert output mentions MockBackend reset determinism failure
    Expected Result: Contract test catches the regression in MockBackend
    Evidence: .sisyphus/evidence/task-7-contract-regression.txt
  ```

  **Evidence to Capture**:
  - [ ] task-7-contract-both.txt
  - [ ] task-7-contract-regression.txt
  - [ ] pytest verbose output: task-7-pytest.txt

  **Commit**: YES
  - Message: `feat(backends/mock): add MockBackend + shared backend contract test [T-7]`
  - Files: src/<ship_name>/backends/mock.py, tests/integration/test_backend_contract.py
  - Pre-commit: `pytest tests/integration/test_backend_contract.py -v`

- [x] 8. **Env API + Task Registry**

  **What to do**:
  - Implement `src/<ship_name>/env.py`:
    - `class Environment` implementing `Env` protocol, wrapping a `Backend` + `Task`
    - `Environment.__init__(backend: Backend, task: Task, seed: int | None = None)`
    - `reset(seed) -> (obs, info)`, `step(action) -> (obs, reward, terminated, truncated, info)`
    - Action/observation space derived from task spec
    - Episode termination via task callback + step-count truncation
  - Implement `src/<ship_name>/registry.py`:
    - `register_task(name: str, task_factory: Callable[[], Task]) -> None` — explicit function call only
    - `make(name: str, backend: Backend | str = "mujoco", seed: int | None = None) -> Environment`
    - `list_tasks() -> list[str]`
    - Internal module-level dict `_TASKS: dict[str, Callable[[], Task]]` (private)
    - **NO `entry_points` discovery / NO `importlib.metadata` walks** — users must explicitly call `register_task()` (typically via side-effect import of their module)
    - Built-in tasks (cartpole, franka_pick, etc.) register themselves at import time of `<ship_name>.tasks.__init__` (which imports each task module)
  - Tests `tests/unit/test_env.py`, `tests/unit/test_registry.py`:
    - Register dummy task, make(), step 10 times, no exception
    - Unknown task name raises `TaskNotRegisteredError` with helpful message listing available
    - Backend string "mujoco" resolves to `MuJoCoBackend`, "mock" resolves to `MockBackend`
    - Guardrail test: grep src/<ship_name>/registry.py — assert NO occurrence of `entry_points` or `importlib.metadata`

  **Must NOT do**:
  - Don't use `entry_points` / `importlib.metadata` discovery (per plan-wide "no plug-in machinery" guardrail; deferred to v0.2 with explicit Oracle review at that point)
  - Don't add an OpenAI Gym `gym.make`-style global registry singleton — use explicit module-level dict for now
  - Don't bind reward computation here; reward is task's responsibility
  - Don't add auto-loading from any path — registration is purely explicit

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: API surface choices here are sticky (public API), need careful design
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 1D is a BRIDGE — single-task wave, structural bottleneck after T6+T7)
  - **Parallel Group**: Wave 1D (BRIDGE — depends on T5+T6+T7; gates T9, T11)
  - **Blocks**: 9, 11, 12, 13, 26, 30, 31
  - **Blocked By**: Tasks 5, 6, 7

  **References**:

  **Pattern References**:
  - `gymnasium.envs.registry` (Farama Foundation, MIT) — registry pattern (we take the dict-based core, NOT their entry_points layer)
  - `Hydra` instantiation pattern (Apache-2.0) — alternative if we want config-driven later (deferred to v0.2)

  **API/Type References**:
  - `<ship_name>.protocols.Env`, `Task`, `Backend` (defined in Task 5)

  **Test References**:
  - Task 7's contract test pattern — apply same idea to Env

  **External References**:
  - "Side-effect imports" Python idiom: https://docs.python.org/3/tutorial/modules.html#executing-modules-as-scripts (the mechanism users will rely on to trigger registration)

  **WHY Each Reference Matters**:
  - Gymnasium registry: largest community pattern, our shape should be discoverable to them (minus the discovery layer)
  - Side-effect imports: the entire user-facing registration mechanism. Users write a task module that calls `register_task()` at top level; importing the module is the trigger.

  **Acceptance Criteria**:

  - [ ] `Environment` implements `Env` protocol
  - [ ] `make("test_task", "mock", seed=42)` returns Environment that runs 100 steps cleanly
  - [ ] `make("nonexistent")` raises `TaskNotRegisteredError` with available tasks listed
  - [ ] `list_tasks()` returns sorted list including built-ins
  - [ ] Coverage on env.py + registry.py ≥ 85%

  **QA Scenarios**:

  ```
  Scenario: Happy path - register and make
    Tool: Bash
    Preconditions: Tasks 5-7 done
    Steps:
      1. python -c "
        from <ship_name> import make, register_task, list_tasks
        from <ship_name>.protocols import Task
        # register a dummy task
        class DummyTask:
            name = 'dummy'
            def make_env(self): ...
            def success_metric(self, r): return 0.0
            def reward_signature(self): return 'r=0'
        register_task('dummy', DummyTask)
        assert 'dummy' in list_tasks()
        print('OK')
      "
      2. Assert exit 0, stdout contains "OK"
    Expected: Clean run
    Evidence: .sisyphus/evidence/task-8-env-happy.txt

  Scenario: Failure - unknown task name
    Tool: Bash
    Steps:
      1. python -c "
        from <ship_name> import make
        try:
          make('does_not_exist')
        except Exception as e:
          assert 'TaskNotRegisteredError' in type(e).__name__
          assert 'does_not_exist' in str(e)
          print('OK')
      "
      2. Assert exit 0, stdout "OK"
    Expected: Typed error with helpful message
    Evidence: .sisyphus/evidence/task-8-env-unknown.txt
  ```

  **Evidence**: task-8-env-happy.txt, task-8-env-unknown.txt, task-8-env-tests.txt

  **Commit**: YES
  - Message: `feat(env): add Environment + Task registry with backend resolution [T-8]`
  - Files: src/<ship_name>/env.py, src/<ship_name>/registry.py, src/<ship_name>/__init__.py (re-exports), tests/unit/test_env.py, tests/unit/test_registry.py
  - Pre-commit: `pytest tests/unit/test_env.py tests/unit/test_registry.py -v`

- [x] 9. **First Toy Task — Cartpole (Smoke Test)**

  **What to do**:
  - Implement `src/<ship_name>/tasks/cartpole.py`:
    - MJCF model embedded (or in `assets/cartpole.xml`): cart on rail, pole hinge, single ctrl actuator
    - `CartpoleTask` implementing `Task` protocol
    - Reward: standard `1.0` per timestep pole upright (angle < 0.2 rad)
    - Terminates at: pole_angle > 0.2 rad or |cart_x| > 2.4 or step > 500
    - `success_metric(rollout) = mean_episode_length / 500`
  - Auto-register on import via side-effect (module-level `register_task()` call in `cartpole.py`). NO `entry_points` discovery — that is explicitly v0.2-only per the plan-wide "no plug-in machinery" guardrail.
  - Tests `tests/integration/test_cartpole.py`:
    - `make("cartpole", "mujoco")` runs 100 steps with random actions, no exception
    - Episode terminates within 500 steps with random policy
    - Deterministic with seed (CPU)

  **Must NOT do**:
  - Don't tune for SOTA RL performance; this is a smoke test
  - Don't add multiple cartpole variants (single one is enough for v0.1)
  - Don't pull from gymnasium's cartpole — we own the MJCF for clarity

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: classic task, well-understood, copy-paste-adapt pattern
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T11 after T8 + T10)
  - **Parallel Group**: Wave 1E (PARALLEL-PAIR — with T11; structural 2-task minimum)
  - **Blocks**: 12 (vertical slice uses this)
  - **Blocked By**: Tasks 6, 8

  **References**:

  **Pattern References**:
  - `dm_control/suite/cartpole.py` — DeepMind's MJCF cartpole (Apache-2.0); we adapt the model structure
  - `gymnasium`'s CartPole-v1 — for reward / termination conventions

  **API/Type References**:
  - `<ship_name>.protocols.Task`

  **Test References**:
  - `tests/integration/test_backend_contract.py` pattern from Task 7

  **External References**:
  - MuJoCo MJCF reference: https://mujoco.readthedocs.io/en/stable/XMLreference.html

  **WHY Each Reference Matters**:
  - dm_control cartpole: battle-tested MJCF; we copy structure under Apache-2.0 attribution
  - Gymnasium CartPole conventions: matches users' mental model

  **Acceptance Criteria**:

  - [ ] `CartpoleTask` registered: `"cartpole" in list_tasks()`
  - [ ] `make("cartpole", "mujoco")` produces working Environment
  - [ ] Random policy completes 100+ steps without exception in pytest
  - [ ] Deterministic CPU: two `reset(seed=42)` → identical first obs (bit-exact)

  **QA Scenarios**:

  ```
  Scenario: Happy path - smoke run
    Tool: Bash
    Steps:
      1. python -c "
        from <ship_name> import make
        env = make('cartpole', 'mujoco')
        obs, _ = env.reset(seed=42)
        for _ in range(100):
            obs, r, term, trunc, _ = env.step(env.action_space.sample())
            if term or trunc: break
        print(f'steps={_+1}')
      "
      2. Assert exit 0, stdout contains "steps="
    Evidence: .sisyphus/evidence/task-9-cartpole-smoke.txt

  Scenario: Failure - invalid backend
    Tool: Bash
    Steps:
      1. python -c "
        from <ship_name> import make
        try: make('cartpole', 'invalid_backend')
        except Exception as e: print(f'OK: {type(e).__name__}')
      "
      2. Assert exit 0, "OK:" prefix
    Evidence: .sisyphus/evidence/task-9-cartpole-bad-backend.txt
  ```

  **Evidence**: task-9-cartpole-smoke.txt, task-9-cartpole-bad-backend.txt

  **Commit**: YES
  - Message: `feat(tasks): add cartpole task (smoke-test target) [T-9]`
  - Files: src/<ship_name>/tasks/cartpole.py, src/<ship_name>/assets/cartpole.xml, tests/integration/test_cartpole.py, NOTICE (dm_control attribution)
  - Pre-commit: `pytest tests/integration/test_cartpole.py -v`

- [x] 10. **MCP Server Skeleton (TypeScript, JSON-RPC)**

  **What to do**:
  - Implement `mcp-server/src/server.ts`:
    - Use official MCP SDK: `@modelcontextprotocol/sdk` (preferred) — confirms canonical patterns
    - Server listens on stdio (default for MCP) AND HTTP (configurable port, default 8765) for development
    - Register handler for `tools/list`, `tools/call`, `resources/list`, `resources/read`
    - Initial tool: `ping` (returns "pong", echo arg) — proves wiring works
    - Logging via `pino` (lightweight, JSON-structured)
    - Health check endpoint `/healthz` for ops
  - Type-safe tool registration: each tool has `{name, description, inputSchema (JSON Schema), handler}`
  - Unit tests `mcp-server/tests/server.test.ts` using `bun:test`:
    - Server starts, responds to `tools/list` with `ping`
    - `tools/call` with `ping {msg: "hi"}` returns "pong: hi"
    - Invalid tool name returns JSON-RPC error code -32601
    - Schema validation: missing required arg returns -32602

  **Must NOT do**:
  - Don't implement sim tools here (Task 11)
  - Don't expose tools without strict JSON Schema validation (security)
  - Don't add auth in v0.1 (single-user local; documented as risk)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: MCP protocol details + JSON-RPC error handling + TS strict mode
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 9)
  - **Parallel Group**: Wave 1C (PARALLEL — with T6, T7; orthogonal dep only on T2)
  - **Blocks**: 11, 12
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - Reference MCP servers in `modelcontextprotocol/servers` GitHub org — many MIT examples

  **API/Type References**:
  - `@modelcontextprotocol/sdk` README and TS types
  - JSON-RPC 2.0 spec: https://www.jsonrpc.org/specification

  **Test References**:
  - bun:test docs: https://bun.sh/docs/cli/test
  - MCP integration tests in `modelcontextprotocol/servers/src/filesystem`

  **External References**:
  - MCP spec: https://spec.modelcontextprotocol.io/
  - pino logger: https://github.com/pinojs/pino

  **WHY Each Reference Matters**:
  - MCP SDK: canonical patterns; ensures interop with Claude/opencode/codex
  - JSON-RPC spec: ensures error codes correct for the freedom test (Task 27)
  - MCP example servers: prove the wiring patterns work in production

  **Acceptance Criteria**:

  - [ ] `bun run mcp-server` (or `bun mcp-server/src/server.ts`) starts the server, prints "listening on stdio + http://localhost:8765"
  - [ ] `curl -X POST http://localhost:8765 -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' | jq '.result.tools[0].name'` returns `"ping"`
  - [ ] `curl ... tools/call name=ping args={"msg":"hi"} ...` returns "pong: hi"
  - [ ] Invalid tool returns JSON-RPC error -32601
  - [ ] `bun test mcp-server/tests/server.test.ts` all green
  - [ ] `bun run typecheck` exits 0 (strict TS)

  **QA Scenarios**:

  ```
  Scenario: Happy path - server starts and tools/list works
    Tool: interactive_bash (tmux for server lifecycle)
    Preconditions: bun install done
    Steps:
      1. tmux new-window -d 'bun run mcp-server'
      2. sleep 2
      3. curl -sS -X POST http://localhost:8765 -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' > /tmp/tools.json
      4. Assert jq '.result.tools | length' >= 1
      5. tmux kill-window -t mcp-server
    Expected: tools/list returns valid JSON with ≥1 tool
    Evidence: .sisyphus/evidence/task-10-mcp-tools-list.json

  Scenario: Failure - invalid tool name returns -32601
    Tool: Bash
    Steps:
      1. # (server still running or restart)
      2. curl -sS -X POST http://localhost:8765 -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"nope"},"id":2}' | jq '.error.code'
      3. Assert output == -32601
    Expected: JSON-RPC method-not-found error
    Evidence: .sisyphus/evidence/task-10-mcp-invalid.json
  ```

  **Evidence**: task-10-mcp-tools-list.json, task-10-mcp-invalid.json, task-10-mcp-tests.txt

  **Commit**: YES
  - Message: `feat(mcp): MCP server skeleton with ping tool and JSON-RPC handling [T-10]`
  - Files: mcp-server/src/server.ts, mcp-server/src/tools/ping.ts, mcp-server/tests/server.test.ts, mcp-server/package.json (deps)
  - Pre-commit: `bun run typecheck && bun test mcp-server/tests/server.test.ts`

- [x] 11. **MCP Sim Tools (sim.make/reset/step/observe + task.list)**

  **What to do**:
  - Implement `mcp-server/src/tools/sim.ts` with 5 tools:
    - `sim.make` — input: `{task: string, backend?: string, seed?: number}`, output: `{handle_id: string, obs_spec, action_spec}`
    - `sim.reset` — input: `{handle_id, seed?}`, output: `{observation: number[], info: object}`
    - `sim.step` — input: `{handle_id, action: number[]}`, output: `{observation, reward, terminated, truncated, info}`
    - `sim.observe` — input: `{handle_id}`, output: `{observation, info}` (no advance)
    - `task.list` — input: `{}`, output: `{tasks: string[]}`
  - Tools invoke Python via subprocess (long-lived `python -u` worker process pool) using stdin/stdout JSON protocol, OR via Python embedded via something like `pyodide`/`pythonmonkey` — **prefer subprocess pool** (simpler, more isolated)
  - Internal: `PythonWorker` class manages worker lifecycle, handle ID registry, request routing
  - JSON Schemas for each tool match `<ship_name>` Python types exactly (use a generator script `tools/gen_schemas.py` from Python protocols → JSON Schemas)
  - Tests `mcp-server/tests/sim_tools.test.ts`:
    - Start worker, call `task.list` → array includes "cartpole"
    - `sim.make("cartpole")` returns handle, then `sim.step(handle, [0])` returns observation array
    - Stale handle returns -32602 error
    - 10 concurrent handles isolated (no state bleed)

  **Must NOT do**:
  - Don't embed Python via FFI (PyO3 / pyo3-bun) — fragile and over-engineered for v0.1
  - Don't add streaming/async tool output yet (v0.2 if needed)
  - Don't expose raw mjModel/mjData — only observation arrays

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: subprocess lifecycle + JSON protocol + handle isolation = nontrivial
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO with 10 (depends on it)
  - **Parallel Group**: Wave 1E (PARALLEL-PAIR — with T9 after T8 + T10)
  - **Blocks**: 12, 15, 20, 27
  - **Blocked By**: Tasks 8, 10

  **References**:

  **Pattern References**:
  - `modelcontextprotocol/servers/src/everything` — example server with multiple tools (subprocess-style backend optional)
  - `playwright`'s browser pool architecture (subprocess management at scale)

  **API/Type References**:
  - `<ship_name>.protocols.Env` (Python side)
  - MCP `Tool` interface (TS side)

  **Test References**:
  - `bun test` with subprocess fixtures

  **External References**:
  - Node.js `child_process` docs (bun is mostly compatible)
  - JSON Schema 2020-12 (for tool input schemas)

  **WHY Each Reference Matters**:
  - MCP example servers: shows real handler patterns
  - Playwright pool: proven pattern for managing long-lived child processes safely

  **Acceptance Criteria**:

  - [ ] `tools/list` returns ≥6 tools: ping, sim.make, sim.reset, sim.step, sim.observe, task.list
  - [ ] `sim.make("cartpole")` returns handle_id; `sim.step` with that handle works
  - [ ] 10 concurrent `sim.make` handles work, no cross-handle observation leak
  - [ ] Stale handle returns -32602 with clear message
  - [ ] p50 latency for `sim.observe`: <50ms on M5 Pro
  - [ ] `bun test mcp-server/tests/sim_tools.test.ts` all green
  - [ ] JSON Schemas generated by `python tools/gen_schemas.py` match what server registers

  **QA Scenarios**:

  ```
  Scenario: Happy path - full sim cycle via MCP
    Tool: Bash
    Preconditions: Server running (tmux), cartpole task registered
    Steps:
      1. # Make
      2. HANDLE=$(curl -sS -X POST http://localhost:8765 -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"sim.make","arguments":{"task":"cartpole","backend":"mujoco","seed":42}},"id":1}' | jq -r '.result.handle_id')
      3. # Reset
      4. curl -sS -X POST http://localhost:8765 -d "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"sim.reset\",\"arguments\":{\"handle_id\":\"$HANDLE\",\"seed\":42}},\"id\":2}" | jq '.result.observation | length' > /tmp/obs_len.txt
      5. Assert obs_len ≥ 1
      6. # Step
      7. curl -sS -X POST ... sim.step ... action: [0.0] ... | jq '.result.reward'
      8. Assert reward is number (not error)
    Expected: Full cycle clean
    Evidence: .sisyphus/evidence/task-11-mcp-cycle.txt

  Scenario: Failure - stale handle
    Tool: Bash
    Steps:
      1. curl ... sim.step with handle_id="fake-handle-id" ... | jq '.error.code'
      2. Assert -32602 or custom typed error code
    Expected: Typed error, no crash
    Evidence: .sisyphus/evidence/task-11-mcp-stale-handle.json
  ```

  **Evidence**: task-11-mcp-cycle.txt, task-11-mcp-stale-handle.json, task-11-mcp-tests.txt

  **Commit**: YES
  - Message: `feat(mcp/sim): add sim.make/reset/step/observe + task.list tools [T-11]`
  - Files: mcp-server/src/tools/sim.ts, mcp-server/src/worker.ts, mcp-server/tests/sim_tools.test.ts, tools/gen_schemas.py
  - Pre-commit: `bun test mcp-server/tests/sim_tools.test.ts && python tools/gen_schemas.py --check`

- [x] 12. **Vertical Slice Integration Test (CLI → MCP → MuJoCo → Cartpole)**

  **What to do**:
  - Create `examples/hello_cartpole.py`:
    - Imports `<ship_name>`, runs 1 episode of cartpole with `make("cartpole", "mujoco")`, prints reward summary
  - Create `examples/hello_cartpole_via_mcp.ts` (or `.sh`):
    - Spawns MCP server, connects via JSON-RPC, runs same cartpole episode via tools, prints reward summary
  - Integration test `tests/integration/test_vertical_slice.py`:
    - Spawns MCP server subprocess
    - Connects via `mcp-client-py` (we author a minimal client OR use existing if mature)
    - Runs full cartpole episode
    - Asserts: ≥1 step taken, reward is float, episode terminates within 500 steps
    - Kills server in teardown
  - Add to `pyproject.toml` `[project.scripts]`: `<ship_name>-hello = "examples.hello_cartpole:main"`
  - Document in README the "30-second demo" section pointing to these examples

  **Must NOT do**:
  - Don't make this end-to-end test depend on LLM (no orchestrator yet — that's Task 16+)
  - Don't add visualization (kept headless per workflow freedom)
  - Don't ship `mcp-client-py` as a public package in this task (internal test helper only for v0.1)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: subprocess lifecycle in tests is finicky; cross-language IPC has many pitfalls
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (final integration of Wave 1)
  - **Parallel Group**: Wave 1F (FINAL-INT — Wave 1 capstone; gates Wave 2)
  - **Blocks**: all Wave 2 (vertical slice must work first)
  - **Blocked By**: Tasks 9, 11

  **References**:

  **Pattern References**:
  - Other MCP servers' integration tests (e.g., `everything` server's e2e tests)

  **API/Type References**:
  - `<ship_name>` Python public API; MCP TS server

  **Test References**:
  - `pytest`'s `subprocess` fixture patterns; `pytest-asyncio` if needed

  **External References**:
  - MCP client examples in TypeScript SDK

  **WHY Each Reference Matters**:
  - MCP example tests: proves cross-language e2e patterns work
  - pytest subprocess: idioms for spawning/killing server cleanly

  **Acceptance Criteria**:

  - [ ] `python examples/hello_cartpole.py --seed=42` exits 0, prints "episode_reward=" line
  - [ ] `bun examples/hello_cartpole_via_mcp.ts` (or .sh) does same via MCP
  - [ ] `pytest tests/integration/test_vertical_slice.py -v` green
  - [ ] Wall-clock for full vertical slice <30s on M5 Pro

  **QA Scenarios**:

  ```
  Scenario: Happy path - vertical slice via CLI
    Tool: Bash
    Steps:
      1. python examples/hello_cartpole.py --seed=42 > /tmp/slice.txt
      2. Assert exit 0
      3. Assert grep "episode_reward=" /tmp/slice.txt
    Evidence: .sisyphus/evidence/task-12-slice-cli.txt

  Scenario: Happy path - vertical slice via MCP
    Tool: interactive_bash (tmux for server lifecycle)
    Steps:
      1. tmux new-window -d 'bun run mcp-server'
      2. sleep 3
      3. bun examples/hello_cartpole_via_mcp.ts > /tmp/mcp-slice.txt
      4. Assert exit 0; grep "episode_reward="
      5. tmux kill-window -t mcp-server
    Evidence: .sisyphus/evidence/task-12-slice-mcp.txt

  Scenario: Failure - MCP server killed mid-episode
    Tool: interactive_bash
    Steps:
      1. Start server; start client; sleep 1; kill server mid-run
      2. Assert client surfaces clean "connection lost" error, not unhandled exception
    Evidence: .sisyphus/evidence/task-12-slice-kill.txt
  ```

  **Evidence**: task-12-slice-cli.txt, task-12-slice-mcp.txt, task-12-slice-kill.txt, pytest output

  **Commit**: YES
  - Message: `test(integration): vertical slice E2E (CLI + MCP paths) for cartpole [T-12]`
  - Files: examples/hello_cartpole.py, examples/hello_cartpole_via_mcp.ts, tests/integration/test_vertical_slice.py
  - Pre-commit: `pytest tests/integration/test_vertical_slice.py -v`

- [x] 13. **Franka Pick-Place Task (Anchor Demo Target)**

  **What to do**:
  - Implement `src/<ship_name>/tasks/franka_pick.py` + `assets/franka_pick.xml`
  - MJCF: Franka Emika Panda arm (use `mujoco_menagerie/franka_emika_panda` MJCF, BSD-3, attribution in NOTICE) + table + small cube + target zone
  - `FrankaPickTask` implementing `Task` protocol:
    - Action space: 7-DOF joint velocity OR delta end-effector pose (start with joint velocity, simpler)
    - Observation: joint pos+vel (14d) + cube_pos (3d) + cube_quat (4d) + target_pos (3d) = 24d
    - Reward (this is the BASELINE; LLM-generated rewards replace it during Eureka): distance penalty + sparse +1 on success
    - Success: cube_z > 0.5 AND distance(cube, target) < 0.1
    - Truncate after 200 steps
    - Reset: cube and target positions sampled within a 0.3m × 0.3m × 0.05m region
  - Tests `tests/integration/test_franka_pick.py`:
    - Episode runs to completion without exception
    - Random policy success rate measured (expect ≈0%, sanity check)
    - Determinism with seed (CPU)

  **Must NOT do**:
  - Don't tune the baseline reward to be SOTA (it should be intentionally weak so Eureka has room to improve)
  - Don't use joint torque control (joint velocity is easier for RL to learn baseline)
  - Don't add visual observation (RGB camera) — observation is state-vector for v0.1 (rendering deferred)
  - Don't add gripper opening as continuous action (use simple "auto-close when near cube" heuristic for v0.1)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: robotics task design has many subtle choices (action parameterization, reward shaping, reset distribution) that affect everything downstream
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 14, 15)
  - **Parallel Group**: Wave 2A (PARALLEL — 3 tasks; independent demo components)
  - **Blocks**: 17, 20
  - **Blocked By**: Tasks 6, 8

  **References**:

  **Pattern References**:
  - `mujoco_menagerie/franka_emika_panda` (BSD-3): https://github.com/google-deepmind/mujoco_menagerie/tree/main/franka_emika_panda
  - `robosuite`'s `Lift` task (MIT) for reward/reset patterns
  - Eureka paper's Franka tasks (Apache-2.0) for the kind of task structure that works with LLM-generated rewards

  **API/Type References**:
  - `<ship_name>.protocols.Task` from Task 5
  - MuJoCo XML reference for sites, joints, actuators

  **Test References**:
  - `tests/integration/test_cartpole.py` from Task 9 (same shape, more complex content)

  **External References**:
  - Eureka paper: https://arxiv.org/abs/2310.12931 (background)
  - robosuite docs: https://robosuite.ai/docs/index.html (alternative pattern reference)

  **WHY Each Reference Matters**:
  - mujoco_menagerie: ready-to-use Franka MJCF, BSD-3-licensed, well-tested
  - robosuite Lift: similar task semantics, proven reward shape
  - Eureka tasks: directly relevant — our anchor demo follows this pattern

  **Acceptance Criteria**:

  - [ ] `make("franka_pick", "mujoco")` returns Environment, runs 200 steps with random policy without exception
  - [ ] Random-policy success rate over 100 episodes: < 5% (sanity: task is hard enough)
  - [ ] Determinism: two `reset(seed=42)` produce identical cube_pos byte-for-byte (CPU)
  - [ ] `pytest tests/integration/test_franka_pick.py -v` green
  - [ ] Wall-clock per episode (random policy, 200 steps): <2s on M5 Pro

  **QA Scenarios**:

  ```
  Scenario: Happy path - random policy runs
    Tool: Bash
    Steps:
      1. python -c "
        from <ship_name> import make
        env = make('franka_pick', 'mujoco')
        successes = 0
        for ep in range(20):
            obs, _ = env.reset(seed=ep)
            for t in range(200):
                obs, r, term, trunc, info = env.step(env.action_space.sample())
                if info.get('success'): successes += 1; break
                if term or trunc: break
        print(f'random_success_rate={successes/20:.2f}')
      "
      2. Assert exit 0, success rate < 0.30 (random shouldn't solve it)
    Evidence: .sisyphus/evidence/task-13-franka-random.txt

  Scenario: Failure - missing MJCF asset
    Tool: Bash
    Steps:
      1. Temporarily rename assets/franka_pick.xml
      2. python -c "from <ship_name> import make; make('franka_pick', 'mujoco')"
      3. Assert exit non-zero; stderr mentions asset path or FileNotFoundError
    Evidence: .sisyphus/evidence/task-13-franka-no-asset.txt
  ```

  **Evidence**: task-13-franka-random.txt, task-13-franka-no-asset.txt, pytest output

  **Commit**: YES
  - Message: `feat(tasks): add franka_pick task for anchor demo (Eureka target) [T-13]`
  - Files: src/<ship_name>/tasks/franka_pick.py, src/<ship_name>/assets/franka_pick.xml, tests/integration/test_franka_pick.py, NOTICE (Franka Menagerie attribution)
  - Pre-commit: `pytest tests/integration/test_franka_pick.py -v`

- [x] 14. **Minimal RL Trainer (PPO, Small-Scale)**

  **What to do**:
  - Implement `src/<ship_name>/training/ppo.py`:
    - Minimal PPO (~200 lines) using PyTorch (MPS backend on Mac)
    - Synchronous rollout (no vector env yet — single env, n_steps=2048, repeat for total_steps)
    - Actor + Critic shared MLP `[obs_dim → 64 → 64 → action_dim/1]`, tanh activations
    - Standard PPO loss: clip ratio 0.2, value loss coef 0.5, entropy coef 0.01
    - GAE λ=0.95, γ=0.99
    - Optimizer: Adam(lr=3e-4)
    - Stop condition: reach `total_steps` OR reach `target_success_rate`
    - Logs: train/value_loss, train/policy_loss, eval/success_rate per epoch — JSONL to `runs/<ts>/train.jsonl`
  - CLI: `python -m <ship_name>.training.ppo --task=cartpole --total-steps=100000 --eval-every=10000 --seed=42`
  - Tests `tests/unit/test_ppo.py`:
    - PPO converges on cartpole within 200k steps to ≥80% mean episode length (smoke test that trainer is functional)
    - Seed determinism check (CPU): two runs same seed → close eval curves
  - Mark trainer test as `@pytest.mark.slow` (run in extended CI, not on every push)

  **Must NOT do**:
  - Don't add distributed training, multi-GPU, vector envs (v0.2)
  - Don't use stable-baselines3 wholesale (we own this for transparency); we may borrow PPO loop structure under MIT
  - Don't add hyperparameter search; one set of hyperparams works for v0.1
  - Don't add Weights & Biases integration (just JSONL; W&B is v0.2 nice-to-have)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: RL implementations have many tiny bugs that silently break learning; needs careful TDD
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 13, 15)
  - **Parallel Group**: Wave 2A (PARALLEL — 3 tasks; independent demo components)
  - **Blocks**: 18, 20
  - **Blocked By**: Task 8

  **References**:

  **Pattern References**:
  - `cleanrl` PPO single-file (MIT): https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/ppo.py — gold-standard minimal PPO reference
  - `stable-baselines3` PPO (MIT) for sanity-checking hyperparameters

  **API/Type References**:
  - `<ship_name>.protocols.Env`
  - PyTorch `torch.nn.Module`, `torch.optim.Adam`, MPS device

  **Test References**:
  - cleanrl's smoke test pattern (cartpole solves in <100k steps)

  **External References**:
  - PPO paper: https://arxiv.org/abs/1707.06347
  - PPO implementation details blog: https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/

  **WHY Each Reference Matters**:
  - cleanrl PPO: minimal single-file implementation that just works; copy structure
  - ICLR blog: every PPO bug we might silently hit is enumerated here
  - PPO paper: original semantics

  **Acceptance Criteria**:

  - [ ] `python -m <ship_name>.training.ppo --task=cartpole --total-steps=200000 --seed=42` finishes; final eval success_rate ≥ 0.80
  - [ ] JSONL log written; parses cleanly
  - [ ] Two runs with `--seed=42` produce eval curves within 10% absolute at all checkpoints
  - [ ] `pytest tests/unit/test_ppo.py -v --slow` green
  - [ ] Trainer runs on MPS without crash (skip if MPS unavailable, e.g., in Linux CI)

  **QA Scenarios**:

  ```
  Scenario: Happy path - cartpole solved
    Tool: Bash
    Steps:
      1. python -m <ship_name>.training.ppo --task=cartpole --total-steps=200000 --seed=42 --eval-every=20000 2>&1 | tee /tmp/ppo.log
      2. Assert exit 0
      3. # Parse final success rate
      4. tail -1 runs/*/train.jsonl | jq '.eval.success_rate' > /tmp/final_sr.txt
      5. Assert final_sr ≥ 0.80
    Evidence: .sisyphus/evidence/task-14-ppo-cartpole.txt + JSONL

  Scenario: Failure - invalid task name
    Tool: Bash
    Steps:
      1. python -m <ship_name>.training.ppo --task=nope --total-steps=1000
      2. Assert exit non-zero; stderr mentions TaskNotRegisteredError
    Evidence: .sisyphus/evidence/task-14-ppo-bad-task.txt
  ```

  **Evidence**: task-14-ppo-cartpole.txt, runs/*/train.jsonl, task-14-ppo-bad-task.txt

  **Commit**: YES
  - Message: `feat(training): minimal PPO trainer with MPS support [T-14]`
  - Files: src/<ship_name>/training/ppo.py, src/<ship_name>/training/__init__.py, tests/unit/test_ppo.py
  - Pre-commit: `ruff check . && pytest tests/unit/test_ppo.py -v -m "not slow"`

- [x] 15. **LLM Client Wrapper (opencode Integration)**

  **What to do**:
  - Implement `src/<ship_name>/llm/client.py`:
    - `LLMClient` Protocol — `complete(prompt: str, system: str | None = None, **kwargs) -> str`, `name() -> str`
    - `OpencodeClient` implementation: invokes `opencode` CLI as subprocess with prompt via stdin, captures stdout
    - **Caching**: keyed on `(prompt_hash, model_id, params_hash)` → JSON file in `.<ship_name>_cache/llm/`; deterministic mode reuses cached completion
    - `MockLLMClient`: returns canned responses from fixture for tests
    - Telemetry: log each call (prompt length, response length, latency, cost-tokens-stubbed) to `runs/<ts>/llm.jsonl`
  - CLI: `python -m <ship_name>.llm.client --probe` runs a quick "say hi" against opencode, validates connection
  - Tests `tests/unit/test_llm_client.py`:
    - MockLLMClient round-trip
    - Caching: second call with same args returns from cache (assert cached file exists, mock client not invoked twice)
    - OpencodeClient unit-mocked via `unittest.mock.patch("subprocess.run")` to avoid real LLM calls in CI

  **Must NOT do**:
  - Don't bundle opencode binary; require it on PATH (document)
  - Don't add Anthropic/OpenAI direct SDK in this task (opencode handles model routing — that's its whole job)
  - Don't make caching default opt-in (it's required for determinism in the demo)
  - Don't log full prompts/completions to telemetry without redaction option (sensitivity)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: subprocess + caching + protocol design = interaction-heavy
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 13, 14)
  - **Parallel Group**: Wave 2A (PARALLEL — 3 tasks; independent demo components)
  - **Blocks**: 17, 20
  - **Blocked By**: Task 2

  **References**:

  **Pattern References**:
  - Existing LLM client wrappers in OSS Python projects (langchain, llamaindex) — for caching key patterns
  - opencode CLI invocation pattern (workspace AGENTS.md, opencode --help)

  **API/Type References**:
  - `subprocess.run` API
  - hashlib for cache keys

  **Test References**:
  - `pytest`'s `monkeypatch` for env vars and subprocess mocking

  **External References**:
  - opencode docs (local installation; PATH discovery)

  **WHY Each Reference Matters**:
  - Existing wrappers: proven caching key formats (sha256 of canonicalized JSON)
  - opencode docs: invocation surface we depend on

  **Acceptance Criteria**:

  - [ ] `python -m <ship_name>.llm.client --probe` returns 0 if opencode is on PATH; non-zero with clear message otherwise
  - [ ] Same prompt cached: second call has latency <10ms (file IO) vs first call (whatever LLM takes)
  - [ ] MockLLMClient passes round-trip test
  - [ ] OpencodeClient subprocess-mocked test passes (no real LLM call)
  - [ ] `pytest tests/unit/test_llm_client.py -v` green
  - [ ] `llm.jsonl` records every call with metadata

  **QA Scenarios**:

  ```
  Scenario: Happy path - probe opencode
    Tool: Bash
    Preconditions: opencode binary on PATH (verify with `which opencode`)
    Steps:
      1. python -m <ship_name>.llm.client --probe 2>&1 | tee /tmp/probe.txt
      2. Assert exit 0
      3. Assert /tmp/probe.txt contains "opencode probe OK" or similar success token
    Evidence: .sisyphus/evidence/task-15-llm-probe.txt

  Scenario: Failure - opencode not on PATH
    Tool: Bash
    Steps:
      1. PATH=/nonexistent python -m <ship_name>.llm.client --probe
      2. Assert exit non-zero
      3. Assert stderr mentions "opencode not found"
    Evidence: .sisyphus/evidence/task-15-llm-no-opencode.txt

  Scenario: Happy path - cache hit
    Tool: Bash
    Steps:
      1. python -c "
        from <ship_name>.llm.client import MockLLMClient
        c = MockLLMClient(canned='hello')
        c.complete('test prompt')
        # Inspect cache dir; assert file present
        import pathlib; cache_files = list(pathlib.Path('.<ship_name>_cache/llm').glob('*.json'))
        assert len(cache_files) >= 1
        print('cache_hit_ok')
      "
      2. Assert stdout contains "cache_hit_ok"
    Evidence: .sisyphus/evidence/task-15-llm-cache.txt
  ```

  **Evidence**: task-15-llm-probe.txt, task-15-llm-no-opencode.txt, task-15-llm-cache.txt

  **Commit**: YES
  - Message: `feat(llm): opencode client wrapper with deterministic caching [T-15]`
  - Files: src/<ship_name>/llm/client.py, src/<ship_name>/llm/__init__.py, tests/unit/test_llm_client.py
  - Pre-commit: `pytest tests/unit/test_llm_client.py -v`

- [x] 16. **Research Orchestrator Skeleton (Experiment Loop + Artifact Store)**

  **What to do**:
  - Implement `src/<ship_name>/orchestrator/`:
    - `run.py` — top-level `Run` dataclass: `{run_id, started_at, task, config, iterations: list[Iteration]}`
    - `iteration.py` — `Iteration` dataclass: `{idx, prompt, llm_response, artifact_path, eval_metrics, status, reflection}`
    - `store.py` — `RunStore` writes/reads runs from `runs/<ts>/` filesystem layout:
      ```
      runs/2026-05-27T13-00-00_franka-pick/
        config.json
        manifest.jsonl
        iter_0/
          prompt.md
          reward.py
          eval.json
          reflection.md
      ```
    - `loop.py` — `OrchestratorLoop`: given `task_name, llm_client, num_iterations`, runs iteration loop, hands off to reward generator (T17) and evaluator (T18), records to store
    - `__main__.py` — CLI entry: `python -m <ship_name>.orchestrator --task=franka_pick --iterations=5`
  - This is the SKELETON — actual reward gen and eval are pluggable hooks filled in by T17/18
  - Tests `tests/unit/test_orchestrator.py`:
    - With MockLLMClient + mock reward generator + mock evaluator, runs 3 iterations, store layout correct
    - Manifest JSONL contains 3 entries with required fields
    - Determinism: same seed + same mocks → same run output (artifacts byte-equal modulo timestamps)

  **Must NOT do**:
  - Don't implement the reward gen logic here (T17)
  - Don't run actual RL training here (T18 uses T14's trainer)
  - Don't add wandb/tensorboard (JSONL only for v0.1)
  - Don't make the loop concurrent (sequential iterations only)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: artifact store schema is sticky; needs to support future v0.2 patterns (env gen, reflection chains)
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 2B BRIDGE — orchestrator skeleton must precede subordinate components)
  - **Parallel Group**: Wave 2B (BRIDGE — single-task wave, gates T17, T18, T19)
  - **Blocks**: 17, 18, 19, 20
  - **Blocked By**: Tasks 8, 15

  **References**:

  **Pattern References**:
  - `eureka-research/Eureka` `eureka/eureka.py` (MIT) — reference orchestrator structure
  - `isaac-sim/IsaacLabEureka` `scripts/train.py` (Apache-2.0) — NVIDIA's adaptation

  **API/Type References**:
  - `<ship_name>.protocols.Task`, `LLMClient` from T15

  **Test References**: T15's mock LLM pattern

  **External References**:
  - Eureka paper: https://arxiv.org/abs/2310.12931 (§4 Algorithm)
  - "Reproducibility in ML": principles for run directory structure (e.g., DVC docs)

  **WHY Each Reference Matters**:
  - Eureka code: working orchestrator, our shape mirrors it for credibility
  - IsaacLabEureka: NVIDIA's official adaptation; we want to be familiar to that audience

  **Acceptance Criteria**:

  - [ ] `python -m <ship_name>.orchestrator --task=franka_pick --iterations=3 --llm=mock` creates valid `runs/<ts>/` directory
  - [ ] Manifest JSONL contains 3 lines, each parseable, with required fields (idx, status, eval.success_rate)
  - [ ] Iteration directories contain prompt.md, reward.py (mock), eval.json
  - [ ] `pytest tests/unit/test_orchestrator.py -v` green
  - [ ] Determinism: two runs with same seed + same MockLLMClient canned responses → identical artifacts (modulo timestamps which use `--run-id` override for tests)

  **QA Scenarios**:

  ```
  Scenario: Happy path - 3 iterations
    Tool: Bash
    Steps:
      1. python -m <ship_name>.orchestrator --task=franka_pick --iterations=3 --llm=mock --run-id=test-run
      2. Assert exit 0
      3. Assert ls runs/test-run/manifest.jsonl exists
      4. Assert wc -l runs/test-run/manifest.jsonl returns 3
      5. Assert ls runs/test-run/iter_2/reward.py exists
    Evidence: .sisyphus/evidence/task-16-orchestrator-3iter/

  Scenario: Failure - corrupted prior run
    Tool: Bash
    Steps:
      1. mkdir -p runs/half-baked; echo '{"idx":0,"status":"in_progress"' > runs/half-baked/manifest.jsonl  # invalid JSON
      2. python -m <ship_name>.orchestrator --task=franka_pick --resume=half-baked
      3. Assert exit non-zero; stderr mentions JSON parse error and resumes from clean state
    Evidence: .sisyphus/evidence/task-16-orchestrator-resume-bad.txt
  ```

  **Evidence**: task-16-orchestrator-3iter/ directory tree, task-16-orchestrator-resume-bad.txt, pytest output

  **Commit**: YES
  - Message: `feat(orchestrator): skeleton experiment loop + artifact store [T-16]`
  - Files: src/<ship_name>/orchestrator/{__init__.py,__main__.py,run.py,iteration.py,store.py,loop.py}, tests/unit/test_orchestrator.py
  - Pre-commit: `pytest tests/unit/test_orchestrator.py -v`

- [x] 17. **Reward Function Generator (Eureka-Style Prompt + Code Extraction)**

  **What to do**:
  - Implement `src/<ship_name>/orchestrator/reward_gen.py`:
    - `generate_reward(task: Task, llm: LLMClient, prior_attempts: list[Attempt], ctx_seed: int) -> RewardCode`
    - Prompt template (`prompts/reward_gen.md`): includes task description, observation/action specs, prior attempts with their `eval_metrics + reflection`, asks LLM to emit a single Python function `reward_fn(obs: np.ndarray, action: np.ndarray, info: dict) -> float`
    - LLM response parsing: extract `python ...` fenced code block; if parse fails, return `status=parse_error` with the raw response saved
    - Sandbox import: try compiling the code via `ast.parse`; reject if it imports forbidden modules (`os`, `subprocess`, `socket`, `requests`, etc. — allow list: `numpy`, `math`, `<ship_name>`)
    - `RewardCode` dataclass: `{code: str, signature: str, hash: str, status: Literal["ok", "parse_error", "forbidden_import"]}`
  - Tests `tests/unit/test_reward_gen.py`:
    - With MockLLMClient returning canned good code → status=ok, code extracted correctly
    - Canned code with forbidden `import os` → status=forbidden_import
    - Canned malformed response → status=parse_error
    - Prompt includes task description + obs/action specs

  **Must NOT do**:
  - Don't execute the LLM-generated code here (that's T18 sandbox+eval)
  - Don't use `eval`/`exec` directly here without AST verification
  - Don't add multi-turn reward refinement in v0.1 (single-shot per iteration; iteration loop in T16 handles refinement across iterations)
  - Don't fall back to "just use the baseline reward" silently if generation fails — surface the error, log it, let orchestrator decide

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: prompt engineering + AST analysis + security (no arbitrary imports)
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 18)
  - **Parallel Group**: Wave 2C (PARALLEL-PAIR — with the other sibling after T16)
  - **Blocks**: 19, 20
  - **Blocked By**: Tasks 13, 15, 16

  **References**:

  **Pattern References**:
  - `eureka-research/Eureka/eureka/utils/extract_task_code.py` (MIT) — AST extraction patterns
  - `isaac-sim/IsaacLabEureka/source/isaaclab_eureka/eureka.py` — prompt structure

  **API/Type References**:
  - Python `ast` module: `ast.parse`, `ast.walk`, `ast.Import`, `ast.ImportFrom`
  - `<ship_name>.protocols.Task` + LLMClient

  **Test References**:
  - Eureka's reward extraction tests (if available; otherwise design from scratch)

  **External References**:
  - Eureka paper §4 (prompt design)
  - Python AST docs: https://docs.python.org/3/library/ast.html

  **WHY Each Reference Matters**:
  - Eureka extract_task_code: proven patterns for extracting Python functions from LLM output
  - AST docs: standard module for safe code inspection (vs regex-based, which is fragile)

  **Acceptance Criteria**:

  - [ ] `generate_reward(task=FrankaPickTask, llm=MockLLMClient(canned_good_code), [], 42)` returns `RewardCode(status='ok', code=...)`
  - [ ] Same with canned `import os` code: status='forbidden_import'
  - [ ] Same with malformed code: status='parse_error'
  - [ ] Prompt template includes obs_spec/action_spec strings (verify by mock LLM that records its prompt)
  - [ ] `pytest tests/unit/test_reward_gen.py -v` green

  **QA Scenarios**:

  ```
  Scenario: Happy path - extract well-formed reward
    Tool: Bash
    Steps:
      1. python -c "
        from <ship_name>.orchestrator.reward_gen import generate_reward
        from <ship_name>.llm.client import MockLLMClient
        from <ship_name>.tasks.franka_pick import FrankaPickTask
        llm = MockLLMClient(canned='''
        Here's a reward:
        \`\`\`python
        import numpy as np
        def reward_fn(obs, action, info):
            return -np.linalg.norm(obs[:3] - obs[14:17])
        \`\`\`
        ''')
        rc = generate_reward(FrankaPickTask(), llm, [], 42)
        assert rc.status == 'ok'
        print('OK')
      "
      2. Assert exit 0, stdout 'OK'
    Evidence: .sisyphus/evidence/task-17-reward-gen-ok.txt

  Scenario: Failure - forbidden import detected
    Tool: Bash
    Steps:
      1. Similar to above but canned code has `import os; os.system("rm -rf /")`
      2. Assert rc.status == 'forbidden_import'
      3. Stderr does NOT contain side effects of the forbidden code (proves we didn't exec it)
    Evidence: .sisyphus/evidence/task-17-reward-gen-forbidden.txt
  ```

  **Evidence**: task-17-reward-gen-ok.txt, task-17-reward-gen-forbidden.txt

  **Commit**: YES
  - Message: `feat(orchestrator/reward_gen): Eureka-style prompt + AST-validated extraction [T-17]`
  - Files: src/<ship_name>/orchestrator/reward_gen.py, src/<ship_name>/orchestrator/prompts/reward_gen.md, tests/unit/test_reward_gen.py
  - Pre-commit: `pytest tests/unit/test_reward_gen.py -v`

- [x] 18. **Reward Sandbox + Evaluator (Rollout-Based Scoring)**

  **What to do**:
  - Implement `src/<ship_name>/orchestrator/evaluator.py`:
    - `evaluate_reward(reward_code: RewardCode, task: Task, num_rollouts: int, train_steps: int, seed: int) -> EvalResult`
    - Loads reward function in subprocess (sandboxed exec — `python -c` with prelude that imports only allow-listed modules)
    - Wraps task's `step` to use the LLM-generated reward instead of baseline
    - Runs PPO trainer (Task 14) for `train_steps` steps
    - Evaluates final policy: 10 rollouts with deterministic seed, measures `task.success_metric(rollout)` average
    - Captures: training curve (subset of train.jsonl), final success rate, episode lengths, timing
    - Returns `EvalResult{success_rate, mean_episode_reward, train_steps_used, wall_clock_s, error: str|None}`
    - On crash/timeout in subprocess: capture stderr, return error sub-status
  - Timeout per evaluation: 5 minutes wall-clock (configurable); aggressive for anchor-demo budget
  - Tests `tests/integration/test_evaluator.py`:
    - Eval baseline reward on cartpole: returns success_rate > 0.5 within budget (smoke test)
    - Eval intentionally-bad reward (always returns NaN): returns status='nan_reward' with error message
    - Eval forbidden-import reward (shouldn't get here from T17, but defense-in-depth): rejected by sandbox

  **Must NOT do**:
  - Don't trust `RewardCode.status='ok'` blindly — re-validate AST in sandbox (defense in depth)
  - Don't run eval in main process (sandbox isolation matters)
  - Don't accept rewards that return non-finite values (NaN/Inf) — flag and skip
  - Don't run full 200k steps per iteration; use a small budget (~20k-50k) per iteration for fast feedback

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: subprocess sandboxing + RL eval + numerical safety = many edge cases
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with 17)
  - **Parallel Group**: Wave 2C (PARALLEL-PAIR — with the other sibling after T16)
  - **Blocks**: 19, 20
  - **Blocked By**: Tasks 13, 14, 16

  **References**:

  **Pattern References**:
  - `eureka-research/Eureka/eureka/utils/misc.py` (MIT) — eval subprocess patterns
  - Python `subprocess.run(..., timeout=...)` + `signal.SIGTERM`/`SIGKILL` cleanup

  **API/Type References**:
  - `<ship_name>.training.ppo` from T14
  - `<ship_name>.protocols.Task` from T5

  **Test References**:
  - Eureka's evaluation tests (where available)

  **External References**:
  - Python sandboxing patterns: https://docs.python.org/3/library/subprocess.html
  - Anti-patterns to avoid: https://realpython.com/python-eval-function/

  **WHY Each Reference Matters**:
  - Eureka misc.py: working eval subprocess pattern, including timeout cleanup
  - Python sandboxing: idiomatic isolation; we layer on AST validation from T17

  **Acceptance Criteria**:

  - [ ] `evaluate_reward` on cartpole with baseline reward returns `success_rate > 0.50` within 5 min
  - [ ] Same with NaN-returning reward returns `error='nan_reward'`
  - [ ] Subprocess timeout works: 0.1s timeout kills process; outer call returns `error='timeout'`
  - [ ] No reward function ever runs in the main process (assert via mock + spy in test)
  - [ ] `pytest tests/integration/test_evaluator.py -v -m "not slow"` green (excluding the long PPO smoke test)

  **QA Scenarios**:

  ```
  Scenario: Happy path - baseline reward evaluated
    Tool: Bash
    Preconditions: T13, T14 done
    Steps:
      1. python -c "
        from <ship_name>.orchestrator.evaluator import evaluate_reward
        from <ship_name>.orchestrator.reward_gen import RewardCode
        from <ship_name>.tasks.cartpole import CartpoleTask
        baseline = open('src/<ship_name>/tasks/cartpole_baseline_reward.py').read()
        rc = RewardCode(code=baseline, signature='r=1', hash='x', status='ok')
        res = evaluate_reward(rc, CartpoleTask(), num_rollouts=5, train_steps=20000, seed=42)
        print(f'sr={res.success_rate} err={res.error}')
        assert res.error is None
      "
      2. Assert exit 0; success_rate > 0.5
    Evidence: .sisyphus/evidence/task-18-eval-baseline.txt

  Scenario: Failure - NaN reward
    Tool: Bash
    Steps:
      1. Similar test with reward code `def reward_fn(...): return float("nan")`
      2. Assert res.error == 'nan_reward'
    Evidence: .sisyphus/evidence/task-18-eval-nan.txt

  Scenario: Failure - timeout
    Tool: Bash
    Steps:
      1. evaluate_reward(..., train_steps=99999999, timeout=2)
      2. Assert res.error == 'timeout'; wall-clock approx 2-3s (not 99999999 steps worth)
    Evidence: .sisyphus/evidence/task-18-eval-timeout.txt
  ```

  **Evidence**: task-18-eval-baseline.txt, task-18-eval-nan.txt, task-18-eval-timeout.txt

  **Commit**: YES
  - Message: `feat(orchestrator/eval): sandboxed reward eval with PPO + safety checks [T-18]`
  - Files: src/<ship_name>/orchestrator/evaluator.py, src/<ship_name>/tasks/cartpole_baseline_reward.py, tests/integration/test_evaluator.py
  - Pre-commit: `pytest tests/integration/test_evaluator.py -v -m "not slow"`

- [x] 19. **Iteration Controller (Best-Reward Tracking + Reflection)**

  **What to do**:
  - Implement `src/<ship_name>/orchestrator/controller.py`:
    - `IterationController` orchestrates one iteration: call reward_gen → evaluator → reflection → record
    - State: `best_reward_so_far`, `best_success_rate`, `failure_streak_count`
    - **Reflection step**: after each eval, generate a 3-5 sentence summary of "what worked / what didn't" via LLM, fed back into next iteration's prompt
    - Early stopping: if 3 consecutive iterations < `current_best * 0.5`, raise warning; if 5 consecutive failures (parse_error/forbidden/nan/timeout), abort run
    - Records to T16's store: per-iteration metrics, reflection, accepted/rejected status
  - Tests `tests/unit/test_controller.py`:
    - With mock LLM returning improving rewards: best_success_rate tracks max
    - With mock LLM returning constant failures: aborts after 5 consecutive failures
    - Reflection generation invoked once per iteration; included in next prompt

  **Must NOT do**:
  - Don't use long-running reflection chains (3-5 sentences max; LLM cost matters)
  - Don't auto-tune hyperparameters (PPO config fixed across iterations)
  - Don't cherry-pick "best" reward by metric other than the task's `success_metric` (consistency)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: orchestration logic + LLM reflection prompting + state management
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on 17, 18)
  - **Parallel Group**: Wave 2D (BRIDGE — controller needs T17, T18)
  - **Blocks**: 20
  - **Blocked By**: Tasks 16, 17, 18

  **References**:

  **Pattern References**:
  - `eureka-research/Eureka` iteration loop (MIT)
  - `Voyager`'s self-reflection pattern (MIT) — for reflection prompt structure

  **API/Type References**:
  - Components from T15, T16, T17, T18

  **Test References**: T16's mock-based test patterns

  **External References**:
  - Voyager paper: https://voyager.minedojo.org/ (self-reflection mechanism)

  **WHY Each Reference Matters**:
  - Eureka iteration: proven structure
  - Voyager reflection: best-of-breed reflection-loop design transferable to robotics

  **Acceptance Criteria**:

  - [ ] On a synthetic mock run with 5 iterations, controller correctly identifies and persists "best" iteration
  - [ ] 5 consecutive failures (mock) aborts the run with clear error
  - [ ] Reflection text included in iteration 2+ prompts (verify via mock LLM that records prompts)
  - [ ] `pytest tests/unit/test_controller.py -v` green

  **QA Scenarios**:

  ```
  Scenario: Happy path - 5 mock iterations with improving rewards
    Tool: Bash
    Steps:
      1. # Configure MockLLMClient with 5 canned rewards: each better than the last
      2. python -m <ship_name>.orchestrator --task=cartpole --iterations=5 --llm=mock --mock-script=tests/fixtures/improving_rewards.json --run-id=t19-happy
      3. Assert exit 0
      4. jq '.best_iteration' runs/t19-happy/manifest.jsonl | tail -1 == "4"
    Evidence: .sisyphus/evidence/task-19-controller-improving.txt

  Scenario: Failure - 5 consecutive failures abort run
    Tool: Bash
    Steps:
      1. MockLLM script returns parse_error 5 times
      2. python -m <ship_name>.orchestrator --task=cartpole --iterations=10 --llm=mock --mock-script=tests/fixtures/all_failures.json --run-id=t19-abort
      3. Assert exit non-zero
      4. Assert manifest contains "status":"aborted" with reason="5_consecutive_failures"
    Evidence: .sisyphus/evidence/task-19-controller-abort.txt
  ```

  **Evidence**: task-19-controller-improving.txt, task-19-controller-abort.txt

  **Commit**: YES
  - Message: `feat(orchestrator/controller): iteration loop with reflection + abort [T-19]`
  - Files: src/<ship_name>/orchestrator/controller.py, src/<ship_name>/orchestrator/prompts/reflection.md, tests/unit/test_controller.py, tests/fixtures/{improving_rewards,all_failures}.json
  - Pre-commit: `pytest tests/unit/test_controller.py -v`

- [ ] 20. **Anchor Demo Script — `examples/eureka_franka.py`**

  **What to do**:
  - Wire T13-19 into the canonical demo:
    - `examples/eureka_franka.py`:
      - CLI: `--iterations N` (default 5), `--seed S` (default 42), `--llm opencode|mock` (default opencode), `--train-steps-per-iter K` (default 30000)
      - Calls `OrchestratorLoop` with `task=franka_pick`, `llm=OpencodeClient`, `iterations=N`, `controller=IterationController`, `reward_gen=...`, `evaluator=...`
      - Prints summary table at end: iteration | success_rate | wall_clock | reward_signature
      - Writes summary markdown `runs/<ts>/SUMMARY.md` and final-best `runs/<ts>/BEST_REWARD.py`
  - Document expected outcome in `examples/README.md`: "On M5 Pro, this runs in ~25-30 minutes. Expect best success_rate ≥0.70 by iteration 5 with seed=42 (using cached LLM responses for reproducibility, or live LLM responses with ε variance)."
  - LLM cache fixture: pre-cache the 5 expected responses for `seed=42` to make CI runs deterministic and avoid live LLM dependency

  **Must NOT do**:
  - Don't add visualization (kept headless; v0.2 may add)
  - Don't add `--gpu`/Tier-2 flag (Mac-local only per scope)
  - Don't hide internal failures (any iteration aborting must surface to user)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: this is the centerpiece deliverable; debugging the e2e requires holistic understanding
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (assembles all of Wave 2)
  - **Parallel Group**: Wave 2E (FINAL-INT — anchor demo + gate + polish)
  - **Blocks**: 21, 22
  - **Blocked By**: Tasks 13, 14, 15, 16, 17, 18, 19

  **References**:

  **Pattern References**:
  - `eureka-research/Eureka/eureka/eureka.py` (MIT) — the canonical Eureka script
  - `isaac-sim/IsaacLabEureka/scripts/train.py` (Apache-2.0) — adapted for an analogous framework

  **API/Type References**:
  - All Wave 2 modules

  **Test References**:
  - `tests/integration/test_eureka_franka_smoke.py` — light smoke test (1 iter, mock LLM)

  **External References**:
  - Eureka paper §5 (benchmarks) — sets expectations for results

  **WHY Each Reference Matters**:
  - Eureka script: reference output format that users in the space expect
  - Eureka paper benchmarks: helps set realistic success-rate target for our gate

  **Acceptance Criteria**:

  - [ ] `python examples/eureka_franka.py --iterations=1 --llm=mock --seed=42 --run-id=smoke` runs end-to-end and exits 0
  - [ ] Creates `runs/smoke/` with SUMMARY.md and BEST_REWARD.py
  - [ ] `pytest tests/integration/test_eureka_franka_smoke.py -v` green (smoke only; full ≥70% is gated by T21)
  - [ ] `examples/README.md` documents expected behavior

  **QA Scenarios**:

  ```
  Scenario: Happy path - 1-iter smoke with mock
    Tool: Bash
    Steps:
      1. python examples/eureka_franka.py --iterations=1 --llm=mock --seed=42 --run-id=smoke 2>&1 | tee /tmp/smoke.txt
      2. Assert exit 0
      3. Assert ls runs/smoke/SUMMARY.md exists
    Evidence: .sisyphus/evidence/task-20-anchor-smoke.txt + runs/smoke/

  Scenario: Failure - missing opencode (live mode) gracefully reports
    Tool: Bash
    Steps:
      1. PATH=/nonexistent python examples/eureka_franka.py --iterations=1 --llm=opencode --seed=42
      2. Assert exit non-zero; stderr explains opencode-on-PATH requirement
    Evidence: .sisyphus/evidence/task-20-anchor-no-opencode.txt
  ```

  **Evidence**: task-20-anchor-smoke.txt, runs/smoke/ tree, task-20-anchor-no-opencode.txt

  **Commit**: YES
  - Message: `feat(examples): anchor demo eureka_franka.py wiring [T-20]`
  - Files: examples/eureka_franka.py, examples/README.md, tests/integration/test_eureka_franka_smoke.py
  - Pre-commit: `pytest tests/integration/test_eureka_franka_smoke.py -v`

- [ ] 21. **⚡ DEMO FEASIBILITY GATE (Mid-Week 5, BLOCKING)**

  **What to do**:
  - This task is a **GATE**, not a feature. It is a measurement + decision task.
  - Run the anchor demo (T20) with REAL LLM (opencode) and `--seed=42 --iterations=5 --train-steps-per-iter=30000` on M5 Pro
  - Measure:
    - Wall-clock total time
    - Best `success_rate` across 5 iterations
    - LLM cost (token spend, if surfaced by opencode)
    - Crash/error count
  - Record to `.sisyphus/evidence/task-21-feasibility-gate.md`:
    - All measurements
    - "Pass" verdict if: best success_rate ≥ 0.40 AND wall_clock ≤ 60min AND ≤2 iterations errored
    - "Borderline" verdict if: best 0.30-0.40 OR 60-90min OR 3 errored → propose tuning (more iterations? bigger training budget? simpler reward function structure?)
    - "Fail" verdict if: best < 0.30 OR > 90min OR ≥4 errored → ESCALATE for scope cut
  - On **Fail**: explicit user check-in required. Possible cuts:
    - Drop Franka, use simpler task (e.g., cube-stack or reach-only)
    - Reduce iterations target to 3 in demo
    - Reduce success-rate target from 70% to 50%
    - Or extend timeline (delay Week 6 anchor demo by 1 week)
  - On **Pass/Borderline**: proceed to T22 polish with documented tuning
  - File `task-21-feasibility-gate.md` MUST contain the verdict + measurements + decision

  **Must NOT do**:
  - Don't skip this gate — it's the canary
  - Don't fudge the measurement methodology to pass (be honest)
  - Don't proceed past this gate without recording a verdict
  - Don't run with cached LLM responses for this gate (must be live LLM to measure realistic cost/quality)

  **Recommended Agent Profile**:
  - **Category**: `oracle` (read-only critical decision)
    - Reason: This is consultation, not implementation. Oracle provides decision rigor.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (blocking gate)
  - **Parallel Group**: Wave 2E (FINAL-INT — feasibility GATE within capstone)
  - **Blocks**: 22 (polish) and all of Wave 3 if Fail
  - **Blocked By**: Task 20

  **References**:

  **Pattern References**:
  - Stage-gate engineering management pattern (general PM literature)

  **API/Type References**: N/A

  **Test References**: This IS the test.

  **External References**:
  - Eureka paper §5: their reported success rates and budgets — calibration reference

  **WHY Each Reference Matters**:
  - Eureka benchmarks: sanity check on whether our target is realistic

  **Acceptance Criteria**:

  - [ ] `.sisyphus/evidence/task-21-feasibility-gate.md` exists with VERDICT line
  - [ ] All measurements (wall-clock, success_rate, errors, cost-stub) recorded
  - [ ] On Pass: T22 unblocked
  - [ ] On Borderline: tuning proposed and applied; re-run; record second measurement
  - [ ] On Fail: explicit decision logged (which cut chosen by user)
  - [ ] No silent proceed past this gate

  **QA Scenarios**:

  ```
  Scenario: Pass verdict
    Tool: Bash
    Steps:
      1. python examples/eureka_franka.py --iterations=5 --llm=opencode --seed=42 --run-id=feas-gate-1 2>&1 | tee /tmp/gate.log
      2. # Parse summary: jq '.best.success_rate' runs/feas-gate-1/manifest.jsonl | tail -1
      3. # Apply Pass criteria
      4. # Write task-21-feasibility-gate.md with VERDICT: PASS
    Evidence: .sisyphus/evidence/task-21-feasibility-gate.md + runs/feas-gate-1/

  Scenario: Fail verdict
    Tool: Bash
    Steps:
      1. (If best < 0.30 or wall_clock > 90min)
      2. Document failure modes observed
      3. List proposed cuts
      4. WAIT for user input (this gate explicitly stops auto-proceed)
      5. After decision: update task-21 file with chosen cut
    Expected: Plan execution does NOT proceed past T21 until user okays
    Evidence: .sisyphus/evidence/task-21-feasibility-gate.md (FAIL verdict + decision log)
  ```

  **Evidence**: task-21-feasibility-gate.md (mandatory artifact), runs/feas-gate-*/ outputs

  **Commit**: YES
  - Message: `chore(gate): T-21 feasibility gate verdict [PASS|BORDERLINE|FAIL] [T-21]`
  - Files: `.sisyphus/evidence/task-21-feasibility-gate.md`, possibly tuned `examples/eureka_franka.py` defaults
  - Pre-commit: `cat .sisyphus/evidence/task-21-feasibility-gate.md | grep -q "VERDICT:"`

- [ ] 22. **Anchor Demo Final Polish + Evidence Capture**

  **What to do**:
  - Apply tuning from T21 if any
  - Final run with `seed=42 --iterations=5 --llm=opencode` on M5 Pro
  - Hit acceptance: success_rate ≥ 0.70, wall_clock ≤ 30min (or whatever T21 decided as the v0.1 target)
  - Polish:
    - SUMMARY.md template improved (markdown table, charts via ASCII or mermaid if simple)
    - Capture screenshots of terminal output (optional MuJoCo viewer at the end showing best policy rolling out)
    - Save final `BEST_REWARD.py` with attribution comment
    - Persistent `runs/anchor-v0.1-canonical/` as the "official" reference run
  - Update README.md with "30-second demo" + Animated GIF (terminal recording) of demo running
  - Optional: short video link in README (out of scope to make video here, but document where it should be)
  - Cache the 5 LLM responses so reproducible by any user (committed `examples/anchor_demo_cache/`)

  **Must NOT do**:
  - Don't ship visualization deps in core (kept optional dev-extra)
  - Don't claim better-than-measured performance in README
  - Don't gate CI on the full anchor demo (too long); gate only on smoke (T20)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: polish work, terminal recording, README copywriting — varied
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on T21 passing)
  - **Parallel Group**: Wave 2E (FINAL-INT — anchor demo + gate + polish)
  - **Blocks**: All Wave 3 starts only after T22 done
  - **Blocked By**: Tasks 20, 21

  **References**:

  **Pattern References**:
  - Top-tier OSS README demos (e.g., `pytorch/pytorch`, `astral-sh/ruff`)
  - asciinema for terminal recording: https://asciinema.org

  **API/Type References**: N/A

  **Test References**:
  - `tests/integration/test_eureka_franka_smoke.py` (still passes)

  **External References**:
  - asciinema docs

  **WHY Each Reference Matters**:
  - OSS examples: calibrate quality bar for the README
  - asciinema: standard tool for terminal recording

  **Acceptance Criteria**:

  - [ ] `python examples/eureka_franka.py --seed=42 --iterations=5 --llm=opencode --use-cache` reproduces success_rate ≥ 0.70 in ≤30min on M5 Pro
  - [ ] `runs/anchor-v0.1-canonical/` committed (artifacts checked in OR documented to fetch from release)
  - [ ] README.md "30-second demo" section live
  - [ ] Anchor demo terminal recording exists (asciinema or text capture) at `.sisyphus/evidence/anchor-demo-recording.cast`
  - [ ] LLM cache committed at `examples/anchor_demo_cache/` (allows offline replay)

  **QA Scenarios**:

  ```
  Scenario: Happy path - reproduce canonical run
    Tool: Bash
    Steps:
      1. # With cache (deterministic)
      2. python examples/eureka_franka.py --seed=42 --iterations=5 --llm=opencode --use-cache --run-id=t22-repro
      3. Assert exit 0
      4. # Compare with canonical
      5. diff runs/t22-repro/BEST_REWARD.py runs/anchor-v0.1-canonical/BEST_REWARD.py
      6. Assert no diff (or expected ε numerical diff)
    Evidence: .sisyphus/evidence/task-22-repro-canonical.txt

  Scenario: Failure - no opencode no cache
    Tool: Bash
    Steps:
      1. PATH=/nonexistent python examples/eureka_franka.py --use-cache=false
      2. Assert non-zero exit, clear message
    Evidence: .sisyphus/evidence/task-22-no-opencode-no-cache.txt
  ```

  **Evidence**: task-22-repro-canonical.txt, runs/anchor-v0.1-canonical/, .sisyphus/evidence/anchor-demo-recording.cast, task-22-no-opencode-no-cache.txt

  **Commit**: YES
  - Message: `feat(examples): polish anchor demo, add canonical run + cached responses [T-22]`
  - Files: examples/eureka_franka.py (tuning), examples/anchor_demo_cache/*.json, runs/anchor-v0.1-canonical/ (or reference), README.md updates, .sisyphus/evidence/anchor-demo-recording.cast
  - Pre-commit: `pytest tests/integration/test_eureka_franka_smoke.py -v`

- [ ] 23. **CI Test #1: License Freedom (Encoded)**

  **What to do**:
  - Enhance `tools/check_licenses.py` (from T4) to be the canonical "License Freedom" check
  - Add `bun` script: `"check:licenses": "python ../tools/check_licenses.py --all"` in mcp-server/package.json
  - In `.github/workflows/licenses.yml` (already created in T4), add: post a comment on PRs with license summary table
  - Verify failure modes:
    - Reject if any dep is GPL/AGPL/proprietary
    - Reject if our LICENSE file is not MIT (header check)
    - Reject if NOTICE missing required attributions (MuJoCo, dm_control, etc.)
  - This task ENCODES the "license freedom" claim as a passing CI test

  **Must NOT do**:
  - Don't soften the allowed license list to accommodate convenient deps (architectural integrity)
  - Don't disable on local dev (run via pre-commit)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: CI plumbing + edge case test coverage
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T24-T29)
  - **Parallel Group**: Wave 3A (PARALLEL — 7 freedom CI tests run concurrently)
  - **Blocks**: None
  - **Blocked By**: T4, T22

  **References**:

  **Pattern References**: T4 (license audit infrastructure)
  **API/Type References**: N/A
  **Test References**: T4's QA scenarios
  **External References**: SPDX license list (https://spdx.org/licenses/)

  **WHY Each Reference Matters**: T4 is the substrate; this task hardens it as a CI invariant.

  **Acceptance Criteria**:

  - [ ] `bun run check:licenses` exits 0 on current clean tree
  - [ ] `.github/workflows/licenses.yml` runs successfully on a PR
  - [ ] Removing the NOTICE file (or removing a required attribution) causes a clear CI failure
  - [ ] Adding a fake GPL dep in a test branch causes CI failure with helpful diff

  **QA Scenarios**:

  ```
  Scenario: Happy path - CI green on clean tree
    Tool: Bash
    Steps:
      1. bun run check:licenses
      2. Assert exit 0; stdout shows N deps scanned, 0 violations
    Evidence: .sisyphus/evidence/task-23-license-ci-green.txt

  Scenario: Failure - test branch with GPL dep
    Tool: Bash
    Steps:
      1. Create a test branch; add a placeholder GPL package to pyproject (or simulate via fixture)
      2. bun run check:licenses
      3. Assert exit non-zero; specifies offending package name
    Evidence: .sisyphus/evidence/task-23-license-ci-gpl.txt
  ```

  **Evidence**: task-23-license-ci-green.txt, task-23-license-ci-gpl.txt

  **Commit**: YES
  - Message: `ci(freedom): encode license-freedom claim as CI gate [T-23]`
  - Files: tools/check_licenses.py (updates), .github/workflows/licenses.yml (updates), mcp-server/package.json (script)
  - Pre-commit: `bun run check:licenses`

- [ ] 24. **CI Test #2: API/Backend Freedom (Contract Test in CI)**

  **What to do**:
  - Ensure `tests/integration/test_backend_contract.py` (from T7) runs in CI matrix
  - Encode the "API/backend freedom" claim: same contract suite runs against `MuJoCoBackend` AND `MockBackend`; both must pass
  - Add a "third" pseudo-backend test: a 30-line tutorial backend `tests/fixtures/tutorial_backend.py` showing how a 3rd party would write one — must also pass contract suite
  - This proves "anyone can write a backend; the contract is small and stable"

  **Must NOT do**:
  - Don't add backend impls that aren't shipped (the tutorial backend is in tests/, not in src/)
  - Don't relax the contract to make Mac MPS pass; CPU-only is the bit-exact reference

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3A (PARALLEL — 7 freedom CI tests run concurrently)
  - **Blocks**: None
  - **Blocked By**: T7, T22

  **References**:

  **Pattern References**: T7's contract test pattern
  **API/Type References**: `<ship_name>.protocols.Backend`
  **Test References**: T7 base suite
  **External References**: Martin Fowler contract testing essay

  **WHY Each Reference Matters**: T7 set the substrate; this task hardens it as the "API/backend freedom" guarantee.

  **Acceptance Criteria**:

  - [ ] `pytest tests/integration/test_backend_contract.py -v` shows passes for `[MuJoCoBackend, MockBackend, TutorialBackend]` — 3 parametrizations
  - [ ] All matrix CI jobs green
  - [ ] `tests/fixtures/tutorial_backend.py` is ≤50 lines; docstring explains how to write a backend

  **QA Scenarios**:

  ```
  Scenario: Happy path - 3-impl contract
    Tool: Bash
    Steps:
      1. pytest tests/integration/test_backend_contract.py -v 2>&1 | tee /tmp/contract3.txt
      2. Assert grep -c "PASSED" /tmp/contract3.txt >= (3 backends × N tests)
    Evidence: .sisyphus/evidence/task-24-contract-3impls.txt

  Scenario: Failure - break TutorialBackend, contract catches
    Tool: Bash
    Steps:
      1. Temporarily corrupt the tutorial backend (remove a required method)
      2. pytest tests/integration/test_backend_contract.py
      3. Assert non-zero exit; failure cite TutorialBackend
    Evidence: .sisyphus/evidence/task-24-contract-broken.txt
  ```

  **Evidence**: task-24-contract-3impls.txt, task-24-contract-broken.txt

  **Commit**: YES
  - Message: `ci(freedom): API/backend contract test with 3 implementations [T-24]`
  - Files: tests/integration/test_backend_contract.py (extend), tests/fixtures/tutorial_backend.py
  - Pre-commit: `pytest tests/integration/test_backend_contract.py -v`

- [ ] 25. **CI Test #3: Workflow Freedom (Headless / Scriptable / CI-Friendly)**

  **What to do**:
  - Add `tests/integration/test_workflow_freedom.py`:
    - Asserts NO `import tkinter`, `import mujoco.viewer`, `import matplotlib.pyplot` in any importable `<ship_name>` module (no GUI deps required)
    - Runs `python examples/hello_cartpole.py --headless` and validates exit 0, no DISPLAY env var leak
    - Runs full anchor demo in `--headless --use-cache --iterations=1` and validates clean exit
  - Add `--headless` flag (no-op marker; framework is already headless) to all example CLIs to make the claim explicit
  - Add to CI matrix

  **Must NOT do**:
  - Don't require X11 / display for any test
  - Don't add optional viewer deps to required dependency list (viewers are dev-extras only)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3A (PARALLEL — 7 freedom CI tests run concurrently)
  - **Blocks**: None
  - **Blocked By**: T22

  **References**:

  **Pattern References**: Headless CI patterns in graphics/sim projects
  **API/Type References**: Module-import analysis via `importlib`
  **Test References**: `pytest --no-display` semantics
  **External References**: PEP 410 / "no DISPLAY" convention

  **WHY Each Reference Matters**: Headless requirement is core to "workflow freedom" claim.

  **Acceptance Criteria**:

  - [ ] `pytest tests/integration/test_workflow_freedom.py -v` green
  - [ ] CI runners without DISPLAY env var pass full test suite
  - [ ] Importing `<ship_name>` does NOT pull in tkinter/matplotlib/mujoco.viewer (test asserts via `sys.modules` inspection)

  **QA Scenarios**:

  ```
  Scenario: Happy path - headless module import
    Tool: Bash
    Steps:
      1. unset DISPLAY
      2. python -c "import sys; import <ship_name>; bad = [m for m in ['tkinter','matplotlib.pyplot','mujoco.viewer'] if m in sys.modules]; print(f'bad={bad}'); assert not bad"
      3. Assert exit 0
    Evidence: .sisyphus/evidence/task-25-workflow-headless.txt

  Scenario: Failure - explicit viewer import surfaces violation
    Tool: Bash
    Steps:
      1. python -c "import <ship_name>.tasks.cartpole; import mujoco.viewer; ..."
      2. ... but this should NOT happen via normal import; only on explicit user opt-in
      3. Assert pytest catches if someone adds a transitive viewer import
    Evidence: .sisyphus/evidence/task-25-workflow-violation.txt
  ```

  **Evidence**: task-25-workflow-headless.txt, task-25-workflow-violation.txt

  **Commit**: YES
  - Message: `ci(freedom): workflow-freedom test (headless, no implicit GUI imports) [T-25]`
  - Files: tests/integration/test_workflow_freedom.py
  - Pre-commit: `pytest tests/integration/test_workflow_freedom.py -v`

- [ ] 26. **CI Test #4: Extension Freedom (50-Line Explicit-Registration Example)**

  **What to do**:
  - Create `examples/plugins/hello_task/`:
    - `hello_task.py` (≤50 lines): a third-party task implementing `Task` protocol, with module-level call to `register_task("hello_task", HelloTask)` at import time
    - `pyproject.toml` (for PyPI packaging only — no entry_points discovery section)
    - `README.md` explaining the pattern: "Import + register. No auto-discovery machinery; user explicitly imports the module to trigger registration."
  - Add `tests/integration/test_extension_freedom.py`:
    - Install the plugin example as a regular Python package
    - User does `import hello_task` → module's top-level `register_task()` call fires → task appears in `list_tasks()`
    - `make("hello_task")` runs 10 steps without exception
  - The framework ships ONLY the `register_task()` function (already added in T8). No `entry_points` discovery, no `importlib.metadata` walks, no plug-in lifecycle. Just an explicit function call from user code. This is the minimum-viable "extension freedom" with zero machinery.

  **Must NOT do**:
  - Don't add `entry_points` discovery via `importlib.metadata` (that IS plug-in machinery — defer to v0.2)
  - Don't ship a plug-in loader/lifecycle manager
  - Don't make the example task complicated; 50 lines is the budget
  - Don't use any auto-discovery mechanism — user must `import` explicitly

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3A (PARALLEL — 7 freedom CI tests run concurrently)
  - **Blocks**: 35, 36 (those build on this pattern)
  - **Blocked By**: T8, T22

  **References**:

  **Pattern References**:
  - `register_task()` API from T8 (already implemented)
  - Module-level registration patterns (e.g., Django models registering at import time)

  **API/Type References**:
  - `<ship_name>.register_task` (from T8)
  - `<ship_name>.protocols.Task` (from T5)

  **Test References**:
  - Plugin testing via temporary install + explicit import

  **External References**:
  - "Side-effect imports" Python idiom: https://docs.python.org/3/tutorial/modules.html#executing-modules-as-scripts

  **WHY Each Reference Matters**:
  - register_task API: the ONLY extension mechanism we ship in v0.1
  - Side-effect imports: documented Python pattern; users understand it; no special machinery needed

  **Acceptance Criteria**:

  - [ ] Plugin task source code is ≤50 lines (excluding boilerplate, asserted by `wc -l`)
  - [ ] After `pip install -e examples/plugins/hello_task/` AND `import hello_task` in user code, `list_tasks()` includes "hello_task"
  - [ ] `make("hello_task")` works after explicit import
  - [ ] `list_tasks()` does NOT include "hello_task" WITHOUT explicit import (proves no auto-discovery — guardrail enforced)
  - [ ] `pytest tests/integration/test_extension_freedom.py -v` green
  - [ ] Grep check: `! grep -r "entry_points" src/` (no entry_points usage in our code) — encoded as pre-commit

  **QA Scenarios**:

  ```
  Scenario: Happy path - explicit import triggers registration
    Tool: Bash
    Steps:
      1. pip install -e examples/plugins/hello_task/
      2. python -c "from <ship_name> import list_tasks; assert 'hello_task' not in list_tasks(); import hello_task; assert 'hello_task' in list_tasks(); print('OK')"
      3. python -c "import hello_task; from <ship_name> import make; env = make('hello_task'); env.reset(seed=0); env.step(env.action_space.sample()); print('OK')"
    Evidence: .sisyphus/evidence/task-26-plugin-install.txt

  Scenario: Failure - plugin without explicit import not discovered
    Tool: Bash
    Steps:
      1. pip install -e examples/plugins/hello_task/  (but do NOT import in client code)
      2. python -c "from <ship_name> import list_tasks; assert 'hello_task' not in list_tasks(); print('OK')"
      3. Assert: registration is purely opt-in via explicit import (no auto-discovery)
    Evidence: .sisyphus/evidence/task-26-plugin-no-import.txt

  Scenario: Guardrail - no entry_points machinery in our code
    Tool: Bash
    Steps:
      1. ! grep -rE "from importlib\\.metadata import entry_points|entry_points\\(" src/<ship_name>/
      2. Assert grep returns no matches (exit 1 for grep = success for us)
    Evidence: .sisyphus/evidence/task-26-no-entrypoints-grep.txt
  ```

  **Evidence**: task-26-plugin-install.txt, task-26-plugin-no-import.txt, task-26-no-entrypoints-grep.txt, line-count assertion in test output

  **Commit**: YES
  - Message: `ci(freedom): extension-freedom 50-line explicit-register example [T-26]`
  - Files: examples/plugins/hello_task/{hello_task.py,pyproject.toml,README.md}, tests/integration/test_extension_freedom.py
  - Pre-commit: `pytest tests/integration/test_extension_freedom.py -v && ! grep -rE "entry_points" src/<ship_name>/`

- [ ] 27. **CI Test #5: Agent/LLM Freedom (MCP Protocol Compliance)**

  **What to do**:
  - Add `tests/integration/test_agent_freedom.py`:
    - Spawn MCP server, send `tools/list`, assert ≥6 tools registered including all of `sim.*` + `task.list` + `ping`
    - Each tool's `inputSchema` is valid JSON Schema 2020-12 (use `jsonschema` Python lib or `ajv` in TS)
    - Each tool's `description` is ≥20 chars (no empty/placeholder descriptions)
    - JSON-RPC errors use spec codes (-32601 for unknown method, -32602 for invalid params, etc.)
    - Round-trip via Python MCP client AND via TypeScript MCP client (proves multi-client interop)
    - Save server transcript to evidence
  - Document in README: "Use ANY MCP-speaking client (Claude Desktop, opencode, codex, custom) — same tools work"

  **Must NOT do**:
  - Don't lock-in to opencode at the MCP level (opencode is only canonical for the orchestrator-loop side; MCP must stay open)
  - Don't add auth/token requirements in v0.1 (single-user local; trust boundary documented)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3A (PARALLEL — 7 freedom CI tests run concurrently)
  - **Blocks**: None
  - **Blocked By**: T11, T22

  **References**:

  **Pattern References**: T10/T11 MCP server, MCP spec test patterns
  **API/Type References**: MCP TS SDK + Python helper
  **Test References**: MCP example server tests
  **External References**: MCP spec (https://spec.modelcontextprotocol.io/), JSON-RPC 2.0 spec

  **WHY Each Reference Matters**:
  - MCP spec: defines what "compliance" means
  - JSON-RPC: error code semantics matter for interop

  **Acceptance Criteria**:

  - [ ] `pytest tests/integration/test_agent_freedom.py -v` green
  - [ ] `tools/list` returns ≥6 tools with valid schemas
  - [ ] Invalid method returns -32601
  - [ ] Invalid params returns -32602
  - [ ] Python + TS MCP clients both connect cleanly

  **QA Scenarios**:

  ```
  Scenario: Happy path - tools/list compliance
    Tool: interactive_bash
    Steps:
      1. tmux new-window -d 'bun run mcp-server'
      2. sleep 2
      3. curl -sS -X POST http://localhost:8765 -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' > /tmp/tools.json
      4. jq '.result.tools | length' /tmp/tools.json   # >= 6
      5. # Validate each tool schema
      6. python -c "
        import json, jsonschema
        tools = json.load(open('/tmp/tools.json'))['result']['tools']
        for t in tools:
            jsonschema.Draft202012Validator.check_schema(t['inputSchema'])
            assert len(t['description']) >= 20
        print('OK')
      "
      7. tmux kill-window -t mcp-server
    Evidence: .sisyphus/evidence/task-27-agent-mcp.json

  Scenario: Failure - schema corruption surfaces
    Tool: Bash
    Steps:
      1. Temporarily set a tool's inputSchema to {"type":"invalid_type"}
      2. Restart server
      3. Run schema validation → assert fails with clear message
    Evidence: .sisyphus/evidence/task-27-agent-bad-schema.txt
  ```

  **Evidence**: task-27-agent-mcp.json, task-27-agent-bad-schema.txt

  **Commit**: YES
  - Message: `ci(freedom): agent-freedom MCP protocol compliance test [T-27]`
  - Files: tests/integration/test_agent_freedom.py, mcp-server/tests/protocol_compliance.test.ts (TS side)
  - Pre-commit: `pytest tests/integration/test_agent_freedom.py -v`

- [ ] 28. **CI Test #6: Hardware Freedom (Matrix Green Across 3 OS)**

  **What to do**:
  - Verify GitHub Actions matrix (from T3) runs all of: tests, license check, contract, headless, agent, extension on `macos-14`, `macos-15`, `ubuntu-22.04`
  - Add a "hardware freedom" job to CI that explicitly asserts: "tests passed on all 3 OS in this matrix"
  - Failure-mode test: temporarily disable mac-15 job in a test branch and assert merge gate complains "hardware freedom requires all 3 OS green"
  - Document realistic env-count expectations in README (16-64 parallel envs on Mac vs 4096 on CUDA — set honest expectations)
  - Capture: list of OSes tested + Python versions

  **Must NOT do**:
  - Don't make claims about Windows passing without testing it (Windows is out of v0.1 scope)
  - Don't claim NVIDIA CUDA support (we're explicitly Mac-native; CUDA is unsupported in v0.1)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3A (PARALLEL — 7 freedom CI tests run concurrently)
  - **Blocks**: None
  - **Blocked By**: T3, T22

  **References**:

  **Pattern References**: T3's CI matrix config; status badge patterns
  **API/Type References**: GitHub Actions matrix syntax
  **Test References**: GHA workflow gate patterns
  **External References**: GHA matrix docs

  **WHY Each Reference Matters**: T3 set up the matrix; this task asserts the "hardware freedom" claim is testable.

  **Acceptance Criteria**:

  - [ ] CI matrix shows green for `macos-14`, `macos-15`, `ubuntu-22.04` on `main`
  - [ ] README has a "Supported Platforms" section with the matrix + honest caveats (no Windows, no CUDA, MPS ε-close determinism)
  - [ ] A merge to main is gated on all-3-OS green (branch protection rule documented in CONTRIBUTING.md)
  - [ ] `gh run list --branch main --workflow ci --limit 5 --json conclusion` shows recent all-green

  **QA Scenarios**:

  ```
  Scenario: Happy path - all 3 OS green
    Tool: Bash
    Steps:
      1. gh run list --branch main --workflow ci --limit 1 --json conclusion,status,jobs
      2. Assert all 3 jobs (macos-14, macos-15, ubuntu-22.04) have conclusion=success
    Evidence: .sisyphus/evidence/task-28-hw-matrix-green.json

  Scenario: Failure - simulate one OS failure
    Tool: Bash
    Steps:
      1. On a test branch, intentionally break a Mac-only path (e.g., add `if sys.platform == "linux": raise RuntimeError`)
      2. Push and wait for CI
      3. Assert linux job fails; mac jobs green; merge gate blocks
    Evidence: .sisyphus/evidence/task-28-hw-matrix-fail.json
  ```

  **Evidence**: task-28-hw-matrix-green.json, task-28-hw-matrix-fail.json

  **Commit**: YES
  - Message: `ci(freedom): hardware-freedom 3-OS matrix gate + supported-platforms doc [T-28]`
  - Files: .github/workflows/ci.yml (gate enforcement), README.md (Supported Platforms section), CONTRIBUTING.md (branch protection note)
  - Pre-commit: `yq eval . .github/workflows/ci.yml > /dev/null`

- [ ] 29. **CI Test #7: Research Freedom (Cold-Start Benchmark ≤120s on M5 Pro)**

  **What to do**:
  - Add `tests/integration/test_research_freedom.py` and `scripts/cold_start_bench.sh`:
    - `scripts/cold_start_bench.sh`:
      1. `rm -rf .venv mcp-server/node_modules`
      2. `time (uv venv && source .venv/bin/activate && uv pip install -e .)`
      3. `cd mcp-server && bun install`
      4. `python examples/hello_cartpole.py --headless --steps 10`
      5. Capture total wall-clock to `.sisyphus/evidence/cold_start_<host>.txt`
    - Local target: ≤120s on M5 Pro (canonical M5 baseline)
    - CI target: ≤300s on macOS-15 runner (slower hardware)
  - Add cold-start job to CI (not on every push — runs on PR + main; conditional via `paths: ['pyproject.toml', 'mcp-server/package.json', 'examples/hello_*']`)
  - Record canonical baseline timing in `.sisyphus/evidence/cold-start-baseline-m5pro.txt`

  **Must NOT do**:
  - Don't claim sub-120s on slower runners (be honest)
  - Don't include LLM cost in cold-start (offline-only)
  - Don't run cold-start on every CI push (too expensive); use path filters

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3A (PARALLEL — 7 freedom CI tests run concurrently)
  - **Blocks**: None
  - **Blocked By**: T22

  **References**:

  **Pattern References**: bench scripts in `astral-sh/uv` (MIT) for time-measurement idioms
  **API/Type References**: N/A
  **Test References**: pytest `--durations` flag
  **External References**: `hyperfine` (could be used for stable benchmarking, optional)

  **WHY Each Reference Matters**:
  - uv's bench scripts: clean way to measure install time
  - hyperfine: reduces noise; optional for CI

  **Acceptance Criteria**:

  - [ ] `scripts/cold_start_bench.sh` runs end-to-end, prints timing
  - [ ] On M5 Pro: total <120s recorded as canonical baseline
  - [ ] On macos-15 CI runner: total <300s asserted
  - [ ] CI failure if cold-start regresses by >30% from baseline (sliding-window comparison)

  **QA Scenarios**:

  ```
  Scenario: Happy path - M5 Pro baseline
    Tool: Bash
    Steps:
      1. bash scripts/cold_start_bench.sh
      2. Read .sisyphus/evidence/cold_start_$(hostname).txt
      3. Assert recorded time < 120 (M5 Pro)
    Evidence: .sisyphus/evidence/task-29-cold-start-m5.txt

  Scenario: Failure - inject artificial delay
    Tool: Bash
    Steps:
      1. Add `time.sleep(60)` to <ship_name>/__init__.py (test branch)
      2. Run cold-start bench
      3. Assert total time exceeds threshold; CI fails
    Evidence: .sisyphus/evidence/task-29-cold-start-regression.txt
  ```

  **Evidence**: task-29-cold-start-m5.txt, .sisyphus/evidence/cold-start-baseline-m5pro.txt, task-29-cold-start-regression.txt

  **Commit**: YES
  - Message: `ci(freedom): research-freedom cold-start benchmark + regression gate [T-29]`
  - Files: scripts/cold_start_bench.sh, tests/integration/test_research_freedom.py, .github/workflows/cold-start.yml, .sisyphus/evidence/cold-start-baseline-m5pro.txt
  - Pre-commit: `bash scripts/cold_start_bench.sh --quick`

- [ ] 30. **Second High-Quality Task — Locomotion (Quadruped Stand or Hop)**

  **What to do**:
  - Add `src/<ship_name>/tasks/locomotion.py` + MJCF: pick `ant` (smaller, simpler from mujoco_menagerie) or `quadruped` standing task
  - Goal: standing balance or hopping forward for `N` steps
  - Action space: joint torques; Observation: joint state + body pose + linear vel
  - Reward (baseline): forward velocity + uprightness term - control cost
  - Tests `tests/integration/test_locomotion.py`:
    - Episode runs without exception
    - Random policy fails (success rate <5%)
    - Determinism with seed (CPU)
  - Add to `task.list` via auto-registration

  **Must NOT do**:
  - Don't use humanoid (too hard for v0.1 with budget RL)
  - Don't tune to SOTA (baseline reward is fine; this is to demonstrate breadth, not solve locomotion)
  - Don't add complex terrain (flat ground sufficient)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: locomotion has subtle MJCF + reward issues; needs careful setup
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T31, T32-T34)
  - **Parallel Group**: Wave 3B (PARALLEL-PAIR — 2 tasks for breadth)
  - **Blocks**: None
  - **Blocked By**: T8, T22

  **References**:

  **Pattern References**: `mujoco_menagerie/ant` (BSD-3); `dm_control/suite/quadruped.py` (Apache-2.0)
  **API/Type References**: T5 protocols, T9 cartpole task pattern
  **Test References**: T9, T13 integration test patterns
  **External References**: MuJoCo `xml-reference` for actuator types

  **WHY Each Reference Matters**: Established MJCF + reward patterns from dm_control are battle-tested.

  **Acceptance Criteria**:

  - [ ] `make("ant_stand", "mujoco")` returns Environment; runs 200 steps cleanly
  - [ ] Random policy success_rate <0.05 over 50 episodes
  - [ ] Determinism: bit-exact CPU reset with seed
  - [ ] `pytest tests/integration/test_locomotion.py -v` green
  - [ ] Episode wall-clock <3s on M5 Pro

  **QA Scenarios**:

  ```
  Scenario: Happy path - random policy episodes
    Tool: Bash
    Steps:
      1. python -c "
        from <ship_name> import make
        env = make('ant_stand', 'mujoco')
        for ep in range(20):
            obs, _ = env.reset(seed=ep)
            for t in range(200):
                obs, r, term, trunc, _ = env.step(env.action_space.sample())
                if term or trunc: break
        print('OK')
      "
      2. Assert exit 0
    Evidence: .sisyphus/evidence/task-30-locomotion-random.txt

  Scenario: Failure - missing MJCF file
    Tool: Bash
    Steps:
      1. Rename MJCF; attempt make()
      2. Assert raises FileNotFoundError
    Evidence: .sisyphus/evidence/task-30-locomotion-no-asset.txt
  ```

  **Evidence**: task-30-locomotion-random.txt, task-30-locomotion-no-asset.txt

  **Commit**: YES
  - Message: `feat(tasks): add ant_stand locomotion task [T-30]`
  - Files: src/<ship_name>/tasks/locomotion.py, src/<ship_name>/assets/ant.xml, tests/integration/test_locomotion.py, NOTICE update
  - Pre-commit: `pytest tests/integration/test_locomotion.py -v`

- [ ] 31. **Third High-Quality Task — Manipulation Variant (Franka Push or Drawer-Open)**

  **What to do**:
  - Add `src/<ship_name>/tasks/franka_push.py` (or `franka_drawer.py`) + asset
  - Variant of Franka manipulation: object pushing to target (simpler than pick-place, faster baseline learning) OR drawer-open (more spatial reasoning)
  - Choose ONE based on Phase 0 fluency: if MuJoCo score ≥2, drawer-open; else push (simpler)
  - Reward (baseline): contact + progress towards target
  - Tests mirror T13 pattern

  **Must NOT do**:
  - Don't add multi-object tasks (one object is enough)
  - Don't share MJCF parts between tasks via includes that introduce versioning headaches; just duplicate small files

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T30, T32-T34)
  - **Parallel Group**: Wave 3B (PARALLEL-PAIR — 2 tasks for breadth)
  - **Blocks**: None
  - **Blocked By**: T13, T22

  **References**: T13 pattern; mujoco_menagerie; dm_control suite
  **API/Type References**: T5
  **Test References**: T13 integration tests pattern
  **External References**: Eureka Franka task variations

  **WHY Each Reference Matters**: T13 is the template; this task demonstrates the framework extends to a different manipulation goal.

  **Acceptance Criteria**:

  - [ ] `make("franka_push", "mujoco")` works, 200-step episodes clean
  - [ ] Random success <5% over 50 episodes
  - [ ] Determinism with seed
  - [ ] `pytest tests/integration/test_franka_push.py -v` green

  **QA Scenarios**:

  ```
  Scenario: Happy path - random policy
    Tool: Bash
    Steps:
      1. python -c "from <ship_name> import make; env = make('franka_push', 'mujoco'); env.reset(seed=0); [env.step(env.action_space.sample()) for _ in range(100)]; print('OK')"
      2. Assert exit 0
    Evidence: .sisyphus/evidence/task-31-push-random.txt

  Scenario: Failure - invalid backend
    Tool: Bash
    Steps:
      1. make('franka_push', 'invalid_backend')
      2. Assert clear error message
    Evidence: .sisyphus/evidence/task-31-push-bad-backend.txt
  ```

  **Evidence**: task-31-push-random.txt, task-31-push-bad-backend.txt

  **Commit**: YES
  - Message: `feat(tasks): add franka_push manipulation variant [T-31]`
  - Files: src/<ship_name>/tasks/franka_push.py, src/<ship_name>/assets/franka_push.xml, tests/integration/test_franka_push.py
  - Pre-commit: `pytest tests/integration/test_franka_push.py -v`

- [ ] 32. **Documentation — README + Getting Started**

  **What to do**:
  - Polish `README.md`:
    - Hero section: 1-line description + animated GIF of anchor demo + 30-second quick install
    - Status: alpha (v0.1)
    - Why this exists (Mac-native Eureka workflow, no CUDA) — concise, ≤4 paragraphs
    - Quick demo (copy-paste: `pip install <ship_name> && python -m <ship_name>.examples.hello_cartpole`)
    - Anchor demo callout (with caveat about opencode requirement)
    - 7 Freedoms badges (one per CI test result)
    - Roadmap section: what's in v0.2, v0.3 (Drake, Taichi, VLA, full USD, plug-in machinery, IsaacLab compat, multi-LLM, etc.)
    - Contribution invitation; link to CONTRIBUTING.md
    - License: MIT, with NOTICE link
  - Add `docs/getting-started.md`:
    - Install (uv + bun)
    - First env (cartpole CLI)
    - First task (link to extension example)
    - First Eureka run (link to anchor demo)
    - Common pitfalls
  - Add badges: CI matrix, license, PyPI version, npm version, docs

  **Must NOT do**:
  - Don't oversell ("competes with Isaac Lab" — instead "Mac-native alternative for one specific workflow")
  - Don't bury the realistic-env-count caveat
  - Don't add marketing fluff that doesn't map to a CI test

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: documentation; technical writing skill
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T30, T31, T33, T34)
  - **Parallel Group**: Wave 3C (PARALLEL — 3 docs tasks)
  - **Blocks**: None
  - **Blocked By**: T22 (demo done first)

  **References**:

  **Pattern References**: README of `astral-sh/ruff`, `huggingface/transformers`, `eureka-research/Eureka` for tone calibration
  **API/Type References**: N/A
  **Test References**: Docs build check in CI
  **External References**: keepachangelog.com, shields.io for badges

  **WHY Each Reference Matters**:
  - Top OSS READMEs: define quality bar
  - shields.io: standard badge service

  **Acceptance Criteria**:

  - [ ] README.md exists with all sections listed above
  - [ ] All code snippets in README execute cleanly (validated by `tests/integration/test_readme_snippets.py` running each fenced ` ```bash` block)
  - [ ] No reference to deferred features (Drake/Taichi/VLA) as "current" — only as "roadmap"
  - [ ] Animated GIF or terminal recording linked
  - [ ] Badges resolve (no 404s) — CI check

  **QA Scenarios**:

  ```
  Scenario: Happy path - README snippets execute
    Tool: Bash
    Steps:
      1. pytest tests/integration/test_readme_snippets.py -v
      2. Assert exit 0
    Evidence: .sisyphus/evidence/task-32-readme-snippets.txt

  Scenario: Failure - broken snippet
    Tool: Bash
    Steps:
      1. Modify README to include broken bash command
      2. Run snippet executor
      3. Assert exit non-zero with cite of broken block
    Evidence: .sisyphus/evidence/task-32-readme-broken.txt
  ```

  **Evidence**: task-32-readme-snippets.txt, task-32-readme-broken.txt, README.md screenshot

  **Commit**: YES
  - Message: `docs(readme): v0.1 README + Getting Started [T-32]`
  - Files: README.md, docs/getting-started.md, tests/integration/test_readme_snippets.py
  - Pre-commit: `pytest tests/integration/test_readme_snippets.py -v`

- [ ] 33. **Documentation — Tutorial (Eureka-on-Franka Walkthrough)**

  **What to do**:
  - Create `docs/tutorial-eureka-franka.md`:
    - Step-by-step walkthrough of running the anchor demo
    - Explain each piece: orchestrator → reward gen → evaluator → controller → loop
    - Show example prompts, example LLM outputs, example reward functions
    - Annotated terminal output for one iteration
    - Common gotchas (opencode setup, cache, determinism caveats)
    - "What's next" — try another task, write your own
  - Length: ~1500-2500 words; target 15-20 min reading time
  - Include downloadable runs/anchor-v0.1-canonical/ tree as reference output

  **Must NOT do**:
  - Don't go deep on RL theory (link to external resources)
  - Don't include screenshots that get out of date — use code blocks and ASCII tables
  - Don't claim features not in v0.1

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3C (PARALLEL — 3 docs tasks)
  - **Blocks**: None
  - **Blocked By**: T22 (anchor demo must work)

  **References**:

  **Pattern References**: Eureka paper as content reference, but reworked for our concrete pipeline
  **API/Type References**: T16-T22 modules
  **Test References**: Same snippet-executor as T32 (extends to docs/)
  **External References**: PPO ICLR blog (reference link for readers wanting more)

  **WHY Each Reference Matters**: Tutorial needs to be self-contained but pointers to deeper material help adoption.

  **Acceptance Criteria**:

  - [ ] `docs/tutorial-eureka-franka.md` exists
  - [ ] All code snippets in tutorial execute cleanly via snippet executor
  - [ ] Tutorial cross-links to README and Getting Started

  **QA Scenarios**:

  ```
  Scenario: Happy path - tutorial snippets work
    Tool: Bash
    Steps:
      1. pytest tests/integration/test_readme_snippets.py::test_tutorial_snippets -v
      2. Assert exit 0
    Evidence: .sisyphus/evidence/task-33-tutorial-snippets.txt

  Scenario: Failure - stale tutorial cite
    Tool: Bash
    Steps:
      1. Add a Python snippet that references a removed module name
      2. Snippet executor catches
    Evidence: .sisyphus/evidence/task-33-tutorial-stale.txt
  ```

  **Evidence**: task-33-tutorial-snippets.txt, task-33-tutorial-stale.txt

  **Commit**: YES
  - Message: `docs(tutorial): Eureka-on-Franka step-by-step walkthrough [T-33]`
  - Files: docs/tutorial-eureka-franka.md
  - Pre-commit: `pytest tests/integration/test_readme_snippets.py -v`

- [ ] 34. **Documentation — Auto-Generated API Reference**

  **What to do**:
  - Set up Sphinx (Python) + TypeDoc (TS):
    - Python: `docs/conf.py` with `autodoc`, `napoleon`, `myst_parser` (markdown); output to `docs/_build/python/`
    - TS: `mcp-server/typedoc.json`; output to `docs/_build/ts/`
  - GitHub Pages config to publish on tag push
  - Add `docs/api/` index page linking both
  - CI: docs build job that fails if docstrings missing on public API or if links broken (use `sphinx-linkcheck`)
  - Add docstring coverage gate: ≥80% of public symbols documented

  **Must NOT do**:
  - Don't use heavy theming; default Furo (Sphinx) or pdoc is fine
  - Don't deploy docs on every push (only on tag/release)

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: docs tooling configuration
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3C (PARALLEL — 3 docs tasks)
  - **Blocks**: 41 (demo site references API docs)
  - **Blocked By**: T22

  **References**:

  **Pattern References**: pytorch, FastAPI, ruff docs sites
  **API/Type References**: N/A
  **Test References**: sphinx-linkcheck, typedoc validation
  **External References**: Sphinx docs, TypeDoc docs, MyST parser

  **WHY Each Reference Matters**: Established tools, low surface for bugs.

  **Acceptance Criteria**:

  - [ ] `cd docs && sphinx-build -W .` succeeds (warnings as errors)
  - [ ] `cd mcp-server && bun run docs` builds TS docs
  - [ ] `sphinx-linkcheck` passes (no broken links)
  - [ ] Docstring coverage ≥80% (measured by interrogate or similar)
  - [ ] Docs publish on release tag via GitHub Pages

  **QA Scenarios**:

  ```
  Scenario: Happy path - docs build clean
    Tool: Bash
    Steps:
      1. cd docs && sphinx-build -W . _build/python
      2. Assert exit 0
      3. cd ../mcp-server && bun run docs
      4. Assert exit 0
    Evidence: .sisyphus/evidence/task-34-docs-build.txt

  Scenario: Failure - missing docstring blocks build
    Tool: Bash
    Steps:
      1. Add a new public function with no docstring; lower coverage gate
      2. CI fails
    Evidence: .sisyphus/evidence/task-34-docs-missing-docstring.txt
  ```

  **Evidence**: task-34-docs-build.txt, task-34-docs-missing-docstring.txt

  **Commit**: YES
  - Message: `docs(api): auto-gen Python + TS API reference + linkcheck CI [T-34]`
  - Files: docs/conf.py, docs/index.md, docs/api/*, mcp-server/typedoc.json, .github/workflows/docs.yml
  - Pre-commit: `sphinx-build -W docs/ docs/_build/python`

- [ ] 35. **Extension Points Design Doc (Protocol Interfaces Frozen for v0.1)**

  **What to do**:
  - Create `docs/extension-points.md`:
    - Catalog of CURRENT extension points (the bare minimum we keep open in v0.1 — NO discovery machinery):
      - Tasks via `register_task(name, factory)` function call (already in T8). User imports their module → top-level `register_task()` call fires. No auto-discovery.
      - Backends via `Backend` protocol (T5; we ship MuJoCo + Mock; users can write their own and pass to `make(..., backend=instance)`)
      - LLM clients via `LLMClient` protocol (T15; we ship opencode; users can write their own and pass to orchestrator)
      - Reward functions: hand-written or generated. Pass code string to evaluator (T18) which sandbox-execs.
    - Catalog of FUTURE extension points (documented but explicitly NOT implemented in v0.1):
      - Auto-discovery via `entry_points` (v0.2 — needs careful spec design)
      - Plug-in lifecycle (load/unload/sandboxed; v0.2)
      - PolicyServer (for VLA; v0.2)
      - Env generators (for procedural; v0.2)
      - Multi-LLM adapter (v0.2)
      - Drake/Taichi backends (v0.2)
    - Design principles (called out explicitly):
      - **Protocol-based** (structural typing via `typing.Protocol`)
      - **Rule of Three before generalizing** — don't extract until ≥3 concrete instances
      - **NO machinery beyond explicit function calls in v0.1** — discovery, lifecycle, sandboxing are v0.2 concerns. User imports modules and calls API functions; no `importlib.metadata` walks.
      - Any addition must be ≥3-concrete-uses justified and Oracle-reviewed
  - Freeze v0.1 protocols: any breaking changes after this task require version bump
  - Tests `tests/integration/test_extension_points.py`:
    - Asserts none of the FUTURE extension points have implementation files (defensive: catches scope creep)
    - Asserts CURRENT extension points work (overlapping with T24, T26)
    - Asserts no `entry_points`/`importlib.metadata` walk in `src/<ship_name>/` (guardrail)

  **Must NOT do**:
  - Don't promise future extension points are "coming soon" without a version target
  - Don't add interfaces that have no concrete implementation today (premature abstraction)
  - Don't change public API after this task without semver bump

  **Recommended Agent Profile**:
  - **Category**: `writing`
    - Reason: API design docs + interface stewardship
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (Wave 4A BRIDGE — extension points doc must precede Wave 4B + release)
  - **Parallel Group**: Wave 4A (BRIDGE — single task; gates T36, T37, T38, T39)
  - **Blocks**: T36, T37, T38, T39
  - **Blocked By**: Wave 3 complete (T23-T34)

  **References**:

  **Pattern References**: Anthropic MCP spec / Rust API guidelines / Python typing PEPs
  **API/Type References**: T5 protocols
  **Test References**: T24, T26
  **External References**: SemVer 2.0; "Hyrum's Law" essay (for stability awareness)

  **WHY Each Reference Matters**:
  - SemVer: governance of breaking changes
  - Hyrum's Law: warning about implicit contracts users will form

  **Acceptance Criteria**:

  - [ ] `docs/extension-points.md` exists with sections: Current Extension Points, Future Roadmap, Design Principles
  - [ ] All current EPs have test coverage (cross-link to T24, T26)
  - [ ] `tests/integration/test_extension_points.py` asserts NO `class PolicyServer` non-stub impl exists in `src/` (scope-creep canary)
  - [ ] All snippets in doc execute cleanly

  **QA Scenarios**:

  ```
  Scenario: Happy path - canary test
    Tool: Bash
    Steps:
      1. pytest tests/integration/test_extension_points.py -v
      2. Assert exit 0
      3. # Asserts: no PolicyServer impl, no GenSim impl, etc.
    Evidence: .sisyphus/evidence/task-35-ep-canary.txt

  Scenario: Failure - someone adds PolicyServer impl
    Tool: Bash
    Steps:
      1. Add a stub `class PolicyServer: def serve(): pass` in src/<ship_name>/serving.py
      2. Run canary test
      3. Assert non-zero exit; test names the violation file
    Evidence: .sisyphus/evidence/task-35-ep-violation.txt
  ```

  **Evidence**: task-35-ep-canary.txt, task-35-ep-violation.txt

  **Commit**: YES
  - Message: `docs(extension-points): freeze v0.1 protocol surface + roadmap [T-35]`
  - Files: docs/extension-points.md, tests/integration/test_extension_points.py
  - Pre-commit: `pytest tests/integration/test_extension_points.py -v`

- [ ] 36. **Hello-World Plugin Example (PyPI-Installable)**

  **What to do**:
  - Build on T26 example: package the `hello_task` plugin as a standalone PyPI-installable demo project under `examples/plugins/hello_task/`:
    - Already has pyproject.toml (T26); add `[build-system]`, ready for `python -m build`
    - Add CI step that builds the plugin and installs it in a fresh venv, runs it
    - Add to `examples/plugins/README.md`: full tutorial "How to publish your own task as a PyPI package"

  **Must NOT do**:
  - Don't publish this to real PyPI (it's example code; document the steps)
  - Don't add `entry_points`-based discovery; use the explicit `import + register_task()` pattern only (consistent with the top-level no-plug-in-machinery guardrail and T8/T26/T35). MIT-licensed example only.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T37, T38)
  - **Parallel Group**: Wave 4B (PARALLEL — 3 tasks after T35; mutually independent)
  - **Blocks**: None
  - **Blocked By**: T26, T35

  **References**:

  **Pattern References**: T26 plugin; PyPI publishing tutorials
  **API/Type References**: `<ship_name>.register_task` API (from T8); PEP 517/621 packaging
  **Test References**: T26 plus PyPI install test
  **External References**: Python Packaging User Guide

  **WHY Each Reference Matters**: Plugin pattern needs to be PyPI-installable to be useful in practice. NO entry_points discovery — user imports the module explicitly.

  **Acceptance Criteria**:

  - [ ] `python -m build examples/plugins/hello_task/` produces a valid wheel
  - [ ] Wheel installs cleanly in fresh venv: `pip install dist/hello_task-*.whl`
  - [ ] After install AND explicit `import hello_task`, `<ship_name>.list_tasks()` includes it
  - [ ] After install WITHOUT explicit import, `list_tasks()` does NOT include it (proves no auto-discovery)
  - [ ] `examples/plugins/README.md` is a complete tutorial documenting the "import-and-register" pattern

  **QA Scenarios**:

  ```
  Scenario: Happy path - build, install, explicit import, run
    Tool: Bash
    Steps:
      1. cd examples/plugins/hello_task && python -m build
      2. ls dist/ | grep .whl
      3. python -m venv /tmp/plugin-test
      4. /tmp/plugin-test/bin/pip install dist/*.whl <ship_name>
      5. /tmp/plugin-test/bin/python -c "import hello_task; from <ship_name> import list_tasks; assert 'hello_task' in list_tasks(); print('OK')"
      6. # Also assert: without import, registration does NOT happen
      7. /tmp/plugin-test/bin/python -c "from <ship_name> import list_tasks; assert 'hello_task' not in list_tasks(); print('OK')"
    Evidence: .sisyphus/evidence/task-36-plugin-pypi.txt

  Scenario: Failure - missing pyproject build-system
    Tool: Bash
    Steps:
      1. Remove [build-system] from pyproject.toml
      2. `python -m build`
      3. Assert non-zero exit with build-error mentioning build-system
    Evidence: .sisyphus/evidence/task-36-plugin-no-build-system.txt
  ```

  **Evidence**: task-36-plugin-pypi.txt, task-36-plugin-no-build-system.txt

  **Commit**: YES
  - Message: `feat(examples/plugins): PyPI-installable hello_task plugin + tutorial [T-36]`
  - Files: examples/plugins/hello_task/pyproject.toml (build-system additions), examples/plugins/README.md
  - Pre-commit: `python -m build examples/plugins/hello_task/`

- [ ] 37. **PyPI Packaging Setup**

  **What to do**:
  - Finalize `pyproject.toml` for PyPI release:
    - Project name (ship name from Phase 0)
    - Description (≤140 chars)
    - Classifiers: language, license, OS (macOS/Linux), Python versions
    - Keywords: `simulation`, `robotics`, `reinforcement-learning`, `agentic`, `mcp`
    - URLs: Homepage, Repository, Documentation, Issues
    - `[project.scripts]`: `<ship_name>-hello`, `<ship_name>-orchestrator`
    - `[project.optional-dependencies]`: dev, test, docs (Sphinx etc.)
  - Add `.github/workflows/release.yml` for PyPI publish on tag (manual approval gate)
  - Add `MANIFEST.in` if assets need to be included
  - Test: `python -m build` produces wheel + sdist; `twine check dist/*` passes

  **Must NOT do**:
  - Don't actually publish to real PyPI in this task (T40 does first release)
  - Don't bundle huge assets (MJCFs are small; if any large data, host externally)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T36, T38)
  - **Parallel Group**: Wave 4B (PARALLEL — 3 tasks after T35; mutually independent)
  - **Blocks**: T39, T40
  - **Blocked By**: T35

  **References**:

  **Pattern References**: pyproject.toml from `astral-sh/uv`, `pytorch/torch` (MIT/BSD examples)
  **API/Type References**: PEP 621, PEP 517
  **Test References**: `twine check`
  **External References**: PyPI Packaging User Guide

  **WHY Each Reference Matters**: PEP 621 is the canonical pyproject format; PyPI uses these classifiers.

  **Acceptance Criteria**:

  - [ ] `python -m build` produces wheel + sdist with no warnings
  - [ ] `twine check dist/*` passes
  - [ ] Wheel installs in fresh venv and runs CLI commands
  - [ ] Classifiers and metadata complete (no "UNKNOWN" fields)

  **QA Scenarios**:

  ```
  Scenario: Happy path - build artifacts valid
    Tool: Bash
    Steps:
      1. rm -rf dist && python -m build
      2. twine check dist/*
      3. ls dist/ | grep -E '\\.whl$|\\.tar\\.gz$'
    Evidence: .sisyphus/evidence/task-37-pypi-build.txt

  Scenario: Failure - invalid classifier
    Tool: Bash
    Steps:
      1. Inject `"License :: Bogus"` classifier
      2. `python -m build && twine check dist/*`
      3. Assert non-zero exit citing invalid classifier
    Evidence: .sisyphus/evidence/task-37-pypi-bad-classifier.txt
  ```

  **Evidence**: task-37-pypi-build.txt, task-37-pypi-bad-classifier.txt

  **Commit**: YES
  - Message: `chore(release): finalize pyproject for PyPI [T-37]`
  - Files: pyproject.toml, MANIFEST.in, .github/workflows/release.yml
  - Pre-commit: `python -m build && twine check dist/*`

- [ ] 38. **npm Packaging Setup (MCP Server)**

  **What to do**:
  - Finalize `mcp-server/package.json` for npm publish:
    - Name: `@<ship_name>/mcp-server` (or unscoped `<ship_name>-mcp` if name available)
    - Description, repository, keywords, license MIT
    - `"bin"`: `<ship_name>-mcp-server` → `dist/server.js`
    - `"main"`, `"module"`, `"types"` fields for ESM/CJS/typings
    - `"files"`: only ship `dist/` and `README.md`
    - Build script: `tsc --emitDeclarationOnly + bun build src/server.ts --outdir=dist --target=node` (or use tsup)
  - Set up `dist/` build pipeline; ensure no `dev`-only deps shipped
  - Add npm publish step in `.github/workflows/release.yml` (matches T37's PyPI publish)
  - Add `tsconfig.build.json` for production build
  - `npm pack` smoke test: produces `.tgz`, can install in fresh project

  **Must NOT do**:
  - Don't publish in this task (T40)
  - Don't ship source maps with private path info
  - Don't ship `node_modules`

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T36, T37)
  - **Parallel Group**: Wave 4B (PARALLEL — 3 tasks after T35; mutually independent)
  - **Blocks**: T39, T40
  - **Blocked By**: T35

  **References**:

  **Pattern References**: `@modelcontextprotocol/sdk` package.json for canonical MCP package shape
  **API/Type References**: bun build / tsup docs
  **Test References**: `npm pack && npm install -g ./pkg.tgz` smoke test
  **External References**: npm package conventions, Conventional Commits + semantic-release

  **WHY Each Reference Matters**:
  - MCP SDK package.json: existing pattern that opencode/claude expect

  **Acceptance Criteria**:

  - [ ] `cd mcp-server && bun run build` produces `dist/server.js` + types
  - [ ] `npm pack` produces a `.tgz` (or bun's equivalent); inspect via `tar -tzf` — only `dist/` + `README.md` + `package.json` + `LICENSE`
  - [ ] Installable in fresh node project; CLI bin `<ship_name>-mcp-server` works
  - [ ] No source maps shipped (or only `.d.ts.map` / cleaned source maps)

  **QA Scenarios**:

  ```
  Scenario: Happy path - pack + install + run
    Tool: Bash
    Steps:
      1. cd mcp-server && bun run build && npm pack
      2. ls *.tgz
      3. cd /tmp && mkdir test-install && cd test-install && npm init -y && npm install /path/to/pkg.tgz
      4. npx <ship_name>-mcp-server --help
      5. Assert exit 0
    Evidence: .sisyphus/evidence/task-38-npm-pack.txt

  Scenario: Failure - missing bin in package.json
    Tool: Bash
    Steps:
      1. Remove "bin" field from package.json
      2. Pack & install
      3. `npx <ship_name>-mcp-server` fails with "command not found"
    Evidence: .sisyphus/evidence/task-38-npm-no-bin.txt
  ```

  **Evidence**: task-38-npm-pack.txt, task-38-npm-no-bin.txt

  **Commit**: YES
  - Message: `chore(release): finalize npm packaging for MCP server [T-38]`
  - Files: mcp-server/package.json, mcp-server/tsconfig.build.json, .github/workflows/release.yml (additions)
  - Pre-commit: `cd mcp-server && bun run build && npm pack --dry-run`

- [ ] 39. **Release Process Automation (Semver Bump, CHANGELOG, Signed Tag)**

  **What to do**:
  - Create `scripts/release.sh`:
    - Validates clean working tree
    - Asks (or accepts arg) version bump type (patch/minor/major)
    - Updates `pyproject.toml`, `mcp-server/package.json` to new version
    - Updates `CHANGELOG.md` (Keep-a-Changelog format) with new section from `git log` since last tag
    - Commits "chore: release v0.X.Y"
    - Creates signed git tag `v0.X.Y` (`git tag -s`)
    - Pushes commit + tag
    - GHA `release.yml` then takes over for PyPI + npm publish + GitHub Release notes
  - Use `python-semantic-release` or `release-please` if appropriate; otherwise a simple script
  - Pre-commit: SemVer validation, CHANGELOG format check
  - Test in dry-run mode on a side branch — ensure script works end-to-end without actually publishing

  **Must NOT do**:
  - Don't auto-publish without human approval gate (GHA workflow_dispatch or environment approval)
  - Don't sign with an ephemeral key — document GPG/SSH signing setup

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: release pipelines have many failure modes; careful design needed
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on T37 + T38)
  - **Parallel Group**: Wave 4C (BRIDGE — release automation must precede actual release)
  - **Blocks**: T40
  - **Blocked By**: T37, T38

  **References**:

  **Pattern References**: `astral-sh/ruff` release scripts; `python-semantic-release`
  **API/Type References**: SemVer 2.0
  **Test References**: Dry-run mode
  **External References**: Keep-a-Changelog format

  **WHY Each Reference Matters**: Release scripting bugs cost trust; copy proven patterns.

  **Acceptance Criteria**:

  - [ ] `scripts/release.sh --dry-run --bump=patch` walks through all steps without publishing
  - [ ] CHANGELOG.md updated with valid Keep-a-Changelog format
  - [ ] Tag created with valid SemVer
  - [ ] Release GHA workflow can be triggered via `workflow_dispatch` (manual)

  **QA Scenarios**:

  ```
  Scenario: Happy path - dry run patch bump
    Tool: Bash
    Steps:
      1. git checkout -b test-release
      2. bash scripts/release.sh --dry-run --bump=patch
      3. Assert exit 0
      4. Assert pyproject and package.json version were bumped (in working tree, but rolled back since --dry-run)
    Evidence: .sisyphus/evidence/task-39-release-dryrun.txt

  Scenario: Failure - dirty working tree
    Tool: Bash
    Steps:
      1. Make uncommitted change
      2. bash scripts/release.sh --bump=patch
      3. Assert non-zero exit citing dirty tree
    Evidence: .sisyphus/evidence/task-39-release-dirty.txt
  ```

  **Evidence**: task-39-release-dryrun.txt, task-39-release-dirty.txt

  **Commit**: YES
  - Message: `chore(release): automation script + GHA release workflow [T-39]`
  - Files: scripts/release.sh, .github/workflows/release.yml (finalized), CHANGELOG.md (template)
  - Pre-commit: `bash scripts/release.sh --dry-run --bump=patch`

- [ ] 40. **v0.1.0 First Release (PyPI + npm Publish, GitHub Release)**

  **What to do**:
  - Final pre-flight: all CI green, all F1-F4 prep tests pass (smoke-level)
  - Run `bash scripts/release.sh --bump=minor` (0.0.0 → 0.1.0)
  - Approve GHA release workflow run
  - Verify:
    - PyPI: `pip install <ship_name>==0.1.0` works
    - npm: `npm install -g <ship_name>-mcp@0.1.0` works
    - GitHub Release page shows changelog + checksums
  - Post release: announce via README badge, document `v0.1` tag

  **Must NOT do**:
  - Don't release if any v0.1 CI gates are red
  - Don't release without all F1-F4 review tests already passing
  - Don't release without explicit human approval (workflow_dispatch)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO (capstone)
  - **Parallel Group**: Wave 4D (BRIDGE — actual release is structurally atomic, sequential after Wave 4C)
  - **Blocks**: 41 (demo site links to PyPI page)
  - **Blocked By**: T39

  **References**:

  **Pattern References**: First-release announcements from OSS projects
  **API/Type References**: PyPI + npm public APIs
  **Test References**: post-publish smoke test in fresh container
  **External References**: PyPI security best practices

  **WHY Each Reference Matters**: First release sets the tone for the project's perceived quality.

  **Acceptance Criteria**:

  - [ ] `pip install <ship_name>==0.1.0` succeeds in fresh venv
  - [ ] `npm install <ship_name>-mcp@0.1.0` succeeds
  - [ ] GitHub Release page exists at `v0.1.0` tag
  - [ ] Anchor demo runnable from a freshly-installed PyPI release in <120s install + run

  **QA Scenarios**:

  ```
  Scenario: Happy path - end-to-end fresh install + demo
    Tool: Bash
    Steps:
      1. python -m venv /tmp/fresh-install
      2. /tmp/fresh-install/bin/pip install <ship_name>==0.1.0
      3. /tmp/fresh-install/bin/python -c "from <ship_name> import make; env = make('cartpole'); env.reset(seed=0); print('OK')"
      4. Time the whole sequence; assert under 180s
    Evidence: .sisyphus/evidence/task-40-release-fresh-install.txt

  Scenario: Failure - publish blocked by failing CI
    Tool: Bash
    Steps:
      1. Inject a failing test on main
      2. Trigger release workflow
      3. Assert workflow fails at pre-flight step
    Evidence: .sisyphus/evidence/task-40-release-blocked.txt
  ```

  **Evidence**: task-40-release-fresh-install.txt, task-40-release-blocked.txt, GitHub Release URL

  **Commit**: YES (the release tag commit)
  - Message: `chore: release v0.1.0 🎉 [T-40]`
  - Files: pyproject.toml (version), mcp-server/package.json (version), CHANGELOG.md (release entry)
  - Pre-commit: `bash scripts/release.sh --pre-flight-check`

- [ ] 41. **Demo Site (Static Site with Embedded Demo)**

  **What to do**:
  - Create static site at `site/` (Astro, Eleventy, or just plain HTML+CSS — choose lightest):
    - Landing page: project name, tagline, "30-second demo" terminal recording (asciinema embed)
    - "What this is" section (≤3 paragraphs)
    - 7 freedoms with CI badges live-pulled from GitHub Actions
    - Anchor demo: video/cast embed + final results table
    - Quick install snippets (copy-paste)
    - Links: GitHub repo, PyPI, npm, docs
    - Roadmap section (link to v0.2 milestones)
  - Deploy via GitHub Pages on `main` branch's `/site/` or `gh-pages` branch
  - Add `site/dev-server.sh` for local preview
  - DNS: optional custom subdomain (not required for v0.1)

  **Must NOT do**:
  - Don't add user signup/login (static site only)
  - Don't add tracking/analytics in v0.1 (privacy default)
  - Don't make the site heavy with frameworks (no React/Next.js unless trivially small)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: web design + asset embedding + responsive layout
  - **Skills**: `[frontend-ui-ux]`
    - `frontend-ui-ux`: designer-developer pairing for landing-page quality

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T42, T43)
  - **Parallel Group**: Wave 4E (PARALLEL — 3 post-release tasks)
  - **Blocks**: None
  - **Blocked By**: T22, T40

  **References**:

  **Pattern References**: `astral-sh/uv` landing page, `denoland/deno` landing page (clean, fast, OSS)
  **API/Type References**: GitHub Pages config; asciinema embed
  **Test References**: Lighthouse score gate (optional)
  **External References**: asciinema, plausible (privacy-friendly analytics if needed v0.2)

  **WHY Each Reference Matters**: First impression matters; clean OSS landing pages have a recognizable look.

  **Acceptance Criteria**:

  - [ ] Site builds with `site/build.sh` (or equivalent)
  - [ ] Site live at `https://<gh_username>.github.io/<ship_name>/` (or chosen URL)
  - [ ] Asciinema cast of anchor demo embedded
  - [ ] 7 freedom CI badges visible and live (refresh from GHA)
  - [ ] Mobile-responsive (Lighthouse mobile score ≥80)
  - [ ] No broken links

  **QA Scenarios**:

  ```
  Scenario: Happy path - site loads, badges valid
    Tool: Playwright
    Preconditions: Site deployed
    Steps:
      1. await page.goto('https://<gh_user>.github.io/<ship_name>/')
      2. Assert title contains ship name
      3. const badges = await page.$$('.freedom-badge')
      4. Assert badges.length >= 7
      5. await page.screenshot({path: '.sisyphus/evidence/task-41-site-screenshot.png'})
    Evidence: task-41-site-screenshot.png

  Scenario: Failure - broken link in roadmap
    Tool: Bash
    Steps:
      1. Use `lychee` or similar link-checker on site/
      2. Inject broken URL → checker fails with exit non-zero
    Evidence: .sisyphus/evidence/task-41-link-check.txt
  ```

  **Evidence**: task-41-site-screenshot.png, task-41-link-check.txt, deployed URL

  **Commit**: YES
  - Message: `feat(site): v0.1 demo landing page [T-41]`
  - Files: site/*, .github/workflows/pages.yml
  - Pre-commit: `site/build.sh && lychee site/dist/`

- [ ] 42. **IsaacLab Compat Decision (Week 10 Gate: ONE Case Study OR Drop)**

  **What to do**:
  - This is a **DECISION TASK** with bounded scope:
    - Option A (default if Phase 0 IsaacLab fluency score ≥ 2): Implement ONE concrete IsaacLab task case study
      - Pick a single small IsaacLab task (e.g., `Isaac-Cabinet-Franka-v0` or `Isaac-Lift-Cube-Franka-v0`)
      - Show the diff needed to run it in our framework
      - Document the conversion (USD asset → MJCF, env spec mapping, observation translation)
      - Run for 1000 steps, capture reward distribution
      - Compare against reference (if data available)
      - Document explicit divergence reasons
    - Option B (if Phase 0 IsaacLab fluency score < 2 OR Option A fails): DROP from v0.1, document as v0.2 milestone explicitly
  - Record decision in `.sisyphus/evidence/task-42-isaaclab-decision.md`
  - Either way: publish honest comparison page on the demo site

  **Must NOT do**:
  - Don't promise general IsaacLab compat in v0.1 (regardless of decision)
  - Don't claim parity with reference without measurement
  - Don't burn week 10-11 on this if it's not yielding — abort and drop

  **Recommended Agent Profile**:
  - **Category**: `deep` (if Option A) OR `quick` (if Option B drop decision)
    - Reason: implementation needs deep robotics; drop decision is fast
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T41, T43)
  - **Parallel Group**: Wave 4E (PARALLEL — 3 post-release tasks)
  - **Blocks**: None
  - **Blocked By**: T22 (anchor demo done)

  **References**:

  **Pattern References**: `isaac-sim/IsaacLab` task definitions; conversion shims in other projects (e.g., gymnasium-robotics)
  **API/Type References**: IsaacLab `DirectRLEnv` vs our `Env`
  **Test References**: Comparison harness with reference success rate
  **External References**: IsaacLab docs

  **WHY Each Reference Matters**: Honest comparison requires understanding both APIs.

  **Acceptance Criteria**:

  - [ ] `.sisyphus/evidence/task-42-isaaclab-decision.md` exists with explicit DECISION line (option A or B)
  - [ ] If Option A: case study folder under `examples/isaaclab-compat/` with code + comparison output
  - [ ] If Option B: roadmap doc updated to list IsaacLab compat as v0.2
  - [ ] Site has honest "What about IsaacLab?" section

  **QA Scenarios**:

  ```
  Scenario: Option A - case study runs
    Tool: Bash
    Steps:
      1. python examples/isaaclab-compat/run_cabinet_franka.py --steps=1000 --seed=42
      2. Assert exit 0
      3. Assert prints "mean_reward=" line
    Evidence: .sisyphus/evidence/task-42-isaaclab-case-study.txt

  Scenario: Option B - drop documented
    Tool: Bash
    Steps:
      1. cat .sisyphus/evidence/task-42-isaaclab-decision.md
      2. Assert grep "DECISION: DROP" passes
      3. Assert roadmap doc lists IsaacLab compat under v0.2
    Evidence: .sisyphus/evidence/task-42-isaaclab-drop.txt
  ```

  **Evidence**: task-42-isaaclab-decision.md (mandatory), then either case study artifacts or drop doc

  **Commit**: YES
  - Message: `chore(isaaclab): T-42 compat decision [CASE-STUDY|DROPPED] [T-42]`
  - Files: `.sisyphus/evidence/task-42-isaaclab-decision.md`, optionally `examples/isaaclab-compat/*` or `docs/roadmap.md` update
  - Pre-commit: `cat .sisyphus/evidence/task-42-isaaclab-decision.md | grep -q "DECISION:"`

- [ ] 43. **Post-Release Runbook (Issue Triage, Breaking Changes Policy, Contributor Guide)**

  **What to do**:
  - Create `RUNBOOK.md`:
    - Weekly cadence: triage open issues, review PRs, batch-apply minor fixes
    - Issue templates: bug, feature, plug-in question
    - PR template: tests required, CI must pass
    - Breaking changes policy: SemVer; deprecation cycle (1 minor version warning before removal)
    - Release cadence: monthly patch, bi-monthly minor (for v0.1.x → v0.2)
    - Communication: README + CHANGELOG + GitHub Discussions
  - Finalize `CONTRIBUTING.md`:
    - Dev setup
    - Test invariants (CI must pass)
    - Coding style
    - PR checklist
  - Add `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1)
  - Issue/PR templates in `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`

  **Must NOT do**:
  - Don't over-bureaucratize for v0.1 (small project, lean process)
  - Don't promise SLA on issues

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES (with T41, T42)
  - **Parallel Group**: Wave 4E (PARALLEL — 3 post-release tasks)
  - **Blocks**: None
  - **Blocked By**: T40

  **References**:

  **Pattern References**: Contributor Covenant; RUNBOOKS from `astral-sh/uv`, `huggingface/transformers`
  **API/Type References**: N/A
  **Test References**: N/A
  **External References**: Contributor Covenant v2.1, "Maintaining OSS at scale" essays

  **WHY Each Reference Matters**: Adopting established norms saves bandwidth and gives contributors familiar surface.

  **Acceptance Criteria**:

  - [ ] `RUNBOOK.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` all present
  - [ ] Issue + PR templates in `.github/`
  - [ ] All docs link consistently (no dangling references)
  - [ ] First test issue (manually created or via gh CLI) follows the template

  **QA Scenarios**:

  ```
  Scenario: Happy path - all governance docs present
    Tool: Bash
    Steps:
      1. for f in RUNBOOK.md CONTRIBUTING.md CODE_OF_CONDUCT.md .github/ISSUE_TEMPLATE/bug.yml .github/PULL_REQUEST_TEMPLATE.md; do
           test -f $f || (echo "missing $f"; exit 1);
         done
      2. Assert exit 0
    Evidence: .sisyphus/evidence/task-43-governance.txt

  Scenario: Failure - missing file
    Tool: Bash
    Steps:
      1. Remove CODE_OF_CONDUCT.md
      2. Run check
      3. Assert exit non-zero with "missing CODE_OF_CONDUCT.md"
    Evidence: .sisyphus/evidence/task-43-governance-missing.txt
  ```

  **Evidence**: task-43-governance.txt, task-43-governance-missing.txt

  **Commit**: YES
  - Message: `docs(governance): RUNBOOK + CONTRIBUTING + COC + templates [T-43]`
  - Files: RUNBOOK.md, CONTRIBUTING.md (finalized), CODE_OF_CONDUCT.md, .github/ISSUE_TEMPLATE/*.yml, .github/PULL_REQUEST_TEMPLATE.md
  - Pre-commit: standard markdown lint

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback → fix → re-run → present again → wait for okay.

- [ ] F1. **Plan Compliance Audit** — `oracle`

  Read this plan end-to-end. For each "Must Have": verify implementation exists (read file, run command, curl MCP). For each "Must NOT Have": grep codebase for forbidden patterns; reject with file:line if found (e.g., `import drake`, `from taichi`, `class PolicyServer:` with non-stub body, "Isaac" in ship name). Check evidence files exist in `.sisyphus/evidence/` for every task. Compare deliverables 1:1 against plan's "Concrete Deliverables".

  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | Evidence [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`

  Run `ruff check . && mypy --strict <ship-name>/` on Python; `bun run typecheck && bun test` on TypeScript. Run `pytest -v` and `bun test`. Review all changed files for: `# type: ignore`, `@ts-ignore`, `as any`, empty `except:`, `console.log` in prod, commented-out code, unused imports, magic numbers. Check AI slop: excessive docstrings, over-abstraction (Rule of Three violations), generic names (`data`, `result`, `item`, `obj`).

  Output: `Lint [PASS/FAIL] | Typecheck [PASS/FAIL] | Tests [N pass/N fail] | Coverage [N%] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`

  Start from clean state (`rm -rf .venv node_modules; git clean -xfd`). Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Specifically:
  1. Cold-start: clone → install → run example → time the whole pipeline (assert ≤120s local M5 Pro)
  2. Anchor demo: `python examples/eureka_franka.py --seed=42` → assert ≥70% success in ≤30min
  3. MCP server: start, `curl tools/list`, run a full agent loop end-to-end
  4. 50-line plugin example: register, run, assert reward emitted
  5. CI matrix: trigger via `gh workflow run`, assert all 3 OS green
  6. Cross-task integration: 3 high-quality tasks all runnable via same CLI

  Save evidence to `.sisyphus/evidence/final-qa/`.

  Output: `Scenarios [N/N pass] | Integration [N/N] | Cold-start [Ns] | Anchor demo [success%/wall-clock] | CI matrix [3/3] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`

  For each task in plan: read "What to do" + read actual diff (`git log --since=<plan start>` + per-file `git log`). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Specifically:
  - No Drake/Taichi/VLA-impl/full-USD/general-IsaacLab-compat/plug-in-machinery/multi-LLM-adapter code shipped
  - "Isaac" not in package name or public API
  - Plug-in machinery vs extension points distinction respected
  - Detect cross-task contamination: Task N touching Task M's files
  - Flag unaccounted changes (files not mentioned in any task)
  - Verify Phase 0 fluency gate was actually executed and documented

  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | Scope creep [CLEAN/N found] | VERDICT`

---

## Commit Strategy

Atomic commits per task. Conventional Commits format (`type(scope): description`). Examples:
- `feat(env): add Backend protocol and Env API skeleton`
- `feat(mcp): implement sim.make and sim.reset tools`
- `test(orchestrator): add reward generator contract tests`
- `docs(readme): initial Getting Started section`
- `chore(ci): add license audit workflow`
- `refactor(env): extract Spec types into protocols.py`

Pre-commit hooks (Wave 1 setup): ruff, mypy, prettier, eslint. Block commits on lint/type fail.
Per-task commit message includes task number reference (e.g., `[T-12]`).

---

## Success Criteria

### Verification Commands
```bash
# Cold-start benchmark
time (uv venv && source .venv/bin/activate && uv pip install -e . && python examples/hello_cartpole.py)
# Expected: total ≤120s on M5 Pro, ≤300s on macOS-15 CI runner

# Anchor demo
python examples/eureka_franka.py --seed=42 --iterations=5
# Expected: success_rate ≥ 0.70, wall_clock ≤ 30min on M5 Pro

# MCP server smoke test
bun run mcp-server &
sleep 2
curl -X POST http://localhost:8765 -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' | jq '.result.tools | length'
# Expected: ≥5

# License audit
bun run check:licenses
# Expected: exit 0, only MIT/Apache-2.0/BSD-3/MPL-2.0 in dependency graph

# CI matrix
gh workflow run ci.yml
# Expected: all 3 jobs green

# Type & lint
ruff check . && mypy --strict <ship-name>/ && bun run typecheck
# Expected: exit 0

# Tests
pytest -v && bun test
# Expected: all green, coverage ≥70% on core
```

### Final Checklist
- [ ] All "Must Have" deliverables present and verified
- [ ] All "Must NOT Have" guardrails respected (F1 + F4 confirm)
- [ ] Anchor demo reproducibly hits success rate ≥70% in ≤30min on M5 Pro
- [ ] 7 freedom CI tests all green on all 3 OS matrix entries
- [ ] PyPI + npm packages published, version 0.1.0 tagged
- [ ] Demo site live, README polished
- [ ] All test suites pass (pytest + bun test) green
- [ ] All evidence files captured in `.sisyphus/evidence/`
- [ ] F1-F4 all APPROVE
- [ ] User has reviewed F1-F4 results and given explicit "okay" to mark plan complete
