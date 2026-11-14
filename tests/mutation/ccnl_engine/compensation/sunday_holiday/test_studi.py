"""Studi professionali art. 97 C-D: a holiday on a Sunday pays a further quota.

"In caso di coincidenza di una delle festività sopra elencate con una
domenica o altra festività, in aggiunta alla normale retribuzione sarà
corrisposta [...] la retribuzione giornaliera"; 4 November, celebrated on
the first Sunday, takes the same treatment. November 2026: 1 November is a
Sunday and the first Sunday of the month, two quotas of the monthly pay / 26.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import EmploymentPeriod, NoPensionFund, Permanent


def _quotas(month: int) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=Employment(
                ccnl_id="studi-professionali-confprofessioni",
                level_code="3",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2020, 1, 1), None),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(8)),
        )
    )
    return sum(
        (
            i.quantity
            for i in result.pay_items
            if i.item_id.startswith("sunday_holiday")
        ),
        Decimal(0),
    )


def test_ognissanti_and_4_november_on_the_first_sunday() -> None:
    """Two quotas in November 2026, none in October."""
    assert _quotas(11) == Decimal(2)
    assert _quotas(10) == Decimal(0)
