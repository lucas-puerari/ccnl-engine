"""PayItemPolicy.resolve() scope by kind and effective period."""

from __future__ import annotations

from datetime import date

from ccnl_engine.payroll.amount.policies_pay_item import (
    PayItemPolicy,
    PolicyDecision,
)
from ccnl_engine.payroll.amount.types_treatment import (
    ContributionTreatment,
    CostTreatment,
    TaxTreatment,
    TfrTreatment,
)

_AS_OF = date(2026, 6, 1)


def _policy_decision() -> PolicyDecision:
    """Build a minimal :class:`PolicyDecision` for testing.

    Returns:
        A :class:`PolicyDecision` with ordinary tax treatment.
    """
    return PolicyDecision(
        policy_id="test/pol",
        policy_version="1.0",
        effective_from=date(2020, 1, 1),
        effective_until=None,
        tax_treatment=TaxTreatment.ORDINARY,
        contribution_treatment=ContributionTreatment.INCLUDED,
        tfr_treatment=TfrTreatment.INCLUDED,
        cost_treatment=CostTreatment.EMPLOYEE_CASH,
        legal_basis="Test",
    )


def _policy(
    *,
    kinds: tuple[str, ...] = ("base_salary",),
    from_: date = date(2020, 1, 1),
    until: date | None = None,
) -> PayItemPolicy:
    """Build a minimal :class:`PayItemPolicy` for testing.

    Returns:
        A :class:`PayItemPolicy` covering the given kinds and period.
    """
    return PayItemPolicy(
        policy_id="test/pol",
        policy_version="1.0",
        applies_to_kinds=kinds,
        effective_from=from_,
        effective_until=until,
        default_decision=_policy_decision(),
    )


class TestPayItemPolicyResolve:
    """PayItemPolicy.resolve() out-of-scope branches."""

    def test_kind_not_in_applies_to_kinds_returns_none(self) -> None:
        """resolve() returns None when the kind is not in applies_to_kinds."""
        pol = _policy(kinds=("base_salary",))
        assert pol.resolve("bonus", date(2025, 1, 1)) is None

    def test_as_of_before_effective_from_returns_none(self) -> None:
        """resolve() returns None when as_of is before effective_from."""
        pol = _policy(from_=date(2025, 1, 1))
        assert pol.resolve("base_salary", date(2020, 6, 1)) is None

    def test_as_of_after_effective_until_returns_none(self) -> None:
        """resolve() returns None when as_of is after effective_until."""
        pol = _policy(until=date(2024, 12, 31))
        assert pol.resolve("base_salary", date(2025, 6, 1)) is None

    def test_in_scope_returns_decision(self) -> None:
        """resolve() returns the default_decision when kind and date are in scope."""
        pol = _policy(from_=date(2020, 1, 1), until=date(2030, 12, 31))
        assert pol.resolve("base_salary", _AS_OF) is not None
