"""The CCNL treatment of a sick day: per episode or cumulated.

A per-episode CCNL reads the relapse-chain index (comporto past
``max_duration_days``); a cumulated one counts the sickness of several
episodes (CCNL Federmeccanica, Sez. Quarta Titolo VI Art. 2: 122 full-pay
days, then 80%).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.sickness import (
    SicknessCumulation,
    SicknessRules,
    SicknessSeniorityBand,
)
from ccnl_engine.payroll.domain.sick_cumulation import CcnlDay
from ccnl_engine.payroll.domain.sick_pay_rules import SickPayRules
from ccnl_engine.payroll.domain.sickness import SicknessEpisode, SicknessHistory
from ccnl_engine.tax.domain.sick_pay import (
    InpsSickPayRates,
    SickPayBand,
    SickPayCoverage,
)

_ONE = Decimal(1)
_HALF = Decimal("0.50")
_INPS = InpsSickPayRates(
    carenza_days=3,
    bands=[SickPayBand(day_from=4, day_to=180, rate=_HALF)],
    annual_max_days=180,
    coverage=(SickPayCoverage(covered=True, source="test: every worker"),),
)
_PER_EPISODE = SicknessRules(
    carenza_integration_rate=_HALF,
    full_pay_integration_rate=_ONE,
    max_duration_days=10,
)
_CUMULATED = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    cumulation=SicknessCumulation(
        window_years=3,
        reset_after_days=61,
        reduced_integration_rate=Decimal("0.80"),
        bands=(
            SicknessSeniorityBand(
                seniority_months_from=0, full_pay_days=122, comporto_days=183
            ),
        ),
    ),
)
_EPISODE = SicknessEpisode("a", date(2026, 1, 1), date(2026, 5, 31))


def test_a_per_episode_ccnl_reads_the_index() -> None:
    """Day 11 of the relapse chain is past a 10-day comporto."""
    rules = SickPayRules(_INPS, inps_cover=True, ccnl=_PER_EPISODE)
    treatment = rules.treatment(_EPISODE, SicknessHistory())
    assert rules.cumulative(_EPISODE, SicknessHistory()) is None
    assert treatment(10, date(2026, 1, 10)) == CcnlDay(False, _ONE, _HALF)
    assert treatment(11, date(2026, 1, 11)).beyond_comporto


def test_a_cumulated_ccnl_counts_the_days() -> None:
    """From 1 January, 3 May is day 123 of the chain: 80%."""
    rules = SickPayRules(_INPS, inps_cover=True, ccnl=_CUMULATED)
    treatment = rules.treatment(_EPISODE, SicknessHistory())
    assert rules.cumulative(_EPISODE, SicknessHistory()) is not None
    assert treatment(1, date(2026, 5, 3)).rate == Decimal("0.80")
