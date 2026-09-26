"""Overtime supplement rates read from the bundle match the signed CCNL articles.

The rates were checked by hand against the cited articles when the
reference cases that first carried them were written; the payroll pipeline
takes the hourly rate and multiplier from the caller, so the bundle is the
only place these values live and this is their owner.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.service.loaders import load_ccnl

_METAL = "metalmeccanico-federmeccanica.json"
_SIF_IMPIEGATI = "sistemazioni-idraulico-forestali-impiegati.json"
_SIF_OPERAI = "sistemazioni-idraulico-forestali-operai.json"


@pytest.mark.parametrize(
    ("slug", "code", "rate"),
    [
        # CCNL Federmeccanica-Assistal 12/06/2025, art. 14.
        (_METAL, "OT_DIURNO", "0.15"),
        (_METAL, "OT_NOTTURNO", "0.20"),
        (_METAL, "OT_FESTIVO", "0.30"),
        # CCNL Sistemazioni Idraulico-Forestali 2023, impiegati art. 37 a).
        (_SIF_IMPIEGATI, "OT_DIURNO", "0.30"),
        # CCNL Sistemazioni Idraulico-Forestali 2023, operai art. 50 (1).
        (_SIF_OPERAI, "OT_DIURNO", "0.24"),
    ],
)
def test_overtime_band_rate_matches_article(slug: str, code: str, rate: str) -> None:
    """The band's supplement on 1 June 2026 equals the article's percentage."""
    work_rules = load_ccnl(slug).work_rules
    assert work_rules is not None
    assert work_rules.time_supplements is not None
    (band,) = (
        band for band in work_rules.time_supplements.overtime_bands if band.code == code
    )
    assert band.rate.value_at(date(2026, 6, 1)) == Decimal(rate)
