"""Fasce stipendiali of the scuola staff (CCNL Istruzione e Ricerca).

CCNL 2025-2027 Tabella A2, from 1 January 2026, annual tabellare over 12:
docente dell'infanzia, fascia 0-8 23,343.16 (1,945.26 a month), 9-14
25,813.27 (2,151.11), 15-20 27,979.87 (2,331.66); docente laureato di II
grado, 0-8 25,267.04 (2,105.59), 9-14 28,866.69 (2,405.56).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

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
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource


def _seniority(level: str, months: int) -> Decimal:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="istruzione-ricerca-aran",
            level_code=level,
            seniority=SeniorityFact(months, date(2026, 3, 1), SenioritySource.PAYSLIP),
            opening_state=PeriodState.zero(),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    return sum(
        (i.amount for i in result.pay_items if i.kind == "seniority_earning"),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("level", "months", "amount"),
    [
        ("DOCENTE_INFANZIA_PRIMARIA", 100, "0"),  # 0-8
        ("DOCENTE_INFANZIA_PRIMARIA", 110, "205.85"),  # 9-14: 2151.11 - 1945.26
        ("DOCENTE_INFANZIA_PRIMARIA", 192, "386.40"),  # 15-20: 2331.66 - 1945.26
        ("DOCENTE_LAUREATO_SECONDARIA_II", 110, "299.97"),  # 2405.56 - 2105.59
    ],
    ids=["first", "second", "third", "laureato"],
)
def test_the_fascia_of_the_service(level: str, months: int, amount: str) -> None:
    """The steps add up to the tabellare of the worker's fascia."""
    assert _seniority(level, months) == Decimal(amount)
