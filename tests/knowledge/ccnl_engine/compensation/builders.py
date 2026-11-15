"""A month of a domestic worker run through the public engine."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.event.types import WorkEvent

_ENGINE = PayrollEngine.bundled()
#: Full-time week of each domestic CCNL (art. 14 cc. 1-2).
_WEEK = {
    "lavoro-domestico-convivente": Decimal(54),
    "lavoro-domestico-convivente-orario-ridotto": Decimal(30),
    "lavoro-domestico-non-convivente": Decimal(40),
}


def domestic_month(
    ccnl_id: str, level: str, month: int, *events: WorkEvent, year: int = 2026
) -> PeriodResult:
    """Return the run of ``month`` of a full-time domestic worker.

    Returns:
        The period result of the regular run with ``events``.
    """
    week = _WEEK[ccnl_id]
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=year, month=month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                weekly_hours=WeeklyHours(week),
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(
                contributable_hours=ContributableHours(week * 52 / 12),
                events=events,
            ),
        )
    )
