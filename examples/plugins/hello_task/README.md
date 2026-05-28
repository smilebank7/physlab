# hello_task

Minimal third-party task package for PhysLab's explicit extension pattern.

Install it like a normal Python package:

```bash
uv pip install -e examples/plugins/hello_task
```

Then import the module in user code to run its top-level registration call:

```python
import hello_task
from physlab import list_tasks, make

assert "hello_task" in list_tasks()
env = make("hello_task")
```

PhysLab v0.1 intentionally does not scan installed packages for tasks. Importing user code is the registration trigger.
