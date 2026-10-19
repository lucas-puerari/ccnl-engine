"""Termination event: TFR settlement at cessazione."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_date, require_decimal

if TYPE_CHECKING:
    from datetime import date

__all__ = ["TerminationTFREvent"]

_ZERO = Decimal(0)
_ONE = Decimal(1)
_FEATURE = "termination_tfr"


@dataclass(frozen=True)
class TerminationTFREvent:
    """TFR settlement at cessazione (art. 19 TUIR, tassazione separata).

    Without ``amount`` the engine computes the TFR due and its separate
    tax (:mod:`~ccnl_engine.severance.settlement.services`): the fund at 31
    December of the year before (``Employment.tfr_fund``), the TFR accrued
    in the year by the runs of the employment and the revaluation of the
    year, taxed at the average IRPEF rate of the reference income of art.
    19 c. 1 TUIR.  A ``separate_tax_rate`` without ``amount`` overrides
    that rate on the taxable the engine computes.

    With ``amount`` the caller states the payout and must state its rate
    too: the engine cannot split a payout it did not compute into the TFR
    accrued and the revaluations art. 19 c. 1 leaves out of the taxable,
    so the rate applies to the whole ``amount``.  Every value the caller
    states is reported as a ``caller_supplied`` decision.

    Attributes:
        event_date: Date of cessazione.
        amount: Total TFR payout in EUR, ``None`` for the engine to compute
            it.  Must be >= 0.
        separate_tax_rate: Applicable tassazione separata rate, ``None``
            for the engine to compute it.  Must be in [0, 1].

    Raises:
        InvalidInputError: When a value is out of range, or ``amount`` is
            stated without ``separate_tax_rate``.
    """

    event_date: date
    amount: Decimal | None = None
    separate_tax_rate: Decimal | None = None

    def __post_init__(self) -> None:  # noqa: D105
        require_date(
            self.event_date, "TerminationTFREvent.event_date", feature=_FEATURE
        )
        require_decimal(
            self.amount,
            "TerminationTFREvent.amount",
            feature=_FEATURE,
            minimum=_ZERO,
            optional=True,
        )
        require_decimal(
            self.separate_tax_rate,
            "TerminationTFREvent.separate_tax_rate",
            feature=_FEATURE,
            minimum=_ZERO,
            maximum=_ONE,
            optional=True,
        )
        if self.amount is not None and self.separate_tax_rate is None:
            msg = (
                "TerminationTFREvent.amount needs its separate_tax_rate: the "
                "engine computes the rate only on the TFR it computes (omit "
                "amount), since art. 19 c. 1 TUIR takes the revaluations "
                "already taxed out of the taxable"
            )
            raise InvalidInputError(
                msg, field="TerminationTFREvent.separate_tax_rate", feature=_FEATURE
            )

    @property
    def computed(self) -> bool:
        """Whether the engine computes the payout (no caller ``amount``)."""
        return self.amount is None
