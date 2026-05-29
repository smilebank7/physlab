# Maintainer Runbook

This runbook keeps physlab maintainership small, repeatable, and honest for the
v0.1 line.

## Weekly Cadence

1. Triage new issues and label them as `bug`, `feature`, `question`, or
   `release`.
2. Review open pull requests for scope, tests, and CI status.
3. Batch small fixes into one maintenance window when possible.
4. Re-run release pre-flight before any release branch or tag work:

   ```bash
   bash scripts/release.sh --pre-flight-check
   ```

5. Before the first public release, confirm maintainer-only publishing setup:
   a configured local GPG signing key for `git tag -s`, PyPI trusted publishing
   for the `pypi` environment, npm trusted publishing for the `npm`
   environment, and GitHub environment approval enabled for both publish jobs.
   Run the executable readiness check before cutting the tag:

   ```bash
   uv run python tools/check_release_readiness.py --repo smilebank7/physlab
   ```

   Follow the registry docs for
   [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/) and
   [npm trusted publishing](https://docs.npmjs.com/trusted-publishers/).

There is no guaranteed response-time SLA. Maintainers should prefer clear
status updates over promises about turnaround time.

## Issue Triage

- Bugs need reproduction steps, expected behavior, actual behavior, platform,
  and command output.
- Feature requests need a concrete workflow and must state whether they fit
  v0.1 or belong on the roadmap.
- Plug-in or extension questions should use the explicit-registration model from
  `docs/extension-points.md`.

Close issues that request v0.1-forbidden scope, such as CUDA, Omniverse,
general IsaacLab compatibility, Drake, Taichi, full USD support, VLA serving, or
multi-LLM adapters. Link the roadmap when a deferred topic may fit v0.2+.

## Pull Requests

Pull requests should stay narrow and include the test command that proves the
change. A PR is not ready to merge until CI is green on the required matrix:
`macos-14`, `macos-15`, and `ubuntu-22.04`.

For changes touching public APIs, tasks, MCP tools, packaging, or release
automation, ask for evidence under `.sisyphus/evidence/` before merge.

## Breaking Changes

physlab uses SemVer after v0.1.0:

- Patch releases fix bugs without breaking public behavior.
- Minor releases may add APIs or deprecate APIs.
- Removals require at least one minor release with a deprecation warning first.
- Major releases may break APIs, but should include migration notes.

## Release Cadence

- Patch releases: roughly monthly when fixes exist.
- Minor releases: roughly every two months when features are ready.
- Release notes live in `CHANGELOG.md`.
- PyPI and npm publishing use GitHub Actions OIDC trusted publishing. Do not add
  long-lived npm or PyPI API tokens unless the release workflow is deliberately
  redesigned and reviewed.
- Public communication should update `README.md`, `CHANGELOG.md`, and GitHub
  Discussions or release notes. Do not announce unverified capabilities.
