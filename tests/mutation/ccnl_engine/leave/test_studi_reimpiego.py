"""Studi art. 91 c.4: the ROL of the contratto di reimpiego (art. 56).

"i permessi di cui alle lettere A e B saranno maturati nella misura del 50%
a partire dal sesto mese successivo all'assunzione e nella misura del 75% a
partire dal dodicesimo mese dalla data di assunzione fino al diciottesimo
mese; nella misura del 100% per i mesi successivi" (CCNL 16 febbraio 2024,
p. 47).  A hire of 1 August 2025 has 5 months on 31 January 2026.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.inputs import Permanent
from ccnl_engine.inputs import EmploymentPeriod
from ccnl_engine.leave.types import LeaveBucket
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId


def _rol(*, entry_pay: bool) -> Decimal:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(10)),
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 27),
            ccnl_id="studi-professionali-confprofessioni",
            level_code="3",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            employment_period=EmploymentPeriod(date(2025, 8, 1)),
            contract_type=Permanent(entry_pay=entry_pay),
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


@pytest.mark.parametrize(("entry_pay", "hours"), [(True, "20"), (False, "0")])
def test_the_reimpiego_accrues_half_from_the_sixth_month(
    entry_pay: bool, hours: str
) -> None:
    """50% of 40 hours from the sixth month; the c.3 hire ramp has 0 before 12."""
    assert _rol(entry_pay=entry_pay) == Decimal(hours)
