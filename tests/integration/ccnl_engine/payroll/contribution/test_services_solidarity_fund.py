"""Solidarity fund of the CCNL, through the period calculation.

Bancari ABI: Fondo di solidarietà del credito, 0.133% employer and 0.067%
worker (INPS circ. 90/2015 p. 11).  BCC: 0.36%, two thirds to the employer
(INPS bilancio preventivo 2026, cap. 32, p. 7).  A fixed-term worker owes
none.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.contribution.services_solidarity_fund import (
    EMPLOYEE_COMPONENT,
    EMPLOYER_COMPONENT,
)
from ccnl_engine.payroll.employment.inputs import FixedTerm
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.results import PeriodResult


def _run(ccnl: str, **kwargs: object) -> PeriodResult:
    level = next(iter(_LEVELS[ccnl]))
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug=ccnl,
            level_code=level,
            employer=EmployerProfile(headcount=Headcount(50)),
            opening_state=PeriodState.zero(),
            tfr_treasury_fund=False,
            **kwargs,  # type: ignore[arg-type]
        )
    )


_LEVELS = {
    "bancari-abi.json": ("QD1",),
    "bcc-credito-cooperativo.json": ("QD1",),
}


def _fund(result: PeriodResult) -> dict[str, tuple[Decimal, Decimal]]:
    return {
        c.name: (c.rate, c.amount)
        for c in result.contribution_breakdown.components
        if c.name in {EMPLOYEE_COMPONENT, EMPLOYER_COMPONENT}
    }


@pytest.mark.parametrize(
    ("ccnl", "employer", "employee"),
    [
        ("bancari-abi.json", Decimal("0.00133"), Decimal("0.00067")),
        ("bcc-credito-cooperativo.json", Decimal("0.0024"), Decimal("0.0012")),
    ],
)
def test_permanent_worker_pays_the_fund_of_the_ccnl(
    ccnl: str, employer: Decimal, employee: Decimal
) -> None:
    """Each CCNL charges the rates of its own fund."""
    rates = {name: rate for name, (rate, _) in _fund(_run(ccnl)).items()}
    assert rates == {EMPLOYER_COMPONENT: employer, EMPLOYEE_COMPONENT: employee}


def test_fixed_term_worker_pays_no_fund() -> None:
    """The fund charges permanent contracts only."""
    result = _run("bancari-abi.json", contract_type=FixedTerm())
    assert _fund(result) == {}
