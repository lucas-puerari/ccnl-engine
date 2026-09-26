"""Tests for contribution rate resolution and INPS contribution breakdowns."""

from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.payroll.service._contributions_rates import resolve_rates
from ccnl_engine.payroll.service.contributions import (
    resolve_contributions,
)
from ccnl_engine.payroll.service.rounding import money
from ccnl_engine.tax.domain.ruleset import YearRules
from tests.helpers import make_domestic_year_rules, make_year_rules

_D = Decimal


def _rules(ceiling: str | None = None) -> YearRules:
    """Build minimal YearRules with configurable INPS ceiling.

    Returns:
        A YearRules instance with the specified ceiling value.
    """
    return make_year_rules(
        inps={
            "employee_rate": "0.0919",
            "employee_ivs_rate": "0.0919",
            "employer_rate": "0.2898",
            "employer_ivs_rate": "0.2381",
            "ceiling": ceiling,
            "employer_rate_by_category": {"impiegato": "0.2471"},
        },
        apprentice={
            "employee_rate": "0.0584",
            "employee_ivs_rate": "0.0584",
            "employer_rate_months_0_11": "0.0311",
            "employer_ivs_rate_months_0_11": "0.0150",
            "employer_rate_months_12_23": "0.0461",
            "employer_ivs_rate_months_12_23": "0.0300",
            "employer_rate_after": "0.1161",
            "employer_ivs_rate_after": "0.1000",
        },
    )


class TestResolveRates:
    """resolve_rates() by employment type and worker category."""

    def test_permanent(self) -> None:
        """Permanent: sector rates unchanged."""
        r = resolve_rates(_rules(), Permanent(), None)
        assert (r.employee_rate, r.employer_rate) == (_D("0.0919"), _D("0.2898"))

    def test_permanent_category_override(self) -> None:
        """Category-specific employer rate applies when the category matches."""
        assert resolve_rates(
            _rules(), Permanent(), WorkerCategory.IMPIEGATO
        ).employer_rate == _D("0.2471")
        assert resolve_rates(
            _rules(), Permanent(), WorkerCategory.OPERAIO
        ).employer_rate == _D("0.2898")

    def test_fixed_term_adds_naspi(self) -> None:
        """Fixed-term: employer rate + fixed_term_additional_rate."""
        r = resolve_rates(_rules(), FixedTerm(), None)
        assert r.employer_rate == _D("0.3038")

    def test_apprentice_by_months(self) -> None:
        """Apprentice: statutory employee rate, employer rate stepping by months."""
        rules = _rules()
        assert resolve_rates(rules, Apprentice(months_elapsed=0), None) == (
            resolve_rates(rules, Apprentice(months_elapsed=11), None)
        )
        assert resolve_rates(
            rules, Apprentice(months_elapsed=0), None
        ).employee_rate == (_D("0.0584"))
        assert [
            resolve_rates(
                rules, Apprentice(months_elapsed=m), WorkerCategory.IMPIEGATO
            ).employer_rate
            for m in (0, 12, 24)
        ] == [_D("0.0311"), _D("0.0461"), _D("0.1161")]


class TestResolveRatesGuard:
    """resolve_rates() raises when rules.inps or rules.apprentice is None."""

    def test_none_inps_raises(self) -> None:
        """Domestic rules (inps=None) must raise TypeError from resolve_rates."""
        domestic_rules = make_domestic_year_rules()
        with pytest.raises(TypeError, match="resolve_rates requires standard INPS"):
            resolve_rates(domestic_rules, Permanent(), None)


