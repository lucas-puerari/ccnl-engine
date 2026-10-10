"""Position of a run toward the additional 1% IVS of its competence year.

The 1% follows competence, like the INPS base it is charged on: the runs of
one competence month share the monthly threshold, and the year is settled
by the runs of competence December and of the month the employment ends
(INPS msg. 5327/2015 par. 2.3; circ. 156/2025 par. 5); see
:mod:`~ccnl_engine.payroll.service.additional_ivs`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.service.additional_ivs import AdditionalIvsPosition

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
    from ccnl_engine.payroll.domain.run import PayrollRunId
    from ccnl_engine.provenance.source.models_chain import RuleProvenance
    from ccnl_engine.tax.contribution.models import InpsRates

__all__ = [
    "FACT",
    "UNKNOWN_CODE",
    "additional_ivs_issue",
    "additional_ivs_position",
    "additional_ivs_rules",
]

#: Fact a settling run needs when other employers have a base of the year.
FACT = "other_employers_additional_ivs"
#: Code of the issue of a settlement without the 1% of other employers.
UNKNOWN_CODE = "other_employers_additional_ivs_unknown"

_DECEMBER = 12


def _ends_in(period: EmploymentPeriod | None, run_id: PayrollRunId) -> bool:
    """Return whether the employment ends in the month of ``run_id``.

    Returns:
        ``True`` when its last day falls in the competence month of the run.
    """
    ended_on = None if period is None else period.ended_on
    return ended_on is not None and (ended_on.year, ended_on.month) == (
        run_id.year,
        run_id.month,
    )


def additional_ivs_position(ctx: RunContext) -> AdditionalIvsPosition:
    """Return where the run of ``ctx`` stands toward the additional 1% IVS.

    Returns:
        The base this employment already declared for the run's competence
        month, the 1% already withheld on its competence year by every
        employment, and whether the run settles the year: a run of
        competence December, of the month the employment ends, or a
        termination run.
    """
    run_id = ctx.payment.run_id
    base = ctx.opening.accrual.inps_base(run_id.year)
    settles = (
        run_id.month == _DECEMBER
        or run_id.kind is RunKind.TERMINATION
        or _ends_in(ctx.request.employment_period, run_id)
    )
    return AdditionalIvsPosition(
        month_base=base.base_of_month(run_id.month),
        withheld=base.additional_ivs_withheld,
        settles=settles,
    )


def additional_ivs_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return the missing-fact issue of a settlement short of a fact.

    The conguaglio deducts the 1% other employers withheld on their base
    of the year (INPS circ. 156/2025 par. 5).  When that base is imported
    and the 1% is not, the settlement cannot be determined: the run
    computes it as if they withheld nothing and reports the fact missing.

    Returns:
        An incomplete issue naming ``other_employers_additional_ivs``, or
        ``None`` when the run does not settle, the rules do not model the
        1%, or the fact is known.
    """
    inps = ctx.contract.year_rules.inps
    rule = None if inps is None else inps.employee_additional
    run_id = ctx.payment.run_id
    base = ctx.opening.accrual.inps_base(run_id.year)
    if (
        rule is None
        or not additional_ivs_position(ctx).settles
        or not base.other_employers_withheld_unknown
    ):
        return None
    return CalculationIssue(
        code=UNKNOWN_CODE,
        message=(
            f"the run settles the additional 1% IVS of {run_id.year} "
            f"(D.L. 384/1992 art. 3-ter) on a base of other employers of "
            f"{base.other_employers}, but the 1% they withheld on it is not "
            "stated (InpsBaseYtd.other_employers_additional_ivs); the "
            "settlement shown deducts nothing for it"
        ),
        status=CalculationStatus.INCOMPLETE,
        source=rule.provenance.location if rule.provenance else None,
        fact=FACT,
    )


def additional_ivs_rules(
    name: str, rates: InpsRates | None
) -> tuple[tuple[str, RuleProvenance | None], ...]:
    """Return the 1% employee IVS rule of the sector, when it models one.

    Args:
        name: Id of the INPS ruleset that holds the rule.
        rates: INPS rates of the sector, if any.

    Returns:
        The ``inps.employee_additional`` rule with its record, or nothing.
    """
    rule = None if rates is None else rates.employee_additional
    if rule is None:
        return ()
    return ((f"{name}:inps.employee_additional", rule.provenance),)
