"""The holiday on a Sunday of ANCC, FIAIP, CED, Fiori and Ortofrutticoli.

ANCC art. 132 c. 2-3, FIAIP artt. 110 and 112, CED art. 116, Fiori art. 31,
Ortofrutticoli artt. 55 and 61: a listed holiday on a Sunday pays a further
daily quota, and 4 November, celebrated on the first Sunday of November,
too.  November 2026: 1 November (Ognissanti) is a Sunday and the first
Sunday of the month, two quotas; October 2026 has none.
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


def _quotas(slug: str, level: str, month: int) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=Employment(
                ccnl_id=slug,
                level_code=level,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2020, 1, 1), None),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(10)),
        )
    )
    return sum(
        (
            i.quantity
            for i in result.pay_items
            if i.item_id.startswith("sunday_holiday")
        ),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("slug", "level"),
    [
        ("distribuzione-cooperativa-ancc", "4"),
        ("agenti-immobiliari-fiaip", "IV"),
        ("ced-assoced", "3"),
        ("fiori-recisi-ancef", "3"),
        ("ortofrutticoli-agrumari", "4"),
    ],
)
def test_ognissanti_and_4_november_on_the_first_sunday(slug: str, level: str) -> None:
    """Two quotas in November 2026, none in October."""
    assert _quotas(slug, level, 11) == Decimal(2)
    assert _quotas(slug, level, 10) == Decimal(0)
