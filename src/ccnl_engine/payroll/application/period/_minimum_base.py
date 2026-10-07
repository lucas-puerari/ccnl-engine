"""Minimum INPS base of the run of a context, and its issue.

The rule and its reading are in
:mod:`~ccnl_engine.payroll.service.minimum_base`; this module reads from
the run what it pays of its month.  A run whose base is below a minimum the
bundle cannot fix computes its contributions on the actual base, and its
INPS decisions and an incomplete issue say that they are undetermined.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.employment import Apprentice
from ccnl_engine.payroll.domain.events import AbsenceEvent, SickLeaveEvent
from ccnl_engine.payroll.domain.minimum_base import MinimumBaseReason, MonthPosition
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.service.minimum_base import resolve_minimum_base

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.employment_facts import WeeklyHours
    from ccnl_engine.payroll.domain.minimum_base import MinimumBase

__all__ = ["ISSUE_CODE", "minimum_base_issue", "run_minimum_base"]

#: Code of the issue of a run whose minimum INPS base is undetermined.
ISSUE_CODE = "inps_minimum_base_undetermined"
_LEGAL_BASIS = "D.L. 463/1983 art. 7 c. 1; D.Lgs. 81/2015 art. 11 c. 1"
#: Kinds of run that may post the monthly pay of their month.
_PAYING_KINDS = frozenset({RunKind.REGULAR, RunKind.TERMINATION})
_REDUCING_EVENTS = (AbsenceEvent, SickLeaveEvent)
#: Fact of a sector that excludes a category the request leaves open.
_CATEGORY = "category"


def _hours(fact: WeeklyHours | None) -> Decimal | None:
    return None if fact is None else Decimal(fact.value)


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
        absence=any(isinstance(e, _REDUCING_EVENTS) for e in request.events),
        apprentice=isinstance(request.contract_type, Apprentice),
        category=ctx.worker_category,
        weekly_hours=_hours(request.weekly_hours),
        full_time_weekly_hours=_hours(request.full_time_weekly_hours),
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
