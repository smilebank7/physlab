# Plugin Examples

This directory shows the v0.1 extension pattern for third-party tasks. The
pattern is intentionally ordinary Python packaging plus an explicit import.
There is no package auto-discovery and no `entry_points` registration in v0.1.

## Build the Example Package

From the repository root:

```bash
python -m build examples/plugins/hello_task
```

The build writes a wheel such as
`examples/plugins/hello_task/dist/hello_task-0.0.0-py3-none-any.whl`.

## Install in a Fresh Environment

Install physlab and the example wheel into the same environment:

```bash
python -m venv /tmp/physlab-plugin-test
/tmp/physlab-plugin-test/bin/pip install . examples/plugins/hello_task/dist/hello_task-*.whl
```

Installing the wheel does not register the task. Importing the package is the
registration trigger:

```python
from physlab import list_tasks

assert "hello_task" not in list_tasks()

import hello_task

assert "hello_task" in list_tasks()
```

Now the task can be created through the normal API:

```python
import hello_task
from physlab import make

env = make("hello_task")
obs, info = env.reset(seed=0)
assert obs.shape == env.observation_space.shape
env.close()
```

## Publish Your Own Task Package

Use `examples/plugins/hello_task/pyproject.toml` as the smallest template:

- Add a `[build-system]` table with a PEP 517 backend such as Hatchling.
- Give the package a normal PyPI project name.
- Depend on `physlab`.
- Put task code in an importable module.
- Call `register_task("your_task", YourTask)` at module top level.
- Document that users must `import your_module` before calling `make(...)`.

Keep the task package MIT-compatible if you want it to compose cleanly with
physlab v0.1. Do not add `entry_points` discovery until the v0.2 extension spec
exists.
