"""CNEL 105782 art. 22: category-sensitive sector seniority and biennial scatti."""

from datetime import date
from decimal import Decimal

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.seniority.earned import EarnedIncrements
from ccnl_engine.seniority.repricing.rules import earned_seniority
from ccnl_engine.seniority.rules import (
    _resolve_seniority_count,
    _seniority_amount,
    increments_apply,
)


def test_impiegato_two_scatti() -> None:
    """At level 5, 48 months yield 2 x EUR 80.03 = EUR 160.06 monthly."""
    rules = load_ccnl("multiservizi-anip").parameters.seniority_increments
    assert rules is not None
    count = _resolve_seniority_count(
        rules, "5", None, 48, worker_category=WorkerCategory.IMPIEGATO
    )
    assert count == 2
    assert _seniority_amount(
        rules,
        "5",
        count,
        date(2025, 8, 1),
        worker_category=WorkerCategory.IMPIEGATO,
        is_apprentice=False,
        seniority_months=48,
    ) == Decimal("160.06")


def test_operaio_four_years_and_category_at_mixed_level() -> None:
    """At level 6, month 47 pays zero; month 48 pays EUR 82.99, once only."""
    rules = load_ccnl("multiservizi-anip").parameters.seniority_increments
    assert rules is not None
    assert (
        _resolve_seniority_count(
            rules, "6", None, 47, worker_category=WorkerCategory.OPERAIO
        )
        == 0
    )
    count = _resolve_seniority_count(
        rules, "6", None, 48, worker_category=WorkerCategory.OPERAIO
    )
    assert count == 1
    assert (
        _resolve_seniority_count(
            rules, "6", None, 96, worker_category=WorkerCategory.OPERAIO
        )
        == 1
    )
    assert _seniority_amount(
        rules,
        "6",
        count,
        date(2025, 8, 1),
        worker_category=WorkerCategory.OPERAIO,
        is_apprentice=False,
        seniority_months=48,
    ) == Decimal("82.99")
    assert not increments_apply(rules, "3", WorkerCategory.IMPIEGATO, apprentice=False)


def test_promotion_preserves_stated_matured_amount() -> None:
    """Two level-5 scatti at EUR 73.60 remain EUR 147.20 at level 6 after promotion."""
    rules = load_ccnl("multiservizi-anip").parameters.seniority_increments
    assert rules is not None
    assert earned_seniority(
        rules,
        "6",
        EarnedIncrements(2, Decimal("147.20")),
        48,
        60,
        date(2025, 8, 1),
        worker_category=WorkerCategory.IMPIEGATO,
    ) == Decimal("147.20")
    assert earned_seniority(
        rules,
        "6",
        EarnedIncrements(2, Decimal("147.20")),
        48,
        72,
        date(2025, 8, 1),
        worker_category=WorkerCategory.IMPIEGATO,
    ) == Decimal("242.42")  # EUR 147.20 + EUR 95.22 at the new level.
