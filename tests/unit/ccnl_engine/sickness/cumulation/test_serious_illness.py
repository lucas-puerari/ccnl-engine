"""Particularly serious illness: Logistica Confetra art. 63 cc. 8 and 12.

Up to 5 years of seniority: 90 days in full, 150 at half, comporto 245 days
over 24 months.  A serious illness (INPS circ. 95/2016) is paid in full for
18 months (540 days) and left out of the comporto count.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource
from ccnl_engine.sickness.cumulation.rules import CumulativeTreatment, SicknessWorker
from ccnl_engine.sickness.integration.condition.models import SeriousIllnessRule
from ccnl_engine.sickness.integration.models import (
    SicknessCumulation,
    SicknessDayBand,
    SicknessRules,
    SicknessSeniorityBand,
)
from ccnl_engine.sickness.models import SicknessEpisode

_ONE = Decimal(1)
_HALF = Decimal("0.5")
_CUMULATION = SicknessCumulation(
    window_years=2,
    reduced_integration_rate=Decimal(0),
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
    ),
    serious_illness=SeriousIllnessRule(full_pay_days=540, outside_comporto=True),
)
_RULES = SicknessRules(
    carenza_integration_rate=_ONE,
    full_pay_integration_rate=_ONE,
    cumulation=_CUMULATION,
)
_WORKER = SicknessWorker(
    seniority=SeniorityFact(12, date(2026, 1, 1), SenioritySource.PAYSLIP)
)
_START = date(2026, 1, 1)


def _treatment(
    serious: bool | None, earlier: tuple[SicknessEpisode, ...] = ()
) -> CumulativeTreatment:
    episode = SicknessEpisode(
        "e", _START, _START + timedelta(days=599), serious_illness=serious
    )
    return CumulativeTreatment(_RULES, _CUMULATION, episode, earlier, _WORKER)


@pytest.mark.parametrize(
    ("serious", "day", "rate", "beyond"),
    [
        (False, 100, _HALF, False),  # day 100: past the 90 in full
        (True, 100, _ONE, False),  # serious: in full
        (True, 540, _ONE, False),  # the 540th day, still in full
        (True, 541, Decimal(0), False),  # past 18 months, not past the comporto
        (False, 300, Decimal(0), True),  # ordinary: past the 245 days
    ],
)
def test_serious_illness_is_paid_in_full_outside_the_comporto(
    serious: bool, day: int, rate: Decimal, beyond: bool
) -> None:
    """540 days in full, and the days never reach the comporto."""
    treatment = _treatment(serious)
    ccnl = treatment.day(day, _START + timedelta(days=day - 1))

    assert (ccnl.rate, ccnl.beyond_comporto) == (rate, beyond)


def test_earlier_serious_episodes_leave_the_window() -> None:
    """An earlier serious illness is not summed into the comporto."""
    earlier = SicknessEpisode(
        "old", date(2025, 6, 1), date(2025, 9, 30), serious_illness=True
    )
    assert _treatment(False, (earlier,)).window_days(_START) == 1
    ordinary = SicknessEpisode("old", date(2025, 6, 1), date(2025, 9, 30))
    assert _treatment(False, (ordinary,)).window_days(_START) == 1 + 122


def test_the_fact_must_be_a_bool() -> None:
    """``serious_illness`` is a bool or unstated."""
    with pytest.raises(InvalidInputError, match="serious_illness"):
        SicknessEpisode("e", _START, _START, serious_illness="yes")  # type: ignore[arg-type]
