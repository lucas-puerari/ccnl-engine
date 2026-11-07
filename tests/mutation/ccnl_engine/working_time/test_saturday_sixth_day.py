"""Ordinary work on Saturday or the sixth day (Alimentari art. 31).

FLAI text of the CCNL 2023-2027 (sha256
11792ad3df71999684bae85fea8aaf1e3d492d477043eecc78545b5f41db842c):
birra e malto row 10, "Lavoro effettuato il sabato o il sesto giorno",
50% for both columns (PDF p. 89); avicoli row 5, 65% (PDF p. 92).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.working_time.inputs import HolidayWorkEvent, HolidayWorkKind
from ccnl_engine.working_time.subsector.rules import with_subsector
from ccnl_engine.working_time.supplement.models import SupplementWork
from ccnl_engine.working_time.supplement.policies import work_of

_CCNL = load_ccnl("alimentari-federalimentare")


def test_the_event_kind_selects_the_saturday_work() -> None:
    """The hours declared as Saturday or sixth day select its bands."""
    event = HolidayWorkEvent(
        date(2026, 3, 7), hours=Decimal(8), kind=HolidayWorkKind.SATURDAY_SIXTH_DAY
    )

    assert work_of(event) is SupplementWork.SATURDAY_SIXTH_DAY


def _saturday_rates(subsector: str, category: WorkerCategory) -> list[Decimal]:
    ccnl, unknown = with_subsector(_CCNL, subsector, category)
    assert not unknown
    assert ccnl.work_rules is not None
    supplements = ccnl.work_rules.time_supplements
    assert supplements is not None
    return [
        band.rate.value_at(date(2026, 3, 1))
        for band in supplements.supplement_bands
        if band.work is SupplementWork.SATURDAY_SIXTH_DAY
    ]


@pytest.mark.parametrize(
    ("subsector", "category", "rates"),
    [
        ("birra_malto", WorkerCategory.OPERAIO, [Decimal("0.50")]),
        ("birra_malto", WorkerCategory.IMPIEGATO, [Decimal("0.50")]),
        ("avicoli", WorkerCategory.OPERAIO, [Decimal("0.65")]),
        ("carni", WorkerCategory.OPERAIO, []),
    ],
)
def test_the_tables_that_print_a_saturday_row(
    subsector: str, category: WorkerCategory, rates: list[Decimal]
) -> None:
    """Only birra e malto and avicoli print a Saturday or sixth-day row."""
    assert _saturday_rates(subsector, category) == rates
