#!/usr/bin/env python3
"""Validate the Phase 0 assessment gate.

The validator intentionally checks the documented gate contract rather than a
particular markdown template, so the assessment can stay readable for humans.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSESSMENT = ROOT / ".sisyphus" / "evidence" / "phase-0-assessment.md"
FORBIDDEN_SHIP_TOKENS = ("isaac", "omniverse", "nvidia")
SHIP_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
SECTION_PATTERN = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*$", re.MULTILINE)
SCORE_LABELS = (
    "MuJoCo Python",
    "MCP server building",
    "IsaacLab internals",
    "OSS framework launch experience",
    "Robotics control fundamentals",
)
PLACEHOLDER_PATTERN = re.compile(r"\b(TBD|TODO|FIXME|CHANGEME|PLACEHOLDER)\b", re.IGNORECASE)


def _sections(text: str) -> dict[str, str]:
    matches = list(SECTION_PATTERN.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group("title").strip().lower()] = text[start:end].strip()
    return sections


def _section_contains(sections: dict[str, str], title_part: str) -> str | None:
    needle = title_part.lower()
    for title, body in sections.items():
        if needle in title:
            return body
    return None


def _extract_scores(text: str) -> tuple[dict[str, int], list[str]]:
    errors: list[str] = []
    scores: dict[str, int] = {}
    for label in SCORE_LABELS:
        pattern = re.compile(
            rf"{re.escape(label)}\s*(?:\||:|-)\s*(?P<score>[0-3])\b",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if not match:
            errors.append(f"missing 0-3 fluency score for {label}")
            continue
        scores[label] = int(match.group("score"))
    return scores, errors


def _extract_ship_name(ship_section: str) -> str | None:
    for line in ship_section.splitlines():
        cleaned = line.strip().lstrip("-*0123456789. )").strip().strip("*` ")
        if not cleaned:
            continue
        if ":" in cleaned:
            cleaned = cleaned.split(":", 1)[1].strip().strip("*` ")
        if cleaned:
            return cleaned
    return None


def _validate_ship_name(sections: dict[str, str]) -> list[str]:
    ship_section = _section_contains(sections, "ship name")
    if ship_section is None:
        return ["missing Ship Name section"]
    ship_name = _extract_ship_name(ship_section)
    if not ship_name:
        return ["missing chosen ship name"]

    errors: list[str] = []
    if not SHIP_NAME_PATTERN.fullmatch(ship_name):
        errors.append("ship name violates pattern ^[a-z][a-z0-9-]*$")
    lower_name = ship_name.lower()
    for token in FORBIDDEN_SHIP_TOKENS:
        if token in lower_name:
            errors.append(f"ship name contains forbidden token: {token}")
    return errors


def _sentence_count(text: str) -> int:
    return len(re.findall(r"[.!?](?:\s|$)", text))


def _validate_scope_adjustments(scope_adjustments: str, scores: dict[str, int]) -> list[str]:
    errors: list[str] = []
    checks = (
        (
            "MuJoCo Python",
            ("extend Wave 1", "cut Task 31"),
            r"extend\s+Wave\s+1|cut\s+Task\s+31|cut\s+T31|Task\s+31",
        ),
        (
            "MCP server building",
            ("extend MCP work", "cut Task 41"),
            r"extend\s+MCP|cut\s+Task\s+41|cut\s+T41|Task\s+41",
        ),
        (
            "IsaacLab internals",
            ("drop Task 42",),
            r"drop\s+Task\s+42|cut\s+Task\s+42|drop\s+T42|Task\s+42",
        ),
        (
            "OSS framework launch experience",
            ("cut Task 43 polish", "reduce Task 32 scope"),
            r"cut\s+Task\s+43|cut\s+T43|Task\s+43|reduce\s+docs|reduce\s+Task\s+32|Task\s+32",
        ),
    )
    for score_label, expected_phrases, pattern in checks:
        score = scores.get(score_label)
        if score is None:
            continue
        if score <= 1 and not re.search(pattern, scope_adjustments, re.IGNORECASE):
            expected = "; ".join(expected_phrases)
            errors.append(f"Scope Adjustments must apply {score_label} score <= 1 cut: {expected}")
    return errors


def _validate_required_sections(sections: dict[str, str], scores: dict[str, int]) -> list[str]:
    errors: list[str] = []

    first_user = _section_contains(sections, "first user")
    if first_user is None:
        errors.append("missing First User section")
    elif _sentence_count(first_user) < 3:
        errors.append("First User section must contain at least 3 sentences")

    success_metric = _section_contains(sections, "success metric")
    if success_metric is None:
        errors.append("missing Success Metric section")
    elif not re.search(r"\d|>=|<=|≤|≥|pass|green|success|within", success_metric, re.IGNORECASE):
        errors.append("Success Metric section must contain one measurable criterion")

    kill_switch = _section_contains(sections, "kill-switch") or _section_contains(
        sections,
        "kill switch",
    )
    if kill_switch is None:
        errors.append("missing Kill-Switch section")
    else:
        if not re.search(r"\bweek\s*\d+\b", kill_switch, re.IGNORECASE):
            errors.append("Kill-Switch section must include a week")
        if not re.search(
            r"evidence|metric|result|benchmark|demo|qa|ci",
            kill_switch,
            re.IGNORECASE,
        ):
            errors.append("Kill-Switch section must include a concrete evidence trigger")

    scope_adjustments = _section_contains(sections, "scope adjustments")
    if scope_adjustments is None:
        errors.append("missing Scope Adjustments section")
    elif not re.search(r"MuJoCo|MCP|IsaacLab|OSS", scope_adjustments, re.IGNORECASE):
        errors.append("Scope Adjustments must explicitly list applied cuts")
    else:
        errors.extend(_validate_scope_adjustments(scope_adjustments, scores))

    return errors


def validate(path: Path) -> list[str]:
    if not path.exists():
        return [f"assessment file not found: {path}"]

    text = path.read_text(encoding="utf-8")
    sections = _sections(text)
    errors: list[str] = []
    if PLACEHOLDER_PATTERN.search(text):
        errors.append("assessment contains placeholder text")
    scores, score_errors = _extract_scores(text)
    errors.extend(score_errors)
    errors.extend(_validate_ship_name(sections))
    errors.extend(_validate_required_sections(sections, scores))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 0 assessment markdown.")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_ASSESSMENT,
        help="Assessment markdown path",
    )
    args = parser.parse_args()

    errors = validate(args.file)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
