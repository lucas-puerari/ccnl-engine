"""Percentage apprenticeship tracks of Turismo Confesercenti and Autostrade.

Turismo Confesercenti, renewal of 18 July 2018, art. 54 (36 months for
levels 2-6S, 24 for level 6, 48 and 42 for named craft profiles) and art. 58
("primo anno: 80%; secondo anno: 85%; terzo anno: 90%; dal quarto anno:
95%"). Autostrade e Trafori, CCNL of 18 July 2023, art. 10 cc. 7-8 (36
months, "80% per i primi 12 mesi; 85% per i secondi 12 mesi; 95% per i
successivi mesi") and c. 10: the apprenticeship counts for the increments.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.apprenticeship.rules import _apprentice_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.inputs import Apprentice


def _rate(slug: str, level: str, months: int, track: str | None) -> Decimal | None:
    ccnl = load_ccnl(slug)
    _, rate, _ = _apprentice_chain(
        ccnl,
        ccnl.level_by_code(level),
        Apprentice(months_elapsed=months, track=track),
        0,
        frozenset(),
        date(2026, 6, 1),
    )
    return rate


@pytest.mark.parametrize(
    ("level", "track", "months", "rate"),
    [
        ("5", None, 0, "0.80"),
        ("5", None, 12, "0.85"),
        ("6S", None, 35, "0.90"),
        ("6S", None, 36, "1.00"),
        ("6", None, 23, "0.85"),
        ("6", None, 24, "1.00"),
        ("2", "professionalizzante", 24, "0.90"),
        ("2", "professionalizzante_48_mesi", 47, "0.95"),
        ("4", "professionalizzante_42_mesi", 41, "0.95"),
        ("4", "professionalizzante_42_mesi", 42, "1.00"),
    ],
)
def test_turismo_confesercenti_pays_a_share_of_the_level(
    level: str, track: str | None, months: int, rate: str
) -> None:
    """80/85/90% by year of the level's pay, 95% in a fourth year."""
    assert _rate("turismo-confesercenti", level, months, track) == Decimal(rate)


@pytest.mark.parametrize(
    ("months", "rate"),
    [(0, "0.80"), (11, "0.80"), (12, "0.85"), (24, "0.95"), (35, "0.95"), (36, "1.00")],
)
def test_autostrade_pays_80_85_95_over_36_months(months: int, rate: str) -> None:
    """Art. 10 c. 8 over the 36 months of c. 7."""
    assert _rate("autostrade-trafori", "C", months, None) == Decimal(rate)


def test_autostrade_apprentice_accrues_the_scaled_level_increments() -> None:
    """Art. 10 c. 10: the increments of the level, at the apprentice share."""
    increments = load_ccnl("autostrade-trafori").parameters.seniority_increments
    assert increments is not None
    assert increments.apprentice_level_amount
    assert increments.apprentice_pct_scaled
