"""Tax year attribution of a payroll run from its payment date.

Employment income is taxed on a cash basis (TUIR art. 51 c. 1): a run
belongs to the tax year in which it is paid.  Under the *cassa allargata*
rule of the same paragraph, sums paid by 12 January are attributed to the
previous tax year when they compensate periods of that year.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import ClassVar

from ccnl_engine.engine.errors import InvalidInputError

__all__ = [
    "DEFAULT_PAYMENT_DAY",
    "TaxYearAttribution",
    "TaxYearBasis",
    "TaxYearPolicy",
    "monthly_payment_date",
]

#: Day of the run month on which a year calculation pays each run.
DEFAULT_PAYMENT_DAY = 28
_LAST_DAY_IN_EVERY_MONTH = 28


class TaxYearBasis(StrEnum):
    """Rule that attributed a run to its tax year."""

    CASH = "cash"
    """Paid in the tax year: the payment year."""

    EXTENDED_CASH = "extended_cash"
    """Paid by 12 January for a period of the previous year: that year."""


@dataclass(frozen=True)
class TaxYearAttribution:
    """Tax year of one run and the rule that selected it.

    Attributes:
        tax_year: Calendar year whose statutory tables and year-to-date
            state apply to the run.
        basis: Rule that selected ``tax_year``.
    """

    tax_year: int
    basis: TaxYearBasis


@dataclass(frozen=True)
class TaxYearPolicy:
    """Attribute a payroll run to a tax year from its payment date.

    Rules, in order (TUIR art. 51 c. 1):

    1. A payment before the first day of the competence period is rejected.
    2. A payment in the competence year belongs to that year.
    3. A payment in the next year, on or before 12 January, belongs to the
       competence year (*cassa allargata*).  The extension reaches back one
       year only: December 2025 paid on 10 January 2027 belongs to 2027.
    4. Any other payment belongs to the payment year (cash principle).

    No upper bound is set on the payment date: a run paid two years late is
    attributed to the payment year, and the tax tables bundled for that
    year are the practical limit.  Separate taxation of arrears (TUIR
    art. 17 c. 1 lett. b) is not modelled.
    """

    EXTENDED_CASH_LAST_DAY: ClassVar[tuple[int, int]] = (1, 12)

    def attribute(self, competence: date, payment: date) -> TaxYearAttribution:
        """Return the tax year of a run.

        Args:
            competence: First day of the competence period.
            payment: Date on which the run is paid.

        Returns:
            The attributed tax year and the rule that selected it.

        Raises:
            InvalidInputError: When ``payment`` is before ``competence``.
        """
        if payment < competence:
            msg = (
                f"payment date {payment.isoformat()} is before the start of "
                f"the competence period {competence.isoformat()}"
            )
            raise InvalidInputError(msg, feature="tax_year")
        month, day = self.EXTENDED_CASH_LAST_DAY
        if payment.year == competence.year + 1 and payment <= date(
            payment.year, month, day
        ):
            return TaxYearAttribution(competence.year, TaxYearBasis.EXTENDED_CASH)
        return TaxYearAttribution(payment.year, TaxYearBasis.CASH)


def monthly_payment_date(year: int, month: int, day: int) -> date:
    """Return the payment date of a run paid on *day* of its own month.

    Args:
        year: Year of the run month.
        month: Run month (1-12).
        day: Day of the month, 1-28 so that every month has it.

    Returns:
        ``date(year, month, day)``.

    Raises:
        InvalidInputError: When *day* is outside 1-28.
    """
    if not 1 <= day <= _LAST_DAY_IN_EVERY_MONTH:
        msg = (
            f"payment day must be between 1 and {_LAST_DAY_IN_EVERY_MONTH}, "
            f"so that every month has it; got {day}"
        )
        raise InvalidInputError(msg, feature="payment_date")
    return date(year, month, day)
