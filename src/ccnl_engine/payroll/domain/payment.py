"""Identity of one payment: a competence run and the day it is paid.

A run is the competence of a month (or an extra month); a payment is the
cash event that settles it.  The tax year follows from the payment
(TUIR art. 51 c. 1), so December 2026 paid on 13 January 2027 is a payment
of tax year 2027 of a 2026 competence run.  The tax cash state records
payments; the accrual state records competence runs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import final

from ccnl_engine.payroll.domain.run import PayrollRunId
from ccnl_engine.payroll.domain.tax_year import TaxYearPolicy
from ccnl_engine.shared.domain.validation import reject, require_date, require_instance

__all__ = ["PaymentId"]

_FEATURE = "payment"
_PAYMENT_ID_PATTERN = re.compile(r"(.+)@(\d{4}-\d{2}-\d{2})")


@final
@dataclass(frozen=True)
class PaymentId:
    """Identifier of one payment: the run it pays and its payment date.

    The text form is ``"{run_id}@{payment_date}"``, e.g.
    ``"2026-12-regular@2027-01-13"``.  A run is paid once, so the run id
    alone identifies the payment within an employment; the date fixes the
    tax year the payment belongs to.

    Attributes:
        run_id: The competence run the payment settles.
        payment_date: Day the run is paid, not before the first day of the
            run month.

    Raises:
        InvalidInputError: When a field is not of its type or the payment
            precedes the run month.
    """

    run_id: PayrollRunId
    payment_date: date

    def __post_init__(self) -> None:  # noqa: D105
        require_instance(
            self.run_id, PayrollRunId, "PaymentId.run_id", feature=_FEATURE
        )
        require_date(self.payment_date, "PaymentId.payment_date", feature=_FEATURE)
        if self.payment_date < self.competence:
            reject(
                "PaymentId.payment_date",
                f"on or after the first day of the run month {self.competence}",
                self.payment_date,
                feature=_FEATURE,
            )

    def __str__(self) -> str:
        """Return the text form.

        Returns:
            ``"{run_id}@{payment_date}"``, e.g. ``"2026-12-regular@2027-01-13"``.
        """
        return f"{self.run_id}@{self.payment_date.isoformat()}"

    @classmethod
    def parse(cls, text: str) -> PaymentId:
        """Parse the text form ``"{run_id}@{payment_date}"``.

        Args:
            text: A payment id such as ``"2026-12-regular@2027-01-13"``.

        Returns:
            The typed identifier.  A ``text`` that is not a well-formed
            payment id raises
            :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.
        """
        match = _PAYMENT_ID_PATTERN.fullmatch(text) if isinstance(text, str) else None
        if match is None:
            reject(
                "PaymentId",
                "a payment id such as '2026-12-regular@2027-01-13'",
                text,
                feature=_FEATURE,
            )
        run_id, paid_on = match.groups()
        try:
            payment_date = date.fromisoformat(paid_on)
        except ValueError:
            reject("PaymentId.payment_date", "an ISO date", paid_on, feature=_FEATURE)
        return cls(run_id=PayrollRunId.parse(run_id), payment_date=payment_date)

    @property
    def competence(self) -> date:
        """First day of the run month."""
        return date(self.run_id.year, self.run_id.month, 1)

    @property
    def tax_year(self) -> int:
        """Tax year of the payment (TUIR art. 51 c. 1, cassa allargata)."""
        return TaxYearPolicy().attribute(self.competence, self.payment_date).tax_year

    @property
    def is_prior_competence(self) -> bool:
        """Whether the payment settles a run of a year before its tax year."""
        return self.run_id.year < self.tax_year
