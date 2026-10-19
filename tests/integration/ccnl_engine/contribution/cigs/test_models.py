"""CIGS of the craft firms of an indotto: D.Lgs. 148/2015 artt. 20 and 23.

A craft firm of more than fifteen employees in the indotto of a firm with the
prevailing management influence pays 0.90%: 0.60% employer, 0.30% worker.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import calculate_period
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult


def _run(headcount: int, indotto: bool | None) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(headcount), cigs_indotto=indotto
            ),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="metalmeccanico-artigianato",
            level_code="3",
            opening_state=PeriodState.zero(),
        )
    )


def _account(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account), Decimal(0)
    )


def test_an_indotto_firm_pays_the_cigs() -> None:
    """0.30% more for the worker, 0.60% more for the employer."""
    out, inside = _run(20, False), _run(20, True)
    base = out.contribution_breakdown.components[0].base

    worker = _account(inside, AccountKind.EMPLOYEE_CONTRIBUTIONS) - _account(
        out, AccountKind.EMPLOYEE_CONTRIBUTIONS
    )
    employer = _account(inside, AccountKind.EMPLOYER_CONTRIBUTIONS) - _account(
        out, AccountKind.EMPLOYER_CONTRIBUTIONS
    )
    assert abs(worker - base * Decimal("0.003")) <= Decimal("0.02")
    assert abs(employer - base * Decimal("0.006")) <= Decimal("0.02")


@pytest.mark.parametrize(("headcount", "indotto"), [(15, True), (20, False)])
def test_no_cigs_at_15_employees_or_outside_an_indotto(
    headcount: int, indotto: bool
) -> None:
    """At fifteen employees or outside an indotto nothing changes."""
    assert _account(
        _run(headcount, indotto), AccountKind.EMPLOYEE_CONTRIBUTIONS
    ) == _account(
        _run(headcount, None if headcount > 15 else False),
        AccountKind.EMPLOYEE_CONTRIBUTIONS,
    )


def test_an_unstated_indotto_is_reported() -> None:
    """Above fifteen employees the unknown fact raises an issue."""
    codes = {i.code for i in _run(20, None).issues}
    assert "cigs_indotto_unknown" in codes
    assert "cigs_indotto_unknown" not in {i.code for i in _run(15, None).issues}
