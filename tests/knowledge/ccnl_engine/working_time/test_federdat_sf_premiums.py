"""FEDERDAT servizi fiduciari art. 143: the premiums on ordinary hours.

"lavoro domenicale/festivo: diurno 40% notturno 50%" (CCNL 9 luglio 2026,
p. 72; art. 126 of the 2023 text is the same).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl


def test_ordinary_sunday_and_holiday_premiums() -> None:
    """40% on Sunday and holiday hours by day, 50% on holiday hours at night."""
    rules = load_ccnl("vigilanza-privata-federdat-sf").work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    rates = {
        b.work.value: b.rate.value_at(date(2026, 7, 1))
        for b in rules.time_supplements.supplement_bands
    }

    assert rates == {
        "sunday": Decimal("0.40"),
        "holiday": Decimal("0.40"),
        "night_holiday": Decimal("0.50"),
    }
