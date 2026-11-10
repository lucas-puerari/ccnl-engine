"""C4 first-employment Table C (signed 2025 renewal, PDF p. 11).

For a full-time March 2026 month with no increments: first employment
EUR 1,290.52 versus ordinary C4 EUR 1,512.61, a EUR 222.09 difference.
The caller must check effective service and select ordinary C4 afterward.
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
from ccnl_engine.compensation.entry.transition import transitioned_level
from ccnl_engine.inputs import (
    EmploymentPeriod,
    Permanent,
    SeniorityFact,
    SenioritySource,
)


@pytest.mark.parametrize(
    ("level_code", "expected"),
    [("C4_PRIMO_IMPIEGO", Decimal("1290.52")), ("C4", Decimal("1512.61"))],
)
def test_first_employment_and_regular_c4_monthly_minimum(
    level_code: str, expected: Decimal
) -> None:
    """March 2026: 1290.52 entry vs 1512.61 regular, difference 222.09."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="portieri-fabbricati-confedilizia",
                level_code=level_code,
                seniority=SeniorityFact(0, date(2026, 1, 1), SenioritySource.PAYSLIP),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
        )
    )
    assert (
        sum(
            (
                item.amount
                for item in result.pay_items
                if item.kind == "base_salary_earning"
            ),
            Decimal(0),
        )
        == expected
    )


def test_entry_rate_ends_at_the_last_published_year() -> None:
    """2028 pays 1342.66; no 2029 entry rate was printed, so redirect to C4."""
    agreement = load_ccnl("portieri-fabbricati-confedilizia")
    entry = agreement.level_by_code("C4_PRIMO_IMPIEGO")
    assert entry.base_salary.value_at(date(2027, 3, 1)) == Decimal("1316.33")
    assert entry.base_salary.value_at(date(2028, 3, 1)) == Decimal("1342.66")
    assert (
        transitioned_level(agreement, entry, Permanent(), date(2029, 1, 1), None).code
        == "C4"
    )
