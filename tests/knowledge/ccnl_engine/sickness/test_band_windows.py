"""Bundled sickness rules counted per band window and paid by steps.

- Logistica Confetra art. 63 A) cc. 7-8, 12 (testo unico 25.9.2025, p. 88):
  up to 5 years of seniority, 245 days within 24 months, "intera
  retribuzione globale mensile per 3 mesi e della metà di essa per altri 5
  mesi"; above, 365 days within 30 months, 5 and 7 months.
- Funzioni Locali CCNL 23.2.2026 art. 36: 18 months within three years, 9 in
  full, 3 at 90%, 6 at 50%.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment, SicknessWorker
from ccnl_engine.sickness.models import SicknessEpisode

_LONG = SicknessEpisode("long", date(2026, 1, 1), date(2027, 6, 30))


def _treatment(slug: str, months: int) -> CumulativeTreatment:
    rules = load_ccnl(slug).work_rules
    assert rules is not None
    assert rules.sickness_rules is not None
    cumulation = rules.sickness_rules.cumulation
    assert cumulation is not None
    worker = SicknessWorker(
        seniority=SeniorityFact(months, date(2026, 1, 1), SenioritySource.PAYSLIP)
    )
    return CumulativeTreatment(rules.sickness_rules, cumulation, _LONG, (), worker)


@pytest.mark.parametrize(
    ("slug", "months", "day", "rate"),
    [
        # Logistica up to 5 years: day 90 (31 March) in full, day 91 at half.
        ("logistica-trasporto-confetra.json", 12, date(2026, 3, 31), "1"),
        ("logistica-trasporto-confetra.json", 12, date(2026, 4, 1), "0.5"),
        ("logistica-trasporto-confetra.json", 12, date(2026, 8, 29), "0"),
        # Above 5 years: day 151 (31 May) at half.
        ("logistica-trasporto-confetra.json", 72, date(2026, 5, 31), "0.5"),
        # Funzioni Locali: day 271 (28 September) at 90%, day 361 at 50%.
        ("funzioni-locali-aran.json", 12, date(2026, 9, 28), "0.9"),
        ("funzioni-locali-aran.json", 12, date(2026, 12, 27), "0.5"),
    ],
)
def test_rate_of_the_day(slug: str, months: int, day: date, rate: str) -> None:
    """The rate of the day follows the band's full-pay days and steps."""
    assert _treatment(slug, months).day(1, day).rate == Decimal(rate)
