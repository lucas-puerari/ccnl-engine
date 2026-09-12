"""Human-readable formatter for :class:`~ccnl_engine.engine.diff.domain.diff.RulesDiff`.

The canonical output format matches the specification::

    Changed:
      Level C2 - base salary
      EUR 1,850.00 -> EUR 1,920.00

    Effective:
      2026-11-01

    Affected rules:
      3

    Affected scenarios:
      27

    Regression tests:
      passed

    Verification:
      approved

When multiple rules change, each is listed sequentially under *Changed:*.
``Affected scenarios`` and ``Regression tests`` are omitted when
``affected_scenarios == 0`` and ``regression_status == "not_run"`` (i.e.
the diff was produced without running scenario impact).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.engine.diff.domain.diff import RulesDiff


def format_diff(diff: RulesDiff) -> str:
    """Return the canonical multi-line text representation of *diff*.

    Args:
        diff: A :class:`~ccnl_engine.engine.diff.domain.diff.RulesDiff`
            produced by :func:`~ccnl_engine.engine.diff.compute.diff_ccnl`.

    Returns:
        A human-readable string ready for printing to a terminal or log.
    """
    lines: list[str] = []
    _append_changed_section(lines, diff)
    lines.extend(("", "Affected rules:", f"  {diff.affected_rules}"))
    _append_scenario_section(lines, diff)
    lines.extend(("", "Verification:", f"  {diff.verification_status}"))
    return "\n".join(lines)


def _append_changed_section(lines: list[str], diff: RulesDiff) -> None:
    """Append the Changed: and Effective: blocks to *lines*."""
    if diff.changes:
        lines.append("Changed:")
        for change in diff.changes:
            lines.append(f"  {change.label}")
            from_str = (
                _fmt_value(change.from_value, change.unit)
                if change.from_value is not None
                else "(new)"
            )
            to_str = (
                _fmt_value(change.to_value, change.unit)
                if change.to_value is not None
                else "(removed)"
            )
            lines.append(f"  {from_str} -> {to_str}")
        effective_dates = sorted({c.effective_date for c in diff.changes})
        lines.extend(("", "Effective:"))
        lines.extend(f"  {dt.isoformat()}" for dt in effective_dates)
    else:
        lines.extend(("Changed:", "  (no changes detected)"))


def _append_scenario_section(lines: list[str], diff: RulesDiff) -> None:
    """Append Affected scenarios / Regression tests blocks when present."""
    if diff.affected_scenarios > 0 or diff.regression_status != "not_run":
        lines.extend((
            "",
            "Affected scenarios:",
            f"  {diff.affected_scenarios}",
            "",
            "Regression tests:",
            f"  {diff.regression_status}",
        ))


def _fmt_value(value: object, unit: str) -> str:
    if unit in {"EUR/month", "EUR/year"}:
        return f"€{value:,.2f}"
    if unit == "%":
        return f"{value:.4f}"
    return f"{value} {unit}"
