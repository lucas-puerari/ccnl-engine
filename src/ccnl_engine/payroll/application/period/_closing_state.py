"""Closing state of a run: advance the tax year state and the obligations."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _sum_ledger
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.obligations import (
    ULTERIORE_RECOVERY,
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    TaxYtd,
    WithholdingShortfall,
)
from ccnl_engine.shared.domain.errors import DataIntegrityError

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
    from ccnl_engine.payroll.application.handlers._totals import _EventTotals
    from ccnl_engine.payroll.application.withholding._somma_esente import (
        SommaEsenteOutcome,
    )
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind

_ZERO = Decimal(0)
_TRATTAMENTO = "trattamento_integrativo"


def _decision_of(
    decisions: tuple[CalculationDecision, ...], capability: str
) -> CalculationDecision | None:
    """Return the decision of ``capability`` among ``decisions``, if any.

    Returns:
        The first matching decision, or ``None``.
    """
    return next((d for d in decisions if d.capability == capability), None)


@dataclass(frozen=True)
class RunOutcome:
    """What one run adds to the state it opened with.

    Attributes:
        tax_year: Tax year the run is attributed to.
        withholding_slots: Slots of the withholding schedule of the run.
        run_id: Identifier of the run.
        run_kind: Kind of the run.
        entries: Every ledger entry of the run.
        period_inps_base: INPS base of the run.
        amounts: Monetary amounts of the run.
        events: Aggregated totals of the variable events.
        somma_esente: Somma esente of the run, with its recovery plan.
        recovery_plan: Trattamento integrativo plan of the current tax year
            after the run, if any.
        carried: Recoveries of earlier tax years still running after it.
        shortfall: IRPEF and surtax not yet withheld after the run.
    """

    tax_year: int
    withholding_slots: int
    run_id: PayrollRunId
    run_kind: RunKind
    entries: tuple[LedgerEntry, ...]
    period_inps_base: Decimal
    amounts: _PeriodAmounts
    events: _EventTotals
    somma_esente: SommaEsenteOutcome
    recovery_plan: RecoveryPlan | None
    carried: tuple[RecoveryObligation, ...]
    shortfall: WithholdingShortfall = field(default_factory=WithholdingShortfall)


def closing_state(opening: PeriodState, outcome: RunOutcome) -> PeriodState:
    """Return the state after the run described by ``outcome``.

    Returns:
        The opening tax year state advanced by the run.  The obligations
        hold the carried recoveries still running, then the recoveries of
        the current tax year running after the run: trattamento integrativo
        first, then somma esente, then the ulteriore detrazione, whose
        installments start on the first run of the next tax year.

    Raises:
        DataIntegrityError: When the advanced state breaks an invariant of
            the tax year state, e.g. a negative YTD total: the run produced
            amounts no payslip can carry.
    """
    try:
        ytd = _closing_ytd(opening.ytd, outcome)
    except ValueError as exc:
        msg = f"Closing state rejected: {exc}"
        raise DataIntegrityError(msg) from exc
    somma = outcome.somma_esente
    ulteriore = outcome.amounts.ulteriore
    ulteriore_plan = (
        ulteriore.plan
        if ulteriore is not None and ulteriore.plan is not None
        else opening.obligations.recovery_of(outcome.tax_year, ULTERIORE_RECOVERY)
    )
    current = tuple(
        RecoveryObligation(tax_year=outcome.tax_year, plan=plan)
        for plan in (outcome.recovery_plan, somma.plan, ulteriore_plan)
        if plan is not None
    )
    return PeriodState(
        ytd=ytd,
        obligations=EmploymentObligations(recoveries=outcome.carried + current),
    )


def _closing_ytd(op: TaxYearState, outcome: RunOutcome) -> TaxYearState:
    """Return the tax year state ``op`` advanced by the run ``outcome``.

    Returns:
        The advanced state; its constructors validate it.
    """
    amounts = outcome.amounts
    events = outcome.events
    entries = outcome.entries
    somma = outcome.somma_esente
    tratt = _decision_of(amounts.decisions, _TRATTAMENTO)
    return TaxYearState(
        tax_year=outcome.tax_year,
        regular_periods_closed=op.regular_periods_closed
        + (1 if outcome.run_kind == "regular" else 0),
        tax_withholding_periods_closed=op.tax_withholding_periods_closed
        + (1 if outcome.run_kind.consumes_withholding_slot else 0),
        withholding_slots=outcome.withholding_slots,
        closed_run_ids=(*op.closed_run_ids, outcome.run_id),
        earnings=EarningsYtd(
            gross=op.earnings.gross + _sum_ledger(entries, AccountKind.CASH_EARNINGS),
            inps_base=op.earnings.inps_base + outcome.period_inps_base,
            taxable=op.earnings.taxable + amounts.period_taxable,
            inps_employee=op.earnings.inps_employee
            + _sum_ledger(entries, AccountKind.EMPLOYEE_CONTRIBUTIONS),
        ),
        fringe=FringeYtd(
            value=op.fringe.value + events.fringe_value,
            taxed=op.fringe.taxed + events.fringe_irpef,
            pdr=op.fringe.pdr + amounts.pdr_eligible,
        ),
        tax=TaxYtd(
            irpef=op.tax.irpef + amounts.period_irpef,
            surtax=op.tax.surtax + amounts.period_surtax,
        ),
        trattamento=op.trattamento.after(
            amounts.period_tratt,
            None if tratt is None else tratt.amount,
            None if tratt is None else tratt.reason_code,
        ),
        somma_esente=op.somma_esente.after(somma.amount, somma.due, somma.reason),
        ulteriore_detrazione=(
            op.ulteriore_detrazione
            if amounts.ulteriore is None
            else op.ulteriore_detrazione.after(
                amounts.ulteriore.amount,
                amounts.ulteriore.due,
                amounts.ulteriore.reason,
            )
        ),
        work_time_regime=RegimeCapAccount(
            used=op.work_time_regime.used + events.work_time_cap_used
        ),
        shortfall=outcome.shortfall,
    )
