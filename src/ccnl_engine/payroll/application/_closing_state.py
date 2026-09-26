"""Closing state of a run: advance the tax year state and the obligations."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _sum_ledger
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.period import PeriodState
from ccnl_engine.payroll.domain.tax_year_state import TaxYearState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    SommaEsenteAccount,
    TaxYtd,
    TrattamentoAccount,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.application._period_amounts import _PeriodAmounts
    from ccnl_engine.payroll.application.allocate_events import _EventTotals
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.run import RunKind

_ZERO = Decimal(0)


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
        somma_esente: Somma esente credited on the run.
        recovery_plan: Plan of the current tax year after the run, if any.
        carried: Recoveries of earlier tax years still running after it.
    """

    tax_year: int
    withholding_slots: int
    run_id: str
    run_kind: RunKind
    entries: tuple[LedgerEntry, ...]
    period_inps_base: Decimal
    amounts: _PeriodAmounts
    events: _EventTotals
    somma_esente: Decimal
    recovery_plan: RecoveryPlan | None
    carried: tuple[RecoveryObligation, ...]


def closing_state(opening: PeriodState, outcome: RunOutcome) -> PeriodState:
    """Return the state after the run described by ``outcome``.

    Returns:
        The opening tax year state advanced by the run.  The obligations
        hold the carried recoveries still running, then the recovery of the
        current tax year when one is running after the run.
    """
    op = opening.ytd
    amounts = outcome.amounts
    events = outcome.events
    entries = outcome.entries
    tratt = amounts.period_tratt
    ytd = TaxYearState(
        tax_year=outcome.tax_year,
        regular_periods_closed=op.regular_periods_closed
        + (1 if outcome.run_kind == "regular" else 0),
        tax_withholding_periods_closed=op.tax_withholding_periods_closed
        + (1 if outcome.run_kind.consumes_withholding_slot else 0),
        withholding_slots=outcome.withholding_slots,
        closed_run_ids=op.closed_run_ids | {outcome.run_id},
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
        trattamento=TrattamentoAccount(
            recognized=op.trattamento.recognized + max(_ZERO, tratt),
            recovered=op.trattamento.recovered + max(_ZERO, -tratt),
        ),
        somma_esente=SommaEsenteAccount(
            recognized=op.somma_esente.recognized + outcome.somma_esente
        ),
        work_time_regime=RegimeCapAccount(
            used=op.work_time_regime.used + events.work_time_cap_used
        ),
    )
    current = (
        (RecoveryObligation(tax_year=outcome.tax_year, plan=outcome.recovery_plan),)
        if outcome.recovery_plan is not None
        else ()
    )
    return PeriodState(
        ytd=ytd,
        obligations=EmploymentObligations(recoveries=outcome.carried + current),
    )
