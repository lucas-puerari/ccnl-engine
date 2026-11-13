"""Vigilanza FEDERDAT (HV51) arts. 21 and 64: EBILAV and its health fund."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from tests.mutation.ccnl_engine.sickness.test_handlers import _req


def _items(
    funds: frozenset[str],
    slug: str = "vigilanza-privata-federdat-sf",
    level: str = "D",
) -> dict[str, Decimal]:
    request = _req(11, slug=slug, level=level, category=WorkerCategory.IMPIEGATO)
    request = replace(
        request,
        employer=EmployerProfile(headcount=Headcount(50), contractual_funds=funds),
    )
    result = calculate_period(
        request, repo=bundled_repository(), resolver=bundled_policies()
    )
    totals: dict[str, Decimal] = {}
    for item in result.pay_items:
        if "ebilav" in item.item_id:
            key = item.item_id.split("_2026")[0]
            totals[key] = totals.get(key, Decimal(0)) + item.amount
    return totals


def test_paid_funds_charge_their_shares() -> None:
    """Level D, Nov 2026, 1281.43: EBILAV 2.56 + 1.28, health 12 + 1.20 solidarity."""
    assert _items(frozenset({"ebilav", "ebilav_sanitario"})) == {
        "ebilav": Decimal("3.84"),
        "ebilav_sanitario": Decimal("13.20"),
    }


@pytest.mark.parametrize("funds", [frozenset()])
def test_unpaid_funds_owe_the_elements(funds: frozenset[str]) -> None:
    """An employer that pays neither owes 25 and 15 EUR to the worker."""
    assert _items(funds) == {
        "ebilav_element": Decimal("25.00"),
        "ebilav_sanitario_element": Decimal("15.00"),
    }


def test_the_guards_file_charges_the_same_funds() -> None:
    """GPG level IV, Nov 2026: EBILAV 2.94 + 1.47, health 12 + 1.20 solidarity."""
    funds = frozenset({"ebilav", "ebilav_sanitario"})
    assert _items(funds, "vigilanza-privata-federdat-gpg", "IV") == {
        "ebilav": Decimal("4.41"),
        "ebilav_sanitario": Decimal("13.20"),
    }
