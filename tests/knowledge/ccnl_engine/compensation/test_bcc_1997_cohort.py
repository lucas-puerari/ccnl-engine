"""BCC artt. 101 and 113: the scatti of the staff in service on 31.12.1997.

At most 8 scatti (7 for the 3rd and 4th level of the quadri), but 12 (9)
for the staff in service on 31 December 1997.  With 372 months of service
on 1 January 2026, the 4-year first scatto and then one every 36 months
give 10: 41.55 x 10 = 415.50 for the cohort, 41.55 x 8 = 332.40 after it;
a QD4 of the cohort stops at 9: 95.31 x 9 = 857.79.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from tests.knowledge.ccnl_engine.support import regular_period


def _scatti(level: str, hired: date, ended: date | None = None) -> Decimal:
    employment = Employment(
        ccnl_id="bcc-credito-cooperativo",
        level_code=level,
        seniority=SeniorityFact(
            372, date(2026, 1, 1), SenioritySource.EMPLOYER_RECORDS
        ),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        employment_period=EmploymentPeriod(hired, ended),
    )
    result = regular_period(ccnl_id="bcc-credito-cooperativo", employment=employment)
    return sum(
        (i.amount for i in result.pay_items if i.item_id.startswith("seniority")),
        Decimal(0),
    )


@pytest.mark.parametrize(
    ("level", "hired", "amount"),
    [
        ("3AP4", date(1995, 1, 1), "415.50"),
        ("3AP4", date(1997, 12, 31), "415.50"),
        ("3AP4", date(1998, 1, 1), "332.40"),
        ("QD4", date(1995, 1, 1), "857.79"),
    ],
    ids=["cohort", "hired-on-the-day", "after-the-day", "qd4-nine"],
)
def test_the_cohort_maximum(level: str, hired: date, amount: str) -> None:
    """In service on 31.12.1997: 12 scatti, 9 for QD3 and QD4."""
    assert _scatti(level, hired) == Decimal(amount)
