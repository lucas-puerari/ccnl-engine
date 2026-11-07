"""The 13th of a year with a month of parental or extraordinary leave.

Commercio level 4, 1,818.75 a month in 2026.  The parental leave does not
reduce the 13th: "I periodi di congedo parentale ... non comportano
riduzione di ferie, riposi, tredicesima mensilità o gratifica natalizia"
(art. 34 c. 5 D.Lgs. 151/2001 as amended by D.Lgs. 105/2022; Normattiva,
page sha256 eb17ab78f18b987e65c6e3a4155e69358a5e4a56a98373e1115b1a7eadec9946).
The extraordinary leave accrues no 13th (art. 42 c. 5-quinquies): a month
of it takes one twelfth off, 1,818.75 * 11 / 12, each component rounded.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.events import (
    ExtraordinaryLeaveEvent,
    ParentalLeaveEvent,
    ParentalLeaveTaken,
    WorkEvent,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from ccnl_engine.period.services import bundled_policies, bundled_repository
from ccnl_engine.year.competence.services import calculate_competence_year
from tests.unit.ccnl_engine.builders import year_plan

_HIRED = date(2025, 1, 1)
_MARCH = (date(2026, 3, 1), date(2026, 3, 31))


@pytest.mark.parametrize(
    ("events", "thirteenth"),
    [
        ((), Decimal("1818.75")),
        (
            (
                ParentalLeaveEvent(
                    *_MARCH, date(2025, 6, 1), ParentalLeaveTaken(0, 0, 0)
                ),
            ),
            Decimal("1818.75"),
        ),
        ((ExtraordinaryLeaveEvent(*_MARCH, Decimal(1800)),), Decimal("1667.20")),
    ],
    ids=["none", "parental", "extraordinary"],
)
def test_the_13th_after_a_month_of_leave(
    events: tuple[WorkEvent, ...], thirteenth: Decimal
) -> None:
    """Only the extraordinary leave takes a twelfth off."""
    year = calculate_competence_year(
        year_plan(
            2026,
            "commercio-confcommercio",
            "4",
            events={3: events} if events else None,
            category=WorkerCategory.IMPIEGATO,
            employment_period=EmploymentPeriod(_HIRED, None),
            seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    (run,) = (
        r
        for r in year.period_results
        if r.run is not None and r.run.run_kind.value == "thirteenth"
    )

    assert run.period_gross == thirteenth
