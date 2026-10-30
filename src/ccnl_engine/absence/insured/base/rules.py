"""The INPS base of a maternity or paternity leave, and what its absence means.

Both leaves are paid on the pay of the month before the leave (art. 23
D.Lgs. 151/2001, which art. 29 applies to the paternity leave).  When the
engine can compute that base and the leave does not state it, the fact is
missing; when it cannot (an operaia, a month not worked in full), the run
keeps the pay of its own month under an open engine limitation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.rules import maternity_daily_base
from ccnl_engine.decision.models import CalculationIssue, CalculationStatus

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.absence.insured.services import InsuredTerms
    from ccnl_engine.sickness.base.inputs import InpsSicknessBase

__all__ = ["LeaveBase", "leave_base"]


@dataclass(frozen=True)
class LeaveBase:
    """The daily base of a leave and what the run reports about it.

    Attributes:
        rmgg: The daily base, ``None`` when the run takes its own pay.
        issues: The missing-fact issue of a base the leave did not state.
        limitations: The engine limitation of a base the engine cannot
            compute.
    """

    rmgg: Decimal | None
    issues: tuple[CalculationIssue, ...] = ()
    limitations: tuple[str, ...] = ()


def _payments_before(terms: InsuredTerms, started_on: date) -> Decimal | None:
    """Return the monthly payments of the CCNL in the month before the leave.

    Returns:
        The payments on the last day of that month, ``None`` when unknown.
    """
    series = terms.monthly_payments
    month_before = started_on.replace(day=1) - timedelta(days=1)
    period = None if series is None else series.period_at(month_before)
    return None if period is None else period.value


def leave_base(
    base: InpsSicknessBase | None,
    terms: InsuredTerms,
    started_on: date,
    *,
    capability: str,
    field: str,
    code: str,
    limitation: str,
) -> LeaveBase:
    """Return the daily base of a leave and the issue or limitation it raises.

    Args:
        base: The pay of the month before, as the leave states it.
        terms: The terms of the run.
        started_on: First day of the leave.
        capability: Capability of the leave.
        field: Public field the leave states the base in.
        code: Code of the missing-fact issue.
        limitation: Engine limitation of a base the engine cannot compute.

    Returns:
        The base; an issue when it is computable but not stated, the
        limitation when the engine cannot compute it.
    """
    rmgg, computable = maternity_daily_base(
        base, terms.category, _payments_before(terms, started_on)
    )
    if rmgg is not None:
        return LeaveBase(rmgg)
    if not computable:
        return LeaveBase(None, limitations=(limitation,))
    issue = CalculationIssue(
        code=code,
        message=(
            "INPS pays the indemnity on the pay of the month before the leave "
            f"({field}), which the leave does not state; the indemnity is "
            "computed on the pay of the run meanwhile"
        ),
        status=CalculationStatus.PROVISIONAL,
        capability=capability,
        fact=field.rsplit(".", 1)[-1],
    )
    return LeaveBase(None, issues=(issue,))
