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
deduction less the withholding with it), keeps on the conguaglio payslip
what c. 7 allows (the whole excess up to 60 EUR, otherwise the first
installment) and defers the other nine installments to the next runs as a
recovery obligation.  A part the withholding already took back before the
conguaglio, e.g. on the run that paid the income removing the deduction, is
not an excess found at the conguaglio and is not deferred.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.obligations import RECOVERY_RULES, ULTERIORE_RECOVERY
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.tax import TaxLineItem
from ccnl_engine.payroll.service.credit_decisions import credit_decision
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.tax.domain.rules import YearRules
    from ccnl_engine.payroll.domain.ytd_accounts import CreditAccount
    from ccnl_engine.payroll.service.irpef_credits import CreditOutcome

__all__ = ["UlterioreSettlement", "settle_ulteriore", "ulteriore_items"]

_ZERO = Decimal(0)
#: L. 207/2024 art. 1 c. 7: up to 60 EUR the excess is recovered in full.
_SINGLE_RECOVERY_LIMIT = Decimal(60)
_RULE = "l207-2024-art1-c6"
_RECOVERY_CAPABILITY = f"{ULTERIORE_RECOVERY}_recovery"


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


@dataclass(frozen=True, slots=True)
class UlterioreSettlement:
    """What one run recognizes or recovers of the ulteriore detrazione.

    Attributes:
        amount: Signed change of the account: positive recognized, negative
            taken back by the withholding or recovered at the conguaglio.
        due: Part of the annual deduction that lowers the IRPEF.
        reason: Reason code of the run.
        deferred: Part of the excess not withheld on the conguaglio payslip,
            left to the installments of :attr:`plan`.
        plan: Installments still to post after the conguaglio, if any.
    """

    amount: Decimal
    due: Decimal
    reason: str
    deferred: Decimal = _ZERO
    plan: RecoveryPlan | None = None

    def decisions(self, rules: YearRules) -> tuple[CalculationDecision, ...]:
        """Return the decision of a recovery at the conguaglio, if any.

        Returns:
            One final decision, capability
            ``ulteriore_detrazione_lavoro_recovery``, when the run recovers
            an excess: its amount is the (negative) excess, its inputs the
            part deferred to the installments.  Empty otherwise.
        """
        if not self.reason.startswith("overpayment"):
            return ()
        decision = CalculationDecision(
            capability=_RECOVERY_CAPABILITY,
            status=CalculationStatus.FINAL,
            reason_code=self.reason,
            rule=RECOVERY_RULES[ULTERIORE_RECOVERY].rule,
            rule_version=(
                str(rules.year) if rules.ruleset is None else rules.ruleset.version
            ),
            inputs={"annual_due": self.due, "deferred": self.deferred},
            amount=self.amount,
        )
        return (decision,)


def _recover(
    excess: Decimal, *, defer: bool
) -> tuple[str, Decimal, RecoveryPlan | None]:
    """Split an excess found at the conguaglio (L. 207/2024 art. 1 c. 7).

    Returns:
        ``(reason, deferred, plan)``: nothing deferred up to 60 EUR or,
        above it, when no later payslip exists (``defer`` false); otherwise ten equal
        installments, the first one kept on the conguaglio payslip and the
        other nine deferred.
    """
    if excess <= _SINGLE_RECOVERY_LIMIT:
        return "overpayment_recovered", _ZERO, None
    if not defer:
        return "overpayment_recovered_at_termination", _ZERO, None
    plan = RecoveryPlan.create(
        ULTERIORE_RECOVERY, excess, RECOVERY_RULES[ULTERIORE_RECOVERY].installments
    )
    deferred = excess - plan.next_installment
    return "overpayment_recovery_opened", deferred, plan.advance()


def settle_ulteriore(
    withholding: Decimal,
    withholding_without: Decimal,
    effect: Decimal,
    account: CreditAccount,
    *,
    last_slot: bool,
    defer: bool = True,
) -> UlterioreSettlement:
    """Return what the run recognizes or recovers of the deduction.

    The deduction the run recognizes is what its withholding is lower than
    the withholding without the deduction, computed on the same projection
    from the IRPEF withheld plus the deduction already recognized.  It is
    negative when the run takes back part of it, e.g. on a bonus that
    raises the income above the band; the account never goes below zero.
    On the last slot the difference settles the account on the annual due:
    an excess is the amount found not due at the conguaglio.

    Args:
        withholding: IRPEF of the run with the deduction.
        withholding_without: IRPEF of the run without it.
        effect: IRPEF the annual deduction removes on the projection.
        account: YTD account the run opens with.
        last_slot: Whether the run closes the last withholding slot.
        defer: Whether a payslip follows the conguaglio.  False when the
            employment ends in the tax year: the conguaglio at the
            cessation keeps the whole excess, and what the pay cannot cover
            is left to the worker (art. 33 c. 4 D.Lgs. 33/2025).

    Returns:
        The signed change of the account; on the last slot an excess above
        60 EUR opens ten installments, nine of them deferred, when
        ``defer`` holds.
    """
    amount = max(withholding_without - withholding, -account.net)
    due = money(effect)
    if not last_slot or amount >= _ZERO:
        reason = (
            ("settled_at_conguaglio" if last_slot else "share_recognized")
            if amount > _ZERO
            else ("recovered_by_withholding" if amount else "not_recognized")
        )
        return UlterioreSettlement(amount, due, reason)
    reason, deferred, plan = _recover(-amount, defer=defer)
    return UlterioreSettlement(amount, due, reason, deferred, plan)
