"""Tests for scripts/hooks/check_mandate_scope.py (Phase 0.5 hook rewrite)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

# Make scripts/hooks importable
REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = REPO_ROOT / "scripts" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import check_mandate_scope as hook  # noqa: E402


@pytest.fixture
def patterns() -> tuple[list[re.Pattern[str]], list[re.Pattern[str]]]:
    """Load the actual production config to ensure tests track real rules."""
    cfg = REPO_ROOT / "config" / "mandate_scope.yml"
    return hook._load_config(cfg)  # noqa: SLF001


def test_in_scope_paths_are_accepted(patterns):
    allow, deny = patterns
    files = [
        "src/models/hurst.py",
        "tests/test_garch_fit.py",
        "tests/hooks/test_check_mandate_scope.py",
        "MANDATE_ECONOPHYSIQUE.md",
        "README.md",
        "pyproject.toml",
        "scripts/hooks/check_mandate_scope.py",
        "config/mandate_scope.yml",
        ".github/workflows/mandate_guard.yml",
        ".github/CODEOWNERS",
        ".github/pull_request_template.md",
        "docs/BRANCH_PROTECTION_SETUP.md",
        "archive/hooks_legacy/check_mandate_scope.sh",
    ]
    violations, accepted = hook.classify_files(files, allow, deny)
    assert violations == [], f"unexpected violations: {violations}"
    assert set(accepted) == set(files)


def test_out_of_scope_paths_are_rejected(patterns):
    """Annexe A.7 forbidden patterns must trigger violations."""
    allow, deny = patterns
    files = [
        "src/broker/t212_client.py",
        "dashboard/app.py",
        "src/dca_cspx.py",
        "src/bogle_alloc.py",
        "src/risk_manager_live.py",
        "src/live_trading/runner.py",
        "src/hft_intraday.py",
        "src/sentiment_trade_news.py",
        "src/leverage_trading.py",
    ]
    violations, accepted = hook.classify_files(files, allow, deny)
    assert accepted == [], f"unexpected accepted: {accepted}"
    assert set(violations) == set(files)


def test_unknown_path_default_deny(patterns):
    """A path matching no allow and no deny rule => default REJECT."""
    allow, deny = patterns
    files = ["random_root_file.py", "src/unknown_subdir_outside_allow/x.py"]
    violations, _ = hook.classify_files(files, allow, deny)
    assert set(violations) == set(files)


def test_deny_wins_over_allow(patterns):
    """A file matching both allow and deny patterns must be REJECTED."""
    # craft synthetic deny that overlaps with allow
    allow = [re.compile(r"^src/")]
    deny = [re.compile(r"(?i)dca_")]
    files = ["src/dca_cspx.py"]
    violations, accepted = hook.classify_files(files, allow, deny)
    assert violations == ["src/dca_cspx.py"]
    assert accepted == []


def test_nul_delimited_paths_are_handled(patterns):
    """`git diff -z` returns NUL-separated paths; classify_files trims them."""
    allow, deny = patterns
    files = ["src/models/hurst.py", "src/broker/binance.py", ""]
    violations, accepted = hook.classify_files(files, allow, deny)
    assert "src/broker/binance.py" in violations
    assert "src/models/hurst.py" in accepted
    assert "" not in accepted and "" not in violations


def test_paths_with_backslash_normalized(patterns):
    allow, deny = patterns
    files = ["src\\models\\hurst.py", "tests\\test_x.py"]
    violations, accepted = hook.classify_files(files, allow, deny)
    assert violations == []
    assert accepted == ["src/models/hurst.py", "tests/test_x.py"]


def test_sensitive_tamper_blocks_non_chef(monkeypatch):
    """If GITHUB_ACTOR != swizman777, touching .github/ or scripts/hooks/ FAILS."""
    monkeypatch.setenv("GITHUB_ACTOR", "someone-else")
    bad = hook.detect_sensitive_tamper(
        [".github/workflows/ci.yml", "scripts/hooks/check_mandate_scope.py"]
    )
    assert ".github/workflows/ci.yml" in bad
    assert "scripts/hooks/check_mandate_scope.py" in bad


def test_sensitive_tamper_allows_chef(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTOR", "swizman777")
    bad = hook.detect_sensitive_tamper(
        [".github/workflows/ci.yml", "scripts/hooks/check_mandate_scope.py"]
    )
    assert bad == []


def test_sensitive_tamper_no_actor_skips(monkeypatch):
    """Local pre-commit (no GITHUB_ACTOR) does not enforce author check."""
    monkeypatch.delenv("GITHUB_ACTOR", raising=False)
    bad = hook.detect_sensitive_tamper([".github/workflows/ci.yml"])
    assert bad == []


def test_main_accepts_empty_filelist(tmp_path, monkeypatch):
    """No changed files => exit 0."""
    monkeypatch.delenv("GITHUB_ACTOR", raising=False)
    rc = hook.main(["--files"])
    assert rc == 0


def test_main_rejects_out_of_scope_via_files_arg(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTOR", raising=False)
    rc = hook.main(["--files", "src/dca_cspx.py"])
    assert rc == 1


def test_main_accepts_in_scope_via_files_arg(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTOR", raising=False)
    rc = hook.main(
        ["--files", "src/models/hurst.py", "tests/hooks/test_check_mandate_scope.py"]
    )
    assert rc == 0


def test_config_missing_returns_exit_2(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_ACTOR", raising=False)
    rc = hook.main(
        [
            "--config",
            str(tmp_path / "does_not_exist.yml"),
            "--files",
            "src/x.py",
        ]
    )
    assert rc == 2
