"""The una tantum model and the arrears its installments become."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import pytest
from pydantic import ValidationError

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.una_tantum.models import UnaTantum, UnaTantumInstallment
from ccnl_engine.compensation.una_tantum.rules import _months, una_tantum_events
from ccnl_engine.inputs import EmploymentPeriod, WeeklyHours
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest

_FIAIP = load_ccnl("agenti-immobiliari-fiaip")


def _request(hired: date) -> PeriodCalculationRequest:
    return cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            period_id=PeriodId(year=2025, month=9),
            payment_date=date(2025, 9, 27),
            level_code="IV",
            employment_period=EmploymentPeriod(hired),
            weekly_hours=None,
            full_time_weekly_hours=None,
        ),
    )


def test_a_hire_of_the_year_of_payment_is_taxed_with_the_run() -> None:
    """Hired 1 January 2025: 4 of 16 months, all of 2025, 25.00 ordinary."""
    events, _ = una_tantum_events(_request(date(2025, 1, 1)), _FIAIP, RunKind.REGULAR)
    assert [(e.reference_period, e.amount) for e in events] == [
        (PeriodId(2025, 4), Decimal("25.00"))
    ]


def test_less_than_half_a_covered_month_is_no_month() -> None:
    """Hired 20 April 2025: 11 days of April, no month served, nothing paid."""
    events, met = una_tantum_events(
        _request(date(2025, 4, 20)), _FIAIP, RunKind.REGULAR
    )
    assert (events, met) == ((), True)


def test_fifteen_days_of_a_month_make_a_month() -> None:
    """Hired 16 April 2025: 15 days of April make one month, 6.25."""
    events, _ = una_tantum_events(_request(date(2025, 4, 16)), _FIAIP, RunKind.REGULAR)
    assert [e.amount for e in events] == [Decimal("6.25")]


_PROVENANCE = _FIAIP.parameters.una_tantum[0].provenance


def _una(**fields: Any) -> UnaTantum:  # noqa: ANN401
    values: dict[str, Any] = {
        "code": "UT",
        "covers_from": date(2024, 1, 1),
        "covers_until": date(2024, 12, 31),
        "installments": (
            UnaTantumInstallment(paid_in=date(2025, 3, 1), amounts={"A": Decimal(1)}),
        ),
        "provenance": _PROVENANCE,
        **fields,
    }
    return UnaTantum(**values)


@pytest.mark.parametrize(
    ("paid_in", "amounts", "message"),
    [
        (date(2025, 3, 2), {"A": Decimal(1)}, "first day"),
        (date(2025, 3, 1), {}, "above zero"),
        (date(2025, 3, 1), {"A": Decimal(0)}, "above zero"),
    ],
)
def test_an_installment_is_a_month_and_its_amounts(
    paid_in: date, amounts: dict[str, Decimal], message: str
) -> None:
    """Paid in a month; an amount above zero per level."""
    with pytest.raises(ValidationError, match=message):
        UnaTantumInstallment(paid_in=paid_in, amounts=amounts)


def test_the_vacancy_runs_forward() -> None:
    """Its last day follows its first."""
    with pytest.raises(ValidationError, match="precedes"):
        _una(covers_until=date(2023, 12, 31))


@pytest.mark.parametrize(
    "days",
    [
        (date(2025, 5, 1), date(2025, 3, 1)),
        (date(2025, 3, 1), date(2025, 3, 1)),
        (date(2024, 1, 1),),
    ],
)
def test_installments_follow_the_vacancy_in_order(days: tuple[date, ...]) -> None:
    """Out of order, twice in a month, or on the first day of the vacancy."""
    installments = tuple(
        UnaTantumInstallment(paid_in=d, amounts={"A": Decimal(1)}) for d in days
    )
    with pytest.raises(ValidationError, match="in order"):
        _una(installments=installments)


def test_a_valid_una_tantum_loads() -> None:
    """The default fields make a valid una tantum."""
    assert _una().code == "UT"


def _may_2026(
    hired: date, weekly: int | None = None, full: int | None = None
) -> PeriodCalculationRequest:
    return cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            period_id=PeriodId(year=2026, month=5),
            payment_date=date(2026, 5, 27),
            level_code="IV",
            employment_period=EmploymentPeriod(hired),
            weekly_hours=None if weekly is None else WeeklyHours(Decimal(weekly)),
            full_time_weekly_hours=None if full is None else WeeklyHours(Decimal(full)),
        ),
    )


@pytest.mark.parametrize(
    ("hired", "amount"),
    [
        # 16 October 2024: October has 16 days, every month to April counts.
        (date(2024, 10, 16), "43.75"),
        # 18 October: 14 days of October, six months.
        (date(2024, 10, 18), "37.50"),
    ],
)
def test_the_second_installment_counts_the_months_from_the_hire(
    hired: date, amount: str
) -> None:
    """May 2026 pays the installment of May, after skipping September's."""
    events, _ = una_tantum_events(_may_2026(hired), _FIAIP, RunKind.REGULAR)
    assert [(e.amount, e.event_date) for e in events] == [
        (Decimal(amount), date(2026, 5, 1))
    ]


