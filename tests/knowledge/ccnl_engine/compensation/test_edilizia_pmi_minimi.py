"""The minimi of the CCNL Edilizia CONFAPI ANIEM and its open limitations.

Testo armonizzato of the renewal of 15 April 2025 (FILLEA CGIL, sha256
25828567c377c4892c46d6e1c47734aef275933f4a3619ee74dc424fd080dcba), read on
14 October 2026: Allegato A (operai, p. 187) and Allegato B (impiegati,
p. 188).  One file holds both categories with 13 monthly payments, so the
impiegati premio annuo (Art. 64) and the Edilcassa accrual of the operai
(Art. 16 and 18) are declared limitations.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("edilizia-pmi-confapi-aniem")
_TRANCHES = (date(2025, 4, 1), date(2027, 3, 1))
_TABLE = (
    ("1", ("1087.99", "1162.99")),
    ("2", ("1272.94", "1360.69")),
    ("3", ("1414.38", "1511.88")),
    ("4", ("1523.17", "1628.17")),
    ("5", ("1631.98", "1744.48")),
    ("6", ("1958.36", "2093.36")),
    ("7", ("2175.96", "2325.96")),
)


@pytest.mark.parametrize(("level", "amounts"), _TABLE)
def test_each_tranche_of_the_allegati(level: str, amounts: tuple[str, ...]) -> None:
    """The printed minimo from each tranche, the day before the second too."""
    salary = _CCNL.level_by_code(level).base_salary
    first, second = (Decimal(a) for a in amounts)

    assert salary.value_at(_TRANCHES[0]) == first
    assert salary.value_at(_TRANCHES[1] - timedelta(days=1)) == first
    assert salary.value_at(_TRANCHES[1]) == second


def test_monthly_payment_gaps_are_declared() -> None:
    """Each category whose monthly payments differ from 13 is blocked."""
    scopes = {
        note.limitation.variant: note.limitation.applies_when.worker_categories
        for note in _CCNL.coverage.notes
        if note.limitation is not None
    }

    employees = frozenset({"impiegato", "quadro"})

    assert scopes["impiegati_premio_annuo_missing"] == employees
    assert scopes["cassa_edile_accruals_missing"] == frozenset({"operaio"})
