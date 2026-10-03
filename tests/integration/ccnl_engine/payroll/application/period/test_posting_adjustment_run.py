"""Installments opened by the conguaglio are posted by the adjustment runs.

L. 207/2024 art. 1 c. 7 and D.L. 3/2020 art. 1 c. 3: the installments run
"a partire dalla prima retribuzione alla quale si applicano gli effetti del
conguaglio".  An adjustment run paid after the conguaglio of 2026 is such a
payslip, so it posts the next installment of every plan the conguaglio
opened, not only the runs of 2027.

The ulteriore detrazione plan lives inside the IRPEF of the year: the
conguaglio withholds the first installment and defers the others.  The
adjustment run settles the cumulative balance again, so the check is the
independent IRPEF oracle: IRPEF withheld plus what is still deferred equals
the net IRPEF of the final taxable income.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from functools import cache
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.api.facade import PayrollEngine
from ccnl_engine.payroll.application.calculate_year import (
    YearResult,
    calculate_year,
)
from ccnl_engine.payroll.domain.employment_facts import WeeklyHours
from ccnl_engine.payroll.domain.events import AbsenceEvent, BonusEvent
from ccnl_engine.payroll.domain.inputs import PeriodInput
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.obligations import (
    SOMMA_ESENTE_RECOVERY,
    TRATTAMENTO_RECOVERY,
    ULTERIORE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from tests.fixtures.legal_examples.irpef_2026 import net_irpef
from tests.helpers import EMPLOYER_50, year_input

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_state import PeriodState

_CCNL = "metalmeccanico-federmeccanica.json"
_ZERO = Decimal(0)
_ADJUSTMENT = PayrollRun(run_kind=RunKind.ADJUSTMENT, month=12, year=2026)
_RECOVERY = f"{ULTERIORE_RECOVERY}_recovery"


@cache
def _bonus_year() -> YearResult:
    """C3 full time with a 20,000 EUR bonus on the tredicesima, the conguaglio.

    About 25,800 EUR of taxable income before the bonus: the ulteriore
    detrazione of 1,000 EUR is recognized run by run.  The bonus takes the
    final income above 40,000 EUR, where c. 6 grants nothing: the twelve
    thirteenths recognized are an excess above 60 EUR, recovered in ten
    installments.

    Returns:
        The year result.
    """
    bonus = BonusEvent(event_date=date(2026, 12, 15), amount=Decimal(20000))
    return calculate_year(
        year_input(2026, _CCNL, "C3", events={"2026-12-thirteenth": (bonus,)})
    )


def _adjustment(year: YearResult, opening: PeriodState | None = None) -> PeriodResult:
    last = year.period_results[-1]
    employment = year_input(2026, _CCNL, "C3").employment
    return PayrollEngine().calculate_period(
        PeriodInput(
            run=_ADJUSTMENT,
            payment_date=date(2026, 12, 30),
            employment=employment,
            employer=EMPLOYER_50,
            opening_state=last.closing_state if opening is None else opening,
        )
    )


def _plan_of(result: PeriodResult, kind: str) -> RecoveryPlan | None:
    return result.closing_state.cash.obligations.recovery_of(2026, kind)


def test_adjustment_posts_the_second_ulteriore_installment() -> None:
    """The run withholds one installment more and defers the other eight."""
    conguaglio = _bonus_year().period_results[-1]
    opened = _plan_of(conguaglio, ULTERIORE_RECOVERY)
    assert opened is not None
    assert opened.installments_posted == 1
    # Twelve of thirteen slots recognized 12/13 of 1,000 EUR before the bonus.
    assert abs(opened.original_amount - money(Decimal(12000) / 13)) <= Decimal("0.02")

    result = _adjustment(_bonus_year())

    after = _plan_of(result, ULTERIORE_RECOVERY)
    assert after == opened.advance()
    installment = opened.installment_amount
    assert after.residual == opened.original_amount - 2 * installment
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == _RECOVERY and d.reason_code.startswith("installment")
    )
    assert decision.reason_code == "installment_posted_adjustment_run"
    assert decision.amount == -installment
    ytd = result.closing_state.cash
    oracle = net_irpef(ytd.earnings.taxable)
    assert abs(ytd.tax.irpef + after.residual - oracle) <= Decimal("0.01")


@cache
def _absence_year() -> YearResult:
    """C3 at 33 of 40 hours; 144 absence hours on the tredicesima.

    The final income of 19,639.09 EUR removes the ulteriore detrazione: the
    conguaglio opens a plan.  The adjustment run pays one more month and
    takes the income back above 20,000 EUR, so the deduction is due again.

    Returns:
        The year result.
    """
    absence = AbsenceEvent(
        event_date=date(2026, 12, 10), hours=Decimal(144), hourly_rate=Decimal("12.50")
    )
    return calculate_year(
        year_input(
            2026,
            _CCNL,
            "C3",
            weekly_hours=WeeklyHours(33),
            full_time_weekly_hours=WeeklyHours(40),
            events={"2026-12-thirteenth": (absence,)},
        )
    )


def test_adjustment_restoring_the_deduction_closes_the_plan() -> None:
    """Nothing is left to recover: the cumulative balance settles the year."""
    opened = _plan_of(_absence_year().period_results[-1], ULTERIORE_RECOVERY)
    assert opened is not None
    employment = year_input(
        2026,
        _CCNL,
        "C3",
        weekly_hours=WeeklyHours(33),
        full_time_weekly_hours=WeeklyHours(40),
    ).employment
    result = PayrollEngine().calculate_period(
        PeriodInput(
            run=_ADJUSTMENT,
            payment_date=date(2026, 12, 30),
            employment=employment,
            employer=EMPLOYER_50,
            opening_state=_absence_year().period_results[-1].closing_state,
        )
    )
    assert _plan_of(result, ULTERIORE_RECOVERY) is None
    ytd = result.closing_state.cash
    assert ytd.tax.irpef == net_irpef(ytd.earnings.taxable)
    reasons = {d.reason_code for d in result.decisions if d.capability == _RECOVERY}
    assert reasons == {"recovery_absorbed_by_conguaglio"}


def _with_plan(year: YearResult, plan: RecoveryPlan) -> PeriodState:
    """Return the year-end state with a 2026 plan the conguaglio opened.

    The account records 300 EUR paid and the first installment recovered,
    so the recovery stays within what was recognized.

    Returns:
        The state to open the adjustment run with.
    """
    closing = year.period_results[-1].closing_state
    ytd = closing.cash
    name = "trattamento" if plan.kind == TRATTAMENTO_RECOVERY else "somma_esente"
    account = getattr(ytd, name)
    account = replace(
        account,
        recognized=account.recognized + Decimal(300),
        recovered=account.recovered + plan.installment_amount,
    )
    obligations = EmploymentObligations(
        recoveries=(
            *closing.cash.obligations.recoveries,
            RecoveryObligation(tax_year=2026, plan=plan),
        )
    )
    return replace(
        closing, cash=replace(ytd, **{name: account}, obligations=obligations)
    )


@pytest.mark.parametrize(
    ("plan", "item"),
    [
        # 240 in eight installments of 30, the first on the conguaglio.
        (
            RecoveryPlan.create(TRATTAMENTO_RECOVERY, Decimal(240), 8),
            "tratt_integ_recovery",
        ),
        # 250 in ten installments of 25, the first on the conguaglio.
        (
            RecoveryPlan.create(SOMMA_ESENTE_RECOVERY, Decimal(250), 10),
            "somma_esente_recovery",
        ),
    ],
)
def test_adjustment_posts_the_credit_installment(plan: RecoveryPlan, item: str) -> None:
    """The adjustment run posts the second installment as a credit recovery."""
    opened = plan.advance()
    result = _adjustment(_bonus_year(), _with_plan(_bonus_year(), opened))
    (line,) = (
        e.amount
        for e in result.ledger_entries
        if e.account == AccountKind.CREDIT_RECOVERIES and e.entry_id.startswith(item)
    )
    assert line == plan.installment_amount
    assert _plan_of(result, plan.kind) == opened.advance()
    reasons = {d.reason_code for d in result.decisions}
    assert "installment_posted_adjustment_run" in reasons
