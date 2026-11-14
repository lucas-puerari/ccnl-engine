"""Distribuzione cooperativa funds: Coopersalute, quadri cover, Previcooper.

Renewal 2024 art. 16: Coopersalute 14 EUR a month by the employer from
January 2025, quadri excluded; testo 2011 art. 58: quadri 1,000 EUR a year
by the employer and 100 by the quadro (a twelfth a month: 83.33 and 8.33);
the 10% INPS solidarity contribution on the employer share.
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


def _funds(level: str, funds: frozenset[str]) -> dict[str, Decimal]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="distribuzione-cooperativa-ancc",
                level_code=level,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2020, 1, 1), None),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(10), contractual_funds=funds),
        )
    )
    return {
        i.item_id.replace("_2026-03-regular", ""): i.amount
        for i in result.pay_items
        if i.item_id.startswith(("coopersalute", "sanitaria_quadri"))
    }


def test_coopersalute_for_a_level_4_worker() -> None:
    """14.00 and its 1.40 solidarity."""
    assert _funds("4", frozenset({"coopersalute", "sanitaria_quadri"})) == {
        "coopersalute_er": Decimal("14.00"),
        "coopersalute_solidarity": Decimal("1.40"),
    }


def test_the_quadro_takes_the_quadri_cover_not_coopersalute() -> None:
    """83.33 by the employer, 8.33 by the quadro, 8.33 of solidarity."""
    assert _funds("Q", frozenset({"coopersalute", "sanitaria_quadri"})) == {
        "sanitaria_quadri_er": Decimal("83.33"),
        "sanitaria_quadri_emp": Decimal("8.33"),
        "sanitaria_quadri_solidarity": Decimal("8.33"),
    }
