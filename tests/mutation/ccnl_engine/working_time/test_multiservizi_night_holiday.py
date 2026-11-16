"""Night work on a holiday of the Multiservizi ANIP, art. 38 (CNEL 105782 p. 57).

'Le suddette percentuali di maggiorazione non sono cumulabili, nel senso che
la maggiore assorbe la minore': night hours on a holiday take the 50% of
holiday work alone, as ordinary or as rotating-shift night work.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.working_time.supplement.models import SupplementWork


@pytest.mark.parametrize(
    "work", [SupplementWork.NIGHT_HOLIDAY, SupplementWork.NIGHT_HOLIDAY_SHIFT]
)
def test_the_holiday_rate_absorbs_the_night_one(work: SupplementWork) -> None:
    """50%, not 50% + 30% or 50% + 20%."""
    rules = load_ccnl("multiservizi-anip").work_rules
    assert rules is not None
    supplements = rules.time_supplements
    assert supplements is not None
    (band,) = (b for b in supplements.supplement_bands if b.work is work)
    period = band.rate.period_at(date(2026, 3, 1))
    assert period is not None
    assert period.value == Decimal("0.5")
