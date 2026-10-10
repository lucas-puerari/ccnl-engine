"""Ulteriore detrazione recognized by the withholding and recovered at conguaglio.

L. 207/2024 art. 1 c. 7: the deduction found not due at the conguaglio is
recovered, "in dieci rate di pari ammontare a partire dalla prima
retribuzione alla quale si applicano gli effetti del conguaglio" when above
60 EUR.
"""

from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal
from functools import cache
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.employment.inputs_fact import EmploymentPeriod, WeeklyHours
from ccnl_engine.payroll.event.facade import AbsenceEvent, WorkEvent
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.state.models_obligation import (
    ULTERIORE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.state.models_tax_cash import TaxCashState
from ccnl_engine.payroll.withholding.models_recovery_plan import RecoveryPlan
from ccnl_engine.payroll.year.services_competence import (
    calculate_competence_year,
)
from tests.fixtures.normative_oracles.irpef_2026 import further_deduction, net_irpef
from tests.helpers import year_plan

if TYPE_CHECKING:
    from ccnl_engine.payroll.year.results import CompetenceYearResult

_CCNL = "metalmeccanico-federmeccanica.json"
_ZERO = Decimal(0)


_ABSENCE = AbsenceEvent(
    event_date=date(2026, 12, 10), hours=Decimal(144), hourly_rate=Decimal("12.50")
)


@cache
def _year() -> CompetenceYearResult:
    """C3 at 33 of 40 hours: about 20,950 EUR of taxable, 1,000 EUR deduction.

    144 absence hours on the tredicesima payslip, the conguaglio, bring the
    final taxable income to 19,639.09 EUR: not above 20,000 EUR, so the
    deduction is not due (c. 6) and the somma esente is (c. 4).

    Returns:
        The year result.
    """
    return calculate_competence_year(
        year_plan(
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
        final = _year().period_results[-1].closing_state.cash
        assert final.earnings.taxable <= Decimal(20_000)
        assert further_deduction(final.earnings.taxable) == _ZERO

    def test_twelve_months_recognized_their_days(self) -> None:
        """Before the conguaglio each month recognized 1,000 * its days / 365.

        L. 207/2024 art. 1 c. 6 gives the deduction "rapportata al periodo di
        lavoro"; art. 23 c. 2 lett. a) DPR 600/1973 applies the deductions of
        the period on the pay of each month, none on the tredicesima (lett.
        b).  Seven months of 31 days give 84.93 each, four of 30 give 82.19,
        February 76.71: 594.51 + 328.76 + 76.71 = 999.98.
        """
        before = _year().period_results[-2].closing_state.cash.ulteriore_detrazione
        expected = sum(
            (
                money(Decimal(1000) * monthrange(2026, month)[1] / 365)
                for month in range(1, 13)
            ),
            _ZERO,
        )
        assert expected == Decimal("999.98")
        assert before.net == expected

    def test_excess_is_recovered_in_ten_installments(self) -> None:
        """The excess opens a ten installment plan, the first one on the payslip."""
        last = _year().period_results[-1]
        before = _year().period_results[-2].closing_state.cash.ulteriore_detrazione
        excess = before.net
        (obligation,) = last.closing_state.cash.obligations.recoveries
        assert obligation.tax_year == 2026
        assert obligation.plan.kind == ULTERIORE_RECOVERY
        assert obligation.plan.original_amount == excess
        assert obligation.plan.installment_amount == money(excess / 10)
        assert obligation.plan.residual == excess - money(excess / 10)
        account = last.closing_state.cash.ulteriore_detrazione
        assert account.net == _ZERO
        assert account.due == _ZERO

    def test_irpef_of_the_year_is_withheld_or_deferred(self) -> None:
        """IRPEF withheld plus the nine deferred installments is the oracle net."""
        last = _year().period_results[-1]
        final = last.closing_state.cash
        (obligation,) = last.closing_state.cash.obligations.recoveries
        settled = final.tax.irpef + obligation.plan.residual
        assert abs(settled - net_irpef(final.earnings.taxable)) <= Decimal("0.01")


@cache
def _terminated() -> CompetenceYearResult:
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
    return calculate_competence_year(
        year_plan(
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
    ytd = last.closing_state.cash
    assert last.closing_state.cash.obligations.recoveries == ()
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
    opening = PeriodState(
        cash=TaxCashState(obligations=EmploymentObligations(recoveries=(_carried(7),)))
    )
    with_plan = calculate_competence_year(
        year_plan(2026, _CCNL, "C3", opening_state=opening)
    )
    without = calculate_competence_year(year_plan(2026, _CCNL, "C3"))
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
    assert with_plan.period_results[-1].closing_state.cash == (
        without.period_results[-1].closing_state.cash
    )
