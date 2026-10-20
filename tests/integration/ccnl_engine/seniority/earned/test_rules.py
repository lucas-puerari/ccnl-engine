"""Increments stated as matured, then priced by the CCNL: Federmeccanica C3.

Art. 6: an increment every two years of service, at most five, 29.64 EUR
at C3 (5a categoria), due from the month after the biennium.  The worker
states on 1 January 2026 sixty months of service and two increments
matured at 40.00 EUR in all (fixed by the norme transitorie).
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
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import (
    EarnedIncrements,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.seniority.repricing.rules import earned_seniority


def _seniority(month: int, year: int, earned: EarnedIncrements | None) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year, month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-federmeccanica",
                level_code="C3",
                contract_type=Permanent(),
                seniority=SeniorityFact(
                    60, date(2026, 1, 1), SenioritySource.PAYSLIP, earned
                ),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(60)),
        )
    )
    return sum(
        (i.amount for i in result.pay_items if "seniority" in i.item_id), Decimal(0)
    )


_EARNED = EarnedIncrements(2, Decimal("40.00"))


@pytest.mark.parametrize(
    ("year", "month", "expected"),
    [
        (2026, 6, "40.00"),
        (2027, 2, "69.64"),
    ],
)
def test_the_stated_increments_then_the_table(
    year: int, month: int, expected: str
) -> None:
    """40.00, then 29.64 for the increment matured in January 2027."""
    assert _seniority(month, year, _EARNED) == Decimal(expected)


def test_without_the_statement_the_table_prices_every_increment() -> None:
    """Two increments at the table: 2 x 29.64 = 59.28."""
    assert _seniority(6, 2026, None) == Decimal("59.28")


@pytest.mark.parametrize(
    "fields",
    [{"count": -1, "monthly": Decimal(1)}, {"count": 1, "monthly": Decimal(-1)}],
)
def test_an_invalid_statement_is_rejected(fields: dict[str, object]) -> None:
    """A negative count or amount fails."""
    with pytest.raises(InvalidInputError):
        EarnedIncrements(**fields)  # type: ignore[arg-type]


def test_earned_must_be_earned_increments() -> None:
    """A bare amount is not a statement of increments."""
    with pytest.raises(InvalidInputError, match=r"SeniorityFact\.earned"):
        SeniorityFact(60, date(2026, 1, 1), SenioritySource.PAYSLIP, Decimal(40))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("months_now", "expected"),
    [(60, "40.00"), (84, "69.64"), (108, "99.28"), (200, "128.92")],
)
def test_the_table_adds_up_to_the_maximum_count(months_now: int, expected: str) -> None:
    """Five increments at most: the two stated and three from the table."""
    increments = load_ccnl(
        "metalmeccanico-federmeccanica"
    ).parameters.seniority_increments

    assert earned_seniority(
        increments,
        "C3",
        _EARNED,
        60,
        months_now,
        date(2026, 6, 1),
        worker_category=None,
    ) == Decimal(expected)
