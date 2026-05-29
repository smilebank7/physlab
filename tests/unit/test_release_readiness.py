from __future__ import annotations

import pytest

from tools.check_release_readiness import (
    ReleaseReadinessError,
    check_github_environments,
    check_gpg_ready,
    check_release_workflow,
    parse_environment_names,
)


def test_release_workflow_requires_trusted_publishers() -> None:
    workflow = """
name: Release
on:
  workflow_dispatch:
jobs:
  publish-pypi:
    permissions:
      id-token: write
    environment: pypi
  publish-npm:
    permissions:
      id-token: write
    environment: npm
    steps:
      - uses: actions/setup-node@v6
        with:
          node-version: "24"
      - run: npm publish npm-dist/*.tgz --access public
"""

    check_release_workflow(workflow)


def test_release_workflow_rejects_long_lived_npm_token() -> None:
    workflow = """
jobs:
  publish-npm:
    permissions:
      id-token: write
    environment: npm
    steps:
      - uses: actions/setup-node@v6
        with:
          node-version: "24"
      - run: npm publish npm-dist/*.tgz --access public --provenance
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
"""

    with pytest.raises(ReleaseReadinessError, match="NODE_AUTH_TOKEN"):
        check_release_workflow(workflow)


def test_release_readiness_requires_configured_secret_gpg_key() -> None:
    secret_keys = """
sec   rsa4096/ABCDEF1234567890 2026-05-29 [SC]
      ABCDEF1234567890ABCDEF1234567890ABCDEF12
uid                 [ultimate] Release Bot <release@example.com>
"""

    check_gpg_ready("ABCDEF1234567890", secret_keys)


def test_release_readiness_rejects_missing_gpg_secret_key() -> None:
    with pytest.raises(ReleaseReadinessError, match="secret key"):
        check_gpg_ready("", "")


def test_parse_github_environment_names() -> None:
    payload = """{"environments":[{"name":"pypi"},{"name":"npm"}]}"""

    assert parse_environment_names(payload) == {"pypi", "npm"}


def test_release_readiness_requires_publish_environments() -> None:
    with pytest.raises(ReleaseReadinessError, match="npm"):
        check_github_environments({"pypi"})
