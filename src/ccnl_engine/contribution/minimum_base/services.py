"""Minimum INPS base of the run of a context, and its issue.

The rule and its reading are in
:mod:`~ccnl_engine.contribution.minimum_base.rules`; this module reads from
the run what it pays of its month.  A run whose base is below a minimum the
bundle cannot fix computes its contributions on the actual base, and its
INPS decisions and an incomplete issue say that they are undetermined.
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contribution.minimum_base.models import (
    MinimumBaseReason,
    MonthPosition,
)
from ccnl_engine.contribution.minimum_base.rules import resolve_minimum_base
from ccnl_engine.decision.models import (
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.employment.inputs import Apprentice
from ccnl_engine.event.facade import (
    AbsenceEvent,
    MaternityLeaveEvent,
    ParentalLeaveEvent,
    PaternityLeaveEvent,
    SickLeaveEvent,
    WorkInjuryEvent,
)
from ccnl_engine.run.models import RunKind

if TYPE_CHECKING:
    from ccnl_engine.contribution.minimum_base.models import MinimumBase
    from ccnl_engine.employment.fact.inputs import WeeklyHours
    from ccnl_engine.period.context.services import RunContext

__all__ = [
    "EXEMPT_CATEGORY_FLOOR",
    "ISSUE_CODE",
    "minimum_base_issue",
    "minimum_base_paths",
    "run_minimum_base",
]

#: Code of the issue of a run whose minimum INPS base is undetermined.
ISSUE_CODE = "inps_minimum_base_undetermined"
_LEGAL_BASIS = "D.L. 463/1983 art. 7 c. 1; D.Lgs. 81/2015 art. 11 c. 1"
#: Kinds of run that may post the monthly pay of their month.
_PAYING_KINDS = frozenset({RunKind.REGULAR, RunKind.TERMINATION})
_REDUCING_EVENTS = (
    AbsenceEvent,
    SickLeaveEvent,
    MaternityLeaveEvent,
    ParentalLeaveEvent,
    PaternityLeaveEvent,
    WorkInjuryEvent,
)
#: Fact of a sector that excludes a category the request leaves open.
_CATEGORY = "category"
#: Engine limitation of a worker whose category art. 7 c. 5 excludes.
EXEMPT_CATEGORY_FLOOR = "inps_minimum_base_exempt_category"


def _hours(fact: WeeklyHours | None) -> Decimal | None:
    return None if fact is None else fact.value


def _indemnified(ctx: RunContext) -> bool:
    """Return whether an insurer indemnifies every employed day of the month.

    Returns:
        ``True`` when a maternity leave, or the inability after a work
        injury of an earlier day, spans the employed days of the month.
    """
    year, month = ctx.cp.year, ctx.cp.month
    first, last = ctx.proration.span or (
        date(year, month, 1),
        date(year, month, calendar.monthrange(year, month)[1]),
    )
    for event in ctx.request.events:
        if isinstance(event, MaternityLeaveEvent):
            start = event.started_on
        elif isinstance(event, WorkInjuryEvent):
            start = event.injury_on + timedelta(days=1)
        else:
            continue
        if start <= first and event.ended_on >= last:
            return True
    return False


def _position(ctx: RunContext) -> MonthPosition:
    """Return what the run of ``ctx`` pays of its month.

    Returns:
        The position of the run: whether it posts the monthly pay of a
        fully employed month, and the worker facts the minimum reads.
    """
    request, proration = ctx.request, ctx.proration
    return MonthPosition(
        month_pay=ctx.regular_gross,
        adds_to_month=(
            ctx.run_kind not in _PAYING_KINDS
            or proration.posted_by is not None
            or bool(request.extra_month_settlements)
        ),
        span=proration.span,
        # A worker paid by the hour is paid only the hours worked: below the
        # minimum, the hours not worked may be absences of any kind.
        absence=proration.hourly is not None
        or any(isinstance(e, _REDUCING_EVENTS) for e in request.events),
        apprentice=isinstance(request.contract_type, Apprentice),
        category=ctx.worker_category,
        weekly_hours=_hours(request.weekly_hours),
        full_time_weekly_hours=_hours(request.full_time_weekly_hours),
        worked=not proration.idle,
        indemnified=_indemnified(ctx),
    )


def run_minimum_base(ctx: RunContext, event_inps_base: Decimal) -> MinimumBase | None:
    """Return the minimum INPS base of the run of ``ctx``.

    Args:
        ctx: Context of the run.
        event_inps_base: INPS base of the events of the run.

    Returns:
        The minimum of the pay chain and events of the run, ``None`` when
        its INPS rules carry no minimum (domestic work).
    """
    inps = ctx.contract.year_rules.inps
    if inps is None or inps.minimum_base is None:
        return None
    return resolve_minimum_base(
        inps.minimum_base, ctx.monthly_gross + event_inps_base, _position(ctx)
    )


def minimum_base_issue(minimum: MinimumBase | None) -> CalculationIssue | None:
    """Return the incomplete issue of an undetermined minimum base.

    Returns:
        An incomplete issue naming the reason, and the ``category`` fact
        when the sector excludes a category the request leaves open;
        ``None`` when the minimum is determined or not modelled.
    """
    if minimum is None or not minimum.undetermined:
        return None
    unknown = minimum.reason is MinimumBaseReason.CATEGORY_UNKNOWN
    return CalculationIssue(
        code=ISSUE_CODE,
        capability="inps_employee",
        message=(
            f"the INPS base {minimum.actual} is below the minimum of up to "
            f"{minimum.bound} the month can have ({_LEGAL_BASIS}) and the "
            f"minimum cannot be fixed ({minimum.reason.value}): the "
            "contributions are undetermined, the amounts shown are computed "
            "on the actual base"
        ),
        status=CalculationStatus.INCOMPLETE,
        source=minimum.source,
        fact=_CATEGORY if unknown else None,
    )


def minimum_base_paths(ctx: RunContext) -> frozenset[str]:
    """Return the limitation path of a worker of an excluded category.

    D.L. 463/1983 art. 7 c. 5 keeps the operai agricoli out of the 9.50%
    minimum, and the run applies none; Tabella A of INPS circ. 6/2026 still
    lists 51.70 for them, "non soggetto all'adeguamento", and whether it is
    a floor of their base is not settled.

    Returns:
        :data:`EXEMPT_CATEGORY_FLOOR` for a worker, not an apprentice, of a
        category the minimum of the sector excludes; nothing otherwise.
    """
    inps = ctx.contract.year_rules.inps
    rule = None if inps is None else inps.minimum_base
    if (
        rule is None
        or isinstance(ctx.request.contract_type, Apprentice)
        or ctx.worker_category not in rule.exempt_categories
    ):
        return frozenset()
    return frozenset({EXEMPT_CATEGORY_FLOOR})
