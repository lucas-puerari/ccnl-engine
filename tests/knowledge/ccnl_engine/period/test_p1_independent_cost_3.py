"""Operai agricoli against the labour cost table of the Regione Toscana.

Price list of the Regione Toscana, Allegato 3, section 4 (sha256
2c3f7282c29ef6725dfbd85b0f0f6abca147016cf8d21f6f3dd1421c7aa18b23): the TFR
of a year is the annual pay over 13.5 (1.312,85 on 17.723,44).  The table
prices provincial wages, so only the structure compares; its contribution
share is recorded as a deviation in the review log.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from ccnl_engine.pay_item.models import BaseSalaryEarning, TfrAccrualItem
from tests.knowledge.ccnl_engine.support import regular_period

_FOUR = Decimal("0.0001")


def test_tfr_is_the_pay_over_13_5() -> None:
    """Area3, January 2026: the TFR of the month is the pay over 13.5."""
    result = regular_period(
        ccnl_slug="operai-agricoli-florovivaisti.json", level_code="Area3", month=1
    )
    (base,) = [i.amount for i in result.pay_items if isinstance(i, BaseSalaryEarning)]
    (tfr,) = [i.amount for i in result.pay_items if isinstance(i, TfrAccrualItem)]

    ratio = (Decimal("1312.85") / Decimal("17723.44")).quantize(_FOUR)

    assert ratio == (Decimal(1) / Decimal("13.5")).quantize(_FOUR)
    assert tfr == (base / Decimal("13.5")).quantize(Decimal("0.01"), ROUND_HALF_UP)
