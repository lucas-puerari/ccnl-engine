"""Agrifondo of the operai agricoli e florovivaisti.

Accordo istitutivo (Allegato n. 15 of the CCNL 2022-2025, PDF p. 152): 1% of
the TFR base from the employer and at least 1% from the worker.  Area2,
March 2026: 1% of 1,341.61 is 13.42 each.
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
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import EmploymentPeriod, Permanent
from ccnl_engine.pension_fund.inputs import PensionFundEnrolment
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


def test_agrifondo_takes_one_percent_each() -> None:
    """Employer 13.42 and worker 13.42 on a TFR base of 1,341.61."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="operai-agricoli-florovivaisti",
                level_code="Area2",
                seniority=new_hire(2023),
                roles=frozenset(),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2023, 3, 1)),
                category=WorkerCategory.OPERAIO,
                pension_fund=PensionFundEnrolment(
                    fund_code="AGRIFONDO",
                    employee_rate=Decimal("0.01"),
                    tfr_to_fund=False,
                ),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )
    (decision,) = (
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    )
    assert decision.inputs["base"] == Decimal("1341.61")
    assert (decision.inputs["employer"], decision.inputs["employee"]) == (
        Decimal("13.42"),
        Decimal("13.42"),
    )
