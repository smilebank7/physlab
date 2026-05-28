# physlab

[![CI](https://github.com/smilebank7/physlab/actions/workflows/ci.yml/badge.svg)](https://github.com/smilebank7/physlab/actions/workflows/ci.yml)

Mac-native physical AI lab scaffold for local MuJoCo and agent workflows.

Status: v0.1 anchor demo in progress.

## 30-second demo

Run the cached Franka Eureka-style anchor replay:

```bash
python examples/eureka_franka.py --seed=42 --iterations=5 --llm=opencode --use-cache --run-id=t22-repro
```

On the reference M5 Pro run, cached replay completed in 35s with best
`success_rate=1.0`. The live local opencode feasibility gate completed in 14m25s
with 0 errored iterations. The terminal recording is checked in at
`.sisyphus/evidence/anchor-demo-recording.cast`.

For a quick smoke path that does not run PPO, use:

```bash
python examples/eureka_franka.py --iterations=1 --llm=mock --seed=42 --run-id=smoke
```

## MCP Clients

Use any MCP-speaking client: Claude Desktop, opencode, Codex, or a custom local
JSON-RPC client can call the same `ping`, `sim.*`, and `task.list` tools. The
MCP layer has no opencode-specific authentication or adapter requirement in
v0.1; opencode is only the canonical local loop driver for the anchor demo.
