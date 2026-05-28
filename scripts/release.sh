#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
DRY_RUN=0
PRE_FLIGHT=0
BUMP=""

die() {
  echo "error: $*" >&2
  exit 1
}

usage() {
  cat <<'USAGE'
Usage:
  scripts/release.sh --dry-run --bump=patch|minor|major
  scripts/release.sh --bump=patch|minor|major
  scripts/release.sh --pre-flight-check

Real releases require a clean working tree, update Python and npm versions,
update CHANGELOG.md, commit, create a signed SemVer tag, then push commit + tag.
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --pre-flight-check) PRE_FLIGHT=1 ;;
    --bump=*) BUMP="${arg#--bump=}" ;;
    -h|--help)
      usage
      exit 0
      ;;
    *) die "unknown argument: $arg" ;;
  esac
done

cd "$ROOT"

current_version() {
  "$PYTHON" - <<'PY'
from pathlib import Path
import re

text = Path("pyproject.toml").read_text(encoding="utf-8")
match = re.search(r'^version = "([^"]+)"$', text, re.M)
if not match:
    raise SystemExit("pyproject.toml version not found")
print(match.group(1))
PY
}

bump_version() {
  "$PYTHON" - "$1" "$2" <<'PY'
import re
import sys

version, bump = sys.argv[1:3]
match = re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version)
if not match:
    raise SystemExit(f"invalid SemVer version: {version}")
major, minor, patch = (int(part) for part in match.groups())
if bump == "patch":
    patch += 1
elif bump == "minor":
    minor += 1
    patch = 0
elif bump == "major":
    major += 1
    minor = 0
    patch = 0
else:
    raise SystemExit(f"invalid bump: {bump}")
print(f"{major}.{minor}.{patch}")
PY
}

assert_semver() {
  "$PYTHON" - "$1" <<'PY'
import re
import sys

version = sys.argv[1]
if not re.fullmatch(r"v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
    raise SystemExit(f"invalid SemVer tag/version: {version}")
PY
}

assert_clean_tree() {
  git diff --quiet || die "dirty working tree: unstaged changes present"
  git diff --cached --quiet || die "dirty working tree: staged changes present"
  test -z "$(git ls-files --others --exclude-standard)" || die "dirty working tree: untracked files present"
}

validate_changelog() {
  "$PYTHON" - <<'PY'
from pathlib import Path
import re

text = Path("CHANGELOG.md").read_text(encoding="utf-8")
if not text.startswith("# Changelog\n"):
    raise SystemExit("CHANGELOG.md must start with '# Changelog'")
if "## [Unreleased]" not in text:
    raise SystemExit("CHANGELOG.md missing [Unreleased] section")
versions = re.findall(r"^## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}$", text, re.M)
for version in versions:
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        raise SystemExit(f"invalid changelog SemVer: {version}")
PY
}

validate_release_workflow() {
  grep -q "workflow_dispatch:" .github/workflows/release.yml || die "release workflow missing workflow_dispatch"
  grep -q "environment:" .github/workflows/release.yml || die "release workflow missing approval environment"
}

update_versions() {
  local next="$1"
  "$PYTHON" - "$next" <<'PY'
from pathlib import Path
import json
import re
import sys

version = sys.argv[1]
pyproject = Path("pyproject.toml")
text = pyproject.read_text(encoding="utf-8")
text = re.sub(r'^version = "[^"]+"$', f'version = "{version}"', text, count=1, flags=re.M)
pyproject.write_text(text, encoding="utf-8")

package_path = Path("mcp-server/package.json")
package = json.loads(package_path.read_text(encoding="utf-8"))
package["version"] = version
package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
PY
}

release_notes() {
  local last_tag
  last_tag="$(git describe --tags --abbrev=0 2>/dev/null || true)"
  if [[ -n "$last_tag" ]]; then
    git log --pretty=format:'- %s' "${last_tag}..HEAD"
  else
    git log --pretty=format:'- %s'
  fi
}

update_changelog() {
  local next="$1"
  local today notes
  today="$(date -u +%F)"
  notes="$(release_notes)"
  if [[ -z "$notes" ]]; then
    notes="- Release v${next}."
  fi
  "$PYTHON" - "$next" "$today" "$notes" <<'PY'
from pathlib import Path
import sys

version, today, notes = sys.argv[1:4]
path = Path("CHANGELOG.md")
text = path.read_text(encoding="utf-8")
heading = f"## [{version}] - {today}"
if heading in text:
    raise SystemExit(f"CHANGELOG.md already contains {heading}")
section = f"## [Unreleased]\n\n{heading}\n\n{notes}\n"
path.write_text(text.replace("## [Unreleased]\n", section, 1), encoding="utf-8")
PY
}

preflight() {
  local version
  version="$(current_version)"
  assert_semver "$version"
  validate_changelog
  validate_release_workflow
  echo "pre-flight ok for ${version}"
}

if [[ "$PRE_FLIGHT" -eq 1 ]]; then
  preflight
  exit 0
fi

[[ -n "$BUMP" ]] || die "--bump=patch|minor|major is required"
case "$BUMP" in patch|minor|major) ;; *) die "invalid bump: $BUMP" ;; esac

CURRENT="$(current_version)"
NEXT="$(bump_version "$CURRENT" "$BUMP")"
assert_semver "$NEXT"
assert_semver "v$NEXT"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "release dry-run"
  echo "current_version=$CURRENT"
  echo "next_version=$NEXT"
  echo "would update pyproject.toml and mcp-server/package.json"
  echo "would update CHANGELOG.md with commits:"
  release_notes
  echo
  echo "would run pre-flight checks"
  preflight
  echo "would commit: chore: release v$NEXT"
  echo "would create signed tag: v$NEXT"
  echo "would push commit and tag"
  exit 0
fi

assert_clean_tree
update_versions "$NEXT"
update_changelog "$NEXT"
preflight
git add pyproject.toml mcp-server/package.json CHANGELOG.md
git commit -m "chore: release v$NEXT"
git tag -s "v$NEXT" -m "v$NEXT"
git push
git push origin "v$NEXT"
