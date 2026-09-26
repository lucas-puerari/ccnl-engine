"""Termination event: TFR settlement at cessazione."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

__all__ = ["TerminationTFREvent"]


@dataclass(frozen=True)
class TerminationTFREvent:
    """TFR settlement at cessazione (art. 19 TUIR, tassazione separata).

    The caller supplies the applicable tax rate (determined via art. 19
    TUIR using the employee's prior-year average IRPEF rate).

    Attributes:
        event_date: Date of cessazione.
        amount: Total TFR payout in EUR.  Must be >= 0.
        separate_tax_rate: Applicable tassazione separata rate.  Must be in [0, 1].
    """

    event_date: date
    amount: Decimal
    separate_tax_rate: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = f"TerminationTFREvent.amount must be >= 0; got {self.amount}"
            raise InvalidInputError(msg, feature="termination_tfr")
        if not (0 <= self.separate_tax_rate <= 1):
            msg = (
                "TerminationTFREvent.separate_tax_rate must be in [0, 1]; "
                f"got {self.separate_tax_rate}"
            )
            raise InvalidInputError(msg, feature="termination_tfr")
