"""Overtime and shift premiums of the first-round CCNLs read from their texts.

Sanità privata: Art. 59 of the CCNL of 8 October 2020 (sha256
183c5c0a01c9a113fd08efffed8132b4e598e4db574f6aed402afb7be880a442, p. 89)
pays daytime overtime at 20%, night or holiday overtime at 30% and
night-holiday overtime at 50%; its shift and on-call indemnities (Art.
60-61) are declared.  The overtime rates of the artisan metalworkers could
not be read from a party text, so a run with overtime is blocked.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl


def _variants(slug: str) -> set[str]:
    ccnl = load_ccnl(f"{slug}.json")
    return {n.limitation.variant for n in ccnl.coverage.notes if n.limitation}


@pytest.mark.parametrize(
    ("code", "rate"),
    [
        ("OT_DIURNO", "0.20"),
        ("OT_NOTTURNO", "0.30"),
        ("OT_FESTIVO", "0.30"),
        ("OT_NOTTURNO_FESTIVO", "0.50"),
    ],
)
def test_sanita_privata_overtime_bands(code: str, rate: str) -> None:
    """The four bands of Art. 59."""
    rules = load_ccnl("sanita-privata-aiop-aris.json").work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    (band,) = [b for b in rules.time_supplements.overtime_bands if b.code == code]

    assert Decimal(str(band.rate.periods[-1].value)) == Decimal(rate)


def test_declared_overtime_gaps() -> None:
    """Shift indemnities and unconfirmed artisan rates are open limitations."""
    assert "shift_on_call_allowances" in _variants("sanita-privata-aiop-aris")
    assert "artisan_saturday_overtime" in _variants("metalmeccanico-artigianato")
