"""Lifecycle, withholding, YTD and net pay invariants of a period run."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from functools import cache

import pytest

from ccnl_engine.payroll.application._period_checks import check_net_covered
from ccnl_engine.payroll.application._reconcile_types import RunFacts
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import (
    YearResult,
    calculate_year,
)
from ccnl_engine.payroll.application.lifecycle_invariants import (
    check_extra_month_accrual_limit,
    check_run_within_employment,
)
from ccnl_engine.payroll.application.reconcile import check_period, reconcile
from ccnl_engine.payroll.application.sign_invariants import check_signs
from ccnl_engine.payroll.application.state_invariants import check_ytd_continuity
from ccnl_engine.payroll.application.withholding_invariants import (
    check_contribution_ceiling,
    check_irpef_annual_reconciliation,
    net_annual_irpef,
)
from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
from ccnl_engine.payroll.domain.calendar import AccrualWindow, ExtraMonthKind
from ccnl_engine.payroll.domain.eligibility import ContributionCeilingStatus
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import EmploymentPeriod
from ccnl_engine.payroll.domain.events import BonusEvent
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from ccnl_engine.payroll.domain.tax import TaxComputation, TaxLineItem
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    TrattamentoAccount,
    WithholdingShortfall,
)
from ccnl_engine.shared.domain.errors import DataIntegrityError, OutOfScopeError
from tests.fixtures.legal_examples.irpef_2026 import net_irpef as oracle_net_irpef
from tests.helpers import year_input

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_OPENING = PeriodState.zero()
_CEILING = Decimal(122_295)


def _run(
    month: int = 1,
    opening: PeriodState = _OPENING,
    **kwargs: object,
) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=_YEAR, month=month),
            payment_date=date(_YEAR, month, 27),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            employer=EmployerProfile(headcount=Headcount(50)),
            opening_state=opening,
            **kwargs,  # type: ignore[arg-type]
        )
    )


def _with_ytd(result: PeriodResult, **ytd: object) -> PeriodResult:
    state = result.closing_state
    closing = replace(state, ytd=replace(state.ytd, **ytd))  # type: ignore[arg-type]
    return replace(result, closing_state=closing)


def _accrual(months: int) -> ExtraMonthAccrual:
    start = date(_YEAR, 1, 1)
    return ExtraMonthAccrual(
        kind=ExtraMonthKind.THIRTEENTH,
        window=AccrualWindow(start, start, date(_YEAR, 12, 31)),
        months=months,
    )


class TestRunWithinEmployment:
    """A regular run falls in a month with a day of employment."""

    def test_run_in_employment_passes(self) -> None:
        """A run of a hire month passes."""
        facts = RunFacts(employment_period=EmploymentPeriod(date(_YEAR, 1, 20)))
        assert check_run_within_employment(_run(), facts) == []

    def test_regular_run_before_hire_is_reported(self) -> None:
        """A regular run before the hire month is a violation."""
        facts = RunFacts(employment_period=EmploymentPeriod(date(_YEAR, 3, 1)))
        (violation,) = check_run_within_employment(_run(), facts)
        assert violation.invariant_id == "run_within_employment"
        assert "2026-01-regular" in violation.message

    def test_extra_month_run_is_not_checked(self) -> None:
        """Only regular runs are bound to the employment months."""
        result = replace(_run(), run=PayrollRun.thirteenth(_YEAR, 1))
        facts = RunFacts(employment_period=EmploymentPeriod(date(_YEAR, 3, 1)))
        assert check_run_within_employment(result, facts) == []

    def test_untracked_employment_is_not_checked(self) -> None:
        """Without an employment period nothing is checked."""
        assert check_run_within_employment(_run(), RunFacts()) == []


class TestExtraMonthAccrualLimit:
    """The ratei of one extra month and window reach at most 12 months."""

    def test_full_rateo_passes(self) -> None:
        """Twelve months of one window are within the limit."""
        facts = RunFacts(accruals=(_accrual(8), _accrual(4)))
        assert check_extra_month_accrual_limit(facts) == []

    def test_ratei_above_twelve_months_are_reported(self) -> None:
        """A run paying 13 months of one window is a violation."""
        facts = RunFacts(accruals=(_accrual(12), _accrual(1)))
        (violation,) = check_extra_month_accrual_limit(facts)
        assert violation.invariant_id == "extra_month_accrual_limit"
        assert violation.actual == Decimal(13)


class TestContributionCeiling:
    """The IVS base of a run fits in the massimale headroom."""

    _NEAR_CEILING = PeriodState(
        ytd=TaxYearState(earnings=EarningsYtd(inps_base=_CEILING - 1_000))
    )

    def _capped_run(self) -> PeriodResult:
        return _run(
            12,
            self._NEAR_CEILING,
            ceiling_status=ContributionCeilingStatus.POST_1995,
        )

    def test_capped_run_passes(self) -> None:
        """A real run near the massimale takes only the headroom."""
        result = self._capped_run()
        facts = RunFacts(ivs_ceiling=_CEILING)
        assert check_contribution_ceiling(result, self._NEAR_CEILING, facts) == []
        assert reconcile(result, self._NEAR_CEILING, facts).ok

    def test_base_above_headroom_is_reported(self) -> None:
        """An IVS base above the headroom is a violation per IVS component."""
        result = self._capped_run()
        facts = RunFacts(ivs_ceiling=_CEILING - 900)
        violations = check_contribution_ceiling(result, self._NEAR_CEILING, facts)
        assert {v.invariant_id for v in violations} == {"contribution_ceiling"}
        assert [v.expected for v in violations] == [Decimal(100)] * 2

    def test_ceiling_not_applied_is_not_checked(self) -> None:
        """Without a massimale nothing is checked."""
        assert check_contribution_ceiling(_run(), _OPENING, RunFacts()) == []


@cache
def _last_two() -> tuple[PeriodResult, PeriodResult]:
    results = calculate_year(year_input(_YEAR, _CCNL, _LEVEL)).period_results
    return results[-2], results[-1]


class TestIrpefAnnualReconciliation:
    """The run closing the last withholding slot settles the IRPEF of the year."""

    def test_real_year_passes(self) -> None:
        """The conguaglio of a real year settles the net annual IRPEF."""
        previous, last = _last_two()
        assert last.closing_state.ytd.is_complete
        assert (
            check_irpef_annual_reconciliation(last, previous.closing_state, RunFacts())
            == []
        )

    def test_withheld_off_by_more_than_a_cent_is_reported(self) -> None:
        """IRPEF withheld one euro above the annual IRPEF is a violation."""
        previous, last = _last_two()
        tax = last.closing_state.ytd.tax
        bad = _with_ytd(last, tax=replace(tax, irpef=tax.irpef + 1))

        (violation,) = check_irpef_annual_reconciliation(
            bad, previous.closing_state, RunFacts()
        )
        assert violation.invariant_id == "irpef_annual_reconciliation"
        assert violation.actual == violation.expected + 1  # type: ignore[operator]

    def test_shortfall_left_counts_as_due(self) -> None:
        """IRPEF the pay did not cover still settles the year with it."""
        previous, last = _last_two()
        tax = last.closing_state.ytd.tax
        short = _with_ytd(
            last,
            tax=replace(tax, irpef=tax.irpef - 30),
            shortfall=WithholdingShortfall(irpef=Decimal(30)),
        )
        assert (
            check_irpef_annual_reconciliation(short, previous.closing_state, RunFacts())
            == []
        )

    def test_one_cent_is_within_rounding(self) -> None:
        """A one-cent difference is rounding, not a violation."""
        previous, last = _last_two()
        tax = last.closing_state.ytd.tax
        bad = _with_ytd(last, tax=replace(tax, irpef=tax.irpef + Decimal("0.01")))
        assert (
            check_irpef_annual_reconciliation(bad, previous.closing_state, RunFacts())
            == []
        )

    def test_earlier_slot_is_not_checked(self) -> None:
        """A run before the last slot is not reconciled."""
        result = _run()
        tax = result.closing_state.ytd.tax
        bad = _with_ytd(result, tax=replace(tax, irpef=tax.irpef + 1))
        assert check_irpef_annual_reconciliation(bad, _OPENING, RunFacts()) == []

    def test_projected_taxable_off_final_is_reported(self) -> None:
        """IRPEF settled on a taxable other than the final one is a violation."""
        previous, last = _last_two()
        final = last.closing_state.ytd.earnings.taxable
        facts = RunFacts(projected_taxable=final + Decimal("22.11"))

        (violation,) = check_irpef_annual_reconciliation(
            last, previous.closing_state, facts
        )
        assert violation.invariant_id == "irpef_annual_reconciliation"
        assert violation.expected == final
        assert violation.actual == final + Decimal("22.11")

    def test_two_cents_of_taxable_are_rounding(self) -> None:
        """A two-cent taxable difference is rounding, not a violation."""
        previous, last = _last_two()
        final = last.closing_state.ytd.earnings.taxable
        facts = RunFacts(projected_taxable=final - Decimal("0.02"))
        assert (
            check_irpef_annual_reconciliation(last, previous.closing_state, facts) == []
        )

    def test_high_earner_settles_on_final_taxable(self) -> None:
        """Above the 1% addizionale threshold the last slot uses actual INPS.

        Bancari QD4 earns about 67,000 EUR, above the 56,224 EUR threshold
        of the 1% addizionale INPS (INPS circ. 4/2026).  The last run must
        project its taxable income with the INPS it actually withholds, so
        the conguaglio settles the IRPEF of the final taxable income.
        """
        results = calculate_year(
            year_input(_YEAR, "bancari-abi.json", "QD4")
        ).period_results
        last = results[-1]
        assert last.closing_state.ytd.tax.irpef == net_annual_irpef(
            last.tax_computation
        )

    def test_net_annual_irpef_uses_deductions_only(self) -> None:
        """Credits paid on the payslip do not lower the IRPEF due."""
        computation = TaxComputation(
            ordinary_tax=Decimal(0),
            trattamento_integrativo=Decimal(0),
            withholding_due=Decimal(0),
            components=(
                TaxLineItem("irpef_gross", Decimal(1_000), "art11-tuir", "Art. 11"),
                TaxLineItem("work_deduction", Decimal(300), "art13-tuir", "Art. 13"),
                TaxLineItem("sterilizzazione_detrazioni", Decimal(-100), "l199", "L."),
                TaxLineItem(
                    "trattamento_integrativo", Decimal(1_200), "dl3", "D.L. 3/2020"
                ),
            ),
        )
        assert net_annual_irpef(computation) == Decimal(800)

    def test_net_annual_irpef_is_floored_at_zero(self) -> None:
        """Deductions above the gross IRPEF give no IRPEF due."""
        computation = TaxComputation(
            ordinary_tax=Decimal(0),
            trattamento_integrativo=Decimal(0),
            withholding_due=Decimal(0),
            components=(
                TaxLineItem("irpef_gross", Decimal(100), "art11-tuir", "Art. 11"),
                TaxLineItem("work_deduction", Decimal(300), "art13-tuir", "Art. 13"),
            ),
        )
        assert net_annual_irpef(computation) == Decimal(0)


class TestYtdContinuity:
    """Each YTD accumulator closes at its opening plus the run amount."""

    def test_real_run_passes(self) -> None:
        """A real run with surtax advances every accumulator."""
        result = _run(regione="IT-25", comune_belfiore="F205")
        assert result.closing_state.ytd.tax.surtax > 0
        assert check_ytd_continuity(result, _OPENING) == []

    def test_wrong_surtax_is_reported(self) -> None:
        """A surtax YTD that ignores the SURTAX posting is a violation."""
        result = _run(regione="IT-25", comune_belfiore="F205")
        tax = result.closing_state.ytd.tax
        bad = _with_ytd(result, tax=replace(tax, surtax=Decimal(0)))

        (violation,) = check_ytd_continuity(bad, _OPENING)
        assert violation.invariant_id == "ytd_continuity"
        assert "surtax_ytd" in violation.message

    def test_wrong_credit_account_is_reported(self) -> None:
        """A trattamento account that the ledger does not explain is caught."""
        bad = _with_ytd(_run(), trattamento=TrattamentoAccount(Decimal(50)))

        (violation,) = check_ytd_continuity(bad, _OPENING)
        assert "trattamento net credit" in violation.message
        assert violation.actual == Decimal(50)


class TestNetPayNonNegative:
    """A negative net pay is an engine error once absences are ruled out."""

    def test_real_run_passes(self) -> None:
        """A real run has a non-negative net."""
        assert check_signs(_run()) == []

    def test_negative_net_is_reported(self) -> None:
        """A negative period_net is a violation."""
        bad = replace(_run(), period_net=Decimal("-19.08"))
        (violation,) = check_signs(bad)
        assert violation.invariant_id == "net_pay_non_negative"
        assert violation.actual == Decimal("-19.08")

    def test_negative_net_with_absences_is_out_of_scope(self) -> None:
        """Deductions other than the capped taxes above the pay left raise."""
        bad = replace(
            _run(),
            period_net=Decimal("-5.00"),
            unpaid_absence_deduction=Decimal(2000),
        )
        with pytest.raises(OutOfScopeError, match=r"other than IRPEF") as exc:
            check_net_covered(bad)
        assert exc.value.reason == "withholding_shortfall"

    def test_negative_net_without_absences_reaches_the_invariant(self) -> None:
        """Without absences a negative net is left to the invariant."""
        bad = replace(_run(), period_net=Decimal("-1.00"))
        check_net_covered(bad)
        with pytest.raises(DataIntegrityError, match=r"\[net_pay_non_negative\]"):
            check_period(bad, _OPENING, RunFacts())


class TestClosingStateRejected:
    """A closing state that breaks the tax year state is an engine error."""

    def test_thirteenth_regular_run_is_rejected(self) -> None:
        """A 13th regular run cannot close: the counter is capped at 12."""
        opening = PeriodState(
            ytd=TaxYearState(
                regular_periods_closed=12, tax_withholding_periods_closed=12
            )
        )
        with pytest.raises(DataIntegrityError, match="Closing state rejected"):
            _run(12, opening)


def _november_irpef(result: YearResult) -> Decimal:
    (november,) = (
        r
        for r in result.period_results
        if r.period_id.month == 11
        and r.run is not None
        and r.run.run_kind is RunKind.REGULAR
    )
    return november.tax_computation.ordinary_tax


def _final_taxable(result: YearResult) -> Decimal:
    return result.period_results[-1].closing_state.ytd.earnings.taxable


def test_large_bonus_leaves_every_net_non_negative() -> None:
    """A 20,000 EUR bonus in November must not make a later net negative.

    The IRPEF of the bonus used to be withheld over the remaining slots of
    the year instead of on the bonus payslip, so the tredicesima run
    withheld more than it paid and ``net_pay_non_negative`` rejected the
    year.
    """
    bonus = BonusEvent(event_date=date(_YEAR, 11, 10), amount=Decimal(20_000))
    result = calculate_year(year_input(_YEAR, _CCNL, _LEVEL, events={11: (bonus,)}))
    assert all(r.period_net >= 0 for r in result.period_results)


def test_large_bonus_is_withheld_on_the_payslip_that_pays_it() -> None:
    """A 20,000 EUR bonus in November is taxed on the November payslip.

    Art. 23 c. 2 lett. a) DPR 600/1973 withholds on the sums paid in each
    pay period.  The November run withholds its share of the recurring tax
    plus the whole tax the bonus adds to the year; spreading that tax over
    the later slots made the tredicesima run withhold more than it paid.

    Expected, from the oracle on the final taxable incomes of the year with
    and without the bonus: the November IRPEF grows by
    ``net_irpef(with) - net_irpef(without)`` (8,398.79 EUR), and the runs
    after it withhold what they withhold without the bonus.  The tolerance
    of 0.50 EUR is the rounding of the projection of the later slots, which
    the conguaglio settles (the engine withholds 8,398.60 more in November,
    then 0.09 and 0.10 more on the two later runs).
    """
    bonus = BonusEvent(event_date=date(_YEAR, 11, 10), amount=Decimal(20_000))
    with_bonus = calculate_year(year_input(_YEAR, _CCNL, _LEVEL, events={11: (bonus,)}))
    without = calculate_year(year_input(_YEAR, _CCNL, _LEVEL))

    bonus_tax = oracle_net_irpef(_final_taxable(with_bonus)) - oracle_net_irpef(
        _final_taxable(without)
    )
    grown = _november_irpef(with_bonus) - _november_irpef(without)

    tail_growth = sum(
        (
            a.tax_computation.ordinary_tax - b.tax_computation.ordinary_tax
            for a, b in zip(
                with_bonus.period_results[-2:], without.period_results[-2:], strict=True
            )
        ),
        Decimal(0),
    )

    assert abs(grown - bonus_tax) <= Decimal("0.50")
    assert abs(tail_growth) <= Decimal("0.50")
