"""Exclusive level validity and sourced pre-renewal pay."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.cash.models import TaxCashState
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

_AGREEMENT = "vigilanza-privata-federdat-sf"


def _run(year: int, month: int, level: str = "F") -> Decimal:
    """Return the gross of a regular month for the stated level.

    Returns:
        The calculated gross amount.
    """
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=year, month=month),
            payment_date=date(year, month, 27),
            ccnl_id=_AGREEMENT,
            level_code=level,
            opening_state=PeriodState(cash=TaxCashState()),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    return result.period_gross


def test_march_level_f_month() -> None:
    """March 2026: 865.68 table pay + 0 fixed allowance = 865.68 gross."""
    assert _run(2026, 3) == Decimal("865.68")


@pytest.mark.parametrize("month", [7, 9])
def test_expired_level_must_be_restated(month: int) -> None:
    """July and September F are rejected; the renewed table prints no transition."""
    with pytest.raises(InvalidInputError, match=rf"F.*2026-{month:02d}-01.*restated"):
        _run(2026, month)


def test_last_valid_month() -> None:
    """June 2026 still pays the 865.68 F base plus zero allowances."""
    assert _run(2026, 6) == Decimal("865.68")


def test_other_levels_remain_usable() -> None:
    """September 2026 E remains payable at its printed 1188.57 base."""
    assert _run(2026, 9, "E") == Decimal("1188.57")