class TestResolveContributions:
    """resolve_contributions: breakdown, IVS ceiling, and zero-rate branches."""

    def test_no_ceiling_uses_full_base_as_ivs_base(self) -> None:
        """When rules carry no ceiling, ivs_base equals the full period base."""
        rules = _rules(ceiling=None)
        base = _D("3000.00")
        bd = resolve_contributions(base, rules, Permanent(), None)
        # emp_ivs_rate == emp_rate, so employee total = base * ivs_rate
        expected_emp = money(base * rules.inps.employee_ivs_rate)  # type: ignore[union-attr]
        assert bd.employee == expected_emp
        # ivs_base == base because ceiling is None
        ivs_comp = next(c for c in bd.components if c.name == "ivs_employee")
        assert ivs_comp.base == base

    def test_ceiling_caps_ivs_base(self) -> None:
        """When ytd already consumed the ceiling, ivs_base is zero."""
        rules = _rules(ceiling="120000")
        ceiling = _D("120000")
        # Simulate ytd already at ceiling
        bd = resolve_contributions(
            _D("3000.00"), rules, Permanent(), None, ytd_inps_base=ceiling
        )
        # IVS components should have base=0
        ivs_emp = next((c for c in bd.components if c.name == "ivs_employee"), None)
        if ivs_emp is not None:
            assert ivs_emp.base == _D(0)

    def test_emp_ivs_rate_zero_skips_ivs_employee_component(self) -> None:
        """When employee_ivs_rate == 0 no ivs_employee component is emitted."""
        rules = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0000",
                "employer_rate": "0.2381",
                "employer_ivs_rate": "0.2381",
                "ceiling": None,
                "employer_rate_by_category": {},
            }
        )
        bd = resolve_contributions(_D("3000.00"), rules, Permanent(), None)
        names = [c.name for c in bd.components]
        assert "ivs_employee" not in names
        assert "non_ivs_employee" in names

    def test_er_ivs_rate_zero_skips_ivs_employer_component(self) -> None:
        """When employer_ivs_rate == 0 no ivs_employer component is emitted."""
        rules = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2898",
                "employer_ivs_rate": "0.0000",
                "ceiling": None,
                "employer_rate_by_category": {},
            }
        )
        bd = resolve_contributions(_D("3000.00"), rules, Permanent(), None)
        names = [c.name for c in bd.components]
        assert "ivs_employer" not in names
        assert "non_ivs_employer" in names

    def test_er_non_ivs_rate_zero_skips_non_ivs_employer_component(self) -> None:
        """When employer_rate == employer_ivs_rate no non_ivs_employer component."""
        rules = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2381",
                "employer_ivs_rate": "0.2381",
                "ceiling": None,
                "employer_rate_by_category": {},
            }
        )
        bd = resolve_contributions(_D("3000.00"), rules, Permanent(), None)
        names = [c.name for c in bd.components]
        assert "non_ivs_employer" not in names
        assert "ivs_employer" in names

    def test_ivs_ceiling_not_applies_bypasses_ceiling(self) -> None:
        """ivs_ceiling_applies=False: full base used even when ceiling is set."""
        rules = _rules(ceiling="120000")
        base = _D("150000.00")
        bd_capped = resolve_contributions(
            base, rules, Permanent(), None, ivs_ceiling_applies=True
        )
        bd_uncapped = resolve_contributions(
            base, rules, Permanent(), None, ivs_ceiling_applies=False
        )
        assert bd_uncapped.employee > bd_capped.employee


class TestAddizionale1Pct:
    """resolve_contributions: 1% addizionale INPS (INPS circ. 4/2026)."""

    def _rules_with_additional(self) -> YearRules:
        return make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2898",
                "employer_ivs_rate": "0.2381",
                "ceiling": None,
                "employee_additional_rate": "0.01",
                "employee_additional_threshold": "56224.00",
            }
        )

    def test_addizionale_emitted_on_threshold_crossing(self) -> None:
        """Component appears when period base crosses the threshold."""
        rules = self._rules_with_additional()
        # ytd=56000, period=1000 → ytd_after=57000 → excess_after=776, excess_before=0
        bd = resolve_contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("56000.00")
        )
        names = {c.name for c in bd.components}
        assert "addizionale_1pct" in names
        comp = next(c for c in bd.components if c.name == "addizionale_1pct")
        assert comp.base == _D("776.00")
        assert comp.amount == money(_D("776.00") * _D("0.01"))

    def test_addizionale_emitted_when_ytd_already_over_threshold(self) -> None:
        """Entire period is excess when ytd already past threshold."""
        rules = self._rules_with_additional()
        # ytd=60000 > 56224 → excess_before=3776, excess_after=4776 → period_excess=1000
        bd = resolve_contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("60000.00")
        )
        comp = next((c for c in bd.components if c.name == "addizionale_1pct"), None)
        assert comp is not None
        assert comp.base == _D("1000.00")

    def test_addizionale_not_emitted_below_threshold(self) -> None:
        """No component when cumulative stays below threshold."""
        rules = self._rules_with_additional()
        bd = resolve_contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("1000.00")
        )
        names = {c.name for c in bd.components}
        assert "addizionale_1pct" not in names

    def test_addizionale_not_emitted_without_rate_configured(self) -> None:
        """No component when employee_additional_rate is absent from rules."""
        rules = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2898",
                "employer_ivs_rate": "0.2381",
                "ceiling": None,
            }
        )
        bd = resolve_contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("60000.00")
        )
        names = {c.name for c in bd.components}
        assert "addizionale_1pct" not in names

    def test_addizionale_added_to_employee_total(self) -> None:
        """Employee total includes the addizionale amount."""
        rules = self._rules_with_additional()
        bd_without = resolve_contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("1000.00")
        )
        bd_with = resolve_contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("60000.00")
        )
        assert bd_with.employee > bd_without.employee
