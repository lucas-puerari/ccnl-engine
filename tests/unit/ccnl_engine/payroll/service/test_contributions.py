"""Tests for INPS contribution breakdowns of standard, apprentice and domestic work."""

from decimal import Decimal

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.payroll.domain.contributions import (
    ContributionComponent,
)
from ccnl_engine.payroll.domain.employment import (
    FixedTerm,
    Permanent,
)
from ccnl_engine.payroll.domain.rounding import money
from tests.fixtures.contribution_rules import first_run_contributions, inps_year_rules
from tests.helpers import make_year_rules

_D = Decimal
_ZERO = Decimal(0)


class TestResolveContributions:
    """resolve_contributions: breakdown, IVS ceiling, and zero-rate branches."""

    def test_no_ceiling_uses_full_base_as_ivs_base(self) -> None:
        """When rules carry no ceiling, ivs_base equals the full period base."""
        rules = inps_year_rules(ceiling=None)
        base = _D("3000.00")
        bd = first_run_contributions(base, rules, Permanent(), None)
        # emp_ivs_rate == emp_rate, so employee total = base * ivs_rate
        expected_emp = money(base * rules.inps.employee_ivs_rate)  # type: ignore[union-attr]
        assert bd.employee == expected_emp
        # ivs_base == base because ceiling is None
        ivs_comp = next(c for c in bd.components if c.name == "ivs_employee")
        assert ivs_comp.base == base

    def test_ceiling_caps_ivs_base(self) -> None:
        """When ytd already consumed the ceiling, ivs_base is zero."""
        rules = inps_year_rules(ceiling="120000")
        ceiling = _D("120000")
        # Simulate ytd already at ceiling
        bd = first_run_contributions(
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
        bd = first_run_contributions(_D("3000.00"), rules, Permanent(), None)
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
        bd = first_run_contributions(_D("3000.00"), rules, Permanent(), None)
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
        bd = first_run_contributions(_D("3000.00"), rules, Permanent(), None)
        names = [c.name for c in bd.components]
        assert "non_ivs_employer" not in names
        assert "ivs_employer" in names

    def test_ivs_ceiling_not_applies_bypasses_ceiling(self) -> None:
        """ivs_ceiling_applies=False: full base used even when ceiling is set."""
        rules = inps_year_rules(ceiling="120000")
        base = _D("150000.00")
        bd_capped = first_run_contributions(
            base, rules, Permanent(), None, ivs_ceiling_applies=True
        )
        bd_uncapped = first_run_contributions(
            base, rules, Permanent(), None, ivs_ceiling_applies=False
        )
        assert bd_uncapped.employee > bd_capped.employee


class TestContributionAmounts:
    """resolve_contributions: totals and components derived by hand.

    Rates of ``inps_year_rules()``: employee 9.19% all IVS; employer 28.98% of which
    23.81% IVS, so 5.17% non-IVS (NASpI, CUAF, CIG) on the full base.
    """

    def test_permanent_components_and_totals(self) -> None:
        """Every component carries its base, rate and amount.

        base 3 000: ivs_employee 3 000 * 0.0919 = 275.70;
        ivs_employer 3 000 * 0.2381 = 714.30;
        non_ivs_employer 3 000 * 0.0517 = 155.10;
        employer = 714.30 + 155.10 = 869.40.
        """
        bd = first_run_contributions(
            _D("3000.00"), inps_year_rules(), Permanent(), None
        )
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
        bd = first_run_contributions(
            _D("3000.00"), inps_year_rules(), FixedTerm(), None
        )
        assert bd.employer == _D("911.40")

    def test_category_selects_employer_rate(self) -> None:
        """Impiegato: employer rate 24.71%, of which 23.81% IVS.

        non-IVS 0.2471 - 0.2381 = 0.0090; 3 000 * 0.0090 = 27.00;
        employer = 714.30 + 27.00 = 741.30.
        """
        bd = first_run_contributions(
            _D("3000.00"), inps_year_rules(), Permanent(), WorkerCategory.IMPIEGATO
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
        bd = first_run_contributions(
            _D("5000.00"), rules, Permanent(), None, ytd_inps_base=_D("120000.00")
        )
        assert bd.components[-1] == ContributionComponent(
            name="addizionale_1pct",
            base=_D("2295.00"),
            rate=_D("0.01"),
            amount=_D("22.95"),
        )
        assert bd.employee == _D("233.86")
