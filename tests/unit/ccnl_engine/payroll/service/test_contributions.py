"""Tests for contribution rate resolution and INPS contribution breakdowns."""

from decimal import Decimal

import pytest

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.payroll.domain.contributions import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.payroll.domain.employment import (
    Apprentice,
    FixedTerm,
    Permanent,
)
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service._contributions_rates import resolve_rates
from ccnl_engine.payroll.service.contributions import resolve_contributions
from ccnl_engine.tax.domain.ruleset import YearRules
from tests.helpers import make_domestic_year_rules, make_year_rules

_D = Decimal
_ZERO = Decimal(0)


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


def _contributions(
    base: Decimal,
    rules: YearRules,
    contract: Permanent | FixedTerm | Apprentice,
    category: WorkerCategory | None,
    *,
    ytd_inps_base: Decimal = _ZERO,
    ivs_ceiling_applies: bool = True,
) -> ContributionBreakdown:
    """Resolve contributions, first run of the year and massimale applied.

    Returns:
        The breakdown of ``resolve_contributions``.
    """
    return resolve_contributions(
        base,
        rules,
        contract,
        category,
        ytd_inps_base=ytd_inps_base,
        ivs_ceiling_applies=ivs_ceiling_applies,
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
        bd = _contributions(base, rules, Permanent(), None)
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
        bd = _contributions(
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
        bd = _contributions(_D("3000.00"), rules, Permanent(), None)
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
        bd = _contributions(_D("3000.00"), rules, Permanent(), None)
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
        bd = _contributions(_D("3000.00"), rules, Permanent(), None)
        names = [c.name for c in bd.components]
        assert "non_ivs_employer" not in names
        assert "ivs_employer" in names

    def test_ivs_ceiling_not_applies_bypasses_ceiling(self) -> None:
        """ivs_ceiling_applies=False: full base used even when ceiling is set."""
        rules = _rules(ceiling="120000")
        base = _D("150000.00")
        bd_capped = _contributions(
            base, rules, Permanent(), None, ivs_ceiling_applies=True
        )
        bd_uncapped = _contributions(
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
        bd = _contributions(
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
        bd = _contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("60000.00")
        )
        comp = next((c for c in bd.components if c.name == "addizionale_1pct"), None)
        assert comp is not None
        assert comp.base == _D("1000.00")

    def test_addizionale_not_emitted_below_threshold(self) -> None:
        """No component when cumulative stays below threshold."""
        rules = self._rules_with_additional()
        bd = _contributions(
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
        bd = _contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("60000.00")
        )
        names = {c.name for c in bd.components}
        assert "addizionale_1pct" not in names

    def test_addizionale_added_to_employee_total(self) -> None:
        """Employee total includes the addizionale amount."""
        rules = self._rules_with_additional()
        bd_without = _contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("1000.00")
        )
        bd_with = _contributions(
            _D("1000.00"), rules, Permanent(), None, ytd_inps_base=_D("60000.00")
        )
        assert bd_with.employee > bd_without.employee


class TestContributionAmounts:
    """resolve_contributions: totals and components derived by hand.

    Rates of ``_rules()``: employee 9.19% all IVS; employer 28.98% of which
    23.81% IVS, so 5.17% non-IVS (NASpI, CUAF, CIG) on the full base.
    """

    def test_permanent_components_and_totals(self) -> None:
        """Every component carries its base, rate and amount.

        base 3 000: ivs_employee 3 000 * 0.0919 = 275.70;
        ivs_employer 3 000 * 0.2381 = 714.30;
        non_ivs_employer 3 000 * 0.0517 = 155.10;
        employer = 714.30 + 155.10 = 869.40.
        """
        bd = _contributions(_D("3000.00"), _rules(), Permanent(), None)
        assert bd.components == (
            ContributionComponent(
                name="ivs_employee",
                base=_D("3000.00"),
                rate=_D("0.0919"),
                amount=_D("275.70"),
            ),
            ContributionComponent(
                name="ivs_employer",
                base=_D("3000.00"),
                rate=_D("0.2381"),
                amount=_D("714.30"),
            ),
            ContributionComponent(
                name="non_ivs_employer",
                base=_D("3000.00"),
                rate=_D("0.0517"),
                amount=_D("155.10"),
            ),
        )
        assert (bd.employee, bd.employer) == (_D("275.70"), _D("869.40"))

    def test_fixed_term_employer_pays_naspi_addizionale(self) -> None:
        """Fixed term: +1.40% non-IVS employer rate (Art. 2 c. 28 L. 92/2012).

        non-IVS 0.2898 + 0.014 - 0.2381 = 0.0657; 3 000 * 0.0657 = 197.10;
        employer = 714.30 + 197.10 = 911.40.
        """
        bd = _contributions(_D("3000.00"), _rules(), FixedTerm(), None)
        assert bd.employer == _D("911.40")

    def test_category_selects_employer_rate(self) -> None:
        """Impiegato: employer rate 24.71%, of which 23.81% IVS.

        non-IVS 0.2471 - 0.2381 = 0.0090; 3 000 * 0.0090 = 27.00;
        employer = 714.30 + 27.00 = 741.30.
        """
        bd = _contributions(
            _D("3000.00"), _rules(), Permanent(), WorkerCategory.IMPIEGATO
        )
        assert bd.employer == _D("741.30")

    def test_addizionale_base_stops_at_the_massimale(self) -> None:
        """The 1% addizionale applies only up to the IVS massimale.

        INPS circ. 4/2026, with the IVS massimale at 122 295
        and threshold 56 224; ytd 120 000, period 5 000:
        IVS base = 122 295 - 120 000 = 2 295; 2 295 * 0.0919 = 210.91;
        addizionale base = (122 295 - 56 224) - (120 000 - 56 224) = 2 295,
        amount 2 295 * 0.01 = 22.95; employee = 210.91 + 22.95 = 233.86.
        """
        rules = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2381",
                "employer_ivs_rate": "0.2381",
                "ceiling": "122295.00",
                "employee_additional_rate": "0.01",
                "employee_additional_threshold": "56224.00",
            }
        )
        bd = _contributions(
            _D("5000.00"), rules, Permanent(), None, ytd_inps_base=_D("120000.00")
        )
        assert bd.components[-1] == ContributionComponent(
            name="addizionale_1pct",
            base=_D("2295.00"),
            rate=_D("0.01"),
            amount=_D("22.95"),
        )
        assert bd.employee == _D("233.86")


