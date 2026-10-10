"""Tests for the 1% addizionale and the IVS massimale of a contribution breakdown."""

from decimal import Decimal

from ccnl_engine.payroll.domain.contributions import (
    ContributionBreakdown,
)
from ccnl_engine.payroll.domain.employment import (
    Permanent,
)
from ccnl_engine.payroll.service.additional_ivs import AdditionalIvsPosition
from ccnl_engine.payroll.service.contributions import resolve_contributions
from ccnl_engine.tax.annual.models import YearRules
from tests.fixtures.contribution_rules import first_run_contributions, inps_year_rules
from tests.helpers import make_year_rules

_D = Decimal
_ZERO = Decimal(0)


#: INPS circ. 6/2026 par. 5: 1%, 56,224.00 a year, 4,685.00 a month.
_ADDITIONAL = {
    "rate": "0.01",
    "annual_threshold": "56224.00",
    "monthly_threshold": "4685.00",
}


class TestAddizionale1Pct:
    """resolve_contributions wires the additional 1% IVS (circ. 6/2026 par. 5).

    The arithmetic of the rule is tested in ``test_additional_ivs``; here
    the component reaches the breakdown and the employee total.
    """

    def _rules_with_additional(self) -> YearRules:
        return make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2898",
                "employer_ivs_rate": "0.2381",
                "ceiling": None,
                "employee_additional": _ADDITIONAL,
            }
        )

    def test_month_above_the_monthly_threshold(self) -> None:
        """Period 5,000, YTD 1,000: 5,000 - 4,685 = 315; x 1% = 3.15."""
        bd = first_run_contributions(
            _D("5000.00"),
            self._rules_with_additional(),
            Permanent(),
            None,
            ytd_inps_base=_D("1000.00"),
        )
        comp = next(c for c in bd.components if c.name == "addizionale_1pct")
        assert (comp.base, comp.amount) == (_D("315.00"), _D("3.15"))
        # 5,000 x 9.19% = 459.50, plus the 3.15.
        assert bd.employee == _D("462.65")

    def test_month_below_the_monthly_threshold_ignores_the_ytd(self) -> None:
        """Period 1,000 with YTD 60,000 above 56,224: no component."""
        bd = first_run_contributions(
            _D("1000.00"),
            self._rules_with_additional(),
            Permanent(),
            None,
            ytd_inps_base=_D("60000.00"),
        )
        assert "addizionale_1pct" not in {c.name for c in bd.components}

    def test_settlement_reaches_the_employee_total(self) -> None:
        """Settling YTD 60,000 + 1,000 with 40.00 withheld.

        61,000 - 56,224 = 4,776; x 1% = 47.76; less 40.00: 7.76.
        Employee: 1,000 x 9.19% = 91.90 + 7.76 = 99.66.
        """
        bd = resolve_contributions(
            _D("1000.00"),
            self._rules_with_additional(),
            Permanent(),
            None,
            ytd_inps_base=_D("60000.00"),
            ivs_ceiling_applies=True,
            additional=AdditionalIvsPosition(withheld=_D("40.00"), settles=True),
        )
        comp = bd.components[-1]
        assert comp.name == "addizionale_1pct_conguaglio"
        assert (comp.base, comp.amount) == (_D("4776.00"), _D("7.76"))
        assert bd.employee == _D("99.66")

    def test_addizionale_not_emitted_without_rate_configured(self) -> None:
        """No component when the rules carry no additional 1% IVS."""
        rules = make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2898",
                "employer_ivs_rate": "0.2381",
                "ceiling": None,
            }
        )
        bd = first_run_contributions(
            _D("9000.00"), rules, Permanent(), None, ytd_inps_base=_D("60000.00")
        )
        names = {c.name for c in bd.components}
        assert "addizionale_1pct" not in names


def _ivs_bases(breakdown: ContributionBreakdown) -> tuple[Decimal, Decimal]:
    """Return the bases of the employee and employer IVS components.

    Returns:
        ``(ivs_employee base, ivs_employer base)``.
    """
    bases = {c.name: c.base for c in breakdown.components}
    return bases["ivs_employee"], bases["ivs_employer"]


class TestMassimaleBoundary:
    """The 2026 massimale of 122 295 EUR around its boundary.

    Rates of ``inps_year_rules()``: employee 9.19% all IVS; employer 28.98% of which
    23.81% IVS and 5.17% non-IVS.  YTD INPS base 120 000, so the headroom
    left under the massimale is 122 295 - 120 000 = 2 295.00.
    """

    _YTD = _D("120000.00")

    def _both(self, period: str) -> tuple[ContributionBreakdown, ...]:
        rules = inps_year_rules(ceiling="122295.00")
        return tuple(
            first_run_contributions(
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
        rules = inps_year_rules(ceiling="122295.00")
        capped, uncapped = (
            first_run_contributions(
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
