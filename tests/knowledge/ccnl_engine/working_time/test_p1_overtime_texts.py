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


def _bands(slug: str) -> dict[str, Decimal]:
    rules = load_ccnl(slug).work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    return {
        kind.value: Decimal(str(b.rate.periods[-1].value))
        for b in rules.time_supplements.overtime_bands
        for kind in b.applies_to_kinds
    }


@pytest.mark.parametrize(
    ("slug", "expected"),
    [
        (
            "bancari-abi",
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
            {
                "weekday": "0.25",
                "night": "0.40",
                "holiday": "0.40",
                "night_holiday": "0.45",
            },
        ),
        (
            "metalmeccanico-artigianato",
            {
                "weekday": "0.25",
                "night": "0.55",
                "holiday": "0.45",
                "night_holiday": "0.55",
            },
        ),
    ],
)
def test_bands_of_the_text(slug: str, expected: dict[str, str]) -> None:
    """Each band of the file is the rate the article prints."""
    assert _bands(slug) == {k: Decimal(v) for k, v in expected.items()}
