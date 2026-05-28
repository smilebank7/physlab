from __future__ import annotations

import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from typing import Protocol, cast

ROOT = Path(__file__).resolve().parents[2]


class ValidatorModule(Protocol):
    def validate(self, path: Path) -> list[str]: ...


class WriterModule(Protocol):
    def render(self, args: argparse.Namespace) -> str: ...

    def score(self, value: str) -> int: ...


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validate_phase_0 = cast(
    ValidatorModule,
    load_module("validate_phase_0", ROOT / "tools" / "validate_phase_0.py"),
)
write_phase_0 = cast(
    WriterModule,
    load_module(
        "write_phase_0_assessment",
        ROOT / "tools" / "write_phase_0_assessment.py",
    ),
)


class Phase0ToolTests(unittest.TestCase):
    def validate_text(self, text: str) -> list[str]:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            suffix=".md",
            delete=False,
        ) as handle:
            handle.write(text)
            path = Path(handle.name)
        try:
            return validate_phase_0.validate(path)
        finally:
            path.unlink(missing_ok=True)

    def generated_assessment(self, **overrides: object) -> str:
        values = {
            "mujoco": 2,
            "mcp": 2,
            "isaaclab": 2,
            "oss": 2,
            "robotics": 2,
            "ship_name": "physlab",
        }
        values.update(overrides)
        args = argparse.Namespace(**values)
        return write_phase_0.render(args)

    def test_generated_assessment_validates(self) -> None:
        errors = self.validate_text(self.generated_assessment())
        self.assertEqual(errors, [])

    def test_low_scores_emit_required_scope_cuts(self) -> None:
        assessment = self.generated_assessment(mujoco=1, mcp=1, isaaclab=1, oss=1, robotics=0)
        self.assertIn("extend Wave 1", assessment)
        self.assertIn("cut Task 31", assessment)
        self.assertIn("extend Tasks 10-11", assessment)
        self.assertIn("cut Task 41", assessment)
        self.assertIn("drop Task 42", assessment)
        self.assertIn("cut Task 43 polish", assessment)
        self.assertIn("reduce Task 32 scope by 30%", assessment)
        self.assertEqual(self.validate_text(assessment), [])

    def test_forbidden_ship_name_fails(self) -> None:
        errors = self.validate_text(self.generated_assessment(ship_name="isaac-clone"))
        self.assertIn("ship name contains forbidden token: isaac", errors)

    def test_placeholder_text_fails(self) -> None:
        errors = self.validate_text(self.generated_assessment() + "\nTBD\n")
        self.assertIn("assessment contains placeholder text", errors)

    def test_missing_low_score_cut_fails(self) -> None:
        assessment = self.generated_assessment(mujoco=1).replace(
            "MuJoCo: extend Wave 1 by 1 week and cut Task 31.",
            "MuJoCo: no additional cut triggered.",
        )
        errors = self.validate_text(assessment)
        self.assertIn(
            "Scope Adjustments must apply MuJoCo Python score <= 1 cut: extend Wave 1; cut Task 31",
            errors,
        )

    def test_score_parser_rejects_out_of_range_value(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            write_phase_0.score("4")


if __name__ == "__main__":
    unittest.main()
