"""The Commercio terzo elemento nazionale and the provincial element fact."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_ELEMENT = "TERZO_ELEMENTO_NAZIONALE"


def _run(in_force: bool | None) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=9),
            payment_date=date(2026, 9, 27),
            ccnl_id="commercio-confcommercio",
            level_code="4",
            employer=EmployerProfile(
                headcount=Headcount(50), provincial_pay_element=in_force
            ),
            opening_state=PeriodState.zero(),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _element(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if _ELEMENT in i.item_id), Decimal(0)
    )


def test_no_provincial_element_pays_the_national_one() -> None:
    """Art. 215: 2.07 a month where no provincial third element is in force."""
    result = _run(in_force=False)
    assert _element(result) == Decimal("2.07")
    assert all(i.code != "provincial_pay_element_unknown" for i in result.issues)


@pytest.mark.parametrize("in_force", [True, None], ids=["replaced", "unknown"])
def test_a_provincial_or_unknown_element_leaves_it_out(in_force: bool | None) -> None:
    """Not due where replaced; unknown, left out and named as a missing fact."""
    result = _run(in_force)
    assert _element(result) == 0
    named = [
        i.fact for i in result.issues if i.code == "provincial_pay_element_unknown"
    ]
    assert named == ([] if in_force else ["provincial_pay_element"])
