"""Full-pay days counted over the comporto window, without a treatment chain.

CCNL lavoro domestico of 28 October 2025, Art. 27 (pp. 37-38 of the
Assindatcolf text): the job is kept 10, 45 or 180 calendar days by
seniority, counted "nell'anno solare, intendendosi per tale il periodo di
365 giorni decorrenti dall'evento" (c. 5); the pay runs "per un massimo di
8, 10, 15 giorni complessivi nell'anno" (c. 7), 50% up to the third day
and 100% from the fourth.  Every count is read off the calendar by hand.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.cumulation.results import cumulation_report
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment, SicknessWorker
from ccnl_engine.sickness.integration.models import (
    SicknessCumulation,
    SicknessRules,
    SicknessSeniorityBand,
)
from ccnl_engine.sickness.models import SicknessEpisode

_ONE = Decimal(1)
_HALF = Decimal("0.5")
_ZERO = Decimal(0)
_CUMULATION = SicknessCumulation(
    window_years=1,
    reduced_integration_rate=_ZERO,
    bands=(
        SicknessSeniorityBand(
            seniority_months_from=0, full_pay_days=8, comporto_days=10
        ),
        SicknessSeniorityBand(
            seniority_months_from=6, full_pay_days=10, comporto_days=45
        ),
        SicknessSeniorityBand(
            seniority_months_from=24, full_pay_days=15, comporto_days=180
        ),
    ),
)
_RULES = SicknessRules(
    carenza_integration_rate=_HALF,
    full_pay_integration_rate=_ONE,
    cumulation=_CUMULATION,
)
_SENIOR = SicknessWorker(
    seniority=SeniorityFact(36, date(2026, 1, 1), SenioritySource.PAYSLIP)
)
#: 6 days in February, then 20 days from 1 June 2026.
_FEBRUARY = SicknessEpisode("feb", date(2026, 2, 2), date(2026, 2, 7))
_JUNE = SicknessEpisode("jun", date(2026, 6, 1), date(2026, 6, 20))


def _june(*earlier: SicknessEpisode) -> CumulativeTreatment:
    return CumulativeTreatment(_RULES, _CUMULATION, _JUNE, earlier, _SENIOR)


def test_full_pay_days_of_the_window_span_episodes() -> None:
    """15 days a year: 6 in February leave 9 for June, to 9 June."""
    treatment = _june(_FEBRUARY)

    assert treatment.chain == (0, _JUNE.started_on)
    assert treatment.chain_days(date(2026, 6, 9)) == 15
    assert treatment.day(9, date(2026, 6, 9)).rate == _ONE
    tenth = treatment.day(10, date(2026, 6, 10))
    assert tenth.rate == _ZERO
    assert tenth.carenza_rate == _ZERO
    assert treatment.first_reduced() == date(2026, 6, 10)


def test_an_episode_out_of_the_window_counts_nothing() -> None:
    """The window of 25 June 2027 starts on 26 June 2026: no earlier day."""
    later = SicknessEpisode("later", date(2027, 6, 25), date(2027, 6, 27))
    treatment = CumulativeTreatment(_RULES, _CUMULATION, later, (_JUNE,), _SENIOR)

    assert treatment.chain_days(date(2027, 6, 25)) == 1
    assert treatment.day(1, date(2027, 6, 25)).carenza_rate == _HALF
    assert treatment.first_reduced() == date(2027, 6, 28)


def test_unknown_history_reaches_the_window_count() -> None:
    """Days before the known history fall in the window: they could count."""
    worker = SicknessWorker(seniority=_SENIOR.seniority, known_from=date(2026, 5, 1))
    treatment = CumulativeTreatment(_RULES, _CUMULATION, _JUNE, (), worker)

    report = cumulation_report(treatment, (date(2026, 6, 1), date(2026, 6, 5)))

    assert report.chain_days == report.window_days == 5
    assert report.history_reach
