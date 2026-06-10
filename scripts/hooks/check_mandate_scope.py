#!/usr/bin/env python3
"""Pre-commit / CI hook — MANDATE_ECONOPHYSIQUE scope guard (Phase 0.5).

Replaces the legacy ``scripts/hooks/check_mandate_scope.sh`` with a portable
Python implementation. Reads allow/deny regex lists from ``config/mandate_scope.yml``
(externalized so non-coders can review scope without touching Python).

Semantics
---------
- A changed file is REJECTED if it matches any ``deny_regex``.
- Otherwise it is ALLOWED iff it matches at least one ``allow_regex``.
- Default deny when no rule matches.
- Workflow / hook integrity guard: any modification of ``.github/`` or
  ``scripts/hooks/`` by an author OTHER than ``swizman777`` FAILS the hook.

CLI
---
``python scripts/hooks/check_mandate_scope.py``                 (pre-commit / local)
``python scripts/hooks/check_mandate_scope.py --from-stdin``    (CI: file list on stdin)
``python scripts/hooks/check_mandate_scope.py --files a b c``   (CI / tests)
``python scripts/hooks/check_mandate_scope.py --diff-range A..B`` (CI on PRs)

Exit codes
----------
0 = OK
1 = scope violation OR hook/workflow tamper
2 = config error (missing/invalid YAML)
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

try:  # PyYAML is a dev dependency.
    import yaml
except ImportError:  # pragma: no cover - handled at CLI
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH_DEFAULT = REPO_ROOT / "config" / "mandate_scope.yml"
SENSITIVE_PATHS = (".github/", "scripts/hooks/")
ALLOWED_AUTHOR = "swizman777"


def _load_config(path: Path) -> tuple[list[re.Pattern[str]], list[re.Pattern[str]]]:
    if yaml is None:
        raise RuntimeError("PyYAML not installed. pip install pyyaml")
    if not path.is_file():
        raise FileNotFoundError(f"mandate scope config not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    allow = [re.compile(p) for p in data.get("allow_regex", [])]
    deny = [re.compile(p) for p in data.get("deny_regex", [])]
    if not allow:
        raise ValueError("mandate scope config: allow_regex is empty")
    return allow, deny


def _git_files_staged() -> list[str]:
    """Files staged in index (pre-commit local mode), NUL-delimited."""
    rc, out = _run(
        ["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"]
    )
    if rc != 0:
        return []
    return [f for f in out.split("\0") if f]


def _git_files_range(rng: str) -> list[str]:
    """Files changed between two SHAs (CI mode), NUL-delimited."""
    rc, out = _run(["git", "diff", "--name-only", "-z", rng])
    if rc != 0:
        return []
    return [f for f in out.split("\0") if f]


def _git_last_author(file_path: str) -> str | None:
    """Return GitHub login (best-effort) of the last committer for ``file_path``."""
    rc, out = _run(["git", "log", "-1", "--format=%ae|%an", "--", file_path])
    if rc != 0 or not out.strip():
        return None
    blob = out.strip().splitlines()[0]
    return blob


def _run(args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            args, capture_output=True, text=True, check=False, encoding="utf-8"
        )
    except (FileNotFoundError, OSError) as exc:
        return 99, f"git invocation failed: {exc}"
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def classify_files(
    files: list[str],
    allow: list[re.Pattern[str]],
    deny: list[re.Pattern[str]],
) -> tuple[list[str], list[str]]:
    """Return (violations, accepted). Deny wins over allow."""
    violations: list[str] = []
    accepted: list[str] = []
    for raw in files:
        if not raw:
            continue
        f = raw.replace("\\", "/").strip()
        if not f:
            continue
        if any(p.search(f) for p in deny):
            violations.append(f)
            continue
        if any(p.search(f) for p in allow):
            accepted.append(f)
            continue
        violations.append(f)
    return violations, accepted


def detect_sensitive_tamper(
    files: list[str], allowed_author: str = ALLOWED_AUTHOR
) -> list[str]:
    """Return list of files under SENSITIVE_PATHS modified by non-Chef.

    In CI, the trigger author is provided via env var GITHUB_ACTOR. If unset
    (local pre-commit), we skip this check — local devs cannot be Chef-spoofed
    because branch protection forbids direct push to main.
    """
    actor = os.environ.get("GITHUB_ACTOR", "").strip()
    if not actor:
        return []
    if actor.lower() == allowed_author.lower():
        return []
    bad = []
    for raw in files:
        f = raw.replace("\\", "/").strip()
        if any(f.startswith(s) for s in SENSITIVE_PATHS):
            bad.append(f)
    return bad


def _print_violations(violations: list[str]) -> None:
    print(
        "ERROR: MANDATE_ECONOPHYSIQUE scope violation.",
        file=sys.stderr,
    )
    print(
        "The following files are HORS-SCOPE (only R&D économphysique allowed):",
        file=sys.stderr,
    )
    for f in violations:
        print(f"  - {f}", file=sys.stderr)
    print(
        "\nSee config/mandate_scope.yml for allow_regex / deny_regex.",
        file=sys.stderr,
    )
    print(
        "Override: `git commit --no-verify` + justification + Chef notification.",
        file=sys.stderr,
    )


def _resolve_files(args: argparse.Namespace) -> list[str]:
    if args.files:
        return list(args.files)
    if args.from_stdin:
        # accept newline or NUL-delimited
        raw = sys.stdin.read()
        if "\0" in raw:
            return [f for f in raw.split("\0") if f.strip()]
        return [line.strip() for line in raw.splitlines() if line.strip()]
    if args.diff_range:
        return _git_files_range(args.diff_range)
    return _git_files_staged()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH_DEFAULT)
    parser.add_argument("--files", nargs="*", help="explicit file list")
    parser.add_argument(
        "--from-stdin",
        action="store_true",
        help="read file list from stdin (CI mode)",
    )
    parser.add_argument(
        "--diff-range",
        type=str,
        help="git diff range (e.g. base..head) used in CI on PRs",
    )
    args = parser.parse_args(argv)

    try:
        allow, deny = _load_config(args.config)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    files = _resolve_files(args)
    if not files:
        return 0

    violations, _ = classify_files(files, allow, deny)
    sensitive = detect_sensitive_tamper(files)

    if sensitive:
        print(
            "ERROR: sensitive paths (.github/, scripts/hooks/) modified by "
            f"non-Chef actor (GITHUB_ACTOR={os.environ.get('GITHUB_ACTOR')!r}).",
            file=sys.stderr,
        )
        for f in sensitive:
            print(f"  - {f}", file=sys.stderr)
        return 1

    if violations:
        _print_violations(violations)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
