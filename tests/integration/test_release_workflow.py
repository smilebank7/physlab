from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def test_npm_release_uses_trusted_publishing_not_long_lived_token() -> None:
    text = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    assert "id-token: write" in text
    assert 'node-version: "24"' in text
    assert "NODE_AUTH_TOKEN" not in text
    assert "--provenance" not in text
