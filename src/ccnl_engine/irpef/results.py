"""Tax computation: per-component IRPEF audit trace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

__all__ = ["TaxComputation", "TaxLineItem"]


@dataclass(frozen=True)
class TaxLineItem:
    """One named component of the IRPEF computation for a period.

    Attributes:
        name: Short identifier, e.g. ``"irpef_gross"``, ``"work_deduction"``.
        amount: The component amount (annual, positive = reduces tax).
        rule_id: Machine-readable rule identifier, e.g. ``"art11-tuir"``.
        fonte: Human-readable legal reference, e.g. ``"Art. 11 TUIR"``.
    """

    name: str
    amount: Decimal
    rule_id: str
    fonte: str


@dataclass(frozen=True)
class TaxComputation:
    """Per-component IRPEF breakdown for one payroll period.

    ``ordinary_tax`` is the period IRPEF posted to the ``ORDINARY_TAX``
    ledger account (monthly withholding via conguaglio YTD).  It is
    negative in the final period when the worker is owed a refund
    (irpef_net_annual < irpef_withheld_ytd).
    ``trattamento_integrativo`` is posted to ``CREDITS``.
    ``components`` carries the annual amounts for each tax rule applied.

    Attributes:
        ordinary_tax: Period IRPEF withheld (monthly share; negative = refund).
        trattamento_integrativo: Period trattamento integrativo (monthly share).
        withholding_due: Net IRPEF still owed for the year (negative = refund).
        components: Per-rule annual amounts, ordered computation sequence.
    """

    ordinary_tax: Decimal
    trattamento_integrativo: Decimal
    withholding_due: Decimal
    components: tuple[TaxLineItem, ...]
