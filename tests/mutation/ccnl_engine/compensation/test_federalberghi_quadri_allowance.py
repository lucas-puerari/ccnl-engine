"""Turismo Art. 145: the Quadri allowance is absorbed by individual treatments."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.compensation.individual.inputs import IndividualElement
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WorkerCategory
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


@pytest.mark.parametrize(
    "ccnl_id", ["turismo-federalberghi", "turismo-federalberghi-alberghi-minori"]
)
@pytest.mark.parametrize(
    ("level", "excess", "expected"),
    [("A", None, "75.00"), ("A", "50.00", "25.00"), ("B", "90.00", "0.00")],
)
def test_quadri_allowance_absorbs_individual_treatments(
    ccnl_id: str, level: str, excess: str | None, expected: str
) -> None:
    """'assorbibile fino a concorrenza': A 75 - 50 = 25, B 70 - 90 = 0 (floor)."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                category=WorkerCategory.QUADRO,
                seniority=new_hire(),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
                individual_elements=(
                    (IndividualElement(code="excess", monthly=Decimal(excess)),)
                    if excess is not None
                    else ()
                ),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )
    paid = [i.amount for i in result.pay_items if "IND_FUNZIONE_QUADRI" in i.item_id]
    assert sum(paid, Decimal(0)) == Decimal(expected)
    individual = [i.amount for i in result.pay_items if "excess" in i.item_id]
    assert sum(individual, Decimal(0)) == Decimal(excess or "0")
