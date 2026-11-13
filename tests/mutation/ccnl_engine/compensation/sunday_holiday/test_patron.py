"""Logistica Confetra art. 60 c. 2: the patron saint holiday on a Saturday."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.sunday_holiday.coincidence import patron_day
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from tests.mutation.ccnl_engine.sickness.test_handlers import _req


def _sunday_holiday(patron: str | None) -> Decimal:
    request = _req(
        9,
        slug="logistica-trasporto-confetra",
        level="3",
        category=WorkerCategory.IMPIEGATO,
    )
    request = replace(
        request,
        employer=EmployerProfile(headcount=Headcount(50), patron_saint_day=patron),
    )
    result = calculate_period(
        request, repo=bundled_repository(), resolver=bundled_policies()
    )
    return sum(
        (i.amount for i in result.pay_items if "sunday_holiday" in i.item_id),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("patron", "paid"),
    [("09-19", True), ("09-18", False), (None, False)],
    ids=["saturday", "friday", "not-stated"],
)
def test_the_patron_on_a_saturday_is_paid_a_further_day(
    patron: str | None, *, paid: bool
) -> None:
    """19 September 2026 is a Saturday: 1/22 of the level 3 pay, 88.49."""
    assert _sunday_holiday(patron) == (Decimal("88.49") if paid else Decimal(0))


@pytest.mark.parametrize(
    ("patron", "expected"),
    [
        ("09-20", date(2026, 9, 20)),
        ("09-19", date(2026, 9, 19)),
        ("08-15", date(2026, 8, 15)),
        ("09-18", None),
    ],
    ids=["sunday", "saturday", "on-another-holiday", "weekday"],
)
def test_patron_day_triggers(patron: str, expected: date | None) -> None:
    """The rest day, a Saturday or another holiday; not a plain weekday."""
    clause = load_ccnl("logistica-trasporto-confetra").work_rules
    assert clause is not None
    holidays = BundledKnowledgeRepository().load_national_holidays().holidays
    dated = [(h, h.on(2026)) for h in holidays]
    got = patron_day(clause.sunday_holidays, patron, 2026, dated, rest_day=6)
    assert got == expected
