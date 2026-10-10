"""Apprentice rates resolved for a headcount, with the wage-integration shares."""

from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.tax.contribution.models_tier import ApprenticeRawRates
from ccnl_engine.tax.contribution.rules_tier import _resolve_apprentice

_RAW: dict[str, Any] = {
    "employee_rate": "0.0584",
    "employee_ivs_rate": "0.0584",
    "employer_rate": "0.1161",
    "employer_ivs_rate": "0.1000",
    "small_firm_max_employees": 9,
    "small_firm_employer_rate_months_0_11": "0.0311",
    "small_firm_employer_ivs_rate_months_0_11": "0.0150",
    "small_firm_employer_rate_months_12_23": "0.0461",
    "small_firm_employer_ivs_rate_months_12_23": "0.0300",
}
#: CIGO 1.70% up to 50, 2.00% above; CIGS 0.60% / 0.30% above 15.
_INDUSTRIA_SHARES: list[dict[str, Any]] = [
    {"max_employees": 15, "employer_rate": "0.0170", "employee_rate": "0"},
    {"max_employees": 50, "employer_rate": "0.0230", "employee_rate": "0.0030"},
    {"max_employees": None, "employer_rate": "0.0260", "employee_rate": "0.0030"},
]


def _raw(shares: list[dict[str, Any]]) -> ApprenticeRawRates:
    return ApprenticeRawRates.model_validate({**_RAW, "headcount_shares": shares})


def test_without_shares_the_statutory_rates_apply() -> None:
    """A sector with no share keeps 11.61% and 5.84%."""
    rates = _resolve_apprentice(_raw([]), 20)
    assert rates.employer_rate_months_0_11 == Decimal("0.1161")
    assert rates.employer_rate_after == Decimal("0.1161")
    assert rates.employee_rate == Decimal("0.0584")


@pytest.mark.parametrize(
    ("headcount", "first", "second", "after", "employee"),
    [
        (9, "0.0481", "0.0631", "0.1331", "0.0584"),
        (15, "0.1331", "0.1331", "0.1331", "0.0584"),
        (16, "0.1391", "0.1391", "0.1391", "0.0614"),
        (51, "0.1421", "0.1421", "0.1421", "0.0614"),
    ],
)
def test_the_share_of_the_headcount_is_added_to_every_period(
    headcount: int, first: str, second: str, after: str, employee: str
) -> None:
    """The share rides on the reduced small-firm years too; IVS is unchanged."""
    rates = _resolve_apprentice(_raw(_INDUSTRIA_SHARES), headcount)
    assert rates.employer_rate_months_0_11 == Decimal(first)
    assert rates.employer_rate_months_12_23 == Decimal(second)
    assert rates.employer_rate_after == Decimal(after)
    assert rates.employee_rate == Decimal(employee)
    assert rates.employee_ivs_rate == Decimal("0.0584")
    assert rates.employer_ivs_rate_after == Decimal("0.1000")


def test_shares_without_an_open_tier_raise() -> None:
    """A share list must close with an open tier, like the INPS tiers."""
    with pytest.raises(DataIntegrityError, match="exactly one open tier"):
        _resolve_apprentice(_raw(_INDUSTRIA_SHARES[:2]), 10)
