"""Readiness bound to the validation matrix: what a production CCNL covers.

A ``production`` CCNL must hold evidence, in the validation matrix
(:mod:`scripts.documentation.validation_matrix.generate`), for every
complete output of the definition of done for operational use: base
salary, gross, employee and employer contributions, tax, net pay, TFR and
employer cost (:data:`AXES`).  Only the totals of a row count: a component
or a rate the row pins covers no output.

The gate reads explicit ``(ccnl, output, independence)`` pairs, never the
union of the outputs and the kinds of evidence of a row, at two levels
(:data:`LEVELS`): ``any`` evidence, and a ``provider output``, the only
evidence independent of the sources the bundle was read from.  A hand
oracle covers an output at the first level, never at the second.

``baseline.json`` lists, per level, what each production CCNL still misses.
The lists only shrink: a CCNL that misses an output its entry does not list
fails, and an entry that names an output now covered, or a CCNL no longer
``production``, is stale and fails too.

The module reads raw JSON with the standard library only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Final

from scripts.documentation.validation_matrix.generate import matrix
from scripts.provenance.reference_case.check import AXES

if TYPE_CHECKING:
    from scripts.documentation.validation_matrix.generate import Row

__all__ = [
    "BASELINE",
    "LEVELS",
    "load_baseline",
    "missing_outputs",
    "readiness_errors",
]

#: Outputs each production CCNL still misses, per level, shrink only.
BASELINE: Final = Path(__file__).with_name("baseline.json")
#: The levels of the gate: any evidence, then an independent one.
LEVELS: Final = ("any", "provider output")

Gaps = dict[str, frozenset[str]]


def load_baseline(path: Path = BASELINE) -> dict[str, Gaps]:
    """Read the outputs each listed production CCNL may still miss, per level.

    Returns:
        The missing outputs by level, then by CCNL id.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        level: {ccnl: frozenset(axes) for ccnl, axes in data[level].items()}
        for level in LEVELS
    }


def _covers(row: Row, output: str, level: str) -> bool:
    return output in row.outputs if level == "any" else row.covered(output, level)


def missing_outputs(rows: dict[str, Row], level: str = "any") -> Gaps:
    """Return the outputs each production CCNL has no evidence of ``level`` for.

    Returns:
        The missing outputs of each production CCNL that misses any.
    """
    found = {
        ccnl: frozenset(a for a in AXES if not _covers(row, a, level))
        for ccnl, row in rows.items()
        if row.readiness == "production"
    }
    return {ccnl: axes for ccnl, axes in found.items() if axes}


def _level_errors(level: str, gaps: Gaps, allowed: Gaps) -> list[str]:
    what = "evidence" if level == "any" else f"{level} evidence"
    errors = [
        f"agreement/{ccnl}.json: production without {what} for "
        + ", ".join(sorted(axes - allowed.get(ccnl, frozenset())))
        for ccnl, axes in sorted(gaps.items())
        if axes - allowed.get(ccnl, frozenset())
    ]
    errors += [
        f"agreement/{ccnl}.json: stale {level!r} entry of {BASELINE.name}: "
        + ", ".join(sorted(axes - gaps.get(ccnl, frozenset())))
        + " now covered or the CCNL is not production"
        for ccnl, axes in sorted(allowed.items())
        if axes - gaps.get(ccnl, frozenset())
    ]
    return errors


def readiness_errors(
    rows: dict[str, Row] | None = None,
    baseline: dict[str, Gaps] | None = None,
) -> list[str]:
    """Return the production CCNLs whose evidence falls short of the rule.

    Returns:
        ``"agreement/<id>.json: ..."`` messages; empty when every gap is
        listed and every entry still holds.
    """
    found = matrix() if rows is None else rows
    allowed = load_baseline() if baseline is None else baseline
    return [
        error
        for level in LEVELS
        for error in _level_errors(
            level, missing_outputs(found, level), allowed.get(level, {})
        )
    ]
