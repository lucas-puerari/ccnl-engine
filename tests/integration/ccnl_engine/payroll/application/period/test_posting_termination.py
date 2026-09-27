"""Credit recoveries still running are settled on the last run of the employment.

AdE circ. 29/E/2020 par. 6 (trattamento integrativo, D.L. 3/2020 art. 1
c. 3) and circ. 4/E/2025 par. 1.2 (somma esente and ulteriore detrazione,
L. 207/2024 art. 1 c. 7) both state that, when the employment ends, the
conguaglio di fine rapporto recovers the credits not due "in un'unica
soluzione, indipendentemente dall'importo, in mancanza di ulteriori
retribuzioni sulle quali operare il recupero in maniera dilazionata".  What
the pay cannot
cover is communicated to the worker (art. 23 c. 3 DPR 600/1973, quoted by
both circolari).

The plans are built by hand, so every expected value follows from them:
an installment is ``installment_amount``, the residual is
``original_amount - installment_amount * installments_posted``.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from functools import cache

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.calculate_year import (
    YearResult,
    calculate_year,
)
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.inputs import PeriodInput
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.obligations import (
    SOMMA_ESENTE_RECOVERY,
    TRATTAMENTO_RECOVERY,
    ULTERIORE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.schedule import WithholdingSchedule, WithholdingSlot
from tests.helpers import EMPLOYER_50, year_input

_CCNL = "metalmeccanico-federmeccanica.json"
_ZERO = Decimal(0)
_Q1 = EmploymentPeriod(started_on=date(2026, 1, 1), ended_on=date(2026, 3, 31))


def _plan(
    kind: str, original: str, installment: str, total: int, posted: int
) -> RecoveryPlan:
    return RecoveryPlan(
        kind=kind,
        original_amount=Decimal(original),
        installment_amount=Decimal(installment),
        installments_total=total,
        installments_posted=posted,
    )


def _carried(plan: RecoveryPlan) -> PeriodState:
    return PeriodState(
        obligations=EmploymentObligations(
            recoveries=(RecoveryObligation(tax_year=2025, plan=plan),)
        )
    )


def _year(
    opening: PeriodState | None = None, period: EmploymentPeriod = _Q1
) -> YearResult:
    return calculate_year(
        year_input(2026, _CCNL, "C3", employment_period=period, opening_state=opening)
    )


@cache
def _q1_without_plan() -> YearResult:
    return _year()


def _recovery_reasons(result: YearResult, kind: str) -> list[str]:
    return [
        d.reason_code for d in result.decisions if d.capability == f"{kind}_recovery"
    ]


def _credit_line(result: YearResult, run: int, item_prefix: str) -> Decimal:
    period = result.period_results[run]
    return sum(
        (
            e.amount
            for e in period.ledger_entries
            if e.account == AccountKind.CREDITS and e.entry_id.startswith(item_prefix)
        ),
        _ZERO,
    )


class TestCarriedPlanAtTermination:
    """A plan of 2025 still running when the employment ends on 31 March 2026."""

    @pytest.mark.parametrize(
        ("plan", "installment", "residual"),
        [
            # 200 in ten installments of 20, three posted in 2025: January and
            # February post 20 each, March the residual 200 - 5 x 20 = 100.
            (_plan(ULTERIORE_RECOVERY, "200", "20", 10, 3), "20", "100"),
            (_plan(SOMMA_ESENTE_RECOVERY, "200", "20", 10, 3), "20", "100"),
            # 200 in eight installments of 25, three posted: March recovers
            # 200 - 5 x 25 = 75.
            (_plan(TRATTAMENTO_RECOVERY, "200", "25", 8, 3), "25", "75"),
        ],
    )
    def test_last_run_recovers_the_residual(
        self, plan: RecoveryPlan, installment: str, residual: str
    ) -> None:
        """Two installments, then the residual on the March payslip."""
        result = _year(_carried(plan))
        prefix = f"{plan.kind}_recovery_2025"
        lines = [_credit_line(result, run, prefix) for run in range(3)]
        assert lines == [
            -Decimal(installment),
            -Decimal(installment),
            -Decimal(residual),
        ]
        assert _recovery_reasons(result, plan.kind) == [
            "installment_posted",
            "installment_posted",
            "settled_at_termination",
        ]
        assert result.period_results[-1].closing_state.obligations.recoveries == ()
        recovered = 2 * Decimal(installment) + Decimal(residual)
        assert _q1_without_plan().annual_net - result.annual_net == recovered
        assert result.period_results[-1].closing_state.ytd == (
            _q1_without_plan().period_results[-1].closing_state.ytd
        )

    def test_december_termination_settles_on_the_thirteenth(self) -> None:
        """Employed November to December: the thirteenth is the last slot.

        The regular December payslip is not the last run: it posts one
        installment, and the thirteenth paid after it settles 200 - 5 x 20.
        """
        period = EmploymentPeriod(
            started_on=date(2026, 11, 1), ended_on=date(2026, 12, 31)
        )
        plan = _plan(SOMMA_ESENTE_RECOVERY, "200", "20", 10, 3)
        result = _year(_carried(plan), period)
        runs = [r.run.run_id for r in result.period_results if r.run is not None]
        assert runs == ["2026-11-regular", "2026-12-regular", "2026-12-thirteenth"]
        prefix = f"{SOMMA_ESENTE_RECOVERY}_recovery_2025"
        lines = [_credit_line(result, run, prefix) for run in range(3)]
        assert lines == [Decimal(-20), Decimal(-20), Decimal(-100)]
        assert _recovery_reasons(result, SOMMA_ESENTE_RECOVERY)[-1] == (
            "settled_at_termination"
        )


def _schedule() -> WithholdingSchedule:
    return WithholdingSchedule(
        year=2026,
        slots=tuple(WithholdingSlot(PayrollRun.regular(2026, m)) for m in (1, 2, 3)),
    )


def _march(opening: PeriodState) -> PeriodInput:
    employment = year_input(2026, _CCNL, "C3", employment_period=_Q1).employment
    return PeriodInput(
        run=PayrollRun.regular(2026, 3),
        payment_date=date(2026, 3, 28),
        employment=employment,
        employer=EMPLOYER_50,
        opening_state=opening,
    )


def _with_current_plan(plan: RecoveryPlan) -> PeriodState:
    """Return the state after February with a 2026 plan of ``plan.kind``.

    The credit account records the 300 EUR paid and the installments
    already recovered, so the recovery stays within what was recognized.

    Returns:
        The state to open the March run with.
    """
    february = _q1_without_plan().period_results[1].closing_state
    ytd = february.ytd
    posted = plan.installment_amount * plan.installments_posted
    if plan.kind == TRATTAMENTO_RECOVERY:
        ytd = replace(
            ytd,
            trattamento=replace(
                ytd.trattamento,
                recognized=ytd.trattamento.recognized + Decimal(300),
                recovered=ytd.trattamento.recovered + posted,
            ),
        )
    else:
        ytd = replace(
            ytd,
            somma_esente=replace(
                ytd.somma_esente,
                recognized=ytd.somma_esente.recognized + Decimal(300),
                recovered=ytd.somma_esente.recovered + posted,
            ),
        )
    return PeriodState(
        ytd=ytd,
        obligations=EmploymentObligations(
            recoveries=(RecoveryObligation(tax_year=2026, plan=plan),)
        ),
    )


@pytest.mark.parametrize(
    ("plan", "item", "reason_capability"),
    [
        # 240 in eight installments of 30, two posted: 240 - 2 x 30 = 180.
        (
            _plan(TRATTAMENTO_RECOVERY, "240", "30", 8, 2),
            "tratt_integ",
            "trattamento_integrativo_recovery",
        ),
        # 250 in ten installments of 25, two posted: 250 - 2 x 25 = 200.
        (
            _plan(SOMMA_ESENTE_RECOVERY, "250", "25", 10, 2),
            "somma_esente_recovery",
            "somma_esente",
        ),
    ],
)
def test_current_year_plan_is_settled_on_the_last_run(
    plan: RecoveryPlan, item: str, reason_capability: str
) -> None:
    """A plan opened in 2026 posts its whole residual on the March payslip."""
    request = _march(_with_current_plan(plan)).calculation_request(
        withholding_schedule=_schedule()
    )
    result = calculate_period(request)
    residual = plan.original_amount - plan.installment_amount * plan.installments_posted
    (line,) = (
        e.amount
        for e in result.ledger_entries
        if e.account == AccountKind.CREDITS and e.entry_id.startswith(item)
    )
    assert line == -residual
    (decision,) = (d for d in result.decisions if d.capability == reason_capability)
    assert decision.reason_code == "settled_at_termination"
    assert result.closing_state.obligations.recoveries == ()


def test_residual_above_the_pay_is_left_to_the_worker() -> None:
    """A 2025 somma esente plan of 5,000 EUR, 500 per installment, none posted.

    January and February recover 500 each; March owes 5,000 - 2 x 500 =
    4,000, far above its pay.  The run recovers what its pay leaves before
    tax, withholds no IRPEF, and carries the rest as a shortfall the worker
    is told about.  The pay left is the net of the same run without the
    plan plus the IRPEF it withheld (no surtax: no residence is declared).
    """
    plan = _plan(SOMMA_ESENTE_RECOVERY, "5000", "500", 10, 0)
    result = _year(_carried(plan))
    march = result.period_results[-1]
    plain = _q1_without_plan().period_results[-1]
    pay_left = plain.period_net + plain.tax_computation.ordinary_tax
    shortfall = march.closing_state.ytd.shortfall
    assert march.period_net == _ZERO
    assert shortfall.credit_recovery == Decimal(4000) - pay_left
    assert shortfall.irpef == plain.tax_computation.ordinary_tax
    (adjustment,) = (
        e.amount
        for e in march.ledger_entries
        if e.entry_id.startswith("credit_recovery_shortfall_")
    )
    assert adjustment == shortfall.credit_recovery
    assert "withholding_shortfall_unrecovered" in {i.code for i in march.issues}
    assert march.closing_state.obligations.recoveries == ()
