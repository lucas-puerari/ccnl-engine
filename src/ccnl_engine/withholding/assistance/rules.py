"""How the payslips settle a 730-4 statement.

The rules the engine reads (DM 164/1999 art. 19; 730/2026 instructions for
the withholding agent):

- the statement is settled on the pay of the month after its receipt;
- an amount of 12 EUR or less of a tax is neither withheld nor refunded;
- a refund is paid in full on that pay;
- the balances and the first acconti are withheld in the installments the
  worker asked for, ending in November at the latest, each after the first
  with the interest of 0.33% for each month of deferral;
- the second or single acconto is withheld in November, never in
  installments.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.withholding.assistance.inputs import Form730Installment, Form730Kind

if TYPE_CHECKING:
    from ccnl_engine.withholding.assistance.inputs import Form730Settlement

__all__ = [
    "INSTALLMENT_RATE",
    "NOVEMBER",
    "THRESHOLD",
    "first_month",
    "schedule",
]

#: "Non sono effettuati versamenti né rimborsi" of 12 EUR or less, per tax.
THRESHOLD = Decimal(12)
#: Monthly interest on each installment after the first.
INSTALLMENT_RATE = Decimal("0.0033")
#: Month of the second or single acconto, and of the last installment.
NOVEMBER = 11
_ZERO = Decimal(0)


def first_month(settlement: Form730Settlement) -> tuple[int, int]:
    """Return the (year, month) of the payslip that settles first.

    Returns:
        The month after the receipt.
    """
    day = settlement.received_on
    return (day.year + 1, 1) if day.month == 12 else (day.year, day.month + 1)


def _installments(settlement: Form730Settlement, start: int) -> int:
    """Return the installments, cut so that the last falls in November.

    Returns:
        Those asked, at most the months from ``start`` to November, at
        least one.
    """
    return max(1, min(settlement.installments, NOVEMBER - start + 1))


def schedule(settlement: Form730Settlement) -> tuple[Form730Installment, ...]:
    """Return what each payslip of the year settles of ``settlement``.

    Returns:
        The refunds and single amounts on the first month, the balances and
        first acconti in installments with their interest, the second
        acconto in November; nothing for a line within the threshold.
    """
    year, start = first_month(settlement)
    count = _installments(settlement, start)
    out: list[Form730Installment] = []
    for line in settlement.lines:
        if abs(line.amount) <= THRESHOLD:
            continue
        if line.kind is Form730Kind.IRPEF_SECOND_ADVANCE:
            out.append(
                Form730Installment(line.kind, year, max(start, NOVEMBER), line.amount)
            )
            continue
        if line.amount < _ZERO or count == 1:
            out.append(Form730Installment(line.kind, year, start, line.amount))
            continue
        share = money(line.amount / count)
        for n in range(count):
            principal = line.amount - share * (count - 1) if n == count - 1 else share
            interest = money(principal * INSTALLMENT_RATE * n)
            out.append(
                Form730Installment(line.kind, year, start + n, principal, interest)
            )
    return tuple(out)
