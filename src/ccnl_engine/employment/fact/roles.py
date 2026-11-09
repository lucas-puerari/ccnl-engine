"""Missing worker-role facts for role-dependent remuneration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext

ROLES_FACT = "roles"


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
        [
            a.code
            for a in ctx.contract.level.fixed_allowances
            if a.role is not None and a.monthly.applies_on(competence)
        ]
        + [
            a.code
            for a in ctx.contract.ccnl.parameters.daily_presence_allowances
            if (a.role is not None or a.excluded_role is not None)
            and a.rate.applies_on(competence)
        ]
    )
    rules = ctx.contract.ccnl.parameters.seniority_increments
    if ctx.chain.seniority > 0:
        gated.extend(
            role
            for role, amounts in rules.amount_by_level_by_role.items()
            if ctx.contract.level.code in amounts
            and amounts[ctx.contract.level.code].applies_on(competence)
        )
    if not gated:
        return None
    return CalculationIssue(
        code="roles_unknown",
        capability="base_salary",
        message=(
            f"the level pays elements restricted to a role ({', '.join(gated)}) "
            "and the roles of the worker are not stated: the amounts shown "
            "leave them out; state Employment.roles (an empty set for none)"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=ROLES_FACT,
    )
