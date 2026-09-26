"""Typed YTD accumulator sub-containers for TaxYearState.

Each container groups logically related year-to-date running totals.
``TaxYearState`` holds one instance of each; they are all frozen dataclasses
with no circular dependencies so they can be tested and serialised in
isolation.  A running total is a sum of what was paid or withheld this
tax year, so every one of them is non-negative, even when a single run
posts a negative adjustment.

The accounts of the tax credits paid on the payslip live in
:mod:`~ccnl_engine.payroll.domain.credit_accounts`.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

_ZERO = Decimal(0)

__all__ = [
    "EarningsYtd",
    "FringeYtd",
    "RegimeCapAccount",
    "TaxYtd",
    "WithholdingShortfall",
    "check_non_negative",
]


def check_non_negative(totals: DataclassInstance) -> None:
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
        check_non_negative(self)


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
        check_non_negative(self)
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
        check_non_negative(self)


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
        check_non_negative(self)

    @property
    def total(self) -> Decimal:
        """IRPEF plus surtax not yet withheld."""
        return self.irpef + self.surtax


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
