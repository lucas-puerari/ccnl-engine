"""The state that opens a run after balances imported from another provider.

:meth:`~ccnl_engine.api.facade.PayrollEngine.import_opening_balances` checks
the :class:`~ccnl_engine.payroll.application.opening_balances.OpeningBalances`
and maps them here onto the competence and tax cash state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.credit_accounts import (
    SommaEsenteAccount,
    TrattamentoAccount,
    UlterioreDetrazioneAccount,
)
from ccnl_engine.payroll.domain.obligations import EmploymentObligations
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState
from ccnl_engine.payroll.domain.ytd_accounts import (
    EarningsYtd,
    FringeYtd,
    RegimeCapAccount,
    TaxYtd,
    WithholdingShortfall,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.opening_balances import OpeningBalances

__all__ = ["opening_state"]


def opening_state(balances: OpeningBalances) -> PeriodState:
    """Return the state bound to ``balances.tax_year`` that opens the next run.

    Returns:
        The competence and cash state carrying the imported obligations.
    """
    cash = TaxCashState(
        tax_year=balances.tax_year,
        payments=balances.payments,
        earnings=EarningsYtd(
            gross=balances.gross,
            taxable=balances.taxable,
            inps_employee=balances.inps_employee,
            pension_deducted=balances.pension_deducted,
        ),
        fringe=FringeYtd(
            value=balances.fringe_value, taxed=balances.fringe_taxed, pdr=balances.pdr
        ),
        tax=TaxYtd(
            irpef=balances.irpef_withheld,
            surtax=balances.surtax_withheld,
            municipal_advance=balances.municipal_advance_withheld,
            regional_settled=balances.regional_settled,
            municipal_settled=balances.municipal_settled,
        ),
        trattamento=TrattamentoAccount(
            recognized=balances.trattamento_recognized,
            recovered=balances.trattamento_recovered,
            due=balances.trattamento_due,
            reason=balances.trattamento_reason,
        ),
        somma_esente=SommaEsenteAccount(
            recognized=balances.somma_esente_recognized,
            recovered=balances.somma_esente_recovered,
            due=balances.somma_esente_due,
            reason=balances.somma_esente_reason,
        ),
        ulteriore_detrazione=UlterioreDetrazioneAccount(
            recognized=balances.ulteriore_recognized,
            recovered=balances.ulteriore_recovered,
            due=balances.ulteriore_due,
            reason=balances.ulteriore_reason,
        ),
        work_time_regime=RegimeCapAccount(used=balances.work_time_regime_used),
        shortfall=WithholdingShortfall(
            irpef=balances.irpef_shortfall,
            surtax=balances.surtax_shortfall,
            credit_recovery=balances.credit_recovery_shortfall,
        ),
        obligations=_obligations(balances),
    )
    accrual = EmploymentAccrualState(
        competence_runs=(
            *balances.competence_runs,
            *(p.run_id for p in balances.payments),
        ),
        inps_bases=balances.inps_bases,
        sickness_episodes=balances.sickness_episodes,
    )
    return PeriodState(accrual=accrual, cash=cash)


def _obligations(balances: OpeningBalances) -> EmploymentObligations:
    deferred = balances.deferred_shortfall
    return EmploymentObligations(
        recoveries=balances.recoveries,
        surtax=balances.surtax_obligations,
        deferred_shortfall=() if deferred is None else (deferred,),
    )
