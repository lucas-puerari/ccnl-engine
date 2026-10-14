"""The tranches of the operai agricoli renewal of 28 May 2026.

Verbale di accordo of 28 May 2026, Art. 50 and Allegato n. 1 (signed text,
sha256 487f3412d7fdb68c80b4d7e5cff223888c34ce51fc109b6a9ebdecda689dd6fa), read
on 14 October 2026: the salaries in force on 28 May 2026 rise by 3.4% from 1
June 2026 and by a further 1.7% of the same base from 1 January 2027, and the
minimi of area of Allegato n. 1 are that base times 1.051, printed to three
decimals, half up, and paid to the cent.  Every area is pinned at both tranches.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("operai-agricoli-florovivaisti.json")
#: Area, salary in force on 28 May 2026, minimo of Allegato n. 1.
_TABLE = (
    ("Area1", "1458.61", "1532.999"),
    ("Area2", "1330.25", "1398.093"),
    ("Area3", "991.85", "1042.434"),
)


@pytest.mark.parametrize(("area", "base", "minimo"), _TABLE)
def test_both_tranches_apply_to_the_salary_of_28_may(
    area: str, base: str, minimo: str
) -> None:
    """3.4% from June 2026; 5.1% of the same base from January 2027."""
    salary = _CCNL.level_by_code(area).base_salary
    may = Decimal(base)

    assert salary.value_at(date(2026, 5, 28)) == may
    assert salary.value_at(date(2026, 6, 1)) == (may * Decimal("1.034")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    assert salary.value_at(date(2027, 1, 1)) == Decimal(minimo).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    assert (may * Decimal("1.051")).quantize(
        Decimal("0.001"), rounding=ROUND_HALF_UP
    ) == Decimal(minimo)
