"""Impianti sportivi art. 83: 15% for hours 41-48, 20% past the 48th."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl


def test_the_weekday_overtime_bands_of_art_83() -> None:
    """Two thresholded weekday bands: 15% past 40 hours, 20% past 48."""
    rules = load_ccnl("impianti-sportivi-sport").work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    weekday = {
        b.hour_threshold_per_week: b.rate.periods[-1].value
        for b in rules.time_supplements.overtime_bands
        if "weekday" in b.applies_to_kinds
    }
    assert weekday == {40: Decimal("0.15"), 48: Decimal("0.20")}
