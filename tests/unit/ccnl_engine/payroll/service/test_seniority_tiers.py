"""Seniority increments of a tiered ladder: counts and amounts."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.contract.seniority.models import (
    SeniorityIncrements,
    SeniorityTier,
)
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.service.seniority_tiers import (
    count_from_tiers,
    resolve_tier_amount,
)
from tests.helpers import TEST_PROV, _series

_AS_OF = date(2026, 6, 1)


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


class TestCountFromTiers:
    """count_from_tiers multi-tier counting."""

    def test_single_tier_basic(self) -> None:
        """Single tier correctly counts increments and caps at maximum_count."""
        tier = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 5,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        assert count_from_tiers((tier,), 48) == 2
        assert count_from_tiers((tier,), 0) == 0
        assert count_from_tiers((tier,), 120) == 5

    def test_multi_tier_boundary(self) -> None:
        """Multi-tier count correctly crosses tier boundaries."""
        t1 = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 3,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        t2 = SeniorityTier.model_validate({
            "cadence_months": 48,
            "maximum_count": 2,
            "amount_by_level": {"L1": _series("15.00")},
            "provenance": TEST_PROV,
        })
        assert count_from_tiers((t1, t2), 72 + 48) == 4
        assert count_from_tiers((t1, t2), 72) == 3


class TestResolveTierAmount:
    """resolve_tier_amount month-based, count-based, and error paths."""

    def test_month_based_single_tier(self) -> None:
        """Month-based dispatch returns correct amount for a single tier."""
        t1 = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 3,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        result = resolve_tier_amount((t1,), "L1", _AS_OF, seniority_months=48)
        assert result == Decimal("20.00")

    def test_month_based_loop_no_break(self) -> None:
        """Loop exits normally (no break) when months exactly fill a tier."""
        t1 = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 3,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        result = resolve_tier_amount((t1,), "L1", _AS_OF, seniority_months=72)
        assert result == Decimal("30.00")

    def test_count_based_all_tiers_consumed_no_break(self) -> None:
        """count_override consuming all tiers exits the loop without break."""
        inc = _tiered_increments()
        result = resolve_tier_amount(inc.tiers, "L1", _AS_OF, count_override=5)
        assert result == Decimal("60.00")

    def test_both_none_raises(self) -> None:
        """Raises InvalidInputError when both month/count inputs are None."""
        t1 = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 3,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        with pytest.raises(InvalidInputError, match="seniority_months is required"):
            resolve_tier_amount((t1,), "L1", _AS_OF)
