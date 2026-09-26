"""Unit tests for loading the bundled pay-item policy ruleset."""

from __future__ import annotations

from datetime import date

from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
from ccnl_engine.payroll.service.policy_loader import load_policy_resolver


def _ctx() -> PolicyContext:
    """Build a minimal PolicyContext for use in loader tests.

    Returns:
        A PolicyContext for 2026-01-15.
    """
    return PolicyContext(year=2026, as_of=date(2026, 1, 15))


class TestPolicyResolverLoad:
    """load_policy_resolver() loads and indexes the bundled Italian ruleset."""

    def test_load_returns_resolver(self) -> None:
        """load_policy_resolver() returns a PolicyResolver instance."""
        assert isinstance(load_policy_resolver(), PolicyResolver)

    def test_load_resolves_base_salary_earning(self) -> None:
        """The loaded resolver resolves base_salary_earning."""
        resolver = load_policy_resolver()
        result = resolver.resolve("base_salary_earning", _ctx())
        assert result is not None
        assert result.policy_id == "it/earning/ordinary"