@pytest.mark.parametrize(("weekly", "full"), [(20, None), (None, 40), (40, 40)])
def test_hours_stated_in_part_are_a_full_time(
    weekly: int | None, full: int | None
) -> None:
    """Weekly or full-time hours alone, or equal, pay the whole."""
    events, _ = una_tantum_events(
        _may_2026(date(2023, 1, 1), weekly, full), _FIAIP, RunKind.REGULAR
    )
    assert [e.amount for e in events] == [Decimal("100.00")]


@pytest.mark.parametrize(
    ("first", "last", "months"),
    [
        (date(2024, 1, 1), date(2024, 3, 10), [(2024, 1), (2024, 2)]),
        (date(2024, 1, 1), date(2024, 3, 15), [(2024, 1), (2024, 2), (2024, 3)]),
        (date(2024, 1, 17), date(2024, 2, 29), [(2024, 1), (2024, 2)]),
        (date(2024, 1, 18), date(2024, 2, 29), [(2024, 2)]),
    ],
)
def test_a_month_counts_from_its_fifteenth_day(
    first: date, last: date, months: list[tuple[int, int]]
) -> None:
    """15 days of a first or last month make a month, 14 do not."""
    assert _months(first, last) == months


_ANAV = load_ccnl("noleggio-autobus-conducente-anav")


def _january_2026(hired: date) -> PeriodCalculationRequest:
    return cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 27),
            level_code="C2",
            employment_period=EmploymentPeriod(hired),
            weekly_hours=None,
            full_time_weekly_hours=None,
        ),
    )


@pytest.mark.parametrize(
    ("hired", "amounts"),
    [
        # Renewal of 23 May 2025: 300.00 at C2 for January 2024 - May 2025.
        (date(2023, 1, 1), ["300.00"]),
        # 16 days of March 2024 are "superiore ai 15 giorni": 15 of 17 months.
        (date(2024, 3, 16), ["264.71"]),
        # 15 days are not: 14 of 17 months.
        (date(2024, 3, 17), ["247.06"]),
        # Not in service on 23 May 2025, the signing.
        (date(2025, 5, 26), []),
    ],
)
def test_anav_pays_the_months_above_fifteen_days_to_the_staff_in_service(
    hired: date, amounts: list[str]
) -> None:
    """The second installment, January 2026, all of earlier years."""
    events, _ = una_tantum_events(_january_2026(hired), _ANAV, RunKind.REGULAR)
    assert [str(e.amount) for e in events] == amounts
    assert all(e.reference_period == PeriodId(2025, 5) for e in events)


def test_an_employment_ended_before_the_signing_is_owed_nothing() -> None:
    """In service until 30 April 2025: not in force on 23 May 2025."""
    request = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(**{
            **vars(_january_2026(date(2023, 1, 1))),
            "employment_period": EmploymentPeriod(date(2023, 1, 1), date(2025, 4, 30)),
        }),
    )
    assert una_tantum_events(request, _ANAV, RunKind.REGULAR) == ((), True)


def test_a_fixed_term_ended_within_the_period_counts_its_months() -> None:
    """FIAIP has no service day: in service to 31 October 2024, 10 of 16."""
    request = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(**{
            **vars(_may_2026(date(2024, 1, 1))),
            "employment_period": EmploymentPeriod(date(2024, 1, 1), date(2024, 10, 31)),
        }),
    )
    events, _ = una_tantum_events(request, _FIAIP, RunKind.REGULAR)
    assert [e.amount for e in events] == [Decimal("62.50")]
