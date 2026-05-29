# physlab

[![CI](https://github.com/smilebank7/physlab/actions/workflows/ci.yml/badge.svg)](https://github.com/smilebank7/physlab/actions/workflows/ci.yml)
[![License](https://github.com/smilebank7/physlab/actions/workflows/licenses.yml/badge.svg)](https://github.com/smilebank7/physlab/actions/workflows/licenses.yml)
[![Cold Start](https://github.com/smilebank7/physlab/actions/workflows/cold-start.yml/badge.svg)](https://github.com/smilebank7/physlab/actions/workflows/cold-start.yml)
![PyPI](https://img.shields.io/badge/PyPI-planned-lightgrey.svg)
![npm](https://img.shields.io/badge/npm-planned-lightgrey.svg)
![Docs](https://img.shields.io/badge/docs-local-blue.svg)

Mac-native physical AI experiments with MuJoCo, local reward iteration, and an
MCP tool surface.

Status: alpha, v0.1 in progress. The current branch has the Franka anchor demo,
three built-in tasks (`franka_pick`, `ant_stand`, `franka_push`), and CI checks
for license, backend, workflow, extension, MCP, hardware, and research freedom.

## Quick Start

From a clone, install the Python package and run the smallest headless episode:

```bash
uv pip install -e ".[dev]"
uv run python examples/hello_cartpole.py --headless --steps 10
```

The v0.1 release target is `pip install physlab`; until the release is cut, use
the editable install above. For the longer local anchor replay:

```bash
rm -rf runs/readme-smoke
uv run python examples/eureka_franka.py --headless --iterations=1 \
  --llm=mock --seed=42 --run-id=readme-smoke
```

## Why This Exists

physlab is a Mac-native alternative for one specific workflow: local
Eureka-style reward iteration on Apple Silicon without CUDA. It is not an
Isaac Lab clone or Omniverse replacement.

The simulation backend is MuJoCo CPU. That keeps v0.1 small enough to audit,
fast enough for CI, and portable across `macos-14`, `macos-15`, and
`ubuntu-22.04`.

The agent boundary is MCP plus a local opencode-driven anchor loop. MCP tools
are client-agnostic; opencode is only the canonical driver for the Franka
Eureka-style demo.

The honest performance envelope is Mac-scale: expect roughly 16-64 parallel
environments depending on model size, not CUDA-scale 4096-environment claims.

## Anchor Demo

The anchor command is:

```text
python examples/eureka_franka.py --seed=42
```

For CI and offline demos, committed LLM cache responses make the run
deterministic:

```text
python examples/eureka_franka.py --seed=42 --iterations=5 --llm=opencode --use-cache
```

On the reference M5 Pro run, cached replay completed in 35s with best
`success_rate=1.0`. The live local opencode feasibility gate completed in
14m25s with 0 errored iterations. The terminal recording is checked in at
[`.sisyphus/evidence/anchor-demo-recording.cast`](.sisyphus/evidence/anchor-demo-recording.cast).

## Seven Freedoms

![License Freedom](https://img.shields.io/badge/license%20freedom-CI%20tested-brightgreen.svg)
![API Backend Freedom](https://img.shields.io/badge/API%2Fbackend-3%20impl%20contract-brightgreen.svg)
![Workflow Freedom](https://img.shields.io/badge/workflow-headless%20CI-brightgreen.svg)
![Extension Freedom](https://img.shields.io/badge/extension-explicit%20register-brightgreen.svg)
![Agent Freedom](https://img.shields.io/badge/agent-MCP%20compliance-brightgreen.svg)
![Hardware Freedom](https://img.shields.io/badge/hardware-3%20OS%20matrix-brightgreen.svg)
![Research Freedom](https://img.shields.io/badge/research-cold%20start%20bench-brightgreen.svg)

Each badge maps to code, tests, or workflow gates in this repo; none are
marketing-only claims.

## MCP Clients

Use any MCP-speaking client: Claude Desktop, opencode, Codex, or a custom local
JSON-RPC client can call the same `ping`, `sim.*`, and `task.list` tools. The
MCP layer has no opencode-specific authentication or adapter requirement in
v0.1.

## Supported Platforms

CI runs on `macos-14`, `macos-15`, and `ubuntu-22.04` for Python 3.11 and 3.12.
The `Hardware freedom / 3 OS matrix` job gates merges on that full matrix.

Windows and CUDA are out of scope. CPU simulation is the bit-exact deterministic
path; any MPS-accelerated training path should be treated as epsilon-close
(`<=1e-4`) rather than bit-exact.

## Roadmap

v0.2 candidates: plugin machinery, Drake or Taichi experiments, IsaacLab
compatibility research, and richer task packaging. IsaacLab is explicitly not a
v0.1 feature or parity claim.

v0.3 candidates: VLA integration research, full USD asset workflows,
multi-LLM adapters, and larger-scale training experiments.

These are deferred features, not v0.1 capabilities. See the
[roadmap](docs/roadmap.md) for the current scope decisions.

## Contributing

Start with [docs/getting-started.md](docs/getting-started.md), then read
[CONTRIBUTING.md](CONTRIBUTING.md). Maintainer practice is documented in
[RUNBOOK.md](RUNBOOK.md), and project conduct expectations are in
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). The project is MIT licensed; see
[LICENSE](LICENSE) and [NOTICE](NOTICE).
