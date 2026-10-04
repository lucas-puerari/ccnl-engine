"""What one run recognizes or recovers of the ulteriore detrazione.

The run recognizes the part of the deduction its withholding applied; at
the conguaglio an amount found not due is recovered in full up to 60 EUR
and otherwise in ten equal installments, the first one on the conguaglio
payslip (L. 207/2024 art. 1 c. 7).  On the last run of the employment
nothing is deferred (AdE circ. 4/E/2025 par. 1.2).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.obligations import RECOVERY_RULES, ULTERIORE_RECOVERY
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service.ulteriore_running_plan import AT_TERMINATION

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.credit_accounts import CreditAccount
    from ccnl_engine.payroll.domain.recovery_plan import PostedInstallment
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = ["UlterioreSettlement", "settle_ulteriore"]

_ZERO = Decimal(0)
#: L. 207/2024 art. 1 c. 7: up to 60 EUR the excess is recovered in full.
_SINGLE_RECOVERY_LIMIT = Decimal(60)
_RECOVERY_CAPABILITY = f"{ULTERIORE_RECOVERY}_recovery"


@dataclass(frozen=True, slots=True)
class UlterioreSettlement:
    """What one run recognizes or recovers of the ulteriore detrazione.

    Attributes:
        amount: Signed change of the account: positive recognized, negative
            taken back by the withholding or recovered at the conguaglio.
        due: Part of the annual deduction that lowers the IRPEF.
        reason: Reason code of the run.
        deferred: Part of the balance not withheld on the run, left to the
            installments of :attr:`plan`.
        plan: Installments still to post after the run, if any.
        installment: What the run posted of a plan opened by an earlier
            conguaglio of the tax year, ``None`` without one.
        residual_before: Residual of that plan before the run.
    """

    amount: Decimal
    due: Decimal
    reason: str
    deferred: Decimal = _ZERO
    plan: RecoveryPlan | None = None
    installment: PostedInstallment | None = None
    residual_before: Decimal = _ZERO

    def decisions(self, rules: YearRules) -> tuple[CalculationDecision, ...]:
        """Return the decisions of the recoveries of the run, if any.

        Returns:
            Final decisions, capability
            ``ulteriore_detrazione_lavoro_recovery``: one when the run
            recovers an excess, its amount the (negative) excess and its
            inputs the part deferred to the installments; one when the run
            posts an installment of a plan already running, its amount the
            (negative) installment.  Empty otherwise.
        """
        version = str(rules.year) if rules.ruleset is None else rules.ruleset.version
        rule = RECOVERY_RULES[ULTERIORE_RECOVERY].rule
        decisions: list[CalculationDecision] = []
        if self.reason.startswith("overpayment"):
            decisions.append(
                CalculationDecision(
                    capability=_RECOVERY_CAPABILITY,
                    status=CalculationStatus.FINAL,
                    reason_code=self.reason,
                    rule=rule,
                    rule_version=version,
                    inputs={"annual_due": self.due, "deferred": self.deferred},
                    amount=self.amount,
                )
            )
        if self.installment is not None:
            decisions.append(
                CalculationDecision(
                    capability=_RECOVERY_CAPABILITY,
                    status=CalculationStatus.FINAL,
                    reason_code=self.installment.reason,
                    rule=rule,
                    rule_version=version,
                    inputs={
                        "residual_before": self.residual_before,
                        "deferred": self.deferred,
                    },
                    amount=-self.installment.amount,
                )
            )
        return tuple(decisions)


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
        return AT_TERMINATION, _ZERO, None
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
            is left to the worker (art. 23 c. 3 DPR 600/1973; art. 33 c. 4
            D.Lgs. 33/2025 from 2027).

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
