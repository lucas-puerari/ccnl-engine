"""The elemento perequativo a run pays, by run, service and employer fact."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import pytest
from pydantic import ValidationError

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.equalisation.models import EqualisationElement
from ccnl_engine.compensation.equalisation.rules import equalisation_outcome
from ccnl_engine.compensation.individual.inputs import IndividualElement
from ccnl_engine.compensation.second_level.inputs import (
    SecondLevelAgreement,
    SecondLevelElement,
)
from ccnl_engine.inputs import EmploymentPeriod, WeeklyHours
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest

_CONFAPI = load_ccnl("metalmeccanico-confapi")
_ELEMENT = _CONFAPI.parameters.equalisation_element


def _request(
    hired: date | None = date(2020, 1, 1),
    *,
    month: int = 6,
    ended: date | None = None,
    premium: bool | None = False,
    individual: tuple[IndividualElement, ...] = (),
    company: tuple[SecondLevelElement, ...] = (),
    hours: tuple[int, int] | None = None,
) -> PeriodCalculationRequest:
    period = None if hired is None else EmploymentPeriod(hired, ended)
    weekly = full = None
    if hours is not None:
        weekly, full = (WeeklyHours(Decimal(h)) for h in hours)
    return cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            period_id=PeriodId(year=2026, month=month),
            level_code="5",
            employment_period=period,
            individual_elements=individual,
            weekly_hours=weekly,
            full_time_weekly_hours=full,
            employer=SimpleNamespace(
                second_level_premium=premium, second_level_elements=company
            ),
        ),
    )


def _paid(
    request: PeriodCalculationRequest, kind: RunKind = RunKind.REGULAR
) -> list[tuple[date, Decimal, str]]:
    outcome = equalisation_outcome(request, _CONFAPI, kind)
    return [(e.event_date, e.amount, e.kind) for e in outcome.events]


def test_a_full_year_is_paid_in_june_as_an_ordinary_bonus() -> None:
    """Art. 48: 485 with the June pay, an ordinary bonus out of the TFR."""
    assert _paid(_request()) == [(date(2026, 6, 1), Decimal("485.00"), "bonus")]


@pytest.mark.parametrize("month", [5, 7])
def test_another_regular_month_pays_nothing(month: int) -> None:
    """Only the regular run of June pays it."""
    assert _paid(_request(month=month)) == []


@pytest.mark.parametrize(
    ("kind", "month", "expected"),
    [
        (RunKind.TERMINATION, 3, [Decimal("485.00")]),
        (RunKind.TERMINATION, 6, []),
        (RunKind.THIRTEENTH, 6, []),
    ],
    ids=["termination-before-june", "termination-in-june", "extra-month"],
)
def test_a_termination_before_june_pays_it_with_the_settlement(
    kind: RunKind, month: int, expected: list[Decimal]
) -> None:
    """Paid 'all'atto della liquidazione', never twice, never on an extra month."""
    request = _request(month=month, ended=date(2026, month, 10))
    assert [amount for _, amount, _ in _paid(request, kind)] == expected


@pytest.mark.parametrize(
    ("hired", "amount"),
    [
        (date(2025, 3, 10), "404.17"),
        (date(2025, 3, 16), "404.17"),
        (date(2025, 3, 17), "363.75"),
        (date(2025, 12, 20), None),
        (date(2026, 1, 1), None),
        (date(2026, 1, 2), None),
        (None, None),
    ],
    ids=[
        "16-days",
        "exactly-16",
        "15-days",
        "december",
        "1-january",
        "2026",
        "unknown",
    ],
)
def test_the_months_of_the_year_before_over_twelve(
    hired: date | None, amount: str | None
) -> None:
    """A month with more than 15 days counts; in service on 1 January only."""
    expected = [] if amount is None else [Decimal(amount)]
    assert [a for _, a, _ in _paid(_request(hired))] == expected


def test_an_employment_ended_before_january_is_owed_nothing() -> None:
    """Not in service on 1 January of the year."""
    assert _paid(_request(ended=date(2025, 12, 31))) == []


def test_a_part_timer_is_paid_the_whole_amount() -> None:
    """The text prorates by the duration only, not by the hours."""
    assert [a for _, a, _ in _paid(_request(hours=(20, 40)))] == [Decimal("485.00")]


