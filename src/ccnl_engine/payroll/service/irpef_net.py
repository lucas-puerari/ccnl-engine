"""Net annual IRPEF and the withholding of one run.

:func:`net_irpef` gives the imposta netta of a projected annual income: the
gross tax of art. 11 TUIR less the art. 13 and art. 12 TUIR deductions and
the ulteriore detrazione (L. 207/2024 art. 1 c. 6), after the
sterilizzazione of L. 199/2025 art. 1 c. 3-4, floored at zero.

:func:`run_withholding` splits what is still owed between the run and the
slots after it.  Income the run pays once (a bonus, overtime, arrears
taxed ordinarily) is not in the projection of the later slots, so the tax
it adds is withheld on the run that pays it.  Art. 23 c. 2 DPR 600/1973
withholds when the sums are paid: lett. a) on the sums "corrisposti in
ciascun periodo di paga", lett. b) "sulle mensilità aggiuntive e sui
compensi della stessa natura".  The rest of the balance is spread over the
remaining slots as before, and the last slot settles the whole balance at
the conguaglio (art. 23 c. 3).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.service import irpef as irpef_svc
from ccnl_engine.payroll.service import irpef_credits
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.tax.domain.rules import YearRules
    from ccnl_engine.payroll.service.irpef_credits import CreditOutcome

__all__ = ["NetIrpef", "net_irpef", "run_withholding"]

_ZERO = Decimal(0)


@dataclass(frozen=True, slots=True)
class NetIrpef:
    """Net annual IRPEF with the amounts it is built from.

    Attributes:
        gross: Imposta lorda, art. 11 TUIR.
        work_deduction: Art. 13 c. 1 TUIR deduction.
        family_deductions: Art. 12 TUIR deductions, computed by the caller.
        ulteriore: Outcome of the ulteriore detrazione, ``None`` when the
            year does not configure it.
        effective_deductions: Sum of the deductions after the
            sterilizzazione.
    """

    gross: Decimal
    work_deduction: Decimal
    family_deductions: Decimal
    ulteriore: CreditOutcome | None
    effective_deductions: Decimal

    @property
    def total_deductions(self) -> Decimal:
        """Sum of the deductions before the sterilizzazione."""
        ulteriore = _ZERO if self.ulteriore is None else self.ulteriore.amount
        return self.work_deduction + self.family_deductions + ulteriore

    @property
    def net(self) -> Decimal:
        """Imposta netta: gross less the effective deductions, at least zero."""
        return max(_ZERO, self.gross - self.effective_deductions)


def net_irpef(
    taxable: Decimal,
    rules: YearRules,
    *,
    family_deductions: Decimal,
    eligible_work_days: int,
) -> NetIrpef:
    """Return the net annual IRPEF of ``taxable``.

    Args:
        taxable: Annual IRPEF taxable income.
        rules: Year rules.
        family_deductions: Annual art. 12 TUIR deductions.
        eligible_work_days: Days of employment in the tax year, at most 365.

    Returns:
        The net IRPEF and its components.
    """
    gross = irpef_svc.irpef_gross(taxable, rules)
    work = irpef_svc.work_income_deduction(
        taxable, eligible_work_days, constants=rules.work_deduction
    )
    ulteriore = (
        None
        if rules.ulteriore_detrazione is None
        else irpef_credits.ulteriore_detrazione_outcome(
            taxable, rules.ulteriore_detrazione, eligible_work_days
        )
    )
    total = (
        work + family_deductions + (_ZERO if ulteriore is None else ulteriore.amount)
    )
    effective = irpef_svc.apply_sterilizzazione_detrazioni(
        total, taxable, rules.sterilizzazione_detrazioni
    )
    return NetIrpef(gross, work, family_deductions, ulteriore, effective)


def run_withholding(
    net_annual: Decimal,
    net_without_one_off: Decimal | None,
    withheld: Decimal,
    remaining: int,
) -> Decimal:
    """Return the IRPEF the run withholds.

    Args:
        net_annual: Net annual IRPEF on the full projection.
        net_without_one_off: Net annual IRPEF on the projection without the
            one-off income of the run, ``None`` when the run pays none.
        withheld: IRPEF withheld in the tax year before the run.
        remaining: Withholding slots not yet closed, the run included.

    Returns:
        On the last slot the whole balance, which is negative for a refund.
        Before it, the tax the one-off income adds (at least zero) plus the
        share of the remaining balance, the share floored at zero.
    """
    balance = net_annual - withheld
    if remaining == 1:
        return money(balance)
    one_off_tax = (
        _ZERO
        if net_without_one_off is None
        else max(_ZERO, net_annual - net_without_one_off)
    )
    share = max(_ZERO, (balance - one_off_tax) / remaining)
    return money(share) + money(one_off_tax)
