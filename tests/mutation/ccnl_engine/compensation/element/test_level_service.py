"""Level-tenure allowances use the level date, not the worker's career."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import Employment, PeriodResult
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import BlockerCode
from tests.knowledge.ccnl_engine.support import regular_period


def _run(
    start: date | None,
    *,
    career: int | None = None,
    hired: date = date(2013, 7, 1),
    service_months: int = 150,
) -> PeriodResult:
    return regular_period(
        employment=Employment(
            ccnl_id="marittimi-industria-armatoriale",
            level_code="IV",
            contract_type=Permanent(),
            employment_period=EmploymentPeriod(started_on=hired),
            pension_fund=NoPensionFund(),
            seniority=SeniorityFact(
                service_months,
                date(2026, 1, 1),
                SenioritySource.EMPLOYER_RECORDS,
                career_months=career,
            ),
            level_started_on=start,
        )
    )


def _superminimo(result: PeriodResult) -> Decimal:
    return sum(
        (item.amount for item in result.pay_items if "SUPERMINIMO" in item.item_id),
        Decimal("0.00"),
    )


@pytest.mark.parametrize(
    ("start", "career", "expected"),
    [
        (date(2024, 1, 1), 150, Decimal("0.00")),
        (date(2018, 1, 1), 0, Decimal("7.00")),
        (date(2018, 1, 2), None, Decimal("0.00")),
    ],
)
def test_level_months_override_service_and_career(
    start: date, career: int | None, expected: Decimal
) -> None:
    """At January 2026, January 2024 is 24 months, not 150: EUR 7 -> 0.

    January 2018 is 96 completed months (EUR 7), but January 2 is
    only 95 on January 1 (EUR 0), even with 150 service months.
    """
    result = _run(start, career=career)
    assert _superminimo(result) == expected
    assert not any(i.code == "level_service_unknown" for i in result.issues)


def test_new_hire_cannot_reach_the_threshold_without_a_level_date() -> None:
    """A January 2026 hire cannot have 96 months in level in that month."""
    result = _run(None, hired=date(2026, 1, 1), service_months=0)
    assert _superminimo(result) == Decimal("0.00")
    assert not any(i.code == "level_service_unknown" for i in result.issues)


def test_unknown_level_start_blocks_instead_of_paying_service() -> None:
    """150 service months formerly paid EUR 7; unknown level tenure pays 0."""
    result = _run(None, career=150)
    assert _superminimo(result) == Decimal("0.00")
    assert any(
        i.code == "level_service_unknown" and i.fact == "level_started_on"
        for i in result.issues
    )
    assert any(b.code == BlockerCode.MISSING_FACT for b in result.blockers)
