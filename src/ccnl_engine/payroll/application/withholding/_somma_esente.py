"""Somma esente of a run: its share, the conguaglio and the recovery.

The somma esente (L. 207/2024 art. 1 c. 4) is paid by the withholding agent
run by run on the projected annual income.  Its entitlement is verified at
the conguaglio; an amount found not due is recovered there, in full up to
60 EUR and otherwise in ten equal installments from the payslip that
carries the conguaglio (art. 1 c. 7).  Before the conguaglio a run pays
its share of the annual amount, capped at what is still due, and never
recovers: an excess found mid-year waits for the conguaglio.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import (
    _make_entry,
    _require_resolution,
)
from ccnl_engine.payroll.application.withholding._plan import slot_share
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.obligations import (
    RECOVERY_RULES,
    SOMMA_ESENTE_RECOVERY,
)
from ccnl_engine.payroll.domain.pay_items import PayItem, TaxCreditItem
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.credit_accounts import SommaEsenteAccount
    from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
    from ccnl_engine.payroll.domain.tax import TaxComputation
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = ["SommaEsenteOutcome", "SommaEsentePosting", "resolve_somma_esente"]

_ZERO = Decimal(0)
#: L. 207/2024 art. 1 c. 7: up to 60 EUR the excess is recovered in full.
_SINGLE_RECOVERY_LIMIT = Decimal(60)
_RULE = "l207-2024-art1-c4-c7"
CAPABILITY = "somma_esente"


@dataclass(frozen=True)
class SommaEsentePosting:
    """Where the somma esente of a run is posted.

    Attributes:
        resolver: Policy resolver of the run.
        policy_context: Policy context of the run.
        competence_period: Competence period of the run.
        payment_date: Payment date of the run.
        run_id: Identifier of the run, used in the item id.
    """

    resolver: PolicyResolver
    policy_context: PolicyContext
    competence_period: CompetencePeriod
    payment_date: date
    run_id: str


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
        entries: The matching ``CREDITS`` ledger entry, if any.
        decisions: What the run decided on the credit, empty when the
            credit is not in force and no recovery of it is running.
        issues: A provisional issue while an amount is due: the reddito
            complessivo of c. 4 is taken as the employment income.
    """

    amount: Decimal = _ZERO
    due: Decimal | None = None
    reason: str | None = None
    plan: RecoveryPlan | None = None
    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()


#: Other income can only raise the reddito complessivo, so the assumption
#: matters only while the somma esente is due.
INCOME_ASSUMED_ISSUE = CalculationIssue(
    code="somma_esente_income_assumed",
    message=(
        "somma_esente: the reddito complessivo of L. 207/2024 art. 1 c. 4 is "
        "taken as the employment income of this employer; other income may "
        "remove the entitlement, which the conguaglio or the tax return settles"
    ),
    status=CalculationStatus.PROVISIONAL,
)


@dataclass(frozen=True)
class _Settlement:
    amount: Decimal
    reason: str
    plan: RecoveryPlan | None = None


def _installment(plan: RecoveryPlan, reason: str | None = None) -> _Settlement:
    """Post the next installment of ``plan``.

    Args:
        plan: The recovery plan.
        reason: Reason code to record instead of the installment one.

    Returns:
        The negative installment and the plan still running after it.
    """
    last = plan.installments_posted == plan.installments_total - 1
    posted = "last_installment_posted" if last else "installment_posted"
    return _Settlement(
        amount=-plan.next_installment,
        reason=reason or posted,
        plan=None if last else plan.advance(),
    )


def _recover(excess: Decimal) -> _Settlement:
    """Recover an ``excess`` found at the conguaglio (L. 207/2024 art. 1 c. 7).

    Returns:
        The full excess up to 60 EUR, otherwise the first of ten equal
        installments with the plan of the others.
    """
    if excess <= _SINGLE_RECOVERY_LIMIT:
        return _Settlement(amount=-excess, reason="overpayment_recovered")
    plan = RecoveryPlan.create(
        SOMMA_ESENTE_RECOVERY,
        excess,
        RECOVERY_RULES[SOMMA_ESENTE_RECOVERY].installments,
    )
    return _installment(plan, "overpayment_recovery_opened")


