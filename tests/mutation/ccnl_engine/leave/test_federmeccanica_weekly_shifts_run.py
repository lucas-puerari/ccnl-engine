"""Federmeccanica PAR: the weekly shifts reach the accrual of a period run.

A turnista outside the steel sub-sector (general) accrues, in January 2027, the 4 extra
hours of the rotations of 18 weekly shifts or more (renewal of 22 November
2025, Art. 5).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId


def _rol(weekly_shifts: int) -> Decimal:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50), subsector="general"),
            period_id=PeriodId(year=2027, month=1),
            payment_date=date(2027, 1, 27),
            ccnl_id="metalmeccanico-federmeccanica",
            level_code="C3",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            qualifying_shifts=True,
            weekly_shifts=weekly_shifts,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    (rol,) = [
        b
        for b in result.closing_state.accrual.leave.balances
        if b.bucket is LeaveBucket.ROL
    ]
    return rol.accrued_twelfths


def test_eighteen_weekly_shifts_accrue_the_extra_hours() -> None:
    """112 yearly hours on 15 shifts, 116 on 18: a twelfth of 4 more."""
    assert _rol(18) - _rol(15) == Decimal(4)
