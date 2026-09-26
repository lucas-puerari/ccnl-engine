"""Ulteriore detrazione recognized by the withholding and recovered at conguaglio.

L. 207/2024 art. 1 c. 7: the deduction found not due at the conguaglio is
recovered, "in dieci rate di pari ammontare a partire dalla prima
retribuzione alla quale si applicano gli effetti del conguaglio" when above
60 EUR.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import cache

from ccnl_engine.engine.contract.domain.identity import TaxSector
from ccnl_engine.engine.tax.service.tax_annual_assembler import load_year_rules
from ccnl_engine.payroll.application.calculate_year import (
    YearResult,
    calculate_year,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.employment import EmploymentPeriod, WeeklyHours
from ccnl_engine.payroll.domain.events import AbsenceEvent, WorkEvent
from ccnl_engine.payroll.domain.obligations import (
    ULTERIORE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.period import PeriodState
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.ytd_accounts import UlterioreDetrazioneAccount
from ccnl_engine.payroll.service.rounding import money
from ccnl_engine.payroll.service.ulteriore_recovery import settle_ulteriore
from tests.fixtures.legal_examples.irpef_2026 import further_deduction, net_irpef
from tests.helpers import year_input

_CCNL = "metalmeccanico-federmeccanica.json"
_ZERO = Decimal(0)
_RULES = load_year_rules(2026, TaxSector.INDUSTRIA, 50)


def _account(recognized: str, recovered: str = "0") -> UlterioreDetrazioneAccount:
    return UlterioreDetrazioneAccount(
        recognized=Decimal(recognized), recovered=Decimal(recovered)
    )


class TestSettleUlteriore:
    """What one run recognizes or recovers."""

    def test_share_before_the_conguaglio(self) -> None:
        """The run recognizes what its withholding is lower by."""
        settled = settle_ulteriore(
            Decimal(100),
            Decimal("176.92"),
            Decimal(1000),
            _account("0"),
            last_slot=False,
        )
        assert settled.amount == Decimal("76.92")
        assert settled.reason == "share_recognized"
        assert settled.deferred == _ZERO

    def test_taken_back_before_the_conguaglio_is_not_deferred(self) -> None:
        """A run taking back the deduction recovers it by withholding."""
        settled = settle_ulteriore(
            Decimal(900), Decimal(100), _ZERO, _account("500"), last_slot=False
        )
        assert settled.amount == Decimal(-500)
        assert settled.reason == "recovered_by_withholding"
        assert settled.plan is None

    def test_nothing_recognized(self) -> None:
        """Without the deduction the withholding is the same."""
        settled = settle_ulteriore(
            Decimal(100), Decimal(100), _ZERO, _account("0"), last_slot=False
        )
        assert settled.reason == "not_recognized"

    def test_conguaglio_completes_the_deduction(self) -> None:
        """At the conguaglio a positive balance is recognized."""
        settled = settle_ulteriore(
            Decimal(100),
            Decimal("176.93"),
            Decimal(1000),
            _account("923.07"),
            last_slot=True,
        )
        assert settled.amount == Decimal("76.93")
        assert settled.reason == "settled_at_conguaglio"
        assert settled.decisions(_RULES) == ()

    def test_excess_up_to_sixty_is_recovered_in_full(self) -> None:
        """60 EUR found not due are withheld on the conguaglio payslip."""
        settled = settle_ulteriore(
            Decimal(160), Decimal(100), _ZERO, _account("60"), last_slot=True
        )
        assert settled.amount == Decimal(-60)
        assert settled.reason == "overpayment_recovered"
        assert settled.deferred == _ZERO
        assert settled.plan is None

    def test_excess_above_sixty_opens_ten_installments(self) -> None:
        """60.10 EUR: 6.01 on the conguaglio, nine installments deferred."""
        settled = settle_ulteriore(
            Decimal("160.10"),
            Decimal(100),
            _ZERO,
            _account("60.10"),
            last_slot=True,
        )
        assert settled.reason == "overpayment_recovery_opened"
        assert settled.deferred == Decimal("54.09")
        assert settled.plan is not None
        assert settled.plan.installments_posted == 1
        assert settled.plan.residual == Decimal("54.09")
        (decision,) = settled.decisions(_RULES)
        assert decision.capability == "ulteriore_detrazione_lavoro_recovery"
        assert decision.amount == Decimal("-60.10")
        assert decision.status == CalculationStatus.FINAL


_ABSENCE = AbsenceEvent(
    event_date=date(2026, 12, 10), hours=Decimal(144), hourly_rate=Decimal("12.50")
)


@cache
def _year() -> YearResult:
    """C3 at 33 of 40 hours: about 20,950 EUR of taxable, 1,000 EUR deduction.

    144 absence hours on the tredicesima payslip, the conguaglio, bring the
    final taxable income to 19,639.09 EUR: not above 20,000 EUR, so the
    deduction is not due (c. 6) and the somma esente is (c. 4).

    Returns:
        The year result.
    """
    return calculate_year(
        year_input(
            2026,
            _CCNL,
            "C3",
            weekly_hours=WeeklyHours(33),
            full_time_weekly_hours=WeeklyHours(40),
            events={"2026-12-thirteenth": (_ABSENCE,)},
        )
    )


class TestConguaglioRecovery:
    """The absence on the conguaglio removes a deduction already recognized."""

    def test_deduction_is_no_longer_due(self) -> None:
        """The oracle gives no deduction on the final income."""
        final = _year().period_results[-1].closing_state.ytd
        assert final.earnings.taxable <= Decimal(20_000)
        assert further_deduction(final.earnings.taxable) == _ZERO

    def test_twelve_runs_recognized_twelve_thirteenths(self) -> None:
        """Before the conguaglio twelve of 13 slots recognized 12/13 of 1,000."""
        before = _year().period_results[-2].closing_state.ytd.ulteriore_detrazione
        expected = money(Decimal(1000) * 12 / 13)
        assert abs(before.net - expected) <= Decimal("0.02")

    def test_excess_is_recovered_in_ten_installments(self) -> None:
        """The excess opens a ten installment plan, the first one on the payslip."""
        last = _year().period_results[-1]
        before = _year().period_results[-2].closing_state.ytd.ulteriore_detrazione
        excess = before.net
        (obligation,) = last.closing_state.obligations.recoveries
        assert obligation.tax_year == 2026
        assert obligation.plan.kind == ULTERIORE_RECOVERY
        assert obligation.plan.original_amount == excess
        assert obligation.plan.installment_amount == money(excess / 10)
        assert obligation.plan.residual == excess - money(excess / 10)
        account = last.closing_state.ytd.ulteriore_detrazione
        assert account.net == _ZERO
        assert account.due == _ZERO

    def test_irpef_of_the_year_is_withheld_or_deferred(self) -> None:
        """IRPEF withheld plus the nine deferred installments is the oracle net."""
        last = _year().period_results[-1]
        final = last.closing_state.ytd
        (obligation,) = last.closing_state.obligations.recoveries
        settled = final.tax.irpef + obligation.plan.residual
        assert abs(settled - net_irpef(final.earnings.taxable)) <= Decimal("0.01")


def test_excess_is_not_deferred_without_a_later_payslip() -> None:
    """At the cessation the whole excess stays in the conguaglio IRPEF."""
    settled = settle_ulteriore(
        Decimal(500),
        Decimal(100),
        _ZERO,
        _account("400"),
        last_slot=True,
        defer=False,
    )
    assert settled.reason == "overpayment_recovered_at_termination"
    assert settled.deferred == _ZERO
    assert settled.plan is None


@cache
def _terminated() -> YearResult:
    """C3 at 38 of 40 hours, employed 1 January to 30 November 2026.

    About 20,400 EUR of projected taxable income; 144 absence hours in
    October and in November bring the final income to 19,172.46 EUR, so
    the 915.07 EUR deduction for 334 days is not due.  October takes part
    of it back by withholding, the November conguaglio at the cessation the
    rest.

    Returns:
        The year result.
    """
    absence: dict[int, tuple[WorkEvent, ...]] = {
        month: (
            AbsenceEvent(
                event_date=date(2026, month, 10),
                hours=Decimal(144),
                hourly_rate=Decimal("12.50"),
            ),
        )
        for month in (10, 11)
    }
    return calculate_year(
        year_input(
            2026,
            _CCNL,
            "C3",
            weekly_hours=WeeklyHours(38),
            full_time_weekly_hours=WeeklyHours(40),
            employment_period=EmploymentPeriod(
                started_on=date(2026, 1, 1), ended_on=date(2026, 11, 30)
            ),
            events=absence,
        )
    )


def test_termination_recovers_the_excess_in_full() -> None:
    """No installment outlives the employment; the year settles on the oracle."""
    last = _terminated().period_results[-1]
    ytd = last.closing_state.ytd
    assert last.closing_state.obligations.recoveries == ()
    assert ytd.ulteriore_detrazione.net == _ZERO
    (recovery,) = (
        d
        for d in last.decisions
        if d.capability == "ulteriore_detrazione_lavoro_recovery"
    )
    assert recovery.reason_code == "overpayment_recovered_at_termination"
    assert recovery.amount is not None
    assert recovery.amount < Decimal(-60)
    withheld = ytd.tax.irpef + ytd.shortfall.irpef
    assert abs(withheld - net_irpef(ytd.earnings.taxable, 334)) <= Decimal("0.01")


def _carried(posted: int) -> RecoveryObligation:
    return RecoveryObligation(
        tax_year=2025,
        plan=RecoveryPlan(
            kind=ULTERIORE_RECOVERY,
            original_amount=Decimal(200),
            installment_amount=Decimal(20),
            installments_total=10,
            installments_posted=posted,
        ),
    )


def test_installments_carried_into_the_next_year() -> None:
    """A 2025 plan with 7 of 10 posted costs 60.00 EUR on three 2026 runs."""
    opening = PeriodState(obligations=EmploymentObligations(recoveries=(_carried(7),)))
    with_plan = calculate_year(year_input(2026, _CCNL, "C3", opening_state=opening))
    without = calculate_year(year_input(2026, _CCNL, "C3"))
    assert without.annual_net - with_plan.annual_net == Decimal("60.00")
    reasons = [
        d.reason_code
        for d in with_plan.decisions
        if d.capability == "ulteriore_detrazione_lavoro_recovery"
    ]
    assert reasons == [
        "installment_posted",
        "installment_posted",
        "last_installment_posted",
    ]
    assert with_plan.period_results[-1].closing_state.ytd == (
        without.period_results[-1].closing_state.ytd
    )
