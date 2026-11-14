"""Studi art. 92: 30 minutes a week up to 44 hours, 60 up to 48."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.leave.flexibility.models import FlexibilityBand, FlexibilityPermits


def _studi() -> FlexibilityPermits:
    work = load_ccnl("studi-professionali-confprofessioni").work_rules
    assert work is not None
    assert work.leave_rules is not None
    flex = work.leave_rules.flexibility
    assert flex is not None
    return flex


@pytest.mark.parametrize(
    ("worked", "hours"),
    [
        ("40", "0"),
        ("40.5", "0.5"),
        ("44", "0.5"),
        ("44.5", "1"),
        ("48", "1"),
        ("49", "0"),
    ],
)
def test_the_week_earns_the_permit_of_its_band(worked: str, hours: str) -> None:
    """Over 40 up to 44: half an hour; over 44 up to 48: one; beyond: none."""
    assert _studi().hours_for(Decimal(worked)) == Decimal(hours)


@pytest.mark.parametrize(
    "bands",
    [
        (FlexibilityBand(up_to_hours=Decimal(40), minutes=Decimal(30)),),
        (
            FlexibilityBand(up_to_hours=Decimal(48), minutes=Decimal(60)),
            FlexibilityBand(up_to_hours=Decimal(44), minutes=Decimal(30)),
        ),
    ],
)
def test_the_bands_must_ascend_above_the_normal_week(
    bands: tuple[FlexibilityBand, ...],
) -> None:
    """A band at the normal hours, or bands out of order, are rejected."""
    flex = _studi()
    with pytest.raises(ValidationError):
        FlexibilityPermits(
            normal_weekly_hours=Decimal(40),
            bands=bands,
            payout_months_after=6,
            premium_band="OT_DIURNO",
            provenance=flex.provenance,
        )
