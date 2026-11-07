"""The stipendio and scatti of the CCNL of the Banche di Credito Cooperativo.

Testo coordinato of the CCNL of 9 July 2024, signed on 19 December 2024
(Eutekne reproduction, sha256
57296bd057cdff080b59e7d771d5c42e4a8da2c2032e5f26a8657a597fc5c622), read on
14 October 2026: Allegato A, "Tabella trattamento economico" (p. 149), Art. 46
(p. 63) and Art. 101 (p. 117).  Every level at each of the three tranches,
the day before each later one still paying the tranche before.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

_CCNL = load_ccnl("bcc-credito-cooperativo")
_TRANCHES = (date(2024, 9, 1), date(2025, 1, 1), date(2026, 1, 1))
_TABLE = (
    ("QD4", ("4978.66", "5059.28", "5160.06")),
    ("QD3", ("4239.27", "4309.32", "4396.88")),
    ("QD2", ("3815.86", "3882.36", "3965.48")),
    ("QD1", ("3600.61", "3663.99", "3743.21")),
    ("3AP4", ("3206.90", "3266.90", "3341.90")),
    ("3AP3", ("2943.02", "2994.78", "3059.49")),
    ("3AP2", ("2780.38", "2829.28", "2890.41")),
    ("3AP1", ("2637.95", "2684.35", "2742.34")),
    ("2AP2", ("2474.19", "2517.71", "2572.11")),
    ("2AP1", ("2315.18", "2355.90", "2406.80")),
    ("1AP", ("2156.20", "2194.12", "2241.53")),
)


@pytest.mark.parametrize(("level", "amounts"), _TABLE)
def test_each_tranche_of_allegato_a(level: str, amounts: tuple[str, ...]) -> None:
    """The printed stipendio from each tranche."""
    salary = _CCNL.level_by_code(level).base_salary
    values = [Decimal(a) for a in amounts]

    for start, value in zip(_TRANCHES, values, strict=True):
        assert salary.value_at(start) == value
    for start, previous in zip(_TRANCHES[1:], values, strict=False):
        assert salary.value_at(start - timedelta(days=1)) == previous


def test_thirteen_monthly_payments() -> None:
    """Art. 46: the tredicesima is the only further monthly payment."""
    months = _CCNL.parameters.additional_months.value_at(date(2026, 1, 1))

    assert months == 13


def test_scatti_of_later_hires() -> None:
    """Art. 101: 8 scatti, 7 for the 3rd and 4th level of the quadri."""
    seniority = _CCNL.parameters.seniority_increments

    assert seniority.maximum_count == 8
    assert dict(seniority.maximum_count_by_level) == {"QD3": 7, "QD4": 7}
    assert (seniority.cadence_months, seniority.first_cadence_months) == (36, 48)
