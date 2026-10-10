"""Ulteriore detrazione recognized run by run and recovered at the conguaglio.

L. 207/2024 art. 1 c. 7: the withholding agent recognizes the deduction of
c. 6 "all'atto dell'erogazione delle retribuzioni" and verifies it at the
conguaglio; an amount found not due is recovered, and "Nel caso in cui il
predetto importo sia superiore a 60 euro, il recupero dello stesso è
effettuato in dieci rate di pari ammontare a partire dalla prima
retribuzione alla quale si applicano gli effetti del conguaglio".

The deduction lowers the IRPEF, so the cumulative conguaglio would take the
whole excess back on its payslip.  The engine tracks the part of the
deduction each run's withholding applied (the withholding without the
deduction less the withholding with it: before the conguaglio the share of
the deduction the pay period took, see
:mod:`~ccnl_engine.payroll.withholding.rules_period`), keeps on the conguaglio payslip
what c. 7 allows (the whole excess up to 60 EUR, otherwise the first
installment) and defers the other nine installments to the next runs as a
recovery obligation (:mod:`.ulteriore_settlement`).  A part the withholding
already took back before the conguaglio, e.g. on the run that paid the
income removing the deduction, is not an excess found at the conguaglio and
is not deferred.

The installments still deferred in the tax year of the conguaglio are posted
by the adjustment runs of that year, one per run: an adjustment run settles
the cumulative balance again, so it withholds the balance less what is
still deferred after its installment.  On the last run of the employment
nothing is deferred (AdE circ. 4/E/2025 par. 1.2: the conguaglio di fine
rapporto recovers "in un'unica soluzione, indipendentemente dall'importo").
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.state.models_obligation import ULTERIORE_RECOVERY
from ccnl_engine.payroll.taxation.results import TaxLineItem
from ccnl_engine.payroll.taxation.rules_credit_decision import credit_decision
from ccnl_engine.payroll.taxation.rules_irpef_net import run_withholding
from ccnl_engine.payroll.taxation.rules_ulteriore_plan import post_running_plan
from ccnl_engine.payroll.taxation.rules_ulteriore_settlement import settle_ulteriore

if TYPE_CHECKING:
    from ccnl_engine.payroll.assurance.models_decision import CalculationDecision
    from ccnl_engine.payroll.state.models_credit_account import CreditAccount
    from ccnl_engine.payroll.taxation.rules_irpef_credit import CreditOutcome
    from ccnl_engine.payroll.taxation.rules_irpef_net import NetIrpef
    from ccnl_engine.payroll.taxation.rules_ulteriore_settlement import (
        UlterioreSettlement,
    )
    from ccnl_engine.payroll.withholding.models_recovery_plan import (
        InstallmentRun,
        RecoveryPlan,
    )
    from ccnl_engine.payroll.withholding.rules_period import PeriodTax
    from ccnl_engine.tax.annual.models import YearRules

__all__ = ["ulteriore_items", "withhold_with_ulteriore"]

_ZERO = Decimal(0)
_RULE = "l207-2024-art1-c6"


def ulteriore_items(
    outcome: CreditOutcome, rules: YearRules, taxable: Decimal, days: int
) -> tuple[CalculationDecision, tuple[TaxLineItem, ...]]:
    """Return the decision on the annual deduction and its tax component.

    Returns:
        The final decision of ``outcome`` and, when the amount is positive,
        the ``ulteriore_detrazione`` component.
    """
    decision = credit_decision(
        ULTERIORE_RECOVERY,
        _RULE,
        rules,
        outcome,
        {"taxable_income": taxable, "eligible_work_days": str(days)},
    )
    if outcome.amount <= _ZERO:
        return decision, ()
    component = TaxLineItem(
        name="ulteriore_detrazione",
        amount=outcome.amount,
        rule_id=_RULE,
        fonte="Art. 1 c. 6 L. 207/2024",
    )
    return decision, (component,)


def withhold_with_ulteriore(
    annual: NetIrpef,
    remaining: int,
    period: PeriodTax,
    *,
    opening_irpef_withheld: Decimal,
    carried_shortfall: Decimal,
    ulteriore_account: CreditAccount | None,
    run: InstallmentRun,
    running_plan: RecoveryPlan | None = None,
) -> tuple[Decimal, UlterioreSettlement | None]:
    """Return the IRPEF withheld on the run and the ulteriore settlement.

    Before the last slot the run recognizes the share of the deduction its
    pay period took (:attr:`PeriodTax.without_ulteriore` less
    :attr:`PeriodTax.withheld`).  On the last slot the withholding is
    computed again on the year without the deduction, and an excess above
    60 EUR is deferred: the run withholds that much less.  With
    ``running_plan``, a plan opened by a conguaglio of the tax year, the
    run posts its next installment and keeps deferring the rest
    (:func:`post_running_plan`).

    Returns:
        ``(ordinary_tax, ulteriore)``; ``ulteriore`` is ``None`` when the
        detrazione is not in force or not tracked.
    """
    ordinary_tax = run_withholding(
        annual.net,
        opening_irpef_withheld,
        remaining,
        period.withheld,
        carried_shortfall,
    )
    if annual.ulteriore is None or ulteriore_account is None:
        return ordinary_tax, None
    without = run_withholding(
        annual.net + annual.ulteriore_effect,
        opening_irpef_withheld + ulteriore_account.net,
        remaining,
        period.without_ulteriore,
        carried_shortfall,
    )
    ulteriore = settle_ulteriore(
        ordinary_tax,
        without,
        annual.ulteriore_effect,
        ulteriore_account,
        last_slot=remaining == 1,
        defer=not run.final and running_plan is None,
    )
    if running_plan is not None:
        ulteriore = post_running_plan(ordinary_tax, ulteriore, running_plan, run)
    return ordinary_tax - ulteriore.deferred, ulteriore
