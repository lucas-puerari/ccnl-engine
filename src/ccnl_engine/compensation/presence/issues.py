"""Missing attendance-day facts for contractual daily earnings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext


def presence_issues(ctx: RunContext) -> tuple[CalculationIssue, ...]:
    """Report missing day counts only for selected, active daily allowances.

    Unknown worker roles are reported separately before assuming which
    role-gated rules apply. Extra-month runs do not pay these daily rates.

    Returns:
        Missing-fact issues for relevant and unknown day counts.
    """
    request = ctx.request
    if ctx.payment.run_id.kind != "regular" or request.roles is None:
        return ()
    active = tuple(
        rule
        for rule in ctx.contract.ccnl.parameters.daily_presence_allowances
        if rule.applies(request.roles)
        and rule.rate.applies_on(ctx.contract.tctx.competence)
    )
    missing = (
        ("presence_days", "work") if request.presence_days is None else None,
        (
            ("site_presence_days", "site")
            if request.site_presence_days is None
            else None
        ),
    )
    return tuple(
        CalculationIssue(
            code=f"{name}_unknown",
            capability="base_salary",
            message=(
                f"daily presence allowances "
                f"({', '.join(r.code for r in active if r.day_kind == kind)}) "
                f"need the number of qualifying {kind} days in the month; "
                f"state PeriodFacts.{name} (zero if none)"
            ),
            status=CalculationStatus.INCOMPLETE,
            fact=name,
        )
        for item in missing
        if item is not None
        for name, kind in (item,)
        if any(r.day_kind == kind for r in active)
    )
