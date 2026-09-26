"""Typed YTD accumulator sub-containers for TaxYearState.

Each container groups logically related year-to-date running totals.
``TaxYearState`` holds one instance of each; they are all frozen dataclasses
with no circular dependencies so they can be tested and serialised in
isolation.  A running total is a sum of what was paid or withheld this
tax year, so every one of them is non-negative, even when a single run
posts a negative adjustment.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, fields
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, Self

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

_ZERO = Decimal(0)
_CODE = re.compile(r"[a-z][a-z0-9_]*")

__all__ = [
    "CreditAccount",
    "EarningsYtd",
    "FringeYtd",
    "RegimeCapAccount",
    "SommaEsenteAccount",
    "TaxYtd",
    "TrattamentoAccount",
    "UlterioreDetrazioneAccount",
    "WithholdingShortfall",
]


def _check_non_negative(totals: DataclassInstance) -> None:
    """Reject a negative or non-finite amount among the fields of ``totals``.

    Raises:
        ValueError: When a ``Decimal`` field is negative or not finite.
    """
    name = type(totals).__name__
    for f in fields(totals):
        value = getattr(totals, f.name)
        if isinstance(value, Decimal) and (not value.is_finite() or value < _ZERO):
            msg = f"{name}.{f.name} must be a non-negative amount; got {value}"
            raise ValueError(msg)


@dataclass(frozen=True)
class EarningsYtd:
    """Running totals for earned income and INPS contribution bases.

    Every total is non-negative.  No relation between them is enforced:
    ``taxable`` can exceed ``gross`` (a fringe benefit above the threshold
    enters the taxable income but not the cash earnings), and a state
    imported from another provider may carry an INPS base without gross.

    Attributes:
        gross: Sum of contractual gross earnings (CASH_EARNINGS ledger
            entries) closed this tax year.
        inps_base: Total INPS contribution base accumulated YTD.  Used to
            enforce the IVS massimale ceiling across periods.
        taxable: Total IRPEF taxable income accumulated YTD.
        inps_employee: Employee INPS contributions withheld YTD.
    """

    gross: Decimal = _ZERO
    inps_base: Decimal = _ZERO
    taxable: Decimal = _ZERO
    inps_employee: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that every total is non-negative.

        A negative or non-finite total raises ``ValueError``.
        """
        _check_non_negative(self)


@dataclass(frozen=True)
class FringeYtd:
    """Running totals for fringe benefits and Premio di Risultato.

    Attributes:
        value: Total fringe benefit value accumulated YTD.  Used to enforce
            the annual Art. 51 c. 3 TUIR threshold.
        taxed: Cumulative fringe base already subject to IRPEF/INPS this tax
            year.  Updated retroactively when the threshold is crossed.
        pdr: Cumulative Premio di Risultato (PdR) bonus amount eligible for
            the substitute-tax regime this tax year (5,000 EUR cap).
    """

    value: Decimal = _ZERO
    taxed: Decimal = _ZERO
    pdr: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate non-negativity and that taxed fringe is within the value.

        Raises:
            ValueError: When a total is negative or ``taxed > value``.
        """
        _check_non_negative(self)
        if self.taxed > self.value:
            msg = (
                f"FringeYtd.taxed ({self.taxed}) "
                f"must be <= FringeYtd.value ({self.value})"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class TaxYtd:
    """Running totals for tax withheld this year.

    Both totals are non-negative: a refund at the conguaglio lowers the
    IRPEF withheld to the annual tax due, never below zero.

    Attributes:
        irpef: IRPEF already withheld this tax year.
        surtax: Cumulative regional and municipal surtax (addizionale
            regionale/comunale) withheld this tax year.
    """

    irpef: Decimal = _ZERO
    surtax: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that both totals are non-negative.

        A negative or non-finite total raises ``ValueError``.
        """
        _check_non_negative(self)


@dataclass(frozen=True)
class WithholdingShortfall:
    """Tax due on earlier runs of the tax year and not yet withheld.

    A run withholds IRPEF and surtax only up to the pay left after the
    contributions and the other deductions; the rest is carried and added
    to what the next runs withhold.  What is still carried after the last
    withholding slot is not withheld by the employer: it is communicated to
    the worker, who pays it (art. 33 c. 4 D.Lgs. 33/2025, ex art. 23 c. 3
    DPR 600/1973).

    Attributes:
        irpef: IRPEF not yet withheld.
        surtax: Regional and municipal surtax not yet withheld.
    """

    irpef: Decimal = _ZERO
    surtax: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that both amounts are non-negative.

        A negative or non-finite amount raises ``ValueError``.
        """
        _check_non_negative(self)

    @property
    def total(self) -> Decimal:
        """IRPEF plus surtax not yet withheld."""
        return self.irpef + self.surtax


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
        _check_non_negative(self)
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


@dataclass(frozen=True)
class RegimeCapAccount:
    """YTD usage of the annual cap of a capped preferential tax regime.

    Tracks the part of the cap already taxed at the substitute rate this tax
    year, so that a later run only gets the substitute rate on what is left.
    Used for the night, holiday and shift supplement regime (L. 199/2025
    art. 1 cc. 10-11, cap 1,500 EUR).

    Attributes:
        used: Cumulative amount taxed at the substitute rate this tax year.
    """

    used: Decimal = _ZERO

    def __post_init__(self) -> None:
        """Validate that the used amount is non-negative.

        Raises:
            ValueError: When ``used < 0``.
        """
        if self.used < _ZERO:
            msg = f"RegimeCapAccount.used must be >= 0; got {self.used}"
            raise ValueError(msg)

    def available(self, cap: Decimal) -> Decimal:
        """Return the part of ``cap`` not yet used, never negative.

        Returns:
            ``max(cap - used, 0)``.
        """
        return max(cap - self.used, _ZERO)
