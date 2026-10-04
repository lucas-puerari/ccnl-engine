"""Boundary tests for IVS massimale and +1% addizionale through calculate_period.

Verifies that the contribution history on PeriodCalculationRequest correctly
gates the IVS ceiling and addizionale 1% in the period-first pipeline.

INPS limits 2026 (INPS circ. 4/2026):
    Massimale retributivo IVS: 122,295 EUR
    Soglia addizionale +1%:     56,224 EUR
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


class TestAddizionale1Pct:
    """1% addizionale is applied only within the IVS ceiling, above the soglia."""

    def test_no_addizionale_in_january_with_zero_ytd(self) -> None:
        """Normal C3 January (YTD=0) produces no addizionale: base << 56,224 EUR."""
        result = calculate_period(_req(month=1, history=_POST_1995))
        assert _addizionale(result) == _ZERO

    def test_addizionale_when_ytd_crosses_threshold(self) -> None:
        """Addizionale is emitted when cumulative INPS base exceeds 56,224 EUR."""
        # ytd=55000, period will push total past 56,224
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, Decimal("55000.00")),),
            )
        )
        result = calculate_period(_req(month=6, opening=opening, history=_POST_1995))
        assert _addizionale(result) > _ZERO

    def test_addizionale_positive_when_ytd_already_above_threshold(self) -> None:
        """Addizionale is charged on full period base when threshold exceeded."""
        # ytd=70000 > 56224: addizionale applies to the full period base
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, Decimal("70000.00")),),
            )
        )
        result = calculate_period(_req(month=7, opening=opening, history=_POST_1995))
        assert _addizionale(result) > _ZERO

    def test_addizionale_zero_above_massimale(self) -> None:
        """Addizionale stops when YTD already exceeds the IVS massimale (122,295 EUR).

        Source: INPS circ. 4/2026.  The +1% addizionale is an IVS component
        and is subject to the same massimale cap as the base IVS rate.
        """
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, Decimal("130000.00")),),
            )
        )
        result = calculate_period(_req(month=12, opening=opening, history=_POST_1995))
        assert _addizionale(result) == _ZERO

    def test_addizionale_false_ceiling_allows_above_massimale(self) -> None:
        """With _NOT_APPLICABLE ceiling, addizionale can apply above the massimale."""
        # ytd=125000 > massimale; with ceiling bypassed, addizionale still runs
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, Decimal("125000.00")),),
            )
        )
        r_uncapped = calculate_period(
            _req(month=12, opening=opening, history=_NOT_APPLICABLE)
        )
        assert _addizionale(r_uncapped) > _ZERO

    def test_addizionale_only_on_excess_above_threshold(self) -> None:
        """Addizionale base equals only the portion crossing the 56,224 EUR soglia."""
        # ytd=55900, threshold=56224, excess = (55900 + period_base) - 56224
        opening = PeriodState(
            accrual=EmploymentAccrualState(
                inps_bases=(InpsBaseYtd(2026, Decimal("55900.00")),),
            )
        )
        result = calculate_period(_req(month=6, opening=opening, history=_POST_1995))
        comp = next(
            (
                c
                for c in result.contribution_breakdown.components
                if c.name == "addizionale_1pct"
            ),
            None,
        )
        assert comp is not None
        non_ivs = next(
            c
            for c in result.contribution_breakdown.components
            if c.name == "non_ivs_employee"
        )
        assert comp.base < non_ivs.base


# ---------------------------------------------------------------------------
# 1% INPS addizionale on income > 56,224 EUR not computed
#
# INPS circ. 4/2026: workers whose cumulated INPS contribution base exceeds
# 56,224 EUR pay an additional 1% on the excess (charged to the employee).
# The contribution breakdown must include an 'addizionale_1pct' component.
# Normative threshold 2026: 56,224 EUR (source: INPS circ. 4/2026).
# ---------------------------------------------------------------------------


def test_inps_addizionale_1pct_on_threshold_crossing() -> None:
    """1% addizionale must appear when INPS base crosses 56,224 EUR.

    Source: INPS circ. 4/2026.  With inps_base_ytd=56,000 and ~2,200 EUR
    monthly base the cumulative crosses 56,224 EUR; an 'addizionale_1pct'
    component with amount > 0 must appear in contribution_breakdown.
    """
    opening = PeriodState(
        accrual=EmploymentAccrualState(
            inps_bases=(InpsBaseYtd(2026, Decimal("56000.00")),),
        )
    )
    result = calculate_period(period_request(month=6, opening=opening))

    component_names = {c.name for c in result.contribution_breakdown.components}
    assert "addizionale_1pct" in component_names, (
        "ContributionBreakdown must include 'addizionale_1pct' when the "
        "cumulative INPS base crosses 56,224 EUR (INPS circ. 4/2026).  "
        f"Current components: {sorted(component_names)}."
    )
    addizionale = next(
        (
            c.amount
            for c in result.contribution_breakdown.components
            if c.name == "addizionale_1pct"
        ),
        _ZERO,
    )
    assert addizionale > _ZERO, (
        f"'addizionale_1pct' amount must be > 0; got {addizionale}."
    )


# ---------------------------------------------------------------------------
# Addizionale 1% applied above the IVS massimale ceiling
#
# The +1% addizionale threshold (56,224 EUR) and the IVS massimale (122,295 EUR)
# are distinct limits.  When the YTD INPS base already exceeds the massimale,
# no IVS and no +1% should apply to the current period income.  The engine
# currently computes the +1% on the full period base regardless of whether
# the massimale has been reached.
# Source: INPS circ. 4/2026.
# ---------------------------------------------------------------------------


def test_addizionale_zero_above_ivs_massimale() -> None:
    """addizionale_1pct must be 0 when inps_base_ytd exceeds the IVS massimale.

    Source: INPS circ. 4/2026.  massimale IVS 2026 = 122,295 EUR.  With
    inps_base_ytd=130,000 > 122,295, the period adds income above the ceiling
    where no INPS component (including the +1% addizionale) should apply.
    Expected: addizionale_1pct == 0.
    """
    # > 122,295 IVS massimale 2026
    opening = PeriodState(
        accrual=EmploymentAccrualState(
            inps_bases=(InpsBaseYtd(2026, Decimal("130000.00")),)
        )
    )
    result = calculate_period(
        period_request(
            month=12,
            opening=opening,
            contribution_history=ContributionHistory(date(2001, 9, 1)),
        )
    )

    addizionale = next(
        (
            c.amount
            for c in result.contribution_breakdown.components
            if c.name == "addizionale_1pct"
        ),
        _ZERO,
    )
    assert addizionale == _ZERO, (
        "addizionale_1pct must be 0 when inps_base_ytd "
        f"({opening.accrual.inps_base(2026).total}) "
        f"exceeds the IVS massimale (122,295 EUR, INPS circ. 4/2026); "
        f"got {addizionale}.  The +1% is currently not gated on the massimale."
    )
