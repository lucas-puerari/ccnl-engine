"""The daily divisor of the full-time week stated, read by every consumer.

Logistica art. 61 c. 3 (testo unico 2025, p. 86): "La retribuzione
giornaliera del personale si ottiene dividendo la retribuzione mensile per
22. Per il personale non viaggiante, in caso di orario di lavoro
settimanale distribuito su 6 giorni [...] per 26."  Pulizia artigianato art.
34 divides by 22 on a five-day week; BCC art. 114 by 6 x 52 / 12 = 26 on a
six-day one.  In March 2026 the 16th to the 31st hold 12 days Monday to
Friday and 14 Monday to Saturday; 1 November 2026 is a Sunday.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import PayrollEngine
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.compensation.sunday_holiday.services import CAPABILITY
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import AbsenceEvent
from ccnl_engine.inputs import (
    EmploymentChange,
    EmploymentPeriod,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId
from tests.unit.ccnl_engine.builders import year_plan

if TYPE_CHECKING:
    from ccnl_engine.decision.models import CalculationDecision
    from ccnl_engine.event.facade import WorkEvent
    from ccnl_engine.period.results import PeriodResult

_LOGISTICA = "logistica-trasporto-confetra"
_CENT = Decimal("0.01")


def _cents(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _run(
    slug: str,
    level: str,
    month: int,
    days: int | None,
    events: tuple[WorkEvent, ...] = (),
    start: date | None = None,
) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(2026, month),
            payment_date=date(2026, month, 27),
            ccnl_id=slug,
            level_code=level,
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=events,
            full_time_week_days=days,
            employment_period=None if start is None else EmploymentPeriod(start),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _decision(result: PeriodResult, capability: str) -> CalculationDecision:
    (found,) = [d for d in result.decisions if d.capability == capability]
    return found


@pytest.mark.parametrize(("days", "divisor"), [(None, 22), (5, 22), (6, 26)])
def test_an_absence_divides_by_the_days_of_the_week(
    days: int | None, divisor: int
) -> None:
    """Two working days at the monthly pay over 22 or 26."""
    event = AbsenceEvent(
        date(2026, 3, 16), Decimal(16), end_date=date(2026, 3, 17), working_days=2
    )
    decision = _decision(_run(_LOGISTICA, "3", 3, days, (event,)), "absence")

    monthly = Decimal(str(decision.inputs["hourly_base_monthly"]))
    assert decision.inputs["quota_divisor"] == Decimal(divisor)
    assert decision.amount == -_cents(2 * monthly / divisor)


@pytest.mark.parametrize(
    ("days", "method", "payable"), [(None, "by_22", "12"), (6, "by_26", "14")]
)
def test_a_part_month_counts_the_days_of_the_week(
    days: int | None, method: str, payable: str
) -> None:
    """From Monday 16 March: 12 days of 22, or 14 of 26."""
    result = _run(_LOGISTICA, "3", 3, days, start=date(2026, 3, 16))
    (decision,) = [d for d in result.decisions if d.reason_code == "pay_chain_prorated"]

    assert decision.inputs["divisor_method"] == method
    assert decision.inputs["payable_days"] == payable


def test_a_promotion_splits_the_month_by_the_days_of_the_week() -> None:
    """16 July 2026: 12 of 23 days Monday to Friday, 14 of 27 to Saturday."""
    gross = {}
    for days in (None, 6):
        plan = year_plan(
            2026,
            _LOGISTICA,
            "4",
            seniority=SeniorityFact(0, date(2026, 1, 1), SenioritySource.PAYSLIP),
            employment_period=EmploymentPeriod(date(2026, 1, 1)),
            roles=frozenset(),
            full_time_week_days=days,
        )
        plan = replace(
            plan,
            employment_changes=(EmploymentChange(date(2026, 7, 16), level_code="3"),),
        )
        year = PayrollEngine.bundled().calculate_competence_year(plan)
        (july,) = [
            r
            for r in year.period_results
            if r.run is not None
            and (r.run.month, r.run.run_kind) == (7, RunKind.REGULAR)
        ]
        gross[days] = july.period_gross

    assert gross[None] != gross[6]


@pytest.mark.parametrize(
    ("slug", "level", "days", "divisor"),
    [
        ("pulizia-artigianato-confartigianato", "3", None, "26"),
        ("pulizia-artigianato-confartigianato", "3", 5, "22"),
        ("bcc-credito-cooperativo", "3AP1", None, "21.5"),
        ("bcc-credito-cooperativo", "3AP1", 6, "26"),
    ],
)
def test_a_holiday_on_the_rest_day_divides_by_the_days_of_the_week(
    slug: str, level: str, days: int | None, divisor: str
) -> None:
    """Ognissanti on the Sunday rest: Pulizia art. 34, BCC art. 114."""
    decision = _decision(_run(slug, level, 11, days), CAPABILITY)

    assert decision.inputs["divisor"] == Decimal(divisor)


@pytest.mark.parametrize(
    ("slug", "level"),
    [
        ("studi-professionali-confprofessioni", "4"),
        ("pulizia-artigianato-confartigianato", "3"),
        ("multiservizi-anip", "3"),
    ],
)
@pytest.mark.parametrize(("days", "ferie"), [(None, "22"), (5, "22"), (6, "26")])
def test_the_ferie_accrue_by_the_days_of_the_week(
    slug: str, level: str, days: int | None, ferie: str
) -> None:
    """Studi art. 99, Pulizia art. 24, Multiservizi art. 42: 26 on six, 22 on five."""
    result = _run(slug, level, 3, days, start=date(2020, 1, 1))
    (balance,) = [
        b
        for b in result.closing_state.accrual.leave.balances
        if b.bucket is LeaveBucket.FERIE
    ]
    assert balance.accrued_twelfths == Decimal(ferie)
