"""Typed YTD accumulator sub-containers for PeriodState.

Each container groups logically related year-to-date running totals.
``PeriodState`` holds one instance of each; they are all frozen dataclasses
with no circular dependencies so they can be tested and serialised in
isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan

_ZERO = Decimal(0)

__all__ = [
    "EarningsYtd",
    "FringeYtd",
    "SommaEsenteAccount",
    "TaxYtd",
    "TrattamentoAccount",
]


@dataclass(frozen=True)
class EarningsYtd:
    """Running totals for earned income and INPS contribution bases.

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
        """Validate that taxed fringe does not exceed total fringe value.

        Raises:
            ValueError: When ``taxed > value``.
        """
        if self.taxed > self.value:
            msg = (
                f"FringeYtd.taxed ({self.taxed}) "
                f"must be <= FringeYtd.value ({self.value})"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class TaxYtd:
    """Running totals for tax withheld this year.

    Attributes:
        irpef: IRPEF already withheld this tax year.
        surtax: Cumulative regional and municipal surtax (addizionale
            regionale/comunale) withheld this tax year.
    """

    irpef: Decimal = _ZERO
    surtax: Decimal = _ZERO


@dataclass(frozen=True)
class TrattamentoAccount:
    """YTD credit account for trattamento integrativo (Art. 1 D.L. 3/2020).

    Attributes:
        recognized: Cumulative trattamento integrativo given to the worker
            this tax year.
        recovered: Cumulative trattamento integrativo recovered (clawed back)
            this tax year when prior-period credits exceeded the annual
            entitlement.
        plan: Active installment recovery plan from D.L. 3/2020 art. 1 co. 3,
            or ``None`` when no recovery is in progress.
    """

    recognized: Decimal = _ZERO
    recovered: Decimal = _ZERO
    plan: RecoveryPlan | None = field(default=None)

    def __post_init__(self) -> None:
        """Validate that recovered credit does not exceed recognized credit.

        Raises:
            ValueError: When ``recovered > recognized``.
        """
        if self.recovered > self.recognized:
            msg = (
                f"TrattamentoAccount.recovered ({self.recovered}) "
                f"must be <= recognized ({self.recognized})"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class SommaEsenteAccount:
    """YTD credit account for somma esente (L. 207/2024).

    Attributes:
        recognized: Cumulative somma esente bonus given to the worker this
            tax year.  Used to detect and recover over-payments when the
            income projection changes mid-year.
    """

    recognized: Decimal = _ZERO
