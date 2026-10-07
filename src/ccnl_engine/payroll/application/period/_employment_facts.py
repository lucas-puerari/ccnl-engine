"""Facts of the employment the pay of a run depends on, when not stated.

- The part-time fraction is ``weekly_hours / full_time_weekly_hours``
  (D.Lgs. 81/2015 art. 7 c. 2: the pay "è riproporzionato in ragione
  della ridotta entità della prestazione lavorativa").  Contracted hours
  without the full time of the contract give no fraction: the run computes
  the full-time pay and names the missing full time, never takes the
  contracted hours as full time.  On a domestic CCNL the weekly hours
  select the INPS bracket of the flat hourly contributions and the pay
  tables are per kind of employment (convivente, non convivente), so the
  full time is not required there.
- An allowance the CCNL restricts to a role is paid only to a worker who
  holds it.  ``Employment.roles`` left ``None`` does not state that the
  worker holds none: when the level has a role-restricted allowance in
  force, the run leaves it out and names the missing roles.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext

__all__ = ["FULL_TIME_FACT", "ROLES_FACT", "full_time_issue", "roles_issue"]

FULL_TIME_FACT = "full_time_weekly_hours"
ROLES_FACT = "roles"


def full_time_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return the missing-fact issue of contracted hours without a full time.

    Returns:
        An incomplete issue naming ``full_time_weekly_hours`` when the
        weekly hours of a non-domestic CCNL are stated and the full time is
        not, else ``None``.
    """
    request = ctx.request
    hours = request.weekly_hours
    domestic = ctx.contract.year_rules.domestic_contributions is not None
    if domestic or hours is None or request.full_time_weekly_hours is not None:
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
