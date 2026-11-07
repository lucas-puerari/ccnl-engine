"""Seniority bands with their own window in months and rate steps.

- Logistica Confetra art. 63 cc. 7-8, 12: up to 5 years of seniority the job
  is kept 245 days within 24 months, 3 months paid in full and 5 at half;
  above, 365 days within 30 months, 5 months in full and 7 at half;
- PA comparti (e.g. Funzioni Locali 2026 art. 36): 18 months within three
  years, 9 months in full, 3 at 90%, 6 at 50%.

Every count is read off the calendar by hand.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.cumulation.results import cumulation_report
from ccnl_engine.sickness.cumulation.rules import (
    CumulativeTreatment,
    SicknessWorker,
)
from ccnl_engine.sickness.integration.models import (
    SicknessCumulation,
    SicknessDayBand,
    SicknessRules,
    SicknessSeniorityBand,
)
from ccnl_engine.sickness.models import SicknessEpisode
from ccnl_engine.sickness.window.rules import window_start

_ONE = Decimal(1)
_HALF = Decimal("0.5")
_ZERO = Decimal(0)
_LOGISTICA = SicknessCumulation(
    window_years=2,
    reduced_integration_rate=_ZERO,
    bands=(
        SicknessSeniorityBand(
            seniority_months_from=0,
            full_pay_days=90,
            comporto_days=245,
            window_months=24,
            steps=(
                SicknessDayBand(day_from=91, day_until=241, integration_rate=_HALF),
            ),
        ),
        SicknessSeniorityBand(
            seniority_months_from=60,
            full_pay_days=150,
            comporto_days=365,
            window_months=30,
            steps=(
                SicknessDayBand(day_from=151, day_until=361, integration_rate=_HALF),
            ),
        ),
    ),
)
_RULES = SicknessRules(
    carenza_integration_rate=_ONE, full_pay_integration_rate=_ONE, cumulation=_LOGISTICA
)


def _worker(months: int) -> SicknessWorker:
    return SicknessWorker(
        seniority=SeniorityFact(months, date(2026, 1, 1), SenioritySource.PAYSLIP)
    )


def test_window_start_in_months() -> None:
    """24 months back from 31 March 2026 end on 31 March 2024; 30 on 30 September."""
    assert window_start(date(2026, 3, 31), 0, 24) == date(2024, 4, 1)
    assert window_start(date(2026, 3, 31), 0, 30) == date(2023, 10, 1)
    # 31 August less 6 months is 28 February in a common year.
    assert window_start(date(2026, 8, 31), 0, 6) == date(2026, 3, 1)


@pytest.mark.parametrize(
    ("months", "earlier_counts"),
    [(12, False), (84, True)],
    ids=["24_months", "30_months"],
)
def test_each_band_counts_its_own_window(months: int, earlier_counts: bool) -> None:
    """Sick in October 2023: outside 24 months of March 2026, inside 30."""
    october = SicknessEpisode("old", date(2023, 10, 2), date(2023, 10, 11))
    march = SicknessEpisode("new", date(2026, 3, 2), date(2026, 3, 6))
    treatment = CumulativeTreatment(
        _RULES, _LOGISTICA, march, (october,), _worker(months)
    )

    assert treatment.window_days(date(2026, 3, 6)) == 5 + (10 if earlier_counts else 0)


def test_steps_pay_half_then_nothing() -> None:
    """Up to 5 years: days 1-90 in full, 91-240 at half, from 241 unpaid."""
    episode = SicknessEpisode("long", date(2026, 1, 1), date(2026, 9, 30))
    treatment = CumulativeTreatment(_RULES, _LOGISTICA, episode, (), _worker(12))

    assert treatment.day(90, date(2026, 3, 31)).rate == _ONE
    assert treatment.day(91, date(2026, 4, 1)).rate == _HALF
    assert treatment.day(240, date(2026, 8, 28)).rate == _HALF
    assert treatment.day(241, date(2026, 8, 29)).rate == _ZERO
    assert treatment.day(246, date(2026, 9, 3)).beyond_comporto


def test_report_reads_the_band_window() -> None:
    """Unknown history counts from the start of the band's own window."""
    worker = SicknessWorker(
        seniority=SeniorityFact(12, date(2026, 1, 1), SenioritySource.PAYSLIP),
        known_from=date(2026, 1, 1),
    )
    episode = SicknessEpisode("e", date(2026, 3, 2), date(2026, 3, 6))
    treatment = CumulativeTreatment(_RULES, _LOGISTICA, episode, (), worker)

    report = cumulation_report(treatment, (date(2026, 3, 2), date(2026, 3, 6)))

    assert report.window_days == 5


def test_steps_start_after_the_full_pay_days() -> None:
    """A step overlapping the full-pay days is rejected."""
    with pytest.raises(ValueError, match="steps must start after"):
        SicknessSeniorityBand(
            seniority_months_from=0,
            full_pay_days=90,
            comporto_days=245,
            steps=(SicknessDayBand(day_from=90, integration_rate=_HALF),),
        )
