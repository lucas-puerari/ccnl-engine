"""Sickness rule models: one counting model, ordered seniority bands.

The bands and rates are those of CCNL Federmeccanica, Sez. Quarta Titolo VI
Art. 2 (FIOM-CGIL text of 5 February 2021, pp. 196-199): 122/153/214
full-pay days and 183/274/365 comporto days for up to 3, 3 to 6 and over 6
years of seniority; 66% for the fourth short absence of a year, 50% for the
fifth and later.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.domain.sickness import (
    ShortAbsenceReduction,
    SicknessCumulation,
    SicknessRules,
    SicknessSeniorityBand,
    SicknessTier,
)

_ONE = Decimal(1)
_BANDS = (
    SicknessSeniorityBand(
        seniority_months_from=0, full_pay_days=122, comporto_days=183
    ),
    SicknessSeniorityBand(
        seniority_months_from=36, full_pay_days=153, comporto_days=274
    ),
    SicknessSeniorityBand(
        seniority_months_from=72, full_pay_days=214, comporto_days=365
    ),
)
_SHORT = ShortAbsenceReduction(
    max_days=5, from_event=4, first_days=3, rates=(Decimal("0.66"), Decimal("0.50"))
)


def _cumulation(
    bands: tuple[SicknessSeniorityBand, ...] = _BANDS,
) -> SicknessCumulation:
    return SicknessCumulation(
        window_years=3,
        reset_after_days=61,
        reduced_integration_rate=Decimal("0.80"),
        bands=bands,
        short_absences=_SHORT,
    )


@pytest.mark.parametrize(
    ("months", "full_pay_days"), [(0, 122), (35, 122), (36, 153), (71, 153), (72, 214)]
)
def test_band_of_a_seniority(months: int, full_pay_days: int) -> None:
    """A band applies from its first month of seniority."""
    assert _cumulation().band_of(months).full_pay_days == full_pay_days


@pytest.mark.parametrize(
    ("ordinal", "rate"),
    [
        (1, _ONE),
        (3, _ONE),
        (4, Decimal("0.66")),
        (5, Decimal("0.50")),
        (9, Decimal("0.50")),
    ],
)
def test_rate_of_a_short_absence(ordinal: int, rate: Decimal) -> None:
    """The fourth short absence is paid 66%, the fifth and later 50%."""
    assert _SHORT.rate_of(ordinal) == rate


@pytest.mark.parametrize(
    "bands",
    [
        (_BANDS[1], _BANDS[2]),
        (_BANDS[0], _BANDS[2], _BANDS[1]),
        (
            _BANDS[0],
            SicknessSeniorityBand(
                seniority_months_from=36, full_pay_days=100, comporto_days=274
            ),
        ),
    ],
    ids=["no_first_band", "out_of_order", "fewer_full_pay_days"],
)
def test_bands_must_start_at_zero_and_increase(
    bands: tuple[SicknessSeniorityBand, ...],
) -> None:
    """A later band gives more days of every kind."""
    with pytest.raises(ValidationError, match="bands must start at 0 months"):
        _cumulation(bands)


@pytest.mark.parametrize(
    "per_episode",
    [
        {"tiers": (SicknessTier(month_from=1, integration_rate=_ONE),)},
        {"max_duration_days": 180},
    ],
    ids=["tiers", "max_duration_days"],
)
def test_a_rule_counts_one_way(per_episode: dict[str, object]) -> None:
    """Cumulated counting excludes the per-episode tiers and comporto."""
    with pytest.raises(ValidationError, match="drop tiers and max_duration_days"):
        SicknessRules(
            carenza_integration_rate=_ONE,
            full_pay_integration_rate=_ONE,
            cumulation=_cumulation(),
            **per_episode,  # type: ignore[arg-type]
        )


def test_a_cumulated_rule_keeps_the_default_comporto_unread() -> None:
    """Without an explicit max_duration_days the cumulation is accepted."""
    rules = SicknessRules(
        carenza_integration_rate=_ONE,
        full_pay_integration_rate=_ONE,
        cumulation=_cumulation(),
    )
    assert rules.cumulation is not None
