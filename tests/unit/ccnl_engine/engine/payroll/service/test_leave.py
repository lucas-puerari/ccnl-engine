"""Unit tests for the leave accrual service."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.engine.contract.domain.ccnl import LeaveEntitlementTier, LeaveRules
from ccnl_engine.engine.payroll.domain.supplements import LeaveInput
from ccnl_engine.engine.payroll.service.leave import _resolve_annual_days, compute_leave

_ZERO = Decimal(0)


def _rules_no_tiers() -> LeaveRules:
    return LeaveRules(default_annual_days=Decimal(20))


def _rules_with_tiers() -> LeaveRules:
    return LeaveRules(
        default_annual_days=Decimal(20),
        entitlement_tiers=[
            LeaveEntitlementTier(service_months_min=0, annual_days=Decimal(20)),
            LeaveEntitlementTier(service_months_min=36, annual_days=Decimal(25)),
        ],
    )


class TestResolveAnnualDays:
    """_resolve_annual_days selects the correct entitlement."""

    def test_no_tiers_returns_default(self) -> None:
        """No tiers: always return default."""
        assert _resolve_annual_days(_rules_no_tiers(), service_months=None) == Decimal(
            20
        )

    def test_service_months_none_returns_default(self) -> None:
        """Unknown seniority: always return default."""
        result = _resolve_annual_days(_rules_with_tiers(), service_months=None)
        assert result == Decimal(20)

    def test_below_threshold_returns_base_tier(self) -> None:
        """12 months: >= tier(0) but < tier(36) → 20 days."""
        assert _resolve_annual_days(_rules_with_tiers(), service_months=12) == Decimal(
            20
        )

    def test_exactly_at_threshold_returns_higher_tier(self) -> None:
        """36 months: >= tier(36) → 25 days."""
        assert _resolve_annual_days(_rules_with_tiers(), service_months=36) == Decimal(
            25
        )

    def test_above_threshold_returns_higher_tier(self) -> None:
        """48 months: >= tier(36) → 25 days."""
        assert _resolve_annual_days(_rules_with_tiers(), service_months=48) == Decimal(
            25
        )

    def test_no_eligible_tier_falls_back_to_default(self) -> None:
        """All tiers require >= 12 months; service_months=0 → default."""
        rules = LeaveRules(
            default_annual_days=Decimal(20),
            entitlement_tiers=[
                LeaveEntitlementTier(service_months_min=12, annual_days=Decimal(22)),
            ],
        )
        assert _resolve_annual_days(rules, service_months=0) == Decimal(20)


class TestComputeLeave:
    """compute_leave output values."""

    def test_zero_days_taken(self) -> None:
        """Zero taken days: balance equals accrual (20/12 = 1.67)."""
        rules = _rules_no_tiers()
        accrued, taken, balance = compute_leave(
            LeaveInput(taken_days=_ZERO), rules, service_months=None
        )
        assert accrued == Decimal("1.67")
        assert taken == _ZERO
        assert balance == Decimal("1.67")

    def test_3_days_taken_junior(self) -> None:
        """12 months: 20 days/year → 1.67/month; balance = 1.67 - 3 = -1.33."""
        rules = _rules_with_tiers()
        accrued, taken, balance = compute_leave(
            LeaveInput(taken_days=Decimal(3)), rules, service_months=12
        )
        assert accrued == Decimal("1.67")
        assert taken == Decimal(3)
        assert balance == Decimal("-1.33")

    def test_5_days_taken_senior(self) -> None:
        """48 months: 25 days/year → 2.08/month; balance = 2.08 - 5 = -2.92."""
        rules = _rules_with_tiers()
        accrued, taken, balance = compute_leave(
            LeaveInput(taken_days=Decimal(5)), rules, service_months=48
        )
        assert accrued == Decimal("2.08")
        assert taken == Decimal(5)
        assert balance == Decimal("-2.92")

    def test_balance_positive_when_no_days_taken(self) -> None:
        """Senior, no days taken: balance equals accrual (25/12 = 2.08)."""
        rules = _rules_with_tiers()
        accrued, taken, balance = compute_leave(
            LeaveInput(taken_days=_ZERO), rules, service_months=48
        )
        assert accrued == Decimal("2.08")
        assert taken == _ZERO
        assert balance == Decimal("2.08")
