"""A promotion inside a month: each level for its days, one month in all.

Commercio Confcommercio, promoted from level 5 to level 4 on Thursday 16
July 2026 (Art. 118: the new level from the promotion).  The CCNL daily
quota is a twenty-sixth of Monday to Saturday: July 2026 has 27 such days,
13 before the 16th and 14 from it, so the month pays 13/27 of level 5 and
14/27 of level 4, each component rounded apart:

- paga base 1,136.07 x 13/27 = 547.00 and 1,257.46 x 14/27 = 652.02;
- contingenza/EDR 521.94 x 13/27 = 251.30 and 524.22 x 14/27 = 271.82;
- terzo elemento 2.07 x 13/27 = 1.00 and 2.07 x 14/27 = 1.07.

No text says how the month is split: the run reports the engine limitation
``mid_month_level_change``.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine import InvalidInputError, PayrollEngine, PeriodInput
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.change.rules import MID_MONTH_CHANGE, month_change
from ccnl_engine.inputs import (
    EmploymentChange,
    EmploymentPeriod,
    SeniorityFact,
    SeniorityPromotion,
    SenioritySource,
)
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId
from tests.unit.ccnl_engine.builders import year_plan

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest
    from ccnl_engine.period.results import PeriodResult

_ENGINE = PayrollEngine.bundled()
_CENT = Decimal("0.01")
_SENIORITY = SeniorityFact(24, date(2026, 1, 1), SenioritySource.PAYSLIP)


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _split(before: str, after: str) -> Decimal:
    return _money(Decimal(before) * 13 / 27) + _money(Decimal(after) * 14 / 27)


def _plan_runs() -> dict[int, PeriodResult]:
    plan = year_plan(
        2026,
        "commercio-confcommercio",
        "5",
        seniority=SeniorityFact(0, date(2026, 1, 1), SenioritySource.PAYSLIP),
        employment_period=EmploymentPeriod(date(2026, 1, 1)),
        roles=frozenset(),
    )
    plan = replace(
        plan, employment_changes=(EmploymentChange(date(2026, 7, 16), level_code="4"),)
    )
    year = _ENGINE.calculate_competence_year(plan)
    return {
        r.run.month: r
        for r in year.period_results
        if r.run is not None and r.run.run_kind is RunKind.REGULAR
    }


def _components(result: PeriodResult) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = {}
    for item in result.pay_items:
        if item.kind in {"base_salary_earning", "fixed_allowance_earning"}:
            totals[item.item_id.split("_", 2)[-1]] = item.amount
    return totals


def test_july_pays_each_level_for_its_days() -> None:
    """Base, contingenza and terzo elemento split 13/27 and 14/27."""
    july = _plan_runs()[7]
    base = _split("1136.07", "1257.46")
    contingenza = _split("521.94", "524.22")
    terzo = _split("2.07", "2.07")

    assert (base, contingenza, terzo) == (
        Decimal("1199.02"),
        Decimal("523.12"),
        Decimal("2.07"),
    )
    assert july.period_gross == base + contingenza + terzo
    assert MID_MONTH_CHANGE in {lim.id for lim in july.limitations}


def test_the_months_around_pay_one_level_each() -> None:
    """June all at level 5, August all at level 4."""
    runs = _plan_runs()
    assert runs[6].period_gross == Decimal("1136.07") + Decimal("521.94") + Decimal(
        "2.07"
    )
    assert runs[8].period_gross == Decimal("1257.46") + Decimal("524.22") + Decimal(
        "2.07"
    )
    assert MID_MONTH_CHANGE not in {lim.id for lim in runs[8].limitations}


def _request(
    day: date, ccnl: str, *, hired: date = date(2025, 1, 1)
) -> PeriodCalculationRequest:
    return cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            seniority=replace(_SENIORITY, promotion=SeniorityPromotion(day, "5")),
            period_id=PeriodId(year=day.year, month=day.month),
            employment_period=EmploymentPeriod(hired),
        ),
    )


@pytest.mark.parametrize(
    ("ccnl", "day", "hired", "share"),
    [
        # by_26: 14 of the 27 Mondays to Saturdays of July 2026.
        ("commercio-confcommercio", date(2026, 7, 16), date(2025, 1, 1), "14/27"),
        # Hired on Monday 6 July: 14 of the 23 payable days employed.
        ("commercio-confcommercio", date(2026, 7, 16), date(2026, 7, 6), "14/23"),
        # by_30, February 2026: the 15th to the end runs to day 30.
        ("funzioni-centrali-aran", date(2026, 2, 15), date(2025, 1, 1), "16/30"),
    ],
)
def test_the_share_is_the_payable_days_from_the_promotion(
    ccnl: str, day: date, hired: date, share: str
) -> None:
    """Both stretches make one month of the employed days."""
    request = _request(day, ccnl, hired=hired)
    change = month_change(request, load_ccnl(ccnl), RunKind.REGULAR)
    numerator, denominator = share.split("/")

    assert change is not None
    assert change.share == Decimal(numerator) / Decimal(denominator)
    assert month_change(request, load_ccnl(ccnl), RunKind.THIRTEENTH) is None


def test_a_promotion_on_the_first_or_in_another_month_splits_nothing() -> None:
    """1 July, or a promotion of June read by the July run."""
    ccnl = load_ccnl("commercio-confcommercio")
    assert month_change(_request(date(2026, 7, 1), ""), ccnl, RunKind.REGULAR) is None
    june = _request(date(2026, 6, 16), "")
    july = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(**{**vars(june), "period_id": PeriodId(year=2026, month=7)}),
    )
    assert month_change(july, ccnl, RunKind.REGULAR) is None


@pytest.mark.parametrize(
    ("ccnl", "reason"),
    [
        ("agenti-immobiliari-fiaip", "no daily quota"),
        ("edilizia-ance", "by the hour"),
    ],
)
def test_a_month_the_ccnl_cannot_split_is_rejected(ccnl: str, reason: str) -> None:
    """No daily quota for the absences, or a category paid by the hour."""
    request = _request(date(2026, 7, 16), ccnl)
    with pytest.raises(InvalidInputError, match=reason):
        month_change(request, load_ccnl(ccnl), RunKind.REGULAR)


def test_a_single_run_pays_what_the_plan_pays() -> None:
    """A July run alone, with the promotion on its seniority."""
    july = _plan_runs()[7]
    single = _ENGINE.calculate_period(
        PeriodInput(
            run=july.run,  # type: ignore[arg-type]
            payment_date=july.payment_date,
            employment=replace(
                year_plan(2026, "commercio-confcommercio", "4").employment,
                seniority=SeniorityFact(
                    0,
                    date(2026, 1, 1),
                    SenioritySource.PAYSLIP,
                    promotion=SeniorityPromotion(date(2026, 7, 16), "5"),
                ),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
                roles=frozenset(),
            ),
            employer=year_plan(2026, "commercio-confcommercio", "4").employer,
            facts=year_plan(2026, "commercio-confcommercio", "4").default_facts,
        )
    )
    assert single.period_gross == july.period_gross


def test_a_month_without_a_payable_day_is_rejected() -> None:
    """Employed only on Sunday 26 July: no twenty-sixth to share."""
    request = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(**{
            **vars(_request(date(2026, 7, 16), "")),
            "employment_period": EmploymentPeriod(date(2026, 7, 26), date(2026, 7, 26)),
        }),
    )
    with pytest.raises(InvalidInputError, match="no payable day"):
        month_change(request, load_ccnl("commercio-confcommercio"), RunKind.REGULAR)
