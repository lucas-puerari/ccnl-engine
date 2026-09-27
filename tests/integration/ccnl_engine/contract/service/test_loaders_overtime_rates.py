"""Overtime supplement rates read from the bundle match the signed CCNL articles.

The rates were checked by hand against the cited articles when the
reference cases that first carried them were written; the Federmeccanica
rates were corrected against the signed 2021 text.  An overtime event
without a multiplier is paid with these bands, so this is their owner.
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
        # CCNL Federmeccanica-Assistal 5 febbraio 2021, sez. quarta, titolo
        # III, art. 7, lavoro non a turni: straordinario prime due ore 25%,
        # ore successive 30%, straordinario notturno 50%, straordinario
        # festivo 55%, straordinario notturno festivo 75%.
        (_METAL, "OT_DIURNO", "0.25"),
        (_METAL, "OT_DIURNO_EXTRA", "0.30"),
        (_METAL, "OT_NOTTURNO", "0.50"),
        (_METAL, "OT_FESTIVO", "0.55"),
        (_METAL, "OT_NOTTURNO_FESTIVO", "0.75"),
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
