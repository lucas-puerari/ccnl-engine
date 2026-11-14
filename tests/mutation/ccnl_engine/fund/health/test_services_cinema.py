"""Cinema audiovisivi funds: Asfor Cinema and Salute Sempre (CCNL 23 July 2025).

Art. 70 (p. 41): Asfor Cinema "con un contributo dello 0,2% del minimo
tabellare per ciascun dipendente e per ogni mese solare". Allegato n. 1
(p. 56): Salute Sempre "euro 10 mensili (euro 120 annuali)" for the
permanent workers, with the 10% INPS solidarity contribution. Level 4,
December 2026, minimo 1800.32: 3.60, 10.00 and 1.00; none on the 13th.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import EmploymentPeriod, NoPensionFund, Permanent


def _funds(run: PayrollRun) -> dict[str, Decimal]:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(2026, 12, 18),
            employment=Employment(
                ccnl_id="cinema-audiovisivi-industria",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2020, 1, 1), None),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(20),
                contractual_funds=frozenset({"asfor_cinema", "salute_sempre"}),
            ),
        )
    )
    return {
        i.item_id.split("_2026")[0] + i.item_id.rsplit("_", 1)[1]: i.amount
        for i in result.pay_items
        if i.item_id.startswith(("asfor", "salute"))
    }


def test_the_funds_of_a_regular_month() -> None:
    """0.2% of the minimo, 10 EUR and its 10% solidarity."""
    assert _funds(PayrollRun.regular(2026, 12)) == {
        "asfor_cinemaer": Decimal("3.60"),
        "salute_sempreer": Decimal("10.00"),
        "salute_sempresolidarity": Decimal("1.00"),
    }


@pytest.mark.parametrize("run", [PayrollRun.thirteenth(2026, 12)])
def test_no_fund_on_the_thirteenth(run: PayrollRun) -> None:
    """'per ogni mese solare' and '120 annuali': twelve payments."""
    assert _funds(run) == {}
