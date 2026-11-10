"""Tables A, A-bis, A-ter and A-quater, signed renewal PDF pp. 2, 4, 6, 8.

A1's full-time March 2026 monthly conglobated salary is EUR 1,240.42:
one complete monthly base of 1,240.42, with no seniority or allowances.
Before these levels were available no A1 monthly amount could be calculated.
Hourly rates and accommodation-dependent pay are deliberately not asserted.
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
from ccnl_engine.inputs import (
    EmploymentPeriod,
    Permanent,
    SeniorityFact,
    SenioritySource,
)


@pytest.mark.parametrize(
    ("code", "values"),
    [
        ("A1", ("1240.42", "1265.23", "1290.53")),
        ("A2", ("1240.42", "1265.23", "1290.53")),
        ("A3", ("1359.32", "1386.50", "1414.23")),
        ("A4", ("1359.32", "1386.50", "1414.23")),
        ("A5", ("1240.42", "1265.23", "1290.53")),
        ("A6", ("1299.79", "1325.78", "1352.29")),
        ("A7", ("1299.79", "1325.78", "1352.29")),
        ("A8", ("1361.48", "1388.71", "1416.48")),
        ("A9", ("1361.48", "1388.71", "1416.48")),
    ],
)
def test_a_profile_printed_monthly_minimums(
    code: str, values: tuple[str, str, str]
) -> None:
    """Each year's full-time monthly salary matches its printed Table A row."""
    level = load_ccnl("portieri-fabbricati-confedilizia").level_by_code(code)
    assert [level.base_salary.value_at(date(y, 3, 1)) for y in range(2026, 2029)] == [
        Decimal(v) for v in values
    ]


@pytest.mark.parametrize("code", [f"A{i}" for i in range(1, 10)])
def test_a_profile_post_2004_seniority_increment(code: str) -> None:
    """Art. 125: one post-2004 triennium adds EUR 10.00 each month."""
    agreement = load_ccnl("portieri-fabbricati-confedilizia")
    assert agreement.parameters.seniority_increments.amount_by_level[code].value_at(
        date(2026, 3, 1)
    ) == Decimal("10.00")


def test_a1_hand_computed_full_month() -> None:
    """March 2026 A1: 1 x 1240.42 monthly base = EUR 1240.42."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="portieri-fabbricati-confedilizia",
                level_code="A1",
                seniority=SeniorityFact(0, date(2026, 1, 1), SenioritySource.PAYSLIP),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
        )
    )
    assert sum(
        (
            item.amount
            for item in result.pay_items
            if item.kind == "base_salary_earning"
        ),
        Decimal(0),
    ) == Decimal("1240.42")
