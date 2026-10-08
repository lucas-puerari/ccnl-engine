"""Net annual IRPEF and the withholding of one run.

:func:`net_irpef` gives the imposta netta of a projected annual income: the
gross tax of art. 11 TUIR less the art. 13 and art. 12 TUIR deductions and
the ulteriore detrazione (L. 207/2024 art. 1 c. 6), floored at zero.

The 440 EUR reduction of art. 16-ter c. 5-bis TUIR (inserted by L. 199/2025
art. 1 c. 4) for a reddito complessivo above 200,000 EUR is not applied: it
lowers only the deductions for the oneri detraibili al 19% (medical expenses
excluded), the donations to political parties and the catastrophe insurance
premiums, and the payroll computes none of them.  The art. 12 and art. 13
deductions and the ulteriore detrazione are outside its scope.  An input
that brings one of those oneri into the run must carry the reduction.

:func:`run_withholding` returns the IRPEF of the run: before the last slot
the tax of its pay period under art. 23 c. 2 DPR 600/1973
(:mod:`~ccnl_engine.payroll.service.period_withholding`), on the last slot
the whole balance of the year, the conguaglio of art. 23 c. 3.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service import irpef_credits
from ccnl_engine.payroll.service.irpef import irpef_gross
from ccnl_engine.payroll.service.irpef_deductions import work_income_deduction

if TYPE_CHECKING:
    from ccnl_engine.payroll.service.irpef_credits import CreditOutcome
    from ccnl_engine.tax.domain.ruleset import YearRules

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
        ulteriore_effect: IRPEF the ulteriore detrazione actually removes:
            the net without it less the net with it.  Below the deduction
            when the net is floored at zero.
        foreign_credit: Credit for foreign taxes (art. 165 TUIR) deducted
            from the imposta netta, at most :attr:`net_before_credit`.
    """

    gross: Decimal
    work_deduction: Decimal
    family_deductions: Decimal
    ulteriore: CreditOutcome | None
    ulteriore_effect: Decimal = _ZERO
    foreign_credit: Decimal = _ZERO

    @property
    def total_deductions(self) -> Decimal:
        """Sum of the art. 13, art. 12 and ulteriore deductions."""
        ulteriore = _ZERO if self.ulteriore is None else self.ulteriore.amount
        return self.work_deduction + self.family_deductions + ulteriore

    @property
    def net_before_credit(self) -> Decimal:
        """Imposta netta: gross less the deductions, at least zero."""
        return max(_ZERO, self.gross - self.total_deductions)

    @property
    def net(self) -> Decimal:
        """Net IRPEF due: the imposta netta less the foreign tax credit."""
        return self.net_before_credit - self.foreign_credit


def net_irpef(
    taxable: Decimal,
    rules: YearRules,
    *,
    family_deductions: Decimal,
    eligible_work_days: int,
    fixed_term: bool,
    other_income: Decimal = _ZERO,
) -> NetIrpef:
    """Return the net annual IRPEF of ``taxable``.

    Args:
        taxable: Annual IRPEF taxable income.
        rules: Year rules.
        family_deductions: Annual art. 12 TUIR deductions.
        eligible_work_days: Days of employment in the tax year, at most 365.
        fixed_term: Whether an employment of the year is fixed-term, which
            raises the minimum of the art. 13 deduction (c. 1 lett. a) TUIR),
            proportioned to the days in the withholding.
        other_income: Reddito complessivo beyond this employment, which
            the ulteriore detrazione reads with it (L. 207/2024 art. 1 c. 6),
            the exempt share of c. 9 included.

    Returns:
        The net IRPEF and its components.
    """
    gross = irpef_gross(taxable, rules)
    work = work_income_deduction(
        taxable,
        eligible_work_days,
        constants=rules.work_deduction,
        fixed_term=fixed_term,
    )
    ulteriore = (
        None
        if rules.ulteriore_detrazione is None
        else irpef_credits.ulteriore_detrazione_outcome(
            taxable + other_income, rules.ulteriore_detrazione, eligible_work_days
        )
    )
    effect = _ZERO
    if ulteriore is not None:
        without = work + family_deductions
        effect = max(_ZERO, gross - without) - max(
            _ZERO, gross - without - ulteriore.amount
        )
    return NetIrpef(gross, work, family_deductions, ulteriore, effect)


def run_withholding(
    net_annual: Decimal,
    withheld: Decimal,
    remaining: int,
    period: Decimal,
    carried: Decimal = _ZERO,
) -> Decimal:
    """Return the IRPEF the run withholds.

    Args:
        net_annual: Net annual IRPEF on the projection, the final taxable
            income on the last slot.
        withheld: IRPEF withheld in the tax year before the run.
        remaining: Withholding slots not yet paid, the run included.
        period: IRPEF of the pay period of the run (art. 23 c. 2).
        carried: IRPEF due on earlier runs that their pay did not cover,
            withheld in full on this run.

    Returns:
        On the last slot the whole balance, which is negative for a refund.
        Before it, the IRPEF of the period plus the carried IRPEF.
    """
    if remaining == 1:
        return money(net_annual - withheld)
    return period + carried
