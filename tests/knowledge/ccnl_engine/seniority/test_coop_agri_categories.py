"""Cooperative e consorzi agricoli: seniority of impiegati and operai.

Art. 49 (stesura 3 agosto 2022, p. 67): impiegati, a biennial increment of
1° EUR 33.05, 2° 29.44, 3° 26.86, 4° 24.79, 6° 23.76, 7° 22.21, "nel numero
massimo di 12". Art. 61 (p. 81): operai a tempo indeterminato, from 1 July
2006 3° EUR 12.20, 4° 11.93, 5° 11.39, 6° 10.85, 7° 9.44, "nel numero massimo
di 5".
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.seniority.rules import _seniority_amount, seniority_maximum

if TYPE_CHECKING:
    from ccnl_engine.seniority.models import SeniorityIncrements

_SLUG = "cooperative-consorzi-agricoli"
_AS_OF = date(2026, 6, 1)


def _increments() -> SeniorityIncrements:
    increments = load_ccnl(_SLUG).parameters.seniority_increments
    assert increments is not None
    return increments


@pytest.mark.parametrize(
    ("category", "level", "amount"),
    [
        (WorkerCategory.IMPIEGATO, "3", "26.86"),
        (WorkerCategory.IMPIEGATO, "7", "22.21"),
        (WorkerCategory.OPERAIO, "3", "12.20"),
        (WorkerCategory.OPERAIO, "5", "11.39"),
        (WorkerCategory.IMPIEGATO, "1", "33.05"),
    ],
)
def test_each_category_has_its_own_amount(
    category: WorkerCategory, level: str, amount: str
) -> None:
    """One increment of the level, by category."""
    assert _seniority_amount(
        _increments(),
        level,
        1,
        _AS_OF,
        worker_category=category,
        is_apprentice=False,
        seniority_months=None,
    ) == Decimal(amount)


@pytest.mark.parametrize(
    ("category", "maximum"),
    [(WorkerCategory.OPERAIO, 5), (WorkerCategory.IMPIEGATO, 12)],
)
def test_operai_stop_at_five_increments(category: WorkerCategory, maximum: int) -> None:
    """Art. 61: at most 5 for the operai; art. 49: 12 for the impiegati."""
    assert seniority_maximum(_increments(), "4", category) == maximum


def test_levels_3_to_7_need_the_category() -> None:
    """Both articles price levels 3-7: the category decides the amount."""
    increments = _increments()
    assert all(increments.requires_category(c) for c in ("3", "4", "5", "6", "7"))
    assert not increments.requires_category("1")
