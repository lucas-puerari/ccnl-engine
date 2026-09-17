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

from pydantic import ValidationError

from ccnl_engine.engine.contract.domain.ccnl import CCNL

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.engine.contract.domain.validity import TimeSeries

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


def _git_show(git_ref: str, file_path: str) -> str | None:
    """Return the raw content of *file_path* at *git_ref*, or ``None`` if absent.

    Returns:
        File contents as a string, or ``None`` when the file does not exist
        at *git_ref* (e.g. it was added after that commit).
    """
    result = subprocess.run(  # noqa: S603
        ["git", "show", f"{git_ref}:{file_path}"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def _git_load_ccnl_base(base_ref: str, file_path: str) -> CCNL | None:
    """Load a CCNL from the base ref, tolerating schema drift.

    The base branch may predate the current validator (e.g. ``model`` was null
    before PR #344 made it required for AI extractions).  A ``ValidationError``
    is treated as "file existed but cannot be compared" — equivalent to a new
    file from the diff's perspective.

    Returns:
        Validated CCNL instance, or ``None`` if the file did not exist at
        *base_ref* or its schema no longer validates against the HEAD model.
    """
    raw = _git_show(base_ref, file_path)
    if raw is None:
        return None
    try:
        return CCNL.model_validate(json.loads(raw))
    except ValidationError:
        return None


def _git_load_ccnl_head(file_path: str) -> CCNL | None:
    """Load a CCNL from HEAD, failing hard on validation errors.

    A ``ValidationError`` on HEAD indicates a bug in the PR under review and
    should propagate so the CI step turns red rather than silently misreporting
    the file as removed.

    Returns:
        Validated CCNL instance, or ``None`` if the file does not exist at HEAD
        (i.e. the contract was deleted in this diff).
    """
    raw = _git_show("HEAD", file_path)
    if raw is None:
        return None
    return CCNL.model_validate(json.loads(raw))


# ---------------------------------------------------------------------------
# CCNL comparison
# ---------------------------------------------------------------------------


def _ts_valid_from_dates(ts: TimeSeries) -> set[date]:
    """Return all valid_from dates in *ts*.

    Returns:
        Set of period boundary dates.
    """
    return {p.valid_from for p in ts.periods}


def _all_valid_from_dates(ccnl: CCNL) -> set[date]:
    """Return all valid_from dates from every TimeSeries in *ccnl*.

    Covers base salary, fixed allowances, hourly divisor, additional months,
    seniority increments, employer funds, and overtime bands.

    Returns:
        Union of all period boundary dates across the CCNL.
    """
    dates: set[date] = set()
    for level in ccnl.levels:
        dates |= _ts_valid_from_dates(level.base_salary)
        for allowance in level.fixed_allowances:
            dates |= _ts_valid_from_dates(allowance.monthly)
    params = ccnl.parameters
    dates |= _ts_valid_from_dates(params.hourly_divisor)
    dates |= _ts_valid_from_dates(params.additional_months)
    si = params.seniority_increments
    for ts in si.amount_by_level.values():
        dates |= _ts_valid_from_dates(ts)
    if si.apprentice_amount is not None:
        dates |= _ts_valid_from_dates(si.apprentice_amount)
    for fund in params.employer_funds:
        dates |= _ts_valid_from_dates(fund.rate)
    if ccnl.work_rules is not None and ccnl.work_rules.time_supplements is not None:
        for band in ccnl.work_rules.time_supplements.overtime_bands:
            dates |= _ts_valid_from_dates(band.rate)
    return dates


def _fmt_eur(value: Decimal | None) -> str:
    """Format a Decimal as a Euro amount, or ``"(none)"`` if absent.

    Returns:
        Formatted string, e.g. ``"€1,234.56"`` or ``"(none)"``.
    """
    if value is None:
        return "(none)"
    return f"€{value:,.2f}"


def _compare_ts(
    old_ts: TimeSeries | None,
    new_ts: TimeSeries | None,
    ref_dates: set[date],
    label: str,
) -> list[str]:
    """Return change lines for one TimeSeries field across reference dates.

    Returns:
        List of Markdown bullet strings (empty when no changes detected).
    """
    lines: list[str] = []
    for d in sorted(ref_dates):
        old_period = old_ts.period_at(d) if old_ts is not None else None
        new_period = new_ts.period_at(d) if new_ts is not None else None
        old_val = old_period.value if old_period is not None else None
        new_val = new_period.value if new_period is not None else None
        if old_val != new_val:
            lines.append(
                f"  - `{d}` {label}: {_fmt_eur(old_val)} → {_fmt_eur(new_val)}"
            )
    return lines


def _compare_level_versions(
    old: CCNL | None,
    new: CCNL,
    ref_dates: set[date],
) -> Iterator[str]:
    """Yield Markdown lines for per-level salary and allowance changes.

    Yields:
        Markdown-formatted strings for levels with changes.
    """
    new_levels = {lv.code: lv for lv in new.levels}
    old_levels = {lv.code: lv for lv in old.levels} if old is not None else {}
    for code in sorted(new_levels.keys() | old_levels.keys()):
        new_lv = new_levels.get(code)
        old_lv = old_levels.get(code)
        level_lines = _compare_ts(
            old_lv.base_salary if old_lv else None,
            new_lv.base_salary if new_lv else None,
            ref_dates,
            "base salary",
        )
        if new_lv:
            a_codes = {a.code for a in new_lv.fixed_allowances}
            if old_lv:
                a_codes |= {a.code for a in old_lv.fixed_allowances}
            new_al = {a.code: a for a in new_lv.fixed_allowances}
            old_al = {a.code: a for a in old_lv.fixed_allowances} if old_lv else {}
            for ac in sorted(a_codes):
                level_lines += _compare_ts(
                    old_al[ac].monthly if ac in old_al else None,
                    new_al[ac].monthly if ac in new_al else None,
                    ref_dates,
                    f"allowance {ac}",
                )
        if level_lines:
            yield f"**Level {code}**"
            yield from level_lines


def _compare_parameter_versions(
    old: CCNL | None,
    new: CCNL,
    ref_dates: set[date],
) -> list[str]:
    """Return change lines for all CCNL-level parameters.

    Returns:
        List of Markdown bullet strings for parameter changes.
    """
    new_p = new.parameters
    old_p = old.parameters if old is not None else None
    lines: list[str] = []
    lines += _compare_ts(
        old_p.hourly_divisor if old_p else None,
        new_p.hourly_divisor,
        ref_dates,
        "hourly divisor",
    )
    lines += _compare_ts(
        old_p.additional_months if old_p else None,
        new_p.additional_months,
        ref_dates,
        "additional months",
    )
    new_si = new_p.seniority_increments
    old_si = old_p.seniority_increments if old_p else None
    for level_code, ts in new_si.amount_by_level.items():
        old_ts = old_si.amount_by_level.get(level_code) if old_si else None
        lines += _compare_ts(old_ts, ts, ref_dates, f"seniority level {level_code}")
    if new_si.apprentice_amount is not None or (
        old_si is not None and old_si.apprentice_amount is not None
    ):
        lines += _compare_ts(
            old_si.apprentice_amount if old_si else None,
            new_si.apprentice_amount,
            ref_dates,
            "seniority apprentice",
        )
    new_funds = {f.code: f for f in new_p.employer_funds}
    old_funds = {f.code: f for f in old_p.employer_funds} if old_p else {}
    for fc in sorted(new_funds.keys() | old_funds.keys()):
        lines += _compare_ts(
            old_funds[fc].rate if fc in old_funds else None,
            new_funds[fc].rate if fc in new_funds else None,
            ref_dates,
            f"employer fund {fc}",
        )
    return lines


def _compare_ccnl_versions(
    old: CCNL | None,
    new: CCNL,
) -> Iterator[str]:
    """Yield Markdown lines describing all computational changes between versions.

    Covers base salary, fixed allowances, hourly divisor, additional months,
    seniority increments, employer funds, and overtime bands.

    Yields:
        Markdown-formatted strings, one per line of output.
    """
    ref_dates: set[date] = _all_valid_from_dates(new)
    if old is not None:
        ref_dates |= _all_valid_from_dates(old)

    any_change = False
    for line in _compare_level_versions(old, new, ref_dates):
        any_change = True
        yield line

    param_lines = _compare_parameter_versions(old, new, ref_dates)
    if param_lines:
        any_change = True
        yield "**Parameters**"
        yield from param_lines

    if not any_change:
        yield "_No computational changes detected._"


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
        new_ccnl = _git_load_ccnl_head(path)
        if new_ccnl is None:
            lines.extend([f"### `{filename}` _(removed)_", ""])
            continue
        old_ccnl = _git_load_ccnl_base(base_ref, path)
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
    print(_report(args.base or args.since))


if __name__ == "__main__":
    main()
