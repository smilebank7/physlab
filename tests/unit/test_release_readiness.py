from __future__ import annotations

import pytest

from tools.check_release_readiness import (
    ReleaseReadinessError,
    check_github_environments,
    check_release_workflow,
    check_signing_ready,
    parse_approved_environment_names,
)


def test_release_workflow_requires_trusted_publishers() -> None:
    workflow = """
name: Release
on:
  workflow_dispatch:
jobs:
  publish-pypi:
    if: github.event_name == 'workflow_dispatch' && startsWith(github.ref, 'refs/tags/v')
    permissions:
      id-token: write
    environment: pypi
  publish-npm:
    if: github.event_name == 'workflow_dispatch' && startsWith(github.ref, 'refs/tags/v')
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


def test_release_workflow_rejects_tag_push_publishing_without_manual_dispatch() -> None:
    workflow = """
name: Release
on:
  push:
    tags: ["v*"]
  workflow_dispatch:
jobs:
  publish-pypi:
    if: startsWith(github.ref, 'refs/tags/v')
    permissions:
      id-token: write
    environment: pypi
  publish-npm:
    if: startsWith(github.ref, 'refs/tags/v')
    permissions:
      id-token: write
    environment: npm
    steps:
      - uses: actions/setup-node@v6
        with:
          node-version: "24"
"""

    with pytest.raises(ReleaseReadinessError, match="workflow_dispatch"):
        check_release_workflow(workflow)


def test_release_readiness_requires_configured_secret_gpg_key() -> None:
    secret_keys = """
sec   rsa4096/ABCDEF1234567890 2026-05-29 [SC]
      ABCDEF1234567890ABCDEF1234567890ABCDEF12
uid                 [ultimate] Release Bot <release@example.com>
"""

    check_signing_ready("ABCDEF1234567890", "openpgp", secret_keys, set())


def test_release_readiness_rejects_missing_gpg_secret_key() -> None:
    with pytest.raises(ReleaseReadinessError, match="secret key"):
        check_signing_ready("", "openpgp", "", set())


def test_release_readiness_accepts_ssh_signing_key_file() -> None:
    check_signing_ready("~/.ssh/release_signing_key.pub", "ssh", "", {"~/.ssh/release_signing_key"})


def test_release_readiness_rejects_ssh_signing_without_private_key_file() -> None:
    with pytest.raises(ReleaseReadinessError, match="SSH signing key"):
        check_signing_ready("~/.ssh/release_signing_key.pub", "ssh", "", set())


def test_parse_github_environment_names() -> None:
    payload = """
{
  "environments": [
    {"name": "pypi", "protection_rules": [{"type": "required_reviewers"}]},
    {"name": "npm", "protection_rules": [{"type": "required_reviewers"}]},
    {"name": "docs", "protection_rules": []}
  ]
}
"""

    assert parse_approved_environment_names(payload) == {"pypi", "npm"}


def test_release_readiness_requires_publish_environments() -> None:
    with pytest.raises(ReleaseReadinessError, match="npm"):
        check_github_environments({"pypi"})


def test_release_readiness_rejects_environment_without_required_reviewers() -> None:
    payload = """{"environments":[{"name":"pypi","protection_rules":[]}]}"""

    assert parse_approved_environment_names(payload) == set()
