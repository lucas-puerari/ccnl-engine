"""INPS base of the worker's other employments, when it is not stated.

The IVS massimale is per worker (L. 335/1995 art. 2 c. 18; INPS circ.
237/2016 par. 3.1): the base of the other employments of the competence
year counts toward it, and toward the band of the additional 1% IVS
(D.L. 384/1992 art. 3-ter; INPS circ. 6/2026 note 10).  Whether the
base of other employers is stated is a fact
(:class:`~ccnl_engine.payroll.domain.inps_base.InpsBaseYtd`): ``0`` says
there is none, ``None`` is unknown.

An unknown base has no upper bound, so for any run with a positive INPS
base some value of it moves the run across the massimale or the 1%
threshold.  The engine encodes no estimate of it: the run computes on this
employment alone and, whenever its INPS rules carry a massimale the worker
may be subject to or a 1% threshold, reports a ``missing_fact`` issue.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext

__all__ = ["FACT", "other_employers_issue"]

FACT = "other_employers"
_ZERO = Decimal(0)


def other_employers_issue(
    ctx: RunContext, period_inps_base: Decimal
) -> CalculationIssue | None:
    """Return the missing-fact issue of an unknown base of other employers.

    Args:
        ctx: Context of the run.
        period_inps_base: INPS base of the run.

    Returns:
        An incomplete issue naming the base of other employments when it is
        unknown and could change the contributions of the run, else
        ``None``.
    """
    base = ctx.opening.accrual.inps_base(ctx.cp.year)
    inps = ctx.contract.year_rules.inps
    if base.other_employers_known or inps is None or period_inps_base <= _ZERO:
        return None
    history = ctx.request.contribution_history
    massimale = inps.ceiling is not None and (
        history is None or history.ivs_ceiling_applies
    )
    additional = inps.employee_additional is not None
    if not (massimale or additional):
        return None
    return CalculationIssue(
        code="other_employment_inps_base_unknown",
        message=(
            f"the INPS base of the worker's other employments of {ctx.cp.year} "
            "is not stated: it counts toward the IVS massimale (L. 335/1995 "
            "art. 2 c. 18; INPS circ. 237/2016 par. 3.1) and the band of the "
            "additional 1% IVS, so the contributions are computed on "
            "this employment alone as a simulation; state it in "
            "CurrentYearTaxFacts.other_employment_inps_base (0 for none) or "
            "in the imported OpeningBalances.inps_bases"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=FACT,
    )
