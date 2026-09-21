"""Unit tests for PolicyResolver, PolicyContext, PolicyResolution, and helpers."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.policy import (
    ContributionAxis,
    CostAxis,
    PolicyContext,
    PolicyResolution,
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


class TestTaxAxis:
    """TaxAxis holds all seven treatment values plus meta-statuses."""

    def test_ordinary(self) -> None:
        """ORDINARY maps to the string 'ordinary'."""
        assert TaxAxis.ORDINARY.value == "ordinary"

    def test_separate(self) -> None:
        """SEPARATE maps to the string 'separate'."""
        assert TaxAxis.SEPARATE.value == "separate"

    def test_substitute(self) -> None:
        """SUBSTITUTE maps to the string 'substitute'."""
        assert TaxAxis.SUBSTITUTE.value == "substitute"

    def test_exempt(self) -> None:
        """EXEMPT maps to the string 'exempt'."""
        assert TaxAxis.EXEMPT.value == "exempt"

    def test_non_cash_taxable(self) -> None:
        """NON_CASH_TAXABLE maps to the string 'non_cash_taxable'."""
        assert TaxAxis.NON_CASH_TAXABLE.value == "non_cash_taxable"

    def test_not_applicable(self) -> None:
        """NOT_APPLICABLE maps to the string 'not_applicable'."""
        assert TaxAxis.NOT_APPLICABLE.value == "not_applicable"

    def test_unknown(self) -> None:
        """UNKNOWN maps to the string 'unknown'."""
        assert TaxAxis.UNKNOWN.value == "unknown"


class TestContributionAxis:
    """ContributionAxis holds all six values."""

    def test_included(self) -> None:
        """INCLUDED maps to the string 'included'."""
        assert ContributionAxis.INCLUDED.value == "included"

    def test_excluded(self) -> None:
        """EXCLUDED maps to the string 'excluded'."""
        assert ContributionAxis.EXCLUDED.value == "excluded"

    def test_capped(self) -> None:
        """CAPPED maps to the string 'capped'."""
        assert ContributionAxis.CAPPED.value == "capped"

    def test_special_base(self) -> None:
        """SPECIAL_BASE maps to the string 'special_base'."""
        assert ContributionAxis.SPECIAL_BASE.value == "special_base"

    def test_not_applicable(self) -> None:
        """NOT_APPLICABLE maps to the string 'not_applicable'."""
        assert ContributionAxis.NOT_APPLICABLE.value == "not_applicable"

    def test_unknown(self) -> None:
        """UNKNOWN maps to the string 'unknown'."""
        assert ContributionAxis.UNKNOWN.value == "unknown"


class TestTfrAxis:
    """TfrAxis holds all five values."""

    def test_included(self) -> None:
        """INCLUDED maps to the string 'included'."""
        assert TfrAxis.INCLUDED.value == "included"

    def test_excluded(self) -> None:
        """EXCLUDED maps to the string 'excluded'."""
        assert TfrAxis.EXCLUDED.value == "excluded"

    def test_special(self) -> None:
        """SPECIAL maps to the string 'special'."""
        assert TfrAxis.SPECIAL.value == "special"

    def test_not_applicable(self) -> None:
        """NOT_APPLICABLE maps to the string 'not_applicable'."""
        assert TfrAxis.NOT_APPLICABLE.value == "not_applicable"

    def test_unknown(self) -> None:
        """UNKNOWN maps to the string 'unknown'."""
        assert TfrAxis.UNKNOWN.value == "unknown"


class TestCostAxis:
    """CostAxis holds all six values."""

    def test_employee_cash(self) -> None:
        """EMPLOYEE_CASH maps to the string 'employee_cash'."""
        assert CostAxis.EMPLOYEE_CASH.value == "employee_cash"

    def test_employer_cost(self) -> None:
        """EMPLOYER_COST maps to the string 'employer_cost'."""
        assert CostAxis.EMPLOYER_COST.value == "employer_cost"

    def test_third_party_cash(self) -> None:
        """THIRD_PARTY_CASH maps to the string 'third_party_cash'."""
        assert CostAxis.THIRD_PARTY_CASH.value == "third_party_cash"

    def test_accrual_only(self) -> None:
        """ACCRUAL_ONLY maps to the string 'accrual_only'."""
        assert CostAxis.ACCRUAL_ONLY.value == "accrual_only"

    def test_not_applicable(self) -> None:
        """NOT_APPLICABLE maps to the string 'not_applicable'."""
        assert CostAxis.NOT_APPLICABLE.value == "not_applicable"

    def test_unknown(self) -> None:
        """UNKNOWN maps to the string 'unknown'."""
        assert CostAxis.UNKNOWN.value == "unknown"


class TestPolicyContext:
    """PolicyContext stores contextual resolver inputs."""

    def test_required_fields_stored(self) -> None:
        """Year and as_of are required and stored correctly."""
        ctx = PolicyContext(year=2026, as_of=_TODAY)
        assert ctx.year == 2026
        assert ctx.as_of == _TODAY

    def test_optional_fields_default(self) -> None:
        """Optional fields default to None/False/zero when omitted."""
        ctx = PolicyContext(year=2026, as_of=_TODAY)
        assert ctx.ccnl_slug is None
        assert ctx.sector is None
        assert ctx.gross_ytd == Decimal(0)
        assert ctx.is_manager is False
        assert ctx.num_employees is None

    def test_optional_fields_stored(self) -> None:
        """Optional fields are stored when explicitly supplied."""
        ctx = PolicyContext(
            year=2026,
            as_of=_TODAY,
            ccnl_slug="test.json",
            sector="industria",
            gross_ytd=Decimal("50000.00"),
            is_manager=True,
            num_employees=15,
        )
        assert ctx.ccnl_slug == "test.json"
        assert ctx.sector == "industria"
        assert ctx.gross_ytd == Decimal("50000.00")
        assert ctx.is_manager is True
        assert ctx.num_employees == 15

    def test_frozen(self) -> None:
        """PolicyContext is immutable: attribute assignment raises AttributeError."""
        ctx = PolicyContext(year=2026, as_of=_TODAY)
        with pytest.raises(AttributeError):
            ctx.year = 2025  # type: ignore[misc]


class TestPolicyResolution:
    """PolicyResolution stores the per-axis treatment outcomes."""

    def _make(self) -> PolicyResolution:
        """Build a minimal PolicyResolution for assertions.

        Returns:
            A :class:`PolicyResolution` with ordinary tax and included axes.
        """
        return PolicyResolution(
            policy_id="it/earning/ordinary",
            policy_version="2026.1",
            effective_from=date(2000, 1, 1),
            effective_until=None,
            tax=TaxAxis.ORDINARY,
            contribution=ContributionAxis.INCLUDED,
            tfr=TfrAxis.INCLUDED,
            cost=CostAxis.EMPLOYEE_CASH,
            legal_basis="Art. 51 TUIR",
        )

    def test_fields_stored(self) -> None:
        """All fields are accessible after construction."""
        r = self._make()
        assert r.policy_id == "it/earning/ordinary"
        assert r.tax == TaxAxis.ORDINARY
        assert r.contribution == ContributionAxis.INCLUDED
        assert r.tfr == TfrAxis.INCLUDED
        assert r.cost == CostAxis.EMPLOYEE_CASH
        assert r.effective_until is None

    def test_frozen(self) -> None:
        """PolicyResolution is immutable: attribute assignment raises AttributeError."""
        r = self._make()
        with pytest.raises(AttributeError):
            r.tax = TaxAxis.EXEMPT  # type: ignore[misc]


class TestUnresolvablePolicyError:
    """UnresolvablePolicyError carries axis, policy_id, and the full resolution."""

    def _resolution(self) -> PolicyResolution:
        """Return a resolution with an UNKNOWN tax axis for exception tests.

        Returns:
            A :class:`PolicyResolution` with ``tax=TaxAxis.UNKNOWN``.
        """
        return PolicyResolution(
            policy_id="it/earning/arrears",
            policy_version="2026.1",
            effective_from=date(2000, 1, 1),
            effective_until=None,
            tax=TaxAxis.UNKNOWN,
            contribution=ContributionAxis.INCLUDED,
            tfr=TfrAxis.EXCLUDED,
            cost=CostAxis.EMPLOYEE_CASH,
            legal_basis="Art. 17 c.1 lett. b) TUIR",
        )

    def test_message_contains_axis_and_policy_id(self) -> None:
        """Exception message identifies the axis and policy_id."""
        r = self._resolution()
        exc = UnresolvablePolicyError("it/earning/arrears", "tax", r)
        assert "tax" in str(exc)
        assert "it/earning/arrears" in str(exc)

    def test_attributes_stored(self) -> None:
        """policy_id, axis, and resolution are accessible on the exception."""
        r = self._resolution()
        exc = UnresolvablePolicyError("it/earning/arrears", "tax", r)
        assert exc.policy_id == "it/earning/arrears"
        assert exc.axis == "tax"
        assert exc.resolution is r


class TestRequire:
    """require() asserts that an axis is not UNKNOWN."""

    def _resolution(self, tax: TaxAxis) -> PolicyResolution:
        """Build a PolicyResolution with the given tax axis.

        Returns:
            A :class:`PolicyResolution` for use in require() tests.
        """
        return PolicyResolution(
            policy_id="it/test",
            policy_version="test.1",
            effective_from=date(2000, 1, 1),
            effective_until=None,
            tax=tax,
            contribution=ContributionAxis.INCLUDED,
            tfr=TfrAxis.INCLUDED,
            cost=CostAxis.EMPLOYEE_CASH,
            legal_basis="Test",
        )

    def test_ok_axis_returns_resolution(self) -> None:
        """require() returns the resolution unchanged when axis is not UNKNOWN."""
        r = self._resolution(TaxAxis.ORDINARY)
        assert require(r, "tax") is r

    def test_unknown_axis_raises_unresolvable(self) -> None:
        """require() raises UnresolvablePolicyError when the axis is UNKNOWN."""
        r = self._resolution(TaxAxis.UNKNOWN)
        with pytest.raises(UnresolvablePolicyError) as exc_info:
            require(r, "tax")
        assert exc_info.value.axis == "tax"


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


class TestPolicyResolverLoad:
    """PolicyResolver.load() loads and indexes the bundled Italian ruleset."""

    def test_load_returns_resolver(self) -> None:
        """load() returns a PolicyResolver instance."""
        assert isinstance(PolicyResolver.load(), PolicyResolver)

    def test_load_resolves_base_salary_earning(self) -> None:
        """load() produces a resolver that resolves base_salary_earning."""
        resolver = PolicyResolver.load()
        result = resolver.resolve("base_salary_earning", _ctx())
        assert result is not None
        assert result.policy_id == "it/earning/ordinary"


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
        resolver = PolicyResolver.load()
        result = resolver.resolve("tfr_accrual_item", _ctx())
        assert result is not None
        assert result.tax == TaxAxis.NOT_APPLICABLE

    def test_contract_renewal_arrears_tax_unknown(self) -> None:
        """contract_renewal_arrears tax axis is UNKNOWN (context-dependent)."""
        resolver = PolicyResolver.load()
        result = resolver.resolve("contract_renewal_arrears", _ctx())
        assert result is not None
        assert result.tax == TaxAxis.UNKNOWN

    def test_productivity_bonus_tax_unknown(self) -> None:
        """productivity_bonus_earning tax axis is UNKNOWN (regime unknown)."""
        resolver = PolicyResolver.load()
        result = resolver.resolve("productivity_bonus_earning", _ctx())
        assert result is not None
        assert result.tax == TaxAxis.UNKNOWN

    def test_arrears_tax_require_raises(self) -> None:
        """require('tax') on arrears resolution raises UnresolvablePolicyError."""
        resolver = PolicyResolver.load()
        result = resolver.resolve("contract_renewal_arrears", _ctx())
        assert result is not None
        with pytest.raises(UnresolvablePolicyError):
            require(result, "tax")
