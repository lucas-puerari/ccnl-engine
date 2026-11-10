"""Regression checks for multiple independent yearly guarantee elements."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.equalisation.rules import equalisation_outcome
from ccnl_engine.inputs import EmploymentPeriod, WeeklyHours
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest

_CCNL = load_ccnl("tessile-pmi-uniontessile")


def _request(
    hired: date,
    *,
    premium: bool | None = False,
    year: int = 2026,
    month: int = 6,
    ended: date | None = None,
    part_time: bool = False,
) -> PeriodCalculationRequest:
    return cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            period_id=PeriodId(year=year, month=month),
            level_code="5",
            employment_period=EmploymentPeriod(hired, ended),
            individual_elements=(),
            weekly_hours=WeeklyHours(Decimal(20)) if part_time else None,
            full_time_weekly_hours=WeeklyHours(Decimal(40)) if part_time else None,
            employer=SimpleNamespace(
                second_level_premium=premium, second_level_elements=()
            ),
        ),
    )


def _amounts(request: PeriodCalculationRequest) -> list[Decimal]:
    outcome = equalisation_outcome(request, _CCNL, RunKind.REGULAR)
    return [event.amount for event in outcome.events]


def test_two_yearly_elements_in_the_same_june() -> None:
    """Full 2025 and 2026: EUR 240 EGR + EUR 110 indemnity = EUR 350."""
    assert _amounts(_request(date(2020, 1, 1))) == [Decimal(240), Decimal(110)]


def test_march_hire_counts_the_payment_year() -> None:
    """March 10 through December: 10/12 * EUR 110 = EUR 91.67; no EGR."""
    assert _amounts(_request(date(2026, 3, 10))) == [Decimal("91.67")]


def test_january_hire_has_no_prior_year_egr() -> None:
    """Hired January 1: no 2025 EGR; 12/12 * EUR 110 = EUR 110."""
    assert _amounts(_request(date(2026, 1, 1))) == [Decimal(110)]


def test_known_termination_after_june_limits_payment_year_months() -> None:
    """March through September: 7/12 * EUR 110 = EUR 64.17 in June."""
    assert _amounts(_request(date(2026, 3, 10), ended=date(2026, 9, 30))) == [
        Decimal("64.17")
    ]


def test_premium_closes_both_elements() -> None:
    """With a company result premium the June guarantee is EUR 0, not 350."""
    assert _amounts(_request(date(2020, 1, 1), premium=True)) == []


def test_part_time_and_payment_month_service() -> None:
    """Half-time: 240/2 + 110/2 = EUR 175; no June service: EUR 0."""
    assert _amounts(_request(date(2020, 1, 1), part_time=True)) == [
        Decimal(120),
        Decimal(55),
    ]
    assert _amounts(_request(date(2026, 3, 10), ended=date(2026, 5, 31))) == []


def test_unknown_premium_lists_both_elements() -> None:
    """An unstated premium leaves both the EUR 240 and EUR 110 unpayable."""
    result = equalisation_outcome(
        _request(date(2020, 1, 1), premium=None), _CCNL, RunKind.REGULAR
    )
    assert result.events == ()
    assert result.unknown_codes == (
        "elemento_garanzia_retributiva",
        "indennita_sostitutiva",
    )
