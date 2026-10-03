"""Termination event: TFR settlement at cessazione."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.shared.domain.validation import require_date, require_decimal

if TYPE_CHECKING:
    from datetime import date

__all__ = ["TerminationTFREvent"]

_ZERO = Decimal(0)
_ONE = Decimal(1)


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
        feature = "termination_tfr"
        require_date(self.event_date, "TerminationTFREvent.event_date", feature=feature)
        require_decimal(
            self.amount, "TerminationTFREvent.amount", feature=feature, minimum=_ZERO
        )
        require_decimal(
            self.separate_tax_rate,
            "TerminationTFREvent.separate_tax_rate",
            feature=feature,
            minimum=_ZERO,
            maximum=_ONE,
        )
