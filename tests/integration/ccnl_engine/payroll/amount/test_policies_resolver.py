"""PolicyResolver: rules read from dicts and resolved for a context."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.payroll.amount.loaders_policy import load_policy_resolver
from ccnl_engine.payroll.amount.policies import (
    ContributionAxis,
    CostAxis,
    PolicyContext,
    PolicyResolver,
    TaxAxis,
    TfrAxis,
    UnresolvablePolicyError,
    _Rule,
    require,
)

_TODAY = date(2026, 1, 15)
_FUTURE = date(2030, 1, 1)


def _ctx(as_of: date = _TODAY) -> PolicyContext:
    """Build a minimal PolicyContext for use in resolver tests.

    Returns:
        A :class:`PolicyContext` with default zero values and given date.
    """
    return PolicyContext(year=as_of.year, as_of=as_of)


def _rule(
    kind: str,
    effective_from: date = date(2000, 1, 1),
    effective_until: date | None = None,
    tax: str = "ordinary",
    contribution: str = "included",
    tfr: str = "included",
    cost: str = "employee_cash",
) -> _Rule:
    """Build a minimal _Rule for use in PolicyResolver construction tests.

    Returns:
        A :class:`_Rule` instance covering a single kind.
    """
    return _Rule(
        policy_id="test/rule",
        policy_version="test.1",
        kinds=(kind,),
        effective_from=effective_from,
        effective_until=effective_until,
        tax=tax,
        contribution=contribution,
        tfr=tfr,
        cost=cost,
        legal_basis="Test",
    )


class TestRuleFromDict:
    """_Rule.from_dict() parses raw JSON dicts with optional effective_until."""

    def test_with_effective_until(self) -> None:
        """from_dict() parses effective_until when it is a non-null string."""
        d: dict[str, object] = {
            "policy_id": "it/test",
            "policy_version": "1.0",
            "kinds": ["bonus_earning"],
            "effective_from": "2020-01-01",
            "effective_until": "2024-12-31",
            "tax": "ordinary",
            "contribution": "included",
            "tfr": "excluded",
            "cost": "employee_cash",
            "legal_basis": "Art. 51 TUIR",
        }
        rule = _Rule.from_dict(d)
        assert rule.effective_until == date(2024, 12, 31)
        assert rule.effective_from == date(2020, 1, 1)
        assert rule.kinds == ("bonus_earning",)

    def test_without_effective_until(self) -> None:
        """from_dict() stores None when effective_until is null."""
        d: dict[str, object] = {
            "policy_id": "it/test",
            "policy_version": "1.0",
            "kinds": ["base_salary_earning"],
            "effective_from": "2000-01-01",
            "effective_until": None,
            "tax": "ordinary",
            "contribution": "included",
            "tfr": "included",
            "cost": "employee_cash",
            "legal_basis": "Art. 51 TUIR",
        }
        rule = _Rule.from_dict(d)
        assert rule.effective_until is None


class TestPolicyResolverResolve:
    """PolicyResolver.resolve() matches kinds to rules by date range."""

    def test_kind_not_found_returns_none(self) -> None:
        """resolve() returns None for an unknown pay-item kind."""
        resolver = PolicyResolver([_rule("bonus_earning")])
        assert resolver.resolve("nonexistent_kind", _ctx()) is None

    def test_as_of_before_effective_from_skips_rule(self) -> None:
        """resolve() skips a rule whose effective_from is after as_of."""
        resolver = PolicyResolver([_rule("bonus_earning", effective_from=_FUTURE)])
        assert resolver.resolve("bonus_earning", _ctx(_TODAY)) is None

    def test_effective_until_none_matches_any_future_date(self) -> None:
        """A rule with effective_until=None matches any date after effective_from."""
        resolver = PolicyResolver([
            _rule("bonus_earning", effective_from=date(2000, 1, 1))
        ])
        result = resolver.resolve("bonus_earning", _ctx(_TODAY))
        assert result is not None
        assert result.effective_until is None

    def test_within_bounded_range_matches(self) -> None:
        """resolve() returns a resolution when as_of falls within a bounded rule."""
        resolver = PolicyResolver([
            _rule(
                "bonus_earning",
                effective_from=date(2020, 1, 1),
                effective_until=date(2029, 12, 31),
            )
        ])
        result = resolver.resolve("bonus_earning", _ctx(_TODAY))
        assert result is not None
        assert result.effective_until == date(2029, 12, 31)

    def test_as_of_after_effective_until_skips_rule(self) -> None:
        """resolve() skips a rule whose effective_until is before as_of."""
        resolver = PolicyResolver([
            _rule("bonus_earning", effective_until=date(2019, 12, 31))
        ])
        assert resolver.resolve("bonus_earning", _ctx(_TODAY)) is None

    def test_loop_exhausted_returns_none(self) -> None:
        """resolve() returns None when all rules for a kind fail date checks."""
        resolver = PolicyResolver([
            _rule(
                "bonus_earning",
                effective_from=date(2000, 1, 1),
                effective_until=date(2010, 12, 31),
            ),
            _rule(
                "bonus_earning",
                effective_from=_FUTURE,
            ),
        ])
        assert resolver.resolve("bonus_earning", _ctx(_TODAY)) is None

    def test_first_matching_rule_returned(self) -> None:
        """resolve() returns the first matching rule, not subsequent ones."""
        rule1 = _rule("bonus_earning", tax="ordinary")
        rule2 = _rule("bonus_earning", tax="exempt")
        resolver = PolicyResolver([rule1, rule2])
        result = resolver.resolve("bonus_earning", _ctx())
        assert result is not None
        assert result.tax == TaxAxis.ORDINARY

    def test_resolution_fields_populated(self) -> None:
        """PolicyResolution returned by resolve() has correct axis values."""
        resolver = PolicyResolver([
            _rule(
                "bonus_earning",
                tax="ordinary",
                contribution="included",
                tfr="excluded",
                cost="employee_cash",
            )
        ])
        result = resolver.resolve("bonus_earning", _ctx())
        assert result is not None
        assert result.tax == TaxAxis.ORDINARY
        assert result.contribution == ContributionAxis.INCLUDED
        assert result.tfr == TfrAxis.EXCLUDED
        assert result.cost == CostAxis.EMPLOYEE_CASH


class TestMisclassificationFixes:
    """The bundled ruleset correctly classifies the three fixed items."""

    def test_tfr_accrual_tax_not_applicable(self) -> None:
        """tfr_accrual_item tax axis is NOT_APPLICABLE at accrual time."""
        resolver = load_policy_resolver()
        result = resolver.resolve("tfr_accrual_item", _ctx())
        assert result is not None
        assert result.tax == TaxAxis.NOT_APPLICABLE

    def test_contract_renewal_arrears_tax_unknown(self) -> None:
        """contract_renewal_arrears tax axis is UNKNOWN (context-dependent)."""
        resolver = load_policy_resolver()
        result = resolver.resolve("contract_renewal_arrears", _ctx())
        assert result is not None
        assert result.tax == TaxAxis.UNKNOWN

    def test_productivity_bonus_tax_substitute(self) -> None:
        """productivity_bonus_earning tax axis is SUBSTITUTE (L. 199/2025)."""
        resolver = load_policy_resolver()
        result = resolver.resolve("productivity_bonus_earning", _ctx())
        assert result is not None
        assert result.tax == TaxAxis.SUBSTITUTE

    def test_arrears_tax_require_raises(self) -> None:
        """require('tax') on arrears resolution raises UnresolvablePolicyError."""
        resolver = load_policy_resolver()
        result = resolver.resolve("contract_renewal_arrears", _ctx())
        assert result is not None
        with pytest.raises(UnresolvablePolicyError):
            require(result, "tax")
