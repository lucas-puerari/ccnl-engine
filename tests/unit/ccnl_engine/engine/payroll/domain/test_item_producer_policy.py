"""Unit tests for PayItemPolicy.resolve() and _resolve() registry lookup."""

from __future__ import annotations

from datetime import date

from ccnl_engine.engine.payroll.domain.item_producer_policy import (
    POLICY_REGISTRY,
    _resolve,
)
from ccnl_engine.engine.payroll.domain.pay_items import (
    ContributionTreatment,
    CostTreatment,
    PayItemPolicy,
    PolicyDecision,
    TaxTreatment,
    TfrTreatment,
)

# ---------------------------------------------------------------------------
# PayItemPolicy.resolve() branches
# ---------------------------------------------------------------------------


class TestPayItemPolicyResolve:
    """PayItemPolicy.resolve() returns a PolicyDecision or None."""

    def _policy(
        self, kinds: tuple[str, ...], until: date | None = None
    ) -> PayItemPolicy:
        decision = PolicyDecision(
            policy_id="test",
            policy_version="1.0",
            effective_from=date(2020, 1, 1),
            effective_until=until,
            tax_treatment=TaxTreatment.ORDINARY,
            contribution_treatment=ContributionTreatment.INCLUDED,
            tfr_treatment=TfrTreatment.INCLUDED,
            cost_treatment=CostTreatment.EMPLOYEE_CASH,
            legal_basis="test",
        )
        return PayItemPolicy(
            policy_id="test",
            policy_version="1.0",
            applies_to_kinds=kinds,
            effective_from=date(2020, 1, 1),
            effective_until=until,
            default_decision=decision,
        )

    def test_kind_not_in_applies_to_returns_none(self) -> None:
        """Returns None when kind is not in applies_to_kinds."""
        policy = self._policy(("base_salary_earning",))
        result = policy.resolve("seniority_earning", date(2026, 6, 1))
        assert result is None

    def test_as_of_before_effective_from_returns_none(self) -> None:
        """Returns None when as_of is before effective_from."""
        policy = self._policy(("base_salary_earning",))
        result = policy.resolve("base_salary_earning", date(2019, 12, 31))
        assert result is None

    def test_as_of_after_effective_until_returns_none(self) -> None:
        """Returns None when as_of is after effective_until."""
        policy = self._policy(("base_salary_earning",), until=date(2025, 12, 31))
        result = policy.resolve("base_salary_earning", date(2026, 1, 1))
        assert result is None

    def test_valid_with_no_until_returns_decision(self) -> None:
        """Returns default_decision when effective_until is None and dates are valid."""
        policy = self._policy(("base_salary_earning",))
        result = policy.resolve("base_salary_earning", date(2026, 6, 1))
        assert result is not None
        assert result.tax_treatment == TaxTreatment.ORDINARY

    def test_valid_within_period_returns_decision(self) -> None:
        """Returns default_decision when as_of is within the effective period."""
        policy = self._policy(("base_salary_earning",), until=date(2026, 12, 31))
        result = policy.resolve("base_salary_earning", date(2026, 6, 1))
        assert result is not None


# ---------------------------------------------------------------------------
# _resolve() — registry lookup
# ---------------------------------------------------------------------------


class TestResolveFunction:
    """_resolve() returns None for unknown kinds, PolicyDecision for known."""

    def test_unknown_kind_returns_none(self) -> None:
        """Returns None when kind is not in POLICY_REGISTRY."""
        result = _resolve("completely_unknown_kind", date(2026, 6, 1))
        assert result is None

    def test_known_kind_returns_decision(self) -> None:
        """Returns a PolicyDecision for a registered kind."""
        result = _resolve("base_salary_earning", date(2026, 6, 1))
        assert result is not None
        assert result.tax_treatment == TaxTreatment.ORDINARY

    def test_all_registered_kinds_resolve(self) -> None:
        """Every kind in POLICY_REGISTRY resolves to a decision."""
        for kind in POLICY_REGISTRY:
            assert _resolve(kind, date(2026, 6, 1)) is not None
