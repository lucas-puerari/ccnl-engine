"""The provincial wage of an OTD in its terzo elemento.

Operai agricoli Area2, March 2026, 100 hours: the contratto provinciale pays
169.00 a month above the minimo, stated as a territorial element.  Art. 50:
the terzo elemento of 30.44% is on the salario contrattuale of the contratto
provinciale, so the 100.00 of the element on the hours adds 30.44 to it.
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
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.compensation.second_level.inputs import (
    SecondLevelAgreement,
    SecondLevelElement,
)
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    FixedTerm,
    WeeklyHours,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def _terzo(agreement: SecondLevelAgreement | None) -> Decimal:
    elements = (
        ()
        if agreement is None
        else (
            SecondLevelElement(
                code="cpl",
                monthly=Decimal("169.00"),
                agreement=agreement,
                valid_from=date(2025, 1, 1),
            ),
        )
    )
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="operai-agricoli-florovivaisti",
                level_code="Area2",
                seniority=new_hire(2025),
                roles=frozenset(),
                contract_type=FixedTerm(renewals=0),
                employment_period=EmploymentPeriod(date(2025, 3, 1)),
                weekly_hours=WeeklyHours(Decimal(39)),
                full_time_weekly_hours=WeeklyHours(Decimal(39)),
                category=WorkerCategory.OPERAIO,
            ),
            employer=EmployerProfile(
                headcount=Headcount(20), second_level_elements=elements
            ),
            facts=PeriodFacts(
                regione="IT-25",
                comune_belfiore="A005",
                ordinary_hours_worked=ContributableHours(Decimal(100)),
            ),
        )
    )
    (item,) = (i for i in result.pay_items if i.kind == "hourly_percentage_earning")
    return item.amount


def test_the_territorial_element_joins_the_terzo_elemento() -> None:
    """239.60 on the minimo; 239.60 + 30.44 with the provincial wage."""
    assert _terzo(None) == Decimal("239.60")
    assert _terzo(SecondLevelAgreement.TERRITORIAL) == Decimal("270.04")


def test_a_company_element_stays_out() -> None:
    """A company element is not the salario of the contratto provinciale."""
    assert _terzo(SecondLevelAgreement.COMPANY) == Decimal("239.60")
