"""Guard the CI hardware-freedom matrix declaration."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_OSES = ("macos-14", "macos-15", "ubuntu-22.04")
REQUIRED_PYTHONS = ("3.11", "3.12")


class HardwareMatrixError(ValueError):
    """Raised when the CI workflow no longer enforces hardware freedom."""


def check_workflow(text: str) -> None:
    oses = _matrix_values(text, "os")
    pythons = _matrix_values(text, "python-version")
    missing_oses = [os_name for os_name in REQUIRED_OSES if os_name not in oses]
    missing_pythons = [version for version in REQUIRED_PYTHONS if version not in pythons]
    if missing_oses:
        raise HardwareMatrixError(f"missing required OS matrix entries: {missing_oses}")
    if missing_pythons:
        raise HardwareMatrixError(f"missing required Python matrix entries: {missing_pythons}")

    hardware_job = _job_block(text, "hardware-freedom")
    if "needs: test" not in hardware_job:
        raise HardwareMatrixError("hardware-freedom job must depend on the test matrix")
    for os_name in REQUIRED_OSES:
        if os_name not in hardware_job:
            raise HardwareMatrixError(f"hardware-freedom job must name {os_name}")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    path = Path(args[0]) if args else Path(".github/workflows/ci.yml")
    check_workflow(path.read_text(encoding="utf-8"))
    print(
        "OK hardware freedom matrix covers "
        f"{', '.join(REQUIRED_OSES)} on Python {', '.join(REQUIRED_PYTHONS)}"
    )
    return 0


def _matrix_values(text: str, key: str) -> set[str]:
    match = re.search(rf"{re.escape(key)}:\s*\[([^\]]+)\]", text)
    if match is None:
        raise HardwareMatrixError(f"matrix key {key!r} not found")
    return {value.strip().strip("\"'") for value in match.group(1).split(",")}


def _job_block(text: str, job_name: str) -> str:
    match = re.search(rf"^  {re.escape(job_name)}:\n(?P<body>(?:    .*\n|      .*\n)+)", text, re.M)
    if match is None:
        raise HardwareMatrixError(f"job {job_name!r} not found")
    return match.group("body")


if __name__ == "__main__":
    raise SystemExit(main())
