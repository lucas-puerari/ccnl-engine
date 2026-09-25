"""Tests for engine.contributions — rate resolution, INPS and TFR calculations."""

from decimal import Decimal

import pytest

from ccnl_engine.engine.tax.domain.rules import InpsRates, YearRules
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.payroll.service.contributions import (
    inps_contribution,
    inps_employee_additional,
    resolve_contributions,
    resolve_rates,
    tfr,
)
from ccnl_engine.payroll.service.rounding import money
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
        assert resolve_rates(_rules(), Permanent(), "impiegato").employer_rate == _D(
            "0.2471"
        )
        assert resolve_rates(_rules(), Permanent(), "operaio").employer_rate == _D(
            "0.2898"
        )

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
                rules, Apprentice(months_elapsed=m), "impiegato"
            ).employer_rate
            for m in (0, 12, 24)
        ] == [_D("0.0311"), _D("0.0461"), _D("0.1161")]


class TestInpsContribution:
    """inps_contribution() with and without ceiling."""

    def test_uncapped_no_ceiling(self) -> None:
        """No ceiling configured: flat rate on the full base."""
        result = inps_contribution(
            _D("24972.50"),
            _D("0.0919"),
            _D("0.0919"),
            _rules(),
            ivs_ceiling_applies=True,
        )
        assert result == _D("2294.97")

    def test_ceiling_not_applies(self) -> None:
        """ivs_ceiling_applies=False: flat rate even when ceiling is set."""
        result = inps_contribution(
            _D("150000.00"),
            _D("0.3050"),
            _D("0.2381"),
            _rules("119650.00"),
            ivs_ceiling_applies=False,
        )
        assert result == _D("150000.00") * _D("0.3050")

    def test_ceiling_base_below(self) -> None:
        """Ceiling applies but base < ceiling: IVS and non-IVS both on full base."""
        total_rate = _D("0.3050")
        ivs_rate = _D("0.2381")
        base = _D("80000.00")
        result = inps_contribution(
            base,
            total_rate,
            ivs_rate,
            _rules("119650.00"),
            ivs_ceiling_applies=True,
        )
        assert result == base * total_rate

    def test_ceiling_base_above_splits_correctly(self) -> None:
        """Ceiling applies and base > ceiling: IVS portion capped, non-IVS uncapped."""
        total_rate = _D("0.3050")
        ivs_rate = _D("0.2381")
        non_ivs_rate = total_rate - ivs_rate
        base = _D("150000.00")
        ceiling = _D("119650.00")
        result = inps_contribution(
            base,
            total_rate,
            ivs_rate,
            _rules("119650.00"),
            ivs_ceiling_applies=True,
        )
        expected = money(ceiling * ivs_rate + base * non_ivs_rate)
        assert result == expected


class TestTfr:
    """tfr() accrual."""

    def test_standard(self) -> None:
        """TFR = base / 13.5, rounded to nearest cent."""
        assert tfr(_D("24972.50"), _rules()) == _D("1849.81")


class TestResolveRatesGuard:
    """resolve_rates() raises when rules.inps or rules.apprentice is None."""

    def test_none_inps_raises(self) -> None:
        """Domestic rules (inps=None) must raise TypeError from resolve_rates."""
        domestic_rules = make_domestic_year_rules()
        with pytest.raises(TypeError, match="resolve_rates requires standard INPS"):
            resolve_rates(domestic_rules, Permanent(), None)


def _rates_with_additional(
    *,
    ceiling: str | None = "122295.00",
    additional_rate: str | None = "0.01",
    additional_threshold: str | None = "56224.00",
) -> InpsRates:
    """Build InpsRates with optional additional contribution fields.

    Returns:
        InpsRates instance with the given ceiling and additional-rate fields.
    """
    return InpsRates(
        employee_rate=_D("0.0949"),
        employee_ivs_rate=_D("0.0949"),
        employer_rate=_D("0.3050"),
        employer_ivs_rate=_D("0.2381"),
        ceiling=_D(ceiling) if ceiling is not None else None,
        employee_additional_rate=(
            _D(additional_rate) if additional_rate is not None else None
        ),
        employee_additional_threshold=(
            _D(additional_threshold) if additional_threshold is not None else None
        ),
    )


class TestInpsEmployeeAdditional:
    """Unit tests for inps_employee_additional()."""

    def test_rates_none_returns_zero(self) -> None:
        """When rates is None, return zero."""
        assert inps_employee_additional(
            _D("70000"), None, ivs_ceiling_applies=False
        ) == _D(0)

    def test_additional_rate_none_returns_zero(self) -> None:
        """When additional fields are absent (both None), return zero."""
        rates = _rates_with_additional(additional_rate=None, additional_threshold=None)
        assert inps_employee_additional(
            _D("70000"), rates, ivs_ceiling_applies=False
        ) == _D(0)

    def test_additional_both_none_explicit(self) -> None:
        """Both additional fields None: additional contribution not configured."""
        rates = _rates_with_additional(additional_rate=None, additional_threshold=None)
        assert inps_employee_additional(
            _D("100000"), rates, ivs_ceiling_applies=True
        ) == _D(0)

    def test_income_below_threshold_returns_zero(self) -> None:
        """Earnings below the threshold: no additional charge."""
        rates = _rates_with_additional()
        assert inps_employee_additional(
            _D("50000"), rates, ivs_ceiling_applies=False
        ) == _D(0)

    def test_income_at_threshold_returns_zero(self) -> None:
        """Earnings exactly at threshold: excess is zero."""
        rates = _rates_with_additional()
        assert inps_employee_additional(
            _D("56224"), rates, ivs_ceiling_applies=False
        ) == _D(0)

    def test_income_above_threshold_no_ceiling(self) -> None:
        """70 000 - 56 224 = 13 776; 1% = 137.76. No IVS ceiling applied."""
        rates = _rates_with_additional()
        result = inps_employee_additional(_D("70000"), rates, ivs_ceiling_applies=False)
        assert result == _D("137.76")

    def test_ivs_ceiling_caps_base(self) -> None:
        """IVS ceiling applies; base > ceiling: (122 295 - 56 224) * 1% = 660.71."""
        rates = _rates_with_additional()
        result = inps_employee_additional(_D("130000"), rates, ivs_ceiling_applies=True)
        assert result == _D("660.71")

    def test_ivs_ceiling_not_reached(self) -> None:
        """Base below ceiling; ceiling irrelevant: (70 000 - 56 224) * 1% = 137.76."""
        rates = _rates_with_additional()
        result = inps_employee_additional(_D("70000"), rates, ivs_ceiling_applies=True)
        assert result == _D("137.76")

    def test_no_ceiling_configured(self) -> None:
        """No ceiling: base uncapped. (70 000 - 56 224) * 1% = 137.76."""
        rates = _rates_with_additional(ceiling=None)
        result = inps_employee_additional(_D("70000"), rates, ivs_ceiling_applies=True)
        assert result == _D("137.76")


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
