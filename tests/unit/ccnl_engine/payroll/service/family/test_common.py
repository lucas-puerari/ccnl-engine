"""Arithmetic of art. 12 TUIR: truncated ratios, phase-out and proration."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.family import Dependent, DependentRelationship
from ccnl_engine.payroll.service.family.common import phase_out, prorate, truncated

_D = Decimal


@pytest.mark.parametrize(
    ("ratio", "expected"),
    [
        (_D("0.749975"), _D("0.7499")),
        (_D("0.99999999"), _D("0.9999")),
        (_D("0.00009999"), _D("0.0000")),
        (_D("0.5"), _D("0.5000")),
    ],
)
def test_truncated_discards_beyond_four_decimals(
    ratio: Decimal, expected: Decimal
) -> None:
    """Art. 12 c. 4: "si assume nelle prime quattro cifre decimali"."""
    assert truncated(ratio, 4) == expected


@pytest.mark.parametrize(
    ("income", "expected"),
    [
        # (80,000 - 30,001) / 80,000 = 0.6249875 -> 0.6249; 750 x 0.6249
        (_D(30001), _D("468.6750")),
        # ratio exactly zero: not due
        (_D(80000), _D(0)),
        # ratio below zero: not due
        (_D("80000.01"), _D(0)),
        # ratio equal to one (no income): not due
        (_D(0), _D(0)),
    ],
)
def test_phase_out_follows_comma_4(income: Decimal, expected: Decimal) -> None:
    """Zero, negative and unit ratios give nothing; others are truncated."""
    assert phase_out(_D(750), _D(80000), _D(80000), income, 4) == expected


_CHILD = Dependent(
    DependentRelationship.CHILD,
    birth_date=date(2004, 1, 1),
    own_income=_D(0),
    allocation_pct=_D(50),
    residency_eligibility=True,
    dependent_from=None,
    dependent_until=None,
)


def test_prorate_rounds_once_after_months_and_share() -> None:
    """710 x 7 / 12 x 50% = 207.0833... -> 207.08."""
    deduction = prorate(_CHILD, 7, _D(710))
    assert deduction.amount == _D("207.08")
    assert deduction.months == 7
    assert deduction.annual == _D(710)
    assert deduction.missing_facts == ()


def test_prorate_zero_months_is_zero() -> None:
    """A dependent never entitled in the year has no deduction."""
    unknown = replace(_CHILD, own_income=None)
    deduction = prorate(unknown, 0, _D(950))
    assert deduction.amount == _D(0)
    assert deduction.missing_facts == ()


def test_prorate_with_an_unknown_condition_grants_nothing() -> None:
    """A dependant that may qualify with an unknown condition names it."""
    unknown = replace(_CHILD, own_income=None, allocation_pct=None)
    deduction = prorate(unknown, 12, _D(950))
    assert deduction.amount == _D(0)
    assert deduction.missing_facts == ("own_income", "allocation_pct")
