# Contributing

physlab is MIT-licensed and only accepts dependencies with permissive or weak
copyleft licenses approved in `tools/check_licenses.py`.

GPL, AGPL, LGPL, proprietary, unknown, and unlicensed dependencies are not
allowed in v0.1.

## Development Setup

Use Python 3.11 or newer and Node 20 or newer. From a fresh clone:

```bash
uv pip install -e ".[dev]"
cd mcp-server && bun install
```

Run a small smoke episode before opening a pull request:

```bash
uv run python examples/hello_cartpole.py --headless --steps 10
```

## Test Invariants

Every pull request should keep these checks green:

```bash
uv run ruff check .
uv run mypy src tests tools
uv run pytest -q
cd mcp-server && bun test
```

Changes to docs should also run:

```bash
PATH="$PWD/.venv/bin:$PATH" sphinx-build -W docs docs/_build/python
```

## Branch Protection

`main` should require the `CI / Hardware freedom / 3 OS matrix` check and the
license audit before merge. The hardware-freedom job depends on the full
`macos-14`, `macos-15`, and `ubuntu-22.04` CI matrix, so a missing or failing OS
keeps the merge gate red.

## Coding Style

- Prefer the existing public APIs over new abstractions.
- Keep v0.1 scoped to MuJoCo, MCP tools, three built-in tasks, and the local
  reward-iteration anchor demo.
- Do not add CUDA, Omniverse, general IsaacLab compatibility, Drake, Taichi,
  full USD support, VLA serving, or multi-LLM adapters in v0.1.
- Add evidence under `.sisyphus/evidence/` when a plan task asks for it.

## Pull Request Checklist

- The PR description explains the user-visible change.
- Tests and evidence are listed.
- CI is green.
- Documentation is updated when commands, public APIs, or scope change.

See `RUNBOOK.md` for maintainer triage and release practices, and
`CODE_OF_CONDUCT.md` for project conduct expectations.
