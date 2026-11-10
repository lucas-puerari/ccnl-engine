"""Hand oracle: June 2026 enrolled pension fund on frozen 2001 bases.

Level 2: 893.30 * 1% = 8.93 EUR each; level 5: 976.53 * 1% =
9.77 EUR each, irrespective of the current salary. Twelve payments only.
"""

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
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import (
    EmploymentPeriod,
    PensionFundEnrolment,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.pension_fund.models import ComplementaryPensionRules
from ccnl_engine.pension_fund.rules import resolve_terms
from ccnl_engine.results import AccountKind

_HIRED = date(2025, 1, 1)


@pytest.mark.parametrize(
    ("level", "fund", "base", "each"),
    [("2", "PREVIAMBIENTE", "893.30", "8.93"), ("5", "FONDAPI", "976.53", "9.77")],
)
def test_frozen_monthly_base(level: str, fund: str, base: str, each: str) -> None:
    """Each side owes 1% of the printed 2001 base, not of current pay."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="multiservizi-anip",
                level_code=level,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=PensionFundEnrolment(
                    fund_code=fund,
                    employee_rate=Decimal("0.01"),
                    tfr_to_fund=False,
                ),
            ),
            employer=EmployerProfile(headcount=Headcount(30)),
        )
    )
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    assert decision.inputs["base"] == Decimal(base)
    assert sum(
        e.amount
        for e in result.ledger_entries
        if e.account is AccountKind.PENSION_FUND_EMPLOYER
    ) == Decimal(each)
    assert sum(
        e.amount
        for e in result.ledger_entries
        if e.account is AccountKind.PENSION_FUND_EMPLOYEE
    ) == Decimal(each)


def test_missing_historical_level_base_rejected() -> None:
    """A fund cannot silently substitute current pay for an unlisted level."""
    with pytest.raises(InvalidInputError, match="lacks a fixed base"):
        resolve_terms(
            load_ccnl("multiservizi-anip"),
            PensionFundEnrolment("PREVIAMBIENTE", Decimal("0.01"), False),
            None,
            date(2026, 6, 1),
            ComplementaryPensionRules(
                deduction_cap=Decimal("5300.00"), solidarity_rate=Decimal("0.10")
            ),
            apprentice=False,
            level_code="unlisted",
        )
