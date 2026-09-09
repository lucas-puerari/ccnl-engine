"""Rules diff report: surface computational changes in knowledge data files.

Usage:
    # PR mode: compare current files against a base commit SHA
    uv run python scripts/rules_diff_report.py --base <sha>

    # Release mode: compare current files against a tagged version
    uv run python scripts/rules_diff_report.py --since <tag>

Output: Markdown-formatted report printed to stdout.
Exit code: always 0 (informational, non-blocking).
"""

from __future__ import annotations

import argparse
import json
import subprocess  # noqa: S404
from pathlib import Path
from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.domain.ccnl import CCNL

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.engine.contract.domain.ccnl import Level

# Paths inside the repo used for git diff filtering.
_KNOWLEDGE_ROOT = "src/ccnl_engine/knowledge"
_CCNL_PREFIX = f"{_KNOWLEDGE_ROOT}/ccnl/data/"
_OTHER_PREFIXES = (
    f"{_KNOWLEDGE_ROOT}/tax/data/",
    f"{_KNOWLEDGE_ROOT}/inps/data/",
    f"{_KNOWLEDGE_ROOT}/surtax/data/",
)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _git_changed_files(base_ref: str) -> list[str]:
    """Return paths of knowledge data JSON files changed since *base_ref*.

    Returns:
        List of repo-relative file paths ending in ``.json``.
    """
    out = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "git",
            "diff",
            "--name-only",
            f"{base_ref}...HEAD",
            "--",
            _KNOWLEDGE_ROOT,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        line.strip()
        for line in out.stdout.splitlines()
        if line.strip().endswith(".json")
    ]


def _git_load_ccnl(git_ref: str, file_path: str) -> CCNL | None:
    """Load a CCNL from git at *git_ref*, bypassing hash verification.

    Returns:
        Validated CCNL instance, or ``None`` if the file did not exist at
        *git_ref* (e.g. the contract is newly added in this diff).
    """
    result = subprocess.run(  # noqa: S603
        ["git", "show", f"{git_ref}:{file_path}"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    payload = json.loads(result.stdout)
    return CCNL.model_validate(payload)


# ---------------------------------------------------------------------------
# CCNL comparison
# ---------------------------------------------------------------------------


def _all_valid_from_dates(ccnl: CCNL) -> set[date]:
    """Return all valid_from dates from a CCNL's level salary TimeSeries.

    Returns:
        Set of dates appearing as period boundaries in any level.
    """
    return {
        period.valid_from
        for level in ccnl.levels
        for period in level.base_salary.periods
    }


def _fmt_eur(value: Decimal | None) -> str:
    """Format a Decimal as a Euro amount, or ``"(none)"`` if absent.

    Returns:
        Formatted string, e.g. ``"€1,234.56"`` or ``"(none)"``.
    """
    if value is None:
        return "(none)"
    return f"€{value:,.2f}"


def _level_salary_changes(
    old_lv: Level | None,
    new_lv: Level | None,
    ref_dates: set[date],
) -> list[str]:
    """Return change lines for one salary level across all reference dates.

    Returns:
        List of Markdown bullet strings (empty if no changes detected).
    """
    lines: list[str] = []
    for d in sorted(ref_dates):
        new_period = new_lv.base_salary.period_at(d) if new_lv else None
        old_period = old_lv.base_salary.period_at(d) if old_lv else None
        new_val = new_period.value if new_period else None
        old_val = old_period.value if old_period else None
        if new_val != old_val:
            lines.append(
                f"  - `{d}` base salary: {_fmt_eur(old_val)} → {_fmt_eur(new_val)}"
            )
    return lines


def _compare_ccnl_versions(
    old: CCNL | None,
    new: CCNL,
) -> Iterator[str]:
    """Yield Markdown lines describing salary-level changes between versions.

    Yields:
        Markdown-formatted strings, one per line of output.
    """
    ref_dates: set[date] = _all_valid_from_dates(new)
    if old is not None:
        ref_dates |= _all_valid_from_dates(old)

    new_levels = {lv.code: lv for lv in new.levels}
    old_levels = {lv.code: lv for lv in old.levels} if old is not None else {}
    all_codes = sorted(new_levels.keys() | old_levels.keys())

    any_change = False
    for code in all_codes:
        level_lines = _level_salary_changes(
            old_levels.get(code), new_levels.get(code), ref_dates
        )
        if level_lines:
            any_change = True
            yield f"**Level {code}**"
            yield from level_lines

    if not any_change:
        yield "_No level salary changes detected._"


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def _report(base_ref: str) -> str:
    """Build the full Markdown rules diff report for *base_ref*.

    Returns:
        Multi-line Markdown string ready for printing or posting as a comment.
    """
    changed = _git_changed_files(base_ref)
    if not changed:
        return "_No knowledge data changes in this diff._\n"

    lines: list[str] = ["## Rules diff — knowledge data changes", ""]

    ccnl_files = [p for p in changed if p.startswith(_CCNL_PREFIX)]
    other_files = [
        p for p in changed if any(p.startswith(pfx) for pfx in _OTHER_PREFIXES)
    ]

    if other_files:
        lines.extend(["### Tax / INPS / Surtax files changed", ""])
        for path in sorted(other_files):
            rel = path.replace(f"{_KNOWLEDGE_ROOT}/", "")
            lines.append(f"- `{rel}`")
        lines.extend([
            "",
            "> _No automated computational diff for these rules._",
            "",
        ])

    for path in sorted(ccnl_files):
        filename = Path(path).name
        new_ccnl = _git_load_ccnl("HEAD", path)
        if new_ccnl is None:
            lines.extend([f"### `{filename}` _(removed)_", ""])
            continue
        old_ccnl = _git_load_ccnl(base_ref, path)
        ccnl_name = new_ccnl.meta.name
        lines.extend([f"### `{filename}` — {ccnl_name}", ""])
        lines.extend(_compare_ccnl_versions(old_ccnl, new_ccnl))
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse arguments and print the rules diff report to stdout."""
    parser = argparse.ArgumentParser(
        description="Print a Markdown rules diff for changed knowledge files."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--base", metavar="SHA", help="Base commit SHA (PR mode).")
    group.add_argument("--since", metavar="TAG", help="Git tag to compare against.")
    args = parser.parse_args()
    print(_report(args.base or args.since))  # noqa: T201


if __name__ == "__main__":
    main()
