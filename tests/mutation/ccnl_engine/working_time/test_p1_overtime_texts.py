"""Overtime bands of ABI, operai agricoli and artisan metalworkers.

Read on the full texts published by the parties: ABI Art. 114-115 (FABI,
sha256 4d92bc5226736682ddb1eedfaf7940df989fdc3cbbd99d0fa6347fd91979a933),
operai agricoli Art. 43 (FLAI, sha256
49ae5803f2081985a0e1a10f64e9019e1b999e808da9d3681eaab24c3dee674c), area
meccanica artigianato Art. 22 (EBNA, sha256
f8cd3c42582324aa4484bb2bb9465a5a0a442467aae64e3ea3a1c57e089f3151).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.working_time.subsector.rules import with_subsector


def _bands(slug: str, subsector: str | None = None) -> dict[str, Decimal]:
    ccnl = load_ccnl(slug)
    if subsector is not None:
        ccnl, missing = with_subsector(ccnl, subsector, WorkerCategory.OPERAIO)
        assert not missing
    rules = ccnl.work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    return {
        kind.value: Decimal(str(b.rate.periods[-1].value))
        for b in rules.time_supplements.overtime_bands
        for kind in b.applies_to_kinds
        if b.hour_threshold_per_day is None and b.hour_threshold_per_week is None
    }


@pytest.mark.parametrize(
    ("slug", "subsector", "expected"),
    [
        (
            "bancari-abi",
            None,
            {
                "weekday": "0.25",
                "night": "0.55",
                "night_holiday": "0.65",
                "holiday": "0.30",
                "rest_day": "0.25",
            },
        ),
        (
            "operai-agricoli-florovivaisti",
            "agricoli",
            {
                "weekday": "0.25",
                "night": "0.40",
                "holiday": "0.40",
                "night_holiday": "0.45",
            },
        ),
        (
            "operai-agricoli-florovivaisti",
            "florovivaisti",
            {
                "weekday": "0.29",
                "night": "0.48",
                "holiday": "0.50",
                "night_holiday": "0.55",
            },
        ),
        (
            "metalmeccanico-artigianato",
            None,
            {
                "weekday": "0.25",
                "night": "0.55",
                "holiday": "0.45",
                "night_holiday": "0.55",
                "saturday": "0.25",
            },
        ),
    ],
)
def test_bands_of_the_text(
    slug: str, subsector: str | None, expected: dict[str, str]
) -> None:
    """Each selected sub-sector band is the rate its article prints."""
    assert _bands(slug, subsector) == {k: Decimal(v) for k, v in expected.items()}


def test_artisan_saturday_overtime_doubles_after_three_hours() -> None:
    """Area Meccanica (2021 text, PDF p. 84): 25% for the first 3 hours, 50% after."""
    rules = load_ccnl("metalmeccanico-artigianato").work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    saturday = {
        b.hour_threshold_per_day: b.rate.periods[-1].value
        for b in rules.time_supplements.overtime_bands
        if "saturday" in b.applies_to_kinds
    }

    assert saturday == {None: Decimal("0.25"), 3: Decimal("0.50")}
