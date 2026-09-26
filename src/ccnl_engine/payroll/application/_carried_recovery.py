"""Installments of a recovery carried from an earlier tax year.

An installment recovery opened by the conguaglio of year N (D.L. 3/2020
art. 1 c. 3 for the trattamento integrativo, L. 207/2024 art. 1 c. 7 for
the somma esente) keeps running on the runs of N+1.  Those installments
recover a credit of N: they are deducted on the payslip as a negative tax
credit line but do not enter the credit account of N+1, whose own
conguaglio runs as for any other year.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import (
    _make_entry,
    _require_resolution,
)
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.obligations import RECOVERY_RULES, RecoveryObligation
from ccnl_engine.payroll.domain.pay_items import PayItem, TaxCreditItem

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.payroll.domain.obligations import EmploymentObligations
    from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
    from ccnl_engine.payroll.domain.policy import PolicyContext, PolicyResolver


@dataclass(frozen=True)
class CarriedRecoveries:
    """Postings of the carried installments of one run.

    Attributes:
        items: One negative tax credit item per carried recovery.
        entries: The matching ``CREDITS`` ledger entries.
        remaining: The carried recoveries after this run, without those
            whose last installment was just posted.
        decisions: One decision per installment posted, capability
            :func:`recovery_capability` of the recovered credit.
    """

    items: tuple[PayItem, ...] = ()
    entries: tuple[LedgerEntry, ...] = ()
    remaining: tuple[RecoveryObligation, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()


def recovery_capability(kind: str) -> str:
    """Return the capability of the decisions recording a ``kind`` installment.

    Returns:
        ``"{kind}_recovery"``, e.g. ``"trattamento_integrativo_recovery"``.
    """
    return f"{kind}_recovery"


def installment_decision(obligation: RecoveryObligation) -> CalculationDecision:
    """Return the decision recording the next installment of ``obligation``.

    Returns:
        A final decision whose amount is the (negative) installment, with
        reason ``last_installment_posted`` when it settles the recovery and
        ``installment_posted`` otherwise.
    """
    plan = obligation.plan
    number = plan.installments_posted + 1
    last = number == plan.installments_total
    return CalculationDecision(
        capability=recovery_capability(plan.kind),
        status=CalculationStatus.FINAL,
        reason_code="last_installment_posted" if last else "installment_posted",
        rule=RECOVERY_RULES[plan.kind].rule,
        rule_version=str(obligation.tax_year),
        inputs={
            "origin_tax_year": str(obligation.tax_year),
            "installment_number": Decimal(number),
            "installments_total": Decimal(plan.installments_total),
            "residual_before": plan.residual,
        },
        amount=-plan.next_installment,
    )


def carried_item_id(obligation: RecoveryObligation, run_id: str) -> str:
    """Return the pay item id of a carried installment on ``run_id``.

    Returns:
        ``"{kind}_recovery_{origin year}_{run_id}"``.
    """
    return f"{obligation.plan.kind}_recovery_{obligation.tax_year}_{run_id}"


def post_carried_recoveries(
    obligations: EmploymentObligations,
    tax_year: int,
    resolver: PolicyResolver,
    policy_context: PolicyContext,
    competence_period: CompetencePeriod,
    payment_date: date,
    run_id: str,
) -> CarriedRecoveries:
    """Post one installment of every recovery opened before ``tax_year``.

    Returns:
        The postings and the carried recoveries still running; empty when
        no recovery is carried into ``tax_year``.
    """
    carried = obligations.carried_into(tax_year)
    if not carried:
        return CarriedRecoveries()
    policy_id = _require_resolution(
        resolver, "tax_credit_item", policy_context
    ).policy_id
    items: list[PayItem] = []
    entries: list[LedgerEntry] = []
    remaining: list[RecoveryObligation] = []
    for obligation in carried:
        installment = obligation.plan.next_installment
        item_id = carried_item_id(obligation, run_id)
        items.append(
            TaxCreditItem(
                item_id=item_id,
                competence_period=competence_period,
                payment_date=payment_date,
                quantity=Decimal(1),
                amount=-installment,
            )
        )
        entries.append(
            _make_entry(
                item_id,
                item_id,
                "tax_credit_item",
                competence_period,
                payment_date,
                AccountKind.CREDITS,
                -installment,
                policy_id=policy_id,
            )
        )
        advanced = obligation.advanced()
        if advanced is not None:
            remaining.append(advanced)
    return CarriedRecoveries(
        items=tuple(items),
        entries=tuple(entries),
        remaining=tuple(remaining),
        decisions=tuple(installment_decision(o) for o in carried),
    )
