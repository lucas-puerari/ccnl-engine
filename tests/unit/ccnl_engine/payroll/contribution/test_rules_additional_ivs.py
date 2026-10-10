"""The additional 1% IVS of a run: monthly threshold and year-end settlement.

Rule of INPS circ. 6/2026 par. 5: 1% above 56,224.00 a year, mensilizzato
at 4,685.00 a month; each month on the pay of the month above 4,685.00
whatever the annual band (circ. 7/2010 par. 3; msg. 5327/2015 par. 2.1),
settled on the year at year end or termination (msg. 5327/2015 par. 2.3),
both within the massimale of 122,295.00 when it applies (circ. 6/2026
par. 6).  Every expected value below is worked by hand in its docstring.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.contribution.results import ContributionComponent
from ccnl_engine.payroll.contribution.rules_additional_ivs import (
    MONTHLY_COMPONENT,
    SETTLEMENT_COMPONENT,
    AdditionalIvsPosition,
    additional_ivs,
)
from ccnl_engine.tax.contribution.models_additional_ivs import AdditionalIvsRule

_D = Decimal
_RULE = AdditionalIvsRule(
    rate=_D("0.01"),
    annual_threshold=_D("56224.00"),
    monthly_threshold=_D("4685.00"),
)
_CEILING = _D("122295.00")


def _monthly(
    period: str,
    ytd: str,
    month_base: str = "0",
    ceiling: Decimal | None = None,
) -> ContributionComponent | None:
    return additional_ivs(
        _RULE,
        _D(period),
        ytd_base=_D(ytd),
        ceiling=ceiling,
        position=AdditionalIvsPosition(month_base=_D(month_base)),
    )


def _settled(
    period: str, ytd: str, withheld: str, ceiling: Decimal | None = None
) -> ContributionComponent | None:
    return additional_ivs(
        _RULE,
        _D(period),
        ytd_base=_D(ytd),
        ceiling=ceiling,
        position=AdditionalIvsPosition(withheld=_D(withheld), settles=True),
    )


class TestMonthly:
    """The 1% of a month on its pay above the monthly threshold."""

    def test_first_run_of_the_month(self) -> None:
        """5,000 - 4,685 = 315; x 1% = 3.15."""
        assert _monthly("5000.00", "0") == ContributionComponent(
            MONTHLY_COMPONENT, _D("315.00"), _D("0.01"), _D("3.15")
        )

    @pytest.mark.parametrize("ytd", ["0", "60000.00"])
    def test_below_the_threshold_whatever_the_year(self, ytd: str) -> None:
        """4,685.00 is not above 4,685.00: nothing, even past 56,224."""
        assert _monthly("4685.00", ytd) is None

    def test_runs_of_one_month_share_the_threshold(self) -> None:
        """3,000 declared, 3,000 more: 6,000 - 4,685 = 1,315 -> 13.15."""
        component = _monthly("3000.00", "3000.00", month_base="3000.00")

        assert component is not None
        assert (component.base, component.amount) == (_D("1315.00"), _D("13.15"))

    def test_a_later_run_adds_only_its_own_excess(self) -> None:
        """5,000 declared (excess 315), 1,000 more: 1,315 - 315 = 1,000."""
        component = _monthly("1000.00", "5000.00", month_base="5000.00")

        assert component is not None
        assert (component.base, component.amount) == (_D("1000.00"), _D("10.00"))

    def test_a_negative_correction_gives_back_its_share(self) -> None:
        """6,000 declared (excess 1,315), -2,000: 4,000 has none: -13.15."""
        component = _monthly("-2000.00", "6000.00", month_base="6000.00")

        assert component is not None
        assert (component.base, component.amount) == (_D("-1315.00"), _D("-13.15"))

    @pytest.mark.parametrize(
        ("ytd", "month_base", "base"),
        [
            pytest.param("110000.00", "0", "4315.00", id="under"),
            pytest.param("115000.00", "0", "2610.00", id="crossing"),
            pytest.param("120000.00", "0", None, id="headroom-below-threshold"),
            pytest.param("123000.00", "2000.00", None, id="month-started-beyond"),
        ],
    )
    def test_within_the_massimale(
        self, ytd: str, month_base: str, base: str | None
    ) -> None:
        """Period 9,000 against the massimale of 122,295.

        - YTD 110,000: 119,000 is under it: 9,000 - 4,685 = 4,315;
        - YTD 115,000: 7,295 fit, 7,295 - 4,685 = 2,610;
        - YTD 120,000: 2,295 fit, below 4,685: nothing;
        - YTD 123,000 of which 2,000 this month: the month started at
          121,000 and 1,295 of its 11,000 fit: nothing.
        """
        component = _monthly("9000.00", ytd, month_base, ceiling=_CEILING)

        assert (None if component is None else component.base) == (
            None if base is None else _D(base)
        )


class TestSettlement:
    """The conguaglio of the 1% of the year, credit or debit to the worker."""

    def test_debit_above_the_annual_band(self) -> None:
        """60,000 + 1,000 - 56,224 = 4,776 -> 47.76; less 40.00: 7.76."""
        assert _settled("1000.00", "60000.00", "40.00") == ContributionComponent(
            SETTLEMENT_COMPONENT, _D("4776.00"), _D("0.01"), _D("7.76")
        )

    def test_credit_below_the_annual_band(self) -> None:
        """42,000 is below 56,224: nothing due, the 25.00 withheld comes back."""
        component = _settled("2000.00", "40000.00", "25.00")

        assert component is not None
        assert (component.base, component.amount) == (_D(0), _D("-25.00"))

    def test_nothing_left_to_settle(self) -> None:
        """4,776 x 1% = 47.76, all withheld already."""
        assert _settled("1000.00", "60000.00", "47.76") is None

    def test_the_year_counts_up_to_the_massimale(self) -> None:
        """126,000 capped at 122,295: 66,071 -> 660.71; uncapped 697.76."""
        capped = _settled("1000.00", "125000.00", "0", ceiling=_CEILING)
        uncapped = _settled("1000.00", "125000.00", "0")

        assert capped is not None
        assert uncapped is not None
        assert (capped.base, capped.amount) == (_D("66071.00"), _D("660.71"))
        assert (uncapped.base, uncapped.amount) == (_D("69776.00"), _D("697.76"))