def _ivs_bases(breakdown: ContributionBreakdown) -> tuple[Decimal, Decimal]:
    """Return the bases of the employee and employer IVS components.

    Returns:
        ``(ivs_employee base, ivs_employer base)``.
    """
    bases = {c.name: c.base for c in breakdown.components}
    return bases["ivs_employee"], bases["ivs_employer"]


class TestMassimaleBoundary:
    """The 2026 massimale of 122 295 EUR around its boundary.

    Rates of ``_rules()``: employee 9.19% all IVS; employer 28.98% of which
    23.81% IVS and 5.17% non-IVS.  YTD INPS base 120 000, so the headroom
    left under the massimale is 122 295 - 120 000 = 2 295.00.
    """

    _YTD = _D("120000.00")

    def _both(self, period: str) -> tuple[ContributionBreakdown, ...]:
        rules = _rules(ceiling="122295.00")
        return tuple(
            _contributions(
                _D(period),
                rules,
                Permanent(),
                None,
                ytd_inps_base=self._YTD,
                ivs_ceiling_applies=applies,
            )
            for applies in (True, False)
        )

    def test_one_cent_below_the_massimale_is_not_capped(self) -> None:
        """Period 2 294.99: YTD after 122 294.99, under the massimale.

        IVS base 2 294.99 in both branches; employee 2 294.99 * 0.0919 =
        210.909581 -> 210.91; employer 2 294.99 * 0.2381 = 546.437119 ->
        546.44 plus 2 294.99 * 0.0517 = 118.650983 -> 118.65, total 665.09.
        """
        capped, uncapped = self._both("2294.99")
        assert capped == uncapped
        assert _ivs_bases(capped) == (_D("2294.99"), _D("2294.99"))
        assert (capped.employee, capped.employer) == (_D("210.91"), _D("665.09"))

    def test_exactly_the_massimale_is_not_capped(self) -> None:
        """Period 2 295.00 reaches the massimale without exceeding it.

        IVS base 2 295.00 in both branches; employee 2 295 * 0.0919 =
        210.9105 -> 210.91; employer 546.4395 -> 546.44 plus 118.6515 ->
        118.65, total 665.09.
        """
        capped, uncapped = self._both("2295.00")
        assert capped == uncapped
        assert (capped.employee, capped.employer) == (_D("210.91"), _D("665.09"))

    def test_one_cent_above_the_massimale_caps_the_ivs_base(self) -> None:
        """Period 2 295.01: one cent beyond the massimale.

        Capped IVS base 2 295.00, uncapped 2 295.01; the non-IVS employer
        share stays on the full 2 295.01 (* 0.0517 = 118.652017 -> 118.65).
        """
        capped, uncapped = self._both("2295.01")
        assert _ivs_bases(capped) == (_D("2295.00"), _D("2295.00"))
        assert _ivs_bases(uncapped) == (_D("2295.01"), _D("2295.01"))
        non_ivs = {c.name: c for c in capped.components}["non_ivs_employer"]
        assert (non_ivs.base, non_ivs.amount) == (_D("2295.01"), _D("118.65"))

    def test_ytd_already_above_the_massimale(self) -> None:
        """YTD 125 000 is past the massimale: no IVS on the 3 000 of the run.

        Capped: employee 0; employer only non-IVS 3 000 * 0.0517 = 155.10.
        Uncapped: employee 3 000 * 0.0919 = 275.70; employer 3 000 * 0.2381 =
        714.30 plus 155.10 = 869.40.
        """
        rules = _rules(ceiling="122295.00")
        capped, uncapped = (
            _contributions(
                _D("3000.00"),
                rules,
                Permanent(),
                None,
                ytd_inps_base=_D("125000.00"),
                ivs_ceiling_applies=applies,
            )
            for applies in (True, False)
        )
        assert (capped.employee, capped.employer) == (_D("0.00"), _D("155.10"))
        assert (uncapped.employee, uncapped.employer) == (
            _D("275.70"),
            _D("869.40"),
        )
