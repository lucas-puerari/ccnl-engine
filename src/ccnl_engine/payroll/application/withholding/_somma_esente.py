"""Somma esente of a run: its share, the conguaglio and the recovery.

The somma esente (L. 207/2024 art. 1 c. 4) is paid by the withholding agent
run by run on the projected annual income.  Its entitlement is verified at
the conguaglio; an amount found not due is recovered there, in full up to
60 EUR and otherwise in ten equal installments from the payslip that
carries the conguaglio (art. 1 c. 7).  Before the conguaglio a run pays
the percentage of the projected annual income applied to the employment
income it pays ("applicando tale percentuale al reddito effettivamente
corrisposto mensilmente", AdE circ. 4/E/2025 par. 1.2), capped at what is
still due, and never recovers: an excess found mid-year waits for the
conguaglio.

On the last run of the employment nothing is left to installments: the
excess, or the residual of a running recovery, is recovered in full (AdE
circ. 4/E/2025 par. 1.2, "in un'unica soluzione, indipendentemente
dall'importo, in mancanza di ulteriori retribuzioni").
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.withholding._somma_esente_posting import (
    SommaEsentePosting,
    postings,
)
from ccnl_engine.payroll.application.withholding._somma_esente_settlement import (
    settle,
)
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.obligations import SOMMA_ESENTE_RECOVERY
from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.current_year import CurrentYearTaxFacts
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.tax import TaxComputation
    from ccnl_engine.payroll.domain.withholding_schedule import WithholdingPosition
    from ccnl_engine.tax.annual.models import YearRules

__all__ = ["SommaEsenteOutcome", "SommaEsentePosting", "resolve_somma_esente"]

_ZERO = Decimal(0)
_RULE = "l207-2024-art1-c4-c7"
CAPABILITY = "somma_esente"


@dataclass(frozen=True)
class SommaEsenteOutcome:
    """Somma esente of one run.

    Attributes:
        amount: Signed amount posted: positive is paid, negative recovered.
        due: Updated annual entitlement, ``None`` when the credit is not in
            force and no recovery of it is running.
        reason: Reason code of the decision, ``None`` without one.
        plan: Installment recovery of the current tax year after the run.
        items: The tax credit item of the run, if any.
        entries: The matching ledger entry, if any.
        decisions: What the run decided on the credit, empty when the
            credit is not in force and no recovery of it is running.
        issues: While an amount is due, a missing ``current_year`` when
            the income beyond this employment is not stated, or a
            provisional band with employment income of other employers.
    """

    amount: Decimal = _ZERO
    due: Decimal | None = None
    reason: str | None = None
    plan: RecoveryPlan | None = None
    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()


#: Other income can only raise the reddito complessivo, so the income beyond
#: this employment matters only while the somma esente is due.
INCOME_UNKNOWN_ISSUE = CalculationIssue(
    code="somma_esente_income_unknown",
    message=(
        "somma_esente: the reddito complessivo of L. 207/2024 art. 1 c. 4 "
        "includes the income beyond this employment, which the run does not "
        "know: state it in PeriodInput.current_year (zero included); the "
        "amount shown is computed on this employment alone"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="current_year",
)
#: With employment income of other employers, or the exempt share of the
#: impatriati and researcher regimes c. 9 counts in the reddito di lavoro
#: dipendente, the band of c. 4 is taken on the income of this employer alone.
BAND_ASSUMED_ISSUE = CalculationIssue(
    code="somma_esente_band_assumed",
    message=(
        "somma_esente: the worker has employment income from other employers "
        "or exempt regime income (c. 9) this tax year; the percentage of L. "
        "207/2024 art. 1 c. 4 is taken on "
        "the employment income of this employer alone, which the conguaglio "
        "or the tax return settles"
    ),
    status=CalculationStatus.PROVISIONAL,
)


def _income_issues(
    annual: Decimal, facts: CurrentYearTaxFacts | None, tax_year: int
) -> tuple[CalculationIssue, ...]:
    """Return the issues of the income the somma esente was computed on.

    Returns:
        Nothing when no amount is due; otherwise the missing current-year facts,
        or the band taken without the income of other employers.
    """
    if money(annual) <= _ZERO:
        return ()
    if facts is None or facts.tax_year != tax_year:
        return (INCOME_UNKNOWN_ISSUE,)
    if facts.other_employment_income > _ZERO or facts.exempt_regime_income > _ZERO:
        return (BAND_ASSUMED_ISSUE,)
    return ()


def resolve_somma_esente(
    tax_computation: TaxComputation,
    rules: YearRules,
    opening: PeriodState,
    withholding: WithholdingPosition,
    tax_year: int,
    posting: SommaEsentePosting,
    current_year: CurrentYearTaxFacts | None,
) -> SommaEsenteOutcome:
    """Return the somma esente of the run, its postings and its decision.

    Args:
        tax_computation: IRPEF computation of the run, whose
            ``somma_esente`` component is the annual entitlement on the
            projected income.
        rules: Year rules; the credit is in force when they configure it.
        opening: State the run opens with: the YTD account and any recovery
            of the credit opened this tax year.
        withholding: Position of the payment in the withholding schedule.
        tax_year: Tax year of the run.
        posting: Where the amount is posted.
        current_year: Income of the tax year beyond this employment, which
            enters the reddito complessivo of c. 4; ``None`` when not
            stated.

    Returns:
        The outcome; empty when the credit is not in force and nothing of
        it was paid or is being recovered this tax year.
    """
    account = opening.cash.somma_esente
    plan = opening.cash.obligations.recovery_of(tax_year, SOMMA_ESENTE_RECOVERY)
    if rules.somma_esente is None and plan is None and account.net == _ZERO:
        return SommaEsenteOutcome()
    amounts = {c.name: c.amount for c in tax_computation.components}
    annual = amounts.get("somma_esente", _ZERO)
    period = amounts.get("somma_esente_period", _ZERO)
    remaining = withholding.remaining
    settlement = settle(annual, period, withholding, account, plan, posting.run)
    decision = CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code=settlement.reason,
        rule=_RULE,
        rule_version=(
            str(rules.year) if rules.ruleset is None else rules.ruleset.version
        ),
        inputs={
            "annual_due": money(annual),
            "period_share": period,
            "net_paid_before": account.net,
            "remaining_slots": str(remaining),
            "recovery_in_progress": str(plan is not None).lower(),
        },
        amount=settlement.amount,
    )
    items, entries = postings(settlement.amount, posting)
    return SommaEsenteOutcome(
        amount=settlement.amount,
        due=money(annual),
        reason=settlement.reason,
        plan=settlement.plan,
        items=items,
        entries=entries,
        decisions=(decision,),
        issues=_income_issues(annual, current_year, tax_year),
    )