@pytest.mark.parametrize(
    ("monthly", "hours", "amount"),
    [("30", None, "125.00"), ("15", (20, 40), "395.00"), ("50", None, None)],
    ids=["below", "part-time", "absorbed"],
)
def test_the_pay_above_the_ccnl_reduces_it(
    monthly: str, hours: tuple[int, int] | None, amount: str | None
) -> None:
    """'Una cifra inferiore fino a concorrenza': 485 less 12 months of it."""
    element = IndividualElement("superminimo", Decimal(monthly))
    request = _request(individual=(element,), hours=hours)
    expected = [] if amount is None else [Decimal(amount)]
    assert [a for _, a, _ in _paid(request)] == expected


def _company(valid_from: date, valid_until: date | None = None) -> SecondLevelElement:
    return SecondLevelElement(
        "premio",
        Decimal(10),
        SecondLevelAgreement.COMPANY,
        valid_from=valid_from,
        valid_until=valid_until,
    )


@pytest.mark.parametrize(
    ("company", "owed"),
    [
        (None, False),
        (_company(date(2020, 1, 1)), False),
        (_company(date(2025, 12, 31)), False),
        (_company(date(2020, 1, 1), date(2025, 1, 1)), False),
        (_company(date(2026, 1, 1)), True),
        (_company(date(2020, 1, 1), date(2024, 12, 31)), True),
    ],
    ids=["flag", "open", "from-31-dec", "until-1-jan", "next-year", "ended-before"],
)
def test_second_level_bargaining_of_the_year_before_closes_it(
    company: SecondLevelElement | None, *, owed: bool
) -> None:
    """The flag true, or a company element in force in the year before."""
    if company is None:
        request = _request(premium=True)
    else:
        request = _request(company=(company,))
    assert bool(_paid(request)) is owed


@pytest.mark.parametrize(("monthly", "amount"), [("40", "485.00"), ("70", "245.00")])
def test_a_superminimo_counts_at_its_amount_on_31_december(
    monthly: str, amount: str
) -> None:
    """Level 5: the minimo rose by 50 from June 2024 to 31 December 2025."""
    element = IndividualElement(
        "superminimo", Decimal(monthly), absorbable=True, as_of=date(2024, 6, 1)
    )
    request = _request(individual=(element,))
    assert [a for _, a, _ in _paid(request)] == [Decimal(amount)]


def test_an_unstated_firm_owes_nothing_to_an_absorbed_worker() -> None:
    """A superminimo above the element: no amount, so no missing fact."""
    element = IndividualElement("superminimo", Decimal(50))
    request = _request(premium=None, individual=(element,))
    outcome = equalisation_outcome(request, _CONFAPI, RunKind.REGULAR)
    assert (outcome.events, outcome.unknown) == ((), None)


def test_an_unstated_firm_leaves_it_out_and_names_it() -> None:
    """The run pays nothing and names the element left out."""
    outcome = equalisation_outcome(_request(premium=None), _CONFAPI, RunKind.REGULAR)
    assert (outcome.events, outcome.unknown) == ((), "elemento_perequativo")


def test_an_unstated_firm_names_nothing_when_nothing_is_owed() -> None:
    """A worker hired this year is owed nothing whatever the firm."""
    outcome = equalisation_outcome(
        _request(date(2026, 2, 1), premium=None), _CONFAPI, RunKind.REGULAR
    )
    assert outcome.unknown is None


def test_a_ccnl_without_the_element_pays_nothing() -> None:
    """No element in the CCNL data."""
    ccnl = load_ccnl("agenti-immobiliari-fiaip")
    assert equalisation_outcome(_request(), ccnl, RunKind.REGULAR).events == ()


def _element(**fields: Any) -> EqualisationElement:  # noqa: ANN401
    assert _ELEMENT is not None
    values: dict[str, Any] = {
        "code": "EP",
        "yearly": Decimal(485),
        "paid_in_month": 6,
        "provenance": _ELEMENT.provenance,
        **fields,
    }
    return EqualisationElement(**values)


@pytest.mark.parametrize(
    "fields",
    [
        {"yearly": Decimal(0)},
        {"paid_in_month": 13},
        {"paid_in_month": 0},
        {"month_min_days": 0},
        {"code": ""},
    ],
)
def test_the_element_rejects_invalid_values(fields: dict[str, Any]) -> None:
    """An amount above zero, a month of the year, a positive day count."""
    with pytest.raises(ValidationError):
        _element(**fields)


def test_the_month_threshold_defaults_to_more_than_fifteen_days() -> None:
    """'La frazione di mese superiore a 15 giorni': 16."""
    assert _element().month_min_days == 16
