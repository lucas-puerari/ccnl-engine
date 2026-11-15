"""Federmeccanica PAR: the 1979 hour reaches the accrual of a period run."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.inputs import EmploymentPeriod
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId


def _rol(roles: frozenset[str]) -> Decimal:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50), subsector="general"),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="metalmeccanico-federmeccanica",
            level_code="C3",
            opening_state=PeriodState.zero(),
            roles=roles,
            qualifying_shifts=False,
            employment_period=EmploymentPeriod(date(2010, 1, 1)),
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


def test_the_cohort_accrues_8_hours_more() -> None:
    """112 yearly hours for the role, 104 without it."""
    assert _rol(frozenset({"sottosettore_1979"})) - _rol(frozenset()) == Decimal(8)
