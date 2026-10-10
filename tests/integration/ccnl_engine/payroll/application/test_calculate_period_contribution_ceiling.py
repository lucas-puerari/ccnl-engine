"""Boundary tests for IVS massimale and +1% addizionale through calculate_period.

Verifies that the contribution history on PeriodCalculationRequest correctly
gates the IVS ceiling and addizionale 1% in the period-first pipeline.

INPS limits 2026 (INPS circ. 6/2026 par. 5 and 6):
    Massimale retributivo IVS:            122,295 EUR
    Soglia addizionale +1%, annual:        56,224 EUR
    Soglia addizionale +1%, mensilizzata:   4,685 EUR
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.eligibility import ContributionHistory
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from tests.fixtures.period_requests import period_request

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.contributions import ContributionComponent
    from ccnl_engine.payroll.domain.period import PeriodResult

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_ZERO = Decimal(0)

_MASSIMALE = Decimal("122295.00")
_POST_1995 = ContributionHistory(first_enrolled_on=date(2001, 9, 1))
_NOT_APPLICABLE = ContributionHistory(first_enrolled_on=date(1990, 3, 1))


def _req(
    month: int = 1,
    opening: PeriodState | None = None,
    *,
    history: ContributionHistory | None = _POST_1995,
) -> PeriodCalculationRequest:
    if opening is None:
        opening = PeriodState.zero()
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=opening,
        contribution_history=history,
    )


def _ivs_employee(result: PeriodResult) -> Decimal:
    return next(
        (
            c.amount
            for c in result.contribution_breakdown.components
            if c.name == "ivs_employee"
        ),
        _ZERO,
    )


def _addizionale(result: PeriodResult) -> Decimal:
    return next(
        (
            c.amount
            for c in result.contribution_breakdown.components
            if c.name == "addizionale_1pct"
        ),
        _ZERO,
    )


class TestIvsCeilingApplies:
    """A worker enrolled before 1996 bypasses the massimale cap entirely."""

    def test_false_gives_higher_ivs_than_true_when_ytd_near_ceiling(self) -> None:
        """With YTD near the massimale, uncapped IVS > capped IVS."""
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, Decimal("121000.00")),),
            )
        )
        r_capped = calculate_period(_req(month=11, opening=opening, history=_POST_1995))
        r_uncapped = calculate_period(
            _req(month=11, opening=opening, history=_NOT_APPLICABLE)
        )
        assert _ivs_employee(r_uncapped) > _ivs_employee(r_capped)
        assert (
            r_uncapped.contribution_breakdown.employer
            > r_capped.contribution_breakdown.employer
        )

    def test_false_gives_ivs_when_ytd_exceeds_ceiling(self) -> None:
        """ceiling=True gives IVS=0 above massimale; False does not."""
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, Decimal("130000.00")),),
            )
        )
        r_capped = calculate_period(_req(month=12, opening=opening, history=_POST_1995))
        r_uncapped = calculate_period(
            _req(month=12, opening=opening, history=_NOT_APPLICABLE)
        )
        assert _ivs_employee(r_capped) == _ZERO
        assert _ivs_employee(r_uncapped) > _ZERO

    def test_true_and_false_identical_when_ytd_is_zero(self) -> None:
        """With no prior YTD, both modes give identical contributions."""
        r_capped = calculate_period(_req(month=1, history=_POST_1995))
        r_uncapped = calculate_period(_req(month=1, history=_NOT_APPLICABLE))
        assert _ivs_employee(r_capped) == _ivs_employee(r_uncapped)
        assert (
            r_capped.contribution_breakdown.employee
            == r_uncapped.contribution_breakdown.employee
        )


class TestMassimaleThreshold:
    """IVS contribution is zero above the massimale when ceiling applies."""

    def test_ivs_zero_above_massimale(self) -> None:
        """IVS employee component is 0 when YTD already exceeds the massimale."""
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, _MASSIMALE + Decimal("1000.00")),),
            )
        )
        result = calculate_period(_req(month=12, opening=opening, history=_POST_1995))
        assert _ivs_employee(result) == _ZERO

    def test_ivs_partial_when_crossing_massimale(self) -> None:
        """IVS applies only to the headroom when a period crosses the massimale."""
        # ytd=121000, headroom=1295 < typical period base ~2158
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, Decimal("121000.00")),),
            )
        )
        r_capped = calculate_period(_req(month=11, opening=opening, history=_POST_1995))
        r_uncapped = calculate_period(
            _req(month=11, opening=opening, history=_NOT_APPLICABLE)
        )
        ivs_capped = _ivs_employee(r_capped)
        ivs_uncapped = _ivs_employee(r_uncapped)
        assert _ZERO < ivs_capped < ivs_uncapped

    def test_ivs_positive_below_massimale(self) -> None:
        """IVS is positive when YTD is safely below the massimale."""
        result = calculate_period(_req(month=1, history=_POST_1995))
        assert _ivs_employee(result) > _ZERO

    def test_ivs_capped_at_headroom_when_period_overshoots(self) -> None:
        """IVS base equals the ceiling headroom when period overshoots the massimale."""
        headroom = Decimal("500.00")
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, _MASSIMALE - headroom),)
            )
        )
        r_capped = calculate_period(_req(month=11, opening=opening, history=_POST_1995))
        r_uncapped = calculate_period(
            _req(month=11, opening=opening, history=_NOT_APPLICABLE)
        )
        ivs_comp = next(
            (
                c
                for c in r_capped.contribution_breakdown.components
                if c.name == "ivs_employee"
            ),
            None,
        )
        assert ivs_comp is not None
        assert ivs_comp.base == headroom
        ivs_uncapped_comp = next(
            c
            for c in r_uncapped.contribution_breakdown.components
            if c.name == "ivs_employee"
        )
        assert ivs_uncapped_comp.base > headroom


def _opening(own: Decimal, additional_ivs: Decimal = _ZERO) -> PeriodState:
    return PeriodState(
        accrual=EmploymentAccrualState(
            inps_bases=(InpsBaseYtd(2026, own, additional_ivs=additional_ivs),),
        )
    )


def _settlement(result: PeriodResult) -> ContributionComponent | None:
    return next(
        (
            c
            for c in result.contribution_breakdown.components
            if c.name == "addizionale_1pct_conguaglio"
        ),
        None,
    )


class TestAddizionale1Pct:
    """1% addizionale month by month, settled on the year in December.

    Every month of the C3 runs below pays the June 2026 minimum, 2,211.43,
    below the monthly threshold of 4,685.00: no regular month charges the
    1%, whatever the YTD base (circ. 6/2026 par. 5; circ. 7/2010 par. 3).
    December settles the year: 1% of the base of the year within the
    massimale above 56,224.00, less what was withheld (msg. 5327/2015
    par. 2.3).
    """

    def test_no_addizionale_in_january_with_zero_ytd(self) -> None:
        """Normal C3 January (YTD=0) produces no addizionale."""
        result = calculate_period(_req(month=1, history=_POST_1995))
        assert _addizionale(result) == _ZERO
        assert _settlement(result) is None

    def test_regular_month_ignores_the_annual_band(self) -> None:
        """July with YTD 70,000, above 56,224: still nothing until December."""
        result = calculate_period(
            _req(month=7, opening=_opening(Decimal(70000)), history=_POST_1995)
        )
        assert _addizionale(result) == _ZERO
        assert _settlement(result) is None

    def test_december_settles_the_year_above_the_annual_band(self) -> None:
        """YTD 55,900, nothing withheld: 55,900 + 2,211 = 58,111.

        The December base is 2,211.43 to the whole euro (INPS circ.
        208/2001).  58,111 - 56,224 = 1,887; x 1% = 18.87 due.
        """
        result = calculate_period(
            _req(month=12, opening=_opening(Decimal(55900)), history=_POST_1995)
        )
        settlement = _settlement(result)
        assert settlement is not None
        assert settlement.base == Decimal("1887.00")
        assert settlement.amount == Decimal("18.87")
        assert _addizionale(result) == _ZERO

    def test_december_gives_back_what_the_months_over_withheld(self) -> None:
        """Same year with 30.00 withheld by the months: 18.87 - 30.00 = -11.13."""
        opening = _opening(Decimal(55900), additional_ivs=Decimal("30.00"))
        result = calculate_period(_req(month=12, opening=opening, history=_POST_1995))
        settlement = _settlement(result)
        assert settlement is not None
        assert settlement.amount == Decimal("-11.13")
        assert result.closing_state.accrual.inps_base(2026).additional_ivs == (
            Decimal("18.87")
        )

    def test_december_settles_within_the_massimale(self) -> None:
        """Post-1995, YTD 130,000: the year counts up to 122,295 only.

        122,295 - 56,224 = 66,071; x 1% = 660.71, all withheld already:
        nothing to settle.
        """
        opening = _opening(Decimal(130000), additional_ivs=Decimal("660.71"))
        result = calculate_period(_req(month=12, opening=opening, history=_POST_1995))
        assert _settlement(result) is None
        assert _addizionale(result) == _ZERO

    def test_december_without_the_massimale_settles_the_whole_year(self) -> None:
        """Enrolled before 1996, YTD 125,000: no massimale caps the year.

        125,000 + 2,211 - 56,224 = 70,987; x 1% = 709.87,
        less the 660.71 withheld: 49.16.
        """
        opening = _opening(Decimal(125000), additional_ivs=Decimal("660.71"))
        result = calculate_period(
            _req(month=12, opening=opening, history=_NOT_APPLICABLE)
        )
        settlement = _settlement(result)
        assert settlement is not None
        assert settlement.amount == Decimal("49.16")

    def test_a_month_past_the_massimale_pays_no_addizionale(self) -> None:
        """November, post-1995, YTD 130,000: no headroom, no monthly 1%."""
        result = calculate_period(
            period_request(
                month=11,
                opening=_opening(Decimal(130000)),
                contribution_history=ContributionHistory(date(2001, 9, 1)),
            )
        )
        assert _addizionale(result) == _ZERO
        assert _settlement(result) is None
