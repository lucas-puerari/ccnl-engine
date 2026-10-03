"""Seniority increment counting and amounts, flat and tiered."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.contract.domain.seniority import (
    SeniorityIncrements,
)
from ccnl_engine.payroll.service.seniority import (
    _resolve_seniority_count,
    _seniority_amount,
    seniority_first_cadence,
    seniority_maximum,
)
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.helpers import TEST_PROV, _series

_AS_OF = date(2026, 6, 1)


def _flat_increments(
    *,
    cadence: int = 24,
    maximum: int = 5,
    amount: str = "10.00",
    excluded_categories: tuple[str, ...] = (),
    apprentice_amount: str | None = None,
    first_cadence_months: int | None = None,
    first_cadence_months_by_category: dict[str, int] | None = None,
    amount_by_level_by_category: dict[str, dict[str, str]] | None = None,
    maximum_count_by_category: dict[str, int] | None = None,
) -> SeniorityIncrements:
    """Build a flat-mode :class:`SeniorityIncrements` for testing.

    Returns:
        A :class:`SeniorityIncrements` with the given parameters.
    """
    raw: dict[str, Any] = {
        "cadence_months": cadence,
        "maximum_count": maximum,
        "amount_by_level": {"L1": _series(amount)},
        "provenance": TEST_PROV,
        "excluded_categories": list(excluded_categories),
    }
    if apprentice_amount is not None:
        raw["apprentice_amount"] = _series(apprentice_amount)
    if first_cadence_months is not None:
        raw["first_cadence_months"] = first_cadence_months
    if first_cadence_months_by_category:
        raw["first_cadence_months_by_category"] = first_cadence_months_by_category
    if amount_by_level_by_category:
        raw["amount_by_level_by_category"] = {
            cat: {code: _series(v) for code, v in levels.items()}
            for cat, levels in amount_by_level_by_category.items()
        }
    if maximum_count_by_category:
        raw["maximum_count_by_category"] = maximum_count_by_category
    return SeniorityIncrements.model_validate(raw)


def _tiered_increments() -> SeniorityIncrements:
    """Build a two-tier :class:`SeniorityIncrements` for testing.

    Returns:
        A :class:`SeniorityIncrements` with 3 increments at 24-month cadence
        then 2 at 48-month cadence.
    """
    return SeniorityIncrements.model_validate({
        "cadence_months": 24,
        "maximum_count": 5,
        "amount_by_level": {},
        "tiers": [
            {
                "cadence_months": 24,
                "maximum_count": 3,
                "amount_by_level": {"L1": _series("10.00")},
                "provenance": TEST_PROV,
            },
            {
                "cadence_months": 48,
                "maximum_count": 2,
                "amount_by_level": {"L1": _series("15.00")},
                "provenance": TEST_PROV,
            },
        ],
        "provenance": TEST_PROV,
    })


class TestSeniorityLookups:
    """seniority_first_cadence and seniority_maximum override paths."""

    def test_first_cadence_category_override(self) -> None:
        """Category override takes precedence over per-level and global values."""
        inc = _flat_increments(
            cadence=24,
            first_cadence_months=36,
            first_cadence_months_by_category={"operaio": 24},
        )
        assert (
            seniority_first_cadence(inc, "L1", worker_category=WorkerCategory.OPERAIO)
            == 24
        )
        assert (
            seniority_first_cadence(inc, "L1", worker_category=WorkerCategory.IMPIEGATO)
            == 36
        )

    def test_maximum_category_override(self) -> None:
        """Category override to maximum_count_by_category takes precedence."""
        inc = _flat_increments(
            cadence=24,
            maximum=5,
            maximum_count_by_category={"operaio": 3},
        )
        assert seniority_maximum(inc, "L1", worker_category=WorkerCategory.OPERAIO) == 3
        assert (
            seniority_maximum(inc, "L1", worker_category=WorkerCategory.IMPIEGATO) == 5
        )


class TestResolveSeniorityCount:
    """_resolve_seniority_count edge cases."""

    def test_exceeds_maximum_raises(self) -> None:
        """Raises InvalidInputError when seniority_count > maximum."""
        inc = _flat_increments(cadence=24, maximum=3)
        with pytest.raises(InvalidInputError, match="exceeds the maximum"):
            _resolve_seniority_count(
                inc, "L1", seniority_count=10, seniority_months=None
            )

    def test_excluded_category_returns_zero(self) -> None:
        """Excluded category returns 0 regardless of months elapsed."""
        inc = _flat_increments(cadence=24, maximum=5, excluded_categories=("operaio",))
        count = _resolve_seniority_count(
            inc,
            "L1",
            seniority_count=None,
            seniority_months=72,
            worker_category=WorkerCategory.OPERAIO,
        )
        assert count == 0

    def test_tiered_increments_uses_count_from_tiers(self) -> None:
        """Tiered mode dispatches to _count_from_tiers."""
        inc = _tiered_increments()
        count = _resolve_seniority_count(
            inc, "L1", seniority_count=None, seniority_months=48
        )
        assert count == 2

    def test_below_first_cadence_returns_zero(self) -> None:
        """seniority_months below first_cadence yields count=0."""
        inc = _flat_increments(cadence=24, maximum=5, first_cadence_months=36)
        count = _resolve_seniority_count(
            inc, "L1", seniority_count=None, seniority_months=24
        )
        assert count == 0

    def test_count_within_max_returns_count(self) -> None:
        """seniority_count within maximum is returned unchanged."""
        inc = _flat_increments(cadence=24, maximum=5)
        count = _resolve_seniority_count(
            inc, "L1", seniority_count=3, seniority_months=None
        )
        assert count == 3


class TestSeniorityAmount:
    """_seniority_amount paths: excluded category, apprentice, tiered, category."""

    def test_excluded_category_returns_zero(self) -> None:
        """Excluded category yields zero seniority amount."""
        inc = _flat_increments(cadence=24, maximum=5, excluded_categories=("operaio",))
        result = _seniority_amount(
            inc,
            "L1",
            count=3,
            as_of=_AS_OF,
            worker_category=WorkerCategory.OPERAIO,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal(0)

    def test_apprentice_uses_apprentice_amount(self) -> None:
        """Apprentices use apprentice_amount * count."""
        inc = _flat_increments(cadence=24, maximum=5, apprentice_amount="5.00")
        result = _seniority_amount(
            inc,
            "L1",
            count=2,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=True,
            seniority_months=None,
        )
        assert result == Decimal("10.00")

    def test_apprentice_no_apprentice_amount_returns_zero(self) -> None:
        """Apprentices return zero when apprentice_amount is None."""
        inc = _flat_increments(cadence=24, maximum=5)
        result = _seniority_amount(
            inc,
            "L1",
            count=2,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=True,
            seniority_months=None,
        )
        assert result == Decimal(0)

    def test_category_specific_amounts(self) -> None:
        """Category-specific amount table takes precedence over level table."""
        inc = _flat_increments(
            cadence=24,
            maximum=5,
            amount="10.00",
            amount_by_level_by_category={"operaio": {"L1": "7.00"}},
            maximum_count_by_category={"operaio": 5},
        )
        result = _seniority_amount(
            inc,
            "L1",
            count=3,
            as_of=_AS_OF,
            worker_category=WorkerCategory.OPERAIO,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal("21.00")

    def test_category_no_level_override_falls_through_to_level(self) -> None:
        """Category present but no override for this level falls to amount_by_level."""
        inc = _flat_increments(
            cadence=24,
            maximum=5,
            amount="10.00",
            amount_by_level_by_category={"operaio": {"L2": "7.00"}},
            maximum_count_by_category={"operaio": 5},
        )
        result = _seniority_amount(
            inc,
            "L1",
            count=2,
            as_of=_AS_OF,
            worker_category=WorkerCategory.OPERAIO,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal("20.00")

    def test_tiered_uses_months(self) -> None:
        """Tiered mode uses seniority_months when provided."""
        inc = _tiered_increments()
        result = _seniority_amount(
            inc,
            "L1",
            count=3,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=False,
            seniority_months=72,
        )
        assert result == Decimal("30.00")

    def test_tiered_falls_back_to_count(self) -> None:
        """Tiered mode uses count when seniority_months is None."""
        inc = _tiered_increments()
        result = _seniority_amount(
            inc,
            "L1",
            count=2,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal("20.00")

    def test_level_not_in_amounts_returns_zero(self) -> None:
        """Unknown level code with no entry in amount_by_level returns zero."""
        inc = _flat_increments(cadence=24, maximum=5, amount="10.00")
        result = _seniority_amount(
            inc,
            "UNKNOWN_LEVEL",
            count=3,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal(0)
