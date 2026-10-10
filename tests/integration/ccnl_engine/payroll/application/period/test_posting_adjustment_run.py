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

from ccnl_engine.api import PayrollEngine
from ccnl_engine.payroll.application.calculate_competence_year import (
    calculate_competence_year,
)
from ccnl_engine.payroll.domain.employment_facts import WeeklyHours
from ccnl_engine.payroll.domain.events import AbsenceEvent, BonusEvent, OvertimeEvent
from ccnl_engine.payroll.domain.inputs import PeriodFacts, PeriodInput
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.obligations import (
    SOMMA_ESENTE_RECOVERY,
    TRATTAMENTO_RECOVERY,
    ULTERIORE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from tests.fixtures.normative_oracles.irpef_2026 import net_irpef
from tests.helpers import EMPLOYER_50, year_plan

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.year_result import CompetenceYearResult
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_state import PeriodState

_CCNL = "metalmeccanico-federmeccanica.json"
_ZERO = Decimal(0)
_ADJUSTMENT = PayrollRun(run_kind=RunKind.ADJUSTMENT, month=12, year=2026)
_RECOVERY = f"{ULTERIORE_RECOVERY}_recovery"
#: An adjustment run posts no monthly pay (the run it corrects did): it
#: pays only its own items, here 40 overtime hours at 15.00 (600.00).
_ADJUSTMENT_FACTS = PeriodFacts(
    events=(
        OvertimeEvent(
            event_date=date(2026, 12, 29),
            hours=Decimal(40),
            hourly_rate=Decimal("15.00"),
        ),
    )
)


@cache
def _bonus_year() -> CompetenceYearResult:
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
    return calculate_competence_year(
        year_plan(2026, _CCNL, "C3", events={"2026-12-thirteenth": (bonus,)})
    )


def _adjustment(
    year: CompetenceYearResult, opening: PeriodState | None = None
) -> PeriodResult:
    last = year.period_results[-1]
    employment = year_plan(2026, _CCNL, "C3").employment
    return PayrollEngine().calculate_period(
        PeriodInput(
            run=_ADJUSTMENT,
            payment_date=date(2026, 12, 30),
            employment=employment,
            employer=EMPLOYER_50,
            facts=_ADJUSTMENT_FACTS,
            opening_state=last.closing_state if opening is None else opening,
        )
    )


def test_second_adjustment_of_the_month_is_its_own_run() -> None:
    """A second correction of December closes as ``2026-12-adjustment-2``.

    It pays only its own items, the same overtime as the first correction.
    """
    first = _adjustment(_bonus_year())
    employment = year_plan(2026, _CCNL, "C3").employment
    second = PayrollEngine().calculate_period(
        PeriodInput(
            run=PayrollRun.adjustment(2026, 12, sequence=2),
            payment_date=date(2026, 12, 31),
            employment=employment,
            employer=EMPLOYER_50,
            facts=_ADJUSTMENT_FACTS,
            opening_state=first.closing_state,
        )
    )

    assert second.period_gross == first.period_gross > _ZERO
    assert [str(r) for r in second.closing_state.accrual.competence_runs[-2:]] == [
        "2026-12-adjustment",
        "2026-12-adjustment-2",
    ]


def _plan_of(result: PeriodResult, kind: str) -> RecoveryPlan | None:
    return result.closing_state.cash.obligations.recovery_of(2026, kind)


def test_adjustment_posts_the_second_ulteriore_installment() -> None:
    """The run withholds one installment more and defers the other eight."""
    conguaglio = _bonus_year().period_results[-1]
    opened = _plan_of(conguaglio, ULTERIORE_RECOVERY)
    assert opened is not None
    assert opened.installments_posted == 1
    # The twelve months recognized 1,000 * days / 365 each before the bonus
    # (art. 23 c. 2 lett. a) DPR 600/1973, L. 207/2024 art. 1 c. 6): seven
    # months of 84.93, four of 82.19 and February 76.71, 999.98 in all.
    assert opened.original_amount == Decimal("999.98")

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
def _absence_year() -> CompetenceYearResult:
    """C3 at 33 of 40 hours; 144 absence hours on the tredicesima.

    The final income of 19,639.09 EUR removes the ulteriore detrazione: the
    conguaglio opens a plan.  The adjustment run pays 600.00 of overtime
    and takes the income back above 20,000 EUR, so the deduction is due
    again.

    Returns:
        The year result.
    """
    absence = AbsenceEvent(
        event_date=date(2026, 12, 10), hours=Decimal(144), hourly_rate=Decimal("12.50")
    )
    return calculate_competence_year(
        year_plan(
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
    employment = year_plan(
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
            facts=_ADJUSTMENT_FACTS,
            opening_state=_absence_year().period_results[-1].closing_state,
        )
    )
    assert _plan_of(result, ULTERIORE_RECOVERY) is None
    ytd = result.closing_state.cash
    assert ytd.tax.irpef == net_irpef(ytd.earnings.taxable)
    reasons = {d.reason_code for d in result.decisions if d.capability == _RECOVERY}
    assert reasons == {"recovery_absorbed_by_conguaglio"}


def _with_plan(year: CompetenceYearResult, plan: RecoveryPlan) -> PeriodState:
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
