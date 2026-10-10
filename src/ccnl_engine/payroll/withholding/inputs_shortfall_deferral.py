"""Year-end IRPEF shortfall the worker asked in writing to defer.

Art. 23 c. 3 DPR 600/1973, in force for the tax year 2026 (Normattiva:
"in vigore dal 21-5-2022 al 31-12-2026"; the same text is art. 33 c. 4
D.Lgs. 33/2025, which applies from 1 January 2027):

    "In caso di incapienza delle retribuzioni a subire il prelievo delle
    imposte dovute in sede di conguaglio di fine anno entro il 28 febbraio
    dell'anno successivo, il sostituito può dichiarare per iscritto al
    sostituto di volergli versare l'importo corrispondente alle ritenute
    ancora dovute, ovvero, di autorizzarlo a effettuare il prelievo sulle
    retribuzioni dei periodi di paga successivi al secondo dello stesso
    periodo di imposta. Sugli importi di cui è differito il pagamento si
    applica l'interesse in ragione dello 0,50 per cento mensile, che è
    trattenuto e versato nei termini e con le modalità previste per le
    somme cui si riferisce."

The engine reads it as follows:

- the conguaglio of tax year N runs by 28 February of N+1, on the first two
  pay periods of N+1 at the latest, so the deferred IRPEF is withheld on the
  regular payslips of N+1 from March (:data:`FIRST_DEFERRAL_MONTH`) and
  within N+1.  The norm sets no installments: each payslip withholds what
  its pay leaves, until the amount is exhausted;
- the interest is simple, 0.50 per cent for each whole month from the pay
  period of the conguaglio to the pay period of the payslip that withholds the
  amount.  The norm does not say when the count starts; this is the
  engine's reading, recorded on each decision.  The interest is withheld
  and remitted as the IRPEF it refers to ("nei termini e con le modalità
  previste per le somme cui si riferisce");
- what the last withholding slot of N+1, or the last run of the employment,
  still leaves is communicated to the worker as any other shortfall.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal
from typing import final

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.validation import (
    reject,
    require_date,
    require_decimal,
    require_int,
)

__all__ = [
    "DEFERRAL_MONTHLY_RATE",
    "FIRST_DEFERRAL_MONTH",
    "DeferredInstallment",
    "DeferredShortfall",
    "ShortfallDeferralRequest",
]

#: "l'interesse in ragione dello 0,50 per cento mensile" (art. 23 c. 3).
DEFERRAL_MONTHLY_RATE = Decimal("0.005")
#: First month of N+1 whose payslip withholds: "successivi al secondo".
FIRST_DEFERRAL_MONTH = 3
_ZERO = Decimal(0)
_CENT = Decimal("0.01")
_MIN_TAX_YEAR = 2020
_FEATURE = "shortfall_deferral"
#: First tax year of the testo unico of D.Lgs. 33/2025 (art. 243).
_TESTO_UNICO_FROM = 2027


def _conguaglio_rule(tax_year: int) -> str:
    """Return the citation of the deferral rule for the conguaglio of a year.

    Returns:
        Art. 33 c. 4 D.Lgs. 33/2025 from 2027, art. 23 c. 3 DPR 600/1973
        before.
    """
    if tax_year >= _TESTO_UNICO_FROM:
        return "art. 33 c. 4 D.Lgs. 33/2025"
    return "art. 23 c. 3 DPR 600/1973"


@final
@dataclass(frozen=True, slots=True)
class ShortfallDeferralRequest:
    """The worker's written authorization to defer the year-end shortfall.

    Attributes:
        signed_on: Date of the written request.  It must fall between 1
            January of the tax year and the end of February of the next
            one, the deadline of the conguaglio.

    Raises:
        InvalidInputError: When ``signed_on`` is not a date.
    """

    signed_on: date

    def __post_init__(self) -> None:  # noqa: D105
        require_date(
            self.signed_on, "ShortfallDeferralRequest.signed_on", feature=_FEATURE
        )

    def check_for(self, tax_year: int) -> None:
        """Check that the request can defer the conguaglio of ``tax_year``.

        Raises:
            InvalidInputError: When ``signed_on`` is before the tax year or
                after the end of February of the next year.
        """
        first = date(tax_year, 1, 1)
        last = date(tax_year + 1, 3, 1) - timedelta(days=1)
        if not first <= self.signed_on <= last:
            msg = (
                f"the deferral request of the conguaglio {tax_year} must be "
                f"signed between {first.isoformat()} and "
                f"{last.isoformat()} ({_conguaglio_rule(tax_year)}); got "
                f"{self.signed_on.isoformat()}"
            )
            raise InvalidInputError(msg, feature=_FEATURE)


@final
@dataclass(frozen=True, slots=True)
class DeferredInstallment:
    """What one payslip withholds of a deferred shortfall.

    Attributes:
        principal: IRPEF of the earlier year withheld.
        interest: Interest on it, 0.50 per cent a month.
        months: Whole months of deferral the interest is computed on.
    """

    principal: Decimal
    interest: Decimal
    months: int

    @property
    def total(self) -> Decimal:
        """Principal and interest withheld."""
        return self.principal + self.interest


@final
@dataclass(frozen=True, slots=True)
class DeferredShortfall:
    """IRPEF of a conguaglio deferred on the worker's written request.

    Attributes:
        tax_year: Tax year whose conguaglio found the shortfall; it is
            withheld in ``tax_year + 1``.
        signed_on: Date of the written request.
        deferred_from: First day of the pay period of the conguaglio: the
            interest runs from its month.
        irpef: IRPEF still to withhold, positive.
    """

    tax_year: int
    signed_on: date
    deferred_from: date
    irpef: Decimal

    def __post_init__(self) -> None:
        """Validate the tax year, the dates and the amount.

        A ``tax_year`` before 2020, a ``deferred_from`` outside ``tax_year``
        and January and February of the next year, or an ``irpef`` that is
        not a positive finite amount raises
        :class:`~ccnl_engine.errors.InvalidInputError`.
        """
        owner = "DeferredShortfall"
        require_int(
            self.tax_year, f"{owner}.tax_year", feature=_FEATURE, minimum=_MIN_TAX_YEAR
        )
        require_date(self.signed_on, f"{owner}.signed_on", feature=_FEATURE)
        require_date(self.deferred_from, f"{owner}.deferred_from", feature=_FEATURE)
        require_decimal(self.irpef, f"{owner}.irpef", feature=_FEATURE, positive=True)
        start = self.deferred_from
        if not (
            start.year == self.tax_year
            or (start.year == self.tax_year + 1 and start.month < FIRST_DEFERRAL_MONTH)
        ):
            reject(
                f"{owner}.deferred_from",
                f"the payment date of the conguaglio {self.tax_year}",
                start,
                feature=_FEATURE,
            )

    @property
    def withheld_in(self) -> int:
        """Tax year whose payslips withhold the deferred IRPEF."""
        return self.tax_year + 1

    def months_to(self, year: int, month: int) -> int:
        """Whole months from the conguaglio month to ``year`` and ``month``.

        Returns:
            The number of months, at least zero.
        """
        start = self.deferred_from
        return max(0, (year - start.year) * 12 + month - start.month)

    def due_in(self, year: int, month: int) -> bool:
        """Whether a payslip of ``year`` and ``month`` may withhold it.

        Returns:
            ``True`` from March of :attr:`withheld_in` to its December.
        """
        return year == self.withheld_in and month >= FIRST_DEFERRAL_MONTH

    def post(
        self, available: Decimal, year: int, month: int
    ) -> tuple[DeferredInstallment | None, DeferredShortfall | None]:
        """Return what a payslip leaving ``available`` pay withholds of it.

        The principal is the largest amount whose interest still fits in
        ``available``, at most the residual.

        Returns:
            The installment, ``None`` when nothing fits, and the shortfall
            left after it, ``None`` once exhausted.
        """
        months = self.months_to(year, month)
        factor = 1 + DEFERRAL_MONTHLY_RATE * months
        principal = min(
            self.irpef,
            (max(_ZERO, available) / factor).quantize(_CENT, rounding=ROUND_DOWN),
        )
        # principal * factor <= available, both in cents, so the interest
        # rounded half up to the cent still fits in ``available``.
        interest = money(principal * DEFERRAL_MONTHLY_RATE * months)
        if principal <= _ZERO:
            return None, self
        left = self.irpef - principal
        after = (
            None
            if left == _ZERO
            else DeferredShortfall(
                self.tax_year, self.signed_on, self.deferred_from, left
            )
        )
        return DeferredInstallment(principal, interest, months), after
