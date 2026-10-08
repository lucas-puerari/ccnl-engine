"""Facts of the employment the pay of a run depends on, when not stated.

- The part-time fraction is ``weekly_hours / full_time_weekly_hours``
  (D.Lgs. 81/2015 art. 7 c. 2: the pay "è riproporzionato in ragione
  della ridotta entità della prestazione lavorativa").  Contracted hours
  without the full time of the contract give no fraction: the run computes
  the full-time pay and names the missing full time, never takes the
  contracted hours as full time.  The same holds on a domestic CCNL,
  whose weekly hours also select the INPS bracket: its monthly minimum is
  the pay of a full-time week (the bundle derives the non-convivente one
  from 40 hours, the convivente one from 54).
- An allowance the CCNL restricts to a role is paid only to a worker who
  holds it.  ``Employment.roles`` left ``None`` does not state that the
  worker holds none: when the level has a role-restricted allowance in
  force, the run leaves it out and names the missing roles.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.events import AbsenceEvent

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext

__all__ = [
    "FULL_TIME_FACT",
    "NO_PAY_FACT",
    "ROLES_FACT",
    "full_time_issue",
    "no_pay_issue",
    "roles_issue",
]

FULL_TIME_FACT = "full_time_weekly_hours"
ROLES_FACT = "roles"
NO_PAY_FACT = "no_pay_due"


def no_pay_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return the missing-fact issue of an absence whose pay is not stated.

    The days of an absence for which no pay at all is due leave the days of
    the art. 13 TUIR deductions (AdE circ. 15/E/2007 par. 1.5.1), a strike
    does not: only a withholding employer computes them.

    Returns:
        An incomplete issue naming ``no_pay_due`` when an absence of the
        run leaves it unknown, else ``None``.
    """
    if not ctx.withholding_agent or not any(
        isinstance(e, AbsenceEvent) and e.no_pay_due is None for e in ctx.request.events
    ):
        return None
    return CalculationIssue(
        code="deduction_days_unknown",
        message=(
            "an absence of the run does not state whether any pay is due for "
            "its days: the days of the art. 13 TUIR deductions count them; "
            "state AbsenceEvent.no_pay_due"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=NO_PAY_FACT,
    )


def full_time_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return the missing-fact issue of contracted hours without a full time.

    Returns:
        An incomplete issue naming ``full_time_weekly_hours`` when the
        weekly hours are stated and the full time is not, else ``None``;
        never on a flat-pay regime, whose pay does not depend on it.
    """
    request = ctx.request
    hours = request.weekly_hours
    flat = ctx.contract.ccnl.parameters.flat_pay_max_weekly_hours is not None
    if hours is None or request.full_time_weekly_hours is not None or flat:
        return None
    return CalculationIssue(
        code="full_time_hours_unknown",
        message=(
            f"the employment states {hours.value} weekly hours but not the "
            "full time of the contract: the part-time fraction is "
            "undetermined, the amounts shown are those of full time; state "
            "Employment.full_time_weekly_hours"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=FULL_TIME_FACT,
    )


def roles_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return the missing-fact issue of unknown roles on a role-gated level.

    Returns:
        An incomplete issue naming ``roles`` when the roles are not stated
        and the level has an allowance restricted to a role in force on the
        competence date, else ``None``.
    """
    if ctx.request.roles is not None:
        return None
    competence = ctx.contract.tctx.competence
    gated = sorted(
        a.code
        for a in ctx.contract.level.fixed_allowances
        if a.role is not None and a.monthly.applies_on(competence)
    )
    if not gated:
        return None
    return CalculationIssue(
        code="roles_unknown",
        message=(
            f"the level pays allowances restricted to a role ({', '.join(gated)}) "
            "and the roles of the worker are not stated: the amounts shown "
            "leave them out; state Employment.roles (an empty set for none)"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=ROLES_FACT,
    )
