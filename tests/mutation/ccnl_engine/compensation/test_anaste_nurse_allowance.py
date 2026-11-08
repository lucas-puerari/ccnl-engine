"""ANASTE Art. 70(2): monthly nurse allowance offsets individual excess."""

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
from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.compensation.individual.inputs import IndividualElement
from ccnl_engine.compensation.individual.rules import _offset_allowance
from ccnl_engine.compensation.models import Allowance
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WorkerCategory
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


@pytest.mark.parametrize(
    ("excess", "expected"),
    [(None, "155.00"), ("60.00", "95.00"), ("200.00", "0.00")],
)
def test_nurse_allowance_absorbs_individual_excess(
    excess: str | None, expected: str
) -> None:
    """At level 6: 155 - min(155, 0/60/200) = 155/95/0 EUR."""
    engine = PayrollEngine.bundled()

    def items(roles: frozenset[str]) -> tuple[list[Decimal], list[Decimal]]:
        result = engine.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(year=2026, month=1),
                payment_date=date(2026, 1, 27),
                employment=Employment(
                    ccnl_id="istituzioni-servizi-socio-assistenziali-anaste",
                    level_code="6",
                    category=WorkerCategory.IMPIEGATO,
                    seniority=new_hire(),
                    roles=roles,
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
        return (
            [
                i.amount
                for i in result.pay_items
                if "INDENNITA_PROFESSIONALE_INFERMIERI" in i.item_id
            ],
            [i.amount for i in result.pay_items if "excess" in i.item_id],
        )

    allowance, individual = items(frozenset({"infermiere"}))
    assert sum(allowance, Decimal(0)) == Decimal(expected)
    assert sum(individual, Decimal(0)) == Decimal(excess or "0")
    assert items(frozenset())[0] == []


def test_offset_outside_allowance_validity_keeps_original_series() -> None:
    """Before the EUR 155 allowance starts, no offset creates a payment."""
    allowance = Allowance(
        code="nurse",
        description="Nurse allowance",
        monthly=TimeSeries(
            periods=(
                ValidityPeriod(
                    valid_from=date(2023, 1, 1), valid_until=None, value=Decimal(155)
                ),
            )
        ),
    )
    assert _offset_allowance(allowance, Decimal(60), date(2022, 12, 1)) is allowance
