"""The minimi di area of the operai agricoli renewal of 28 May 2026.

Verbale di accordo of 28 May 2026, Art. 50 and Allegato n. 1 (signed text,
sha256 487f3412d7fdb68c80b4d7e5cff223888c34ce51fc109b6a9ebdecda689dd6fa), read
on 18 October 2026: the 3.4% from 1 June 2026 and the 1.7% from 1 January 2027
raise the provincial salari contrattuali; the minimi di area of Allegato n. 1
already include both ("comprensivi degli aumenti di cui al precedente
capoverso"), are the salary of 28 May 2026 times 1.051 printed to three
decimals, half up, and apply from 1 June 2026 in the provinces without a
contratto provinciale (by 1 January 2029 at the latest elsewhere).
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("operai-agricoli-florovivaisti")
#: Area, salary in force on 28 May 2026, minimo of Allegato n. 1.
_TABLE = (
    ("Area1", "1458.61", "1532.999"),
    ("Area2", "1330.25", "1398.093"),
    ("Area3", "991.85", "1042.434"),
)


@pytest.mark.parametrize(("area", "base", "minimo"), _TABLE)
def test_the_minimo_di_area_applies_from_june_2026(
    area: str, base: str, minimo: str
) -> None:
    """The minimo of Allegato n. 1, both tranches included, from June 2026."""
    salary = _CCNL.level_by_code(area).base_salary
    may = Decimal(base)
    paid = Decimal(minimo).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    assert salary.value_at(date(2026, 5, 28)) == may
    assert salary.value_at(date(2026, 6, 1)) == paid
    assert salary.value_at(date(2027, 1, 1)) == paid
    assert (may * Decimal("1.051")).quantize(
        Decimal("0.001"), rounding=ROUND_HALF_UP
    ) == Decimal(minimo)
