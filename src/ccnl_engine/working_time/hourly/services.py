"""The hourly terms of a run: its CCNL, the worker's full-time chain and facts."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.working_time.hourly.policies import HourlyTerms

if TYPE_CHECKING:
    from ccnl_engine.employment.fact.inputs import WeeklyHours
    from ccnl_engine.period.context.services import RunContext

__all__ = ["hourly_terms"]


def _hours(fact: WeeklyHours | None) -> Decimal | None:
    return None if fact is None else Decimal(fact.value)


def hourly_terms(ctx: RunContext) -> HourlyTerms:
    """Return what the hourly base of the run's worker is derived from.

    Returns:
        The CCNL with its ruleset identity, the full-time chain, the level,
        the roles, the full-time week and whether the employment is part
        time.
    """
    ccnl, request = ctx.contract.ccnl, ctx.request
    weekly = _hours(request.weekly_hours)
    full_time = _hours(request.full_time_weekly_hours)
    ruleset = ccnl.ruleset
    return HourlyTerms(
        ccnl=ccnl,
        chain=ctx.full_time_chain,
        level_code=request.level_code,
        roles=request.roles,
        full_time_weekly_hours=full_time,
        part_time=weekly is not None and full_time is not None and weekly < full_time,
        ruleset=f"ccnl/{ccnl.meta.ccnl_id}" if ruleset is None else ruleset.id,
        version=(
            str(ctx.contract.tctx.competence.year)
            if ruleset is None
            else ruleset.version
        ),
    )
