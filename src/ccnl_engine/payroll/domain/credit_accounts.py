"""YTD accounts of the tax credits paid on the payslip and recovered if not due."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar, Self

from ccnl_engine.payroll.domain.ytd_accounts import check_non_negative

_ZERO = Decimal(0)
_CODE = re.compile(r"[a-z][a-z0-9_]*")

__all__ = [
    "CreditAccount",
    "SommaEsenteAccount",
    "TrattamentoAccount",
    "UlterioreDetrazioneAccount",
]


@dataclass(frozen=True)
class CreditAccount:
    """YTD account of a tax credit paid on the payslip and recovered if not due.

    The credit is paid run by run on a projection of the annual income;
    the updated annual entitlement can fall below what was paid, and the
    excess is then recovered.  The installment plan of a recovery is not
    held here: it can outlast the tax year, so it lives in
    :class:`~ccnl_engine.payroll.domain.obligations.EmploymentObligations`
    under the tax year and the :attr:`KIND` of the account.

    Attributes:
        recognized: Credit paid to the worker this tax year.
        recovered: Credit taken back this tax year because it was not due.
            Installments posted in a later tax year do not enter it.
        due: Updated annual entitlement computed by the last run, ``None``
            before a run has computed it.
        reason: Reason code of the last decision on the credit, e.g.
            ``"income_above_upper_threshold"``, ``None`` before a run.
    """

    #: ``RecoveryPlan.kind`` of a recovery of this credit.
    KIND: ClassVar[str] = "tax_credit"

    recognized: Decimal = _ZERO
    recovered: Decimal = _ZERO
    due: Decimal | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        """Validate non-negativity and that recovered is within recognized.

        Raises:
            ValueError: When an amount is negative, ``recovered`` exceeds
                ``recognized`` or ``reason`` is not lower snake case.
        """
        check_non_negative(self)
        name = type(self).__name__
        if self.recovered > self.recognized:
            msg = (
                f"{name}.recovered ({self.recovered}) "
                f"must be <= recognized ({self.recognized})"
            )
            raise ValueError(msg)
        if self.reason is not None and not _CODE.fullmatch(self.reason):
            msg = f"{name}.reason must be lower snake case; got {self.reason!r}"
            raise ValueError(msg)

    @property
    def net(self) -> Decimal:
        """Credit paid and not taken back: ``recognized - recovered``."""
        return self.recognized - self.recovered

    @property
    def residual(self) -> Decimal:
        """Over-payment still to recover against the updated entitlement.

        Returns:
            ``max(net - due, 0)``, zero while ``due`` is unknown.
        """
        if self.due is None:
            return _ZERO
        return max(self.net - self.due, _ZERO)

    def after(
        self, period_amount: Decimal, due: Decimal | None, reason: str | None
    ) -> Self:
        """Return the account after a run that posted ``period_amount``.

        Args:
            period_amount: Signed amount of the run: positive is paid,
                negative is recovered.
            due: Updated annual entitlement, ``None`` to keep the current.
            reason: Reason code of the run's decision, ``None`` to keep it.

        Returns:
            A new account of the same type.
        """
        return type(self)(
            recognized=self.recognized + max(_ZERO, period_amount),
            recovered=self.recovered + max(_ZERO, -period_amount),
            due=self.due if due is None else due,
            reason=self.reason if reason is None else reason,
        )


@dataclass(frozen=True)
class TrattamentoAccount(CreditAccount):
    """YTD credit account for trattamento integrativo (Art. 1 D.L. 3/2020).

    Over-payments are recovered as soon as a run finds them, in eight
    installments above 60 EUR (D.L. 3/2020 art. 1 c. 3).
    """

    KIND: ClassVar[str] = "trattamento_integrativo"


@dataclass(frozen=True)
class SommaEsenteAccount(CreditAccount):
    """YTD credit account for the somma esente (L. 207/2024 art. 1 c. 4).

    Over-payments are recovered at the conguaglio, in ten installments above
    60 EUR (L. 207/2024 art. 1 c. 7).
    """

    KIND: ClassVar[str] = "somma_esente"


@dataclass(frozen=True)
class UlterioreDetrazioneAccount(CreditAccount):
    """YTD account of the ulteriore detrazione (L. 207/2024 art. 1 c. 6).

    The deduction lowers the IRPEF withheld rather than being paid, so
    ``recognized`` is the part of the annual deduction the withholding of
    the runs before the conguaglio has already applied: each run recognizes
    ``(due - net) / remaining slots``, never less than zero.  At the
    conguaglio the excess over the annual due is recovered, in ten
    installments above 60 EUR (art. 1 c. 7).
    """

    KIND: ClassVar[str] = "ulteriore_detrazione_lavoro"