def _settle(
    annual: Decimal,
    schedule: WithholdingSchedule,
    account: SommaEsenteAccount,
    plan: RecoveryPlan | None,
    remaining: int,
) -> _Settlement:
    """Decide the amount of the run.

    Returns:
        The installment of a running recovery; at the conguaglio the balance
        between the annual due and the net paid, recovered when negative;
        before it the slot share capped at what is still due.
    """
    if plan is not None:
        return _installment(plan)
    balance = money(annual) - account.net
    if remaining == 1:
        if balance < _ZERO:
            return _recover(-balance)
        return _Settlement(amount=balance, reason="settled_at_conguaglio")
    if balance < _ZERO:
        return _Settlement(amount=_ZERO, reason="overpayment_pending_conguaglio")
    share = min(slot_share(annual, schedule), balance)
    return _Settlement(amount=share, reason="share_paid" if share else "not_due")


def resolve_somma_esente(
    tax_computation: TaxComputation,
    rules: YearRules,
    opening: PeriodState,
    schedule: WithholdingSchedule,
    tax_year: int,
    posting: SommaEsentePosting,
) -> SommaEsenteOutcome:
    """Return the somma esente of the run, its postings and its decision.

    Args:
        tax_computation: IRPEF computation of the run, whose
            ``somma_esente`` component is the annual entitlement on the
            projected income.
        rules: Year rules; the credit is in force when they configure it.
        opening: State the run opens with: the YTD account and any recovery
            of the credit opened this tax year.
        schedule: Withholding schedule of the year.
        tax_year: Tax year of the run.
        posting: Where the amount is posted.

    Returns:
        The outcome; empty when the credit is not in force and nothing of
        it was paid or is being recovered this tax year.
    """
    account = opening.ytd.somma_esente
    plan = opening.obligations.recovery_of(tax_year, SOMMA_ESENTE_RECOVERY)
    if rules.somma_esente is None and plan is None and account.net == _ZERO:
        return SommaEsenteOutcome()
    annual = next(
        (c.amount for c in tax_computation.components if c.name == "somma_esente"),
        _ZERO,
    )
    slots_closed = opening.ytd.tax_withholding_periods_closed
    remaining = schedule.remaining(slots_closed)
    settlement = _settle(annual, schedule, account, plan, remaining)
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
            "net_paid_before": account.net,
            "remaining_slots": str(remaining),
            "recovery_in_progress": str(plan is not None).lower(),
        },
        amount=settlement.amount,
    )
    items, entries = _postings(settlement.amount, posting)
    return SommaEsenteOutcome(
        amount=settlement.amount,
        due=money(annual),
        reason=settlement.reason,
        plan=settlement.plan,
        items=items,
        entries=entries,
        decisions=(decision,),
        issues=(INCOME_ASSUMED_ISSUE,) if money(annual) > _ZERO else (),
    )


def _postings(
    amount: Decimal, posting: SommaEsentePosting
) -> tuple[tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Return the tax credit item and ``CREDITS`` entry of ``amount``.

    Returns:
        Empty tuples for a zero amount; otherwise one item and one entry,
        ``somma_esente_{run_id}`` when paid and
        ``somma_esente_recovery_{run_id}`` when recovered.
    """
    if amount == _ZERO:
        return (), ()
    policy_id = _require_resolution(
        posting.resolver, "tax_credit_item", posting.policy_context
    ).policy_id
    prefix = "somma_esente" if amount > _ZERO else "somma_esente_recovery"
    item_id = f"{prefix}_{posting.run_id}"
    item = TaxCreditItem(
        item_id=item_id,
        competence_period=posting.competence_period,
        payment_date=posting.payment_date,
        quantity=Decimal(1),
        amount=amount,
    )
    entry = _make_entry(
        item_id,
        item_id,
        "tax_credit_item",
        posting.competence_period,
        posting.payment_date,
        AccountKind.CREDITS,
        amount,
        policy_id=policy_id,
    )
    return (item,), (entry,)
