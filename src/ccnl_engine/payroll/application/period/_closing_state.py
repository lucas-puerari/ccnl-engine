"""Closing state of a run: advance the accrual state and the tax cash state."""

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
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    TaxYtd,
    WithholdingShortfall,
)
from ccnl_engine.shared.domain.errors import DataIntegrityError, InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
    from ccnl_engine.payroll.application.handlers._totals import _EventTotals
    from ccnl_engine.payroll.application.withholding._somma_esente import (
        SommaEsenteOutcome,
    )
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.employment_spells import EmploymentSpell
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.payment import PaymentId
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall

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
        conguaglio: Whether the payment leaves no withholding slot of its
            tax year unpaid, so it settles the conguaglio.
        payment: The payment the run closes: its run and payment date.
        entries: Every ledger entry of the run.
        period_inps_base: INPS base of the run.
        amounts: Monetary amounts of the run.
        events: Aggregated totals of the variable events.
        somma_esente: Somma esente of the run, with its recovery plan.
        recovery_plan: Trattamento integrativo plan of the current tax year
            after the run, if any.
        carried: Recoveries of earlier tax years still running after it.
        shortfall: IRPEF and surtax not yet withheld after the run.
        deferred: IRPEF of conguagli deferred on written request, still to
            withhold after the run.
        additional_ivs: Additional 1% IVS the run withheld, negative when
            its conguaglio gave some back.
        history_known: Whether the run opened with the history of the
            employment; ``False`` marks the closing state, so every run
            that descends from it blocks.
        employment_spells: Employment spells of the tax year after the
            run, the run's included.
    """

    tax_year: int
    conguaglio: bool
    payment: PaymentId
    entries: tuple[LedgerEntry, ...]
    period_inps_base: Decimal
    amounts: _PeriodAmounts
    events: _EventTotals
    somma_esente: SommaEsenteOutcome
    recovery_plan: RecoveryPlan | None
    carried: tuple[RecoveryObligation, ...]
    shortfall: WithholdingShortfall = field(default_factory=WithholdingShortfall)
    deferred: tuple[DeferredShortfall, ...] = ()
    additional_ivs: Decimal = _ZERO
    history_known: bool = True
    employment_spells: tuple[EmploymentSpell, ...] = ()


def closing_state(opening: PeriodState, outcome: RunOutcome) -> PeriodState:
    """Return the state after the run described by ``outcome``.

    Returns:
        The opening state advanced by the run: its competence run closed in
        the accrual state, its payment and amounts added to the tax cash
        state.  The obligations
        hold the carried recoveries still running, then the recoveries of
        the current tax year running after the run: trattamento integrativo
        first, then somma esente, then the ulteriore detrazione, whose
        installments are posted by the adjustment runs of the tax year and
        the runs of the next one; then the surtax still to withhold and the
        IRPEF deferred on written request.  After the last run of the
        employment no recovery, no surtax and no deferral is left.

    Raises:
        DataIntegrityError: When the advanced state breaks an invariant of
            the accrual or tax cash state, e.g. a negative YTD total or a
            run closed twice: the run produced a state no payslip can
            carry.  The opening state was validated before the run, so
            this is an engine fault, not a caller input error.
    """
    try:
        return _advance(opening, outcome)
    except (ValueError, InvalidInputError) as exc:
        msg = f"Closing state rejected: {exc}"
        raise DataIntegrityError(msg) from exc


def _advance(opening: PeriodState, outcome: RunOutcome) -> PeriodState:
    """Return ``opening`` advanced by ``outcome``; see :func:`closing_state`.

    Returns:
        The advanced state; its constructors validate it.
    """
    somma = outcome.somma_esente
    ulteriore = outcome.amounts.ulteriore
    ulteriore_plan = (
        opening.cash.obligations.recovery_of(outcome.tax_year, ULTERIORE_RECOVERY)
        if ulteriore is None
        else ulteriore.plan
    )
    current = tuple(
        RecoveryObligation(tax_year=outcome.tax_year, plan=plan)
        for plan in (outcome.recovery_plan, somma.plan, ulteriore_plan)
        if plan is not None
    )
    obligations = EmploymentObligations(
        recoveries=outcome.carried + current,
        surtax=outcome.amounts.surtax.obligations,
        deferred_shortfall=outcome.deferred,
    )
    return PeriodState(
        accrual=opening.accrual.after(
            outcome.payment.run_id,
            outcome.period_inps_base,
            outcome.events.sickness_episodes,
            outcome.additional_ivs,
        ),
        cash=_closing_cash(opening.cash, outcome, obligations),
        history_known=outcome.history_known,
    )


def _closing_tax(op: TaxCashState, outcome: RunOutcome) -> TaxYtd:
    """Return the tax withheld YTD after the run.

    The surtax refunded by the conguaglio lowers the surtax withheld, and
    the acconto or saldo it was taken from.

    Returns:
        The IRPEF, surtax and municipal acconto withheld after the run.
    """
    amounts = outcome.amounts
    surtax = amounts.surtax
    settled = surtax.conguaglio
    advance = surtax.advance_withheld(amounts.period_surtax, outcome.tax_year)
    return TaxYtd(
        irpef=op.tax.irpef + amounts.period_irpef,
        surtax=op.tax.surtax + amounts.period_surtax - surtax.refund,
        municipal_advance=op.tax.municipal_advance + advance - settled.advance_refunded,
        regional_settled=op.tax.regional_settled + settled.regional_settled,
        municipal_settled=op.tax.municipal_settled + settled.municipal_settled,
    )


def _closing_cash(
    op: TaxCashState, outcome: RunOutcome, obligations: EmploymentObligations
) -> TaxCashState:
    """Return the tax cash state ``op`` advanced by the payment ``outcome``.

    Returns:
        The advanced state; its constructors validate it.
    """
    amounts = outcome.amounts
    events = outcome.events
    entries = outcome.entries
    somma = outcome.somma_esente
    tratt = _decision_of(amounts.decisions, _TRATTAMENTO)
    slot = outcome.payment.run_id.kind.consumes_withholding_slot
    return TaxCashState(
        tax_year=outcome.tax_year,
        payments=(*op.payments, outcome.payment),
        conguaglio=(
            outcome.payment if outcome.conguaglio else None if slot else op.conguaglio
        ),
        earnings=EarningsYtd(
            gross=op.earnings.gross + _sum_ledger(entries, AccountKind.CASH_EARNINGS),
            taxable=op.earnings.taxable + amounts.period_taxable,
            inps_employee=op.earnings.inps_employee
            + _sum_ledger(entries, AccountKind.EMPLOYEE_CONTRIBUTIONS),
            pension_deducted=op.earnings.pension_deducted
            + (_ZERO if amounts.pension is None else amounts.pension.deductible),
        ),
        fringe=FringeYtd(
            value=op.fringe.value + events.fringe_value,
            taxed=op.fringe.taxed + events.fringe_irpef,
            pdr=op.fringe.pdr + amounts.pdr_eligible,
        ),
        tax=_closing_tax(op, outcome),
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
        obligations=obligations,
        employment_spells=outcome.employment_spells,
    )
