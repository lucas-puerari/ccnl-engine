"""Readiness bound to the validation matrix: what a production CCNL covers.

A ``production`` CCNL must hold evidence, in the validation matrix
(:mod:`scripts.documentation.validation_matrix.generate`), for every output
of the definition of done for operational use: base salary, gross,
contributions, tax, net pay, TFR and employer cost (:data:`AXES`).  The
CCNLs promoted before the rule miss some of them; ``baseline.json`` lists
what each still misses.  The list only shrinks: a CCNL that misses an
output its entry does not list fails, and an entry that names an output now
covered, or a CCNL no longer ``production``, is stale and fails too.

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

__all__ = ["BASELINE", "load_baseline", "missing_outputs", "readiness_errors"]

#: Outputs each production CCNL still misses, shrink only.
BASELINE: Final = Path(__file__).with_name("baseline.json")


def load_baseline(path: Path = BASELINE) -> dict[str, frozenset[str]]:
    """Read the outputs each listed production CCNL may still miss.

    Returns:
        The missing outputs by CCNL id.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    return {ccnl: frozenset(axes) for ccnl, axes in data["missing_outputs"].items()}


def missing_outputs(rows: dict[str, Row]) -> dict[str, frozenset[str]]:
    """Return the outputs each production CCNL has no evidence for.

    Returns:
        The missing outputs of each production CCNL that misses any.
    """
    found = {
        ccnl: frozenset(AXES) - row.outputs
        for ccnl, row in rows.items()
        if row.readiness == "production"
    }
    return {ccnl: axes for ccnl, axes in found.items() if axes}


def readiness_errors(
    rows: dict[str, Row] | None = None,
    baseline: dict[str, frozenset[str]] | None = None,
) -> list[str]:
    """Return the production CCNLs whose evidence falls short of the rule.

    Returns:
        ``"agreement/<id>.json: ..."`` messages; empty when every gap is
        listed and every entry still holds.
    """
    gaps = missing_outputs(matrix() if rows is None else rows)
    allowed = load_baseline() if baseline is None else baseline
    errors = [
        f"agreement/{ccnl}.json: production without evidence for "
        + ", ".join(sorted(axes - allowed.get(ccnl, frozenset())))
        for ccnl, axes in sorted(gaps.items())
        if axes - allowed.get(ccnl, frozenset())
    ]
    errors += [
        f"agreement/{ccnl}.json: stale entry of {BASELINE.name}: "
        + ", ".join(sorted(axes - gaps.get(ccnl, frozenset())))
        + " now covered or the CCNL is not production"
        for ccnl, axes in sorted(allowed.items())
        if axes - gaps.get(ccnl, frozenset())
    ]
    return errors
