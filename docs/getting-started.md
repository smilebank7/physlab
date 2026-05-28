# Getting Started

This guide assumes a local clone on macOS or Linux with Python 3.11+ and Node
20+ available.

## Install

Install `uv` and `bun`, then install the editable Python package and MCP server
dependencies:

```bash
uv pip install -e ".[dev]"
cd mcp-server && bun install && cd ..
```

## First Environment

Run the smallest MuJoCo smoke episode:

```bash
uv run python examples/hello_cartpole.py --headless --steps 10
```

You should see `episode_reward=... steps=10`.

## First Task

Built-in tasks are registered on import and can be listed from Python:

```bash
uv run python - <<'PY'
from physlab import list_tasks

print(list_tasks())
PY
```

For a third-party task, see
`examples/plugins/hello_task`. v0.1 uses an
explicit pattern: install the package, import the module, and let its top-level
`register_task(...)` call run. There is no auto-discovery machinery.

## First Eureka Run

Use the mock LLM path for a fast local smoke:

```bash
uv run python examples/eureka_franka.py --headless --iterations=1 --llm=mock --seed=42 --run-id=getting-started
```

For the anchor replay, use the committed cache:

```bash
uv run python examples/eureka_franka.py --headless --seed=42 --iterations=5 --llm=opencode --use-cache --run-id=getting-started-cache
```

Live opencode runs require opencode on `PATH` and may take several minutes.

## Common Pitfalls

- Use MuJoCo CPU for v0.1. CUDA, Windows, Drake, Taichi, and full USD workflows
  are not supported in this release.
- If `bun test` cannot find Python, put `.venv/bin` on `PATH`.
- If an MCP client cannot see a custom task, explicitly import that task module
  before calling `list_tasks()` or `make(...)`.
- Keep LLM calls cached for CI. The mock and cache modes are the deterministic
  paths.
