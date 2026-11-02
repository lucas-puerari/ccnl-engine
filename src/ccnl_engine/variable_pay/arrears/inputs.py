"""The arrears of a contract renewal, taxed by the year they refer to."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.run.types import PeriodId
from ccnl_engine.validators import require_decimal, require_instance
from ccnl_engine.variable_pay.inputs import check_amount

if TYPE_CHECKING:
    from datetime import date

__all__ = ["ArrearsEvent"]

_ZERO = Decimal(0)
_ONE = Decimal(1)


@dataclass(frozen=True)
class ArrearsEvent:
    """Contract renewal arrears, taxed by the year they refer to.

    Arrears of a tax year earlier than the run are taxed separately (art. 17
    c. 1 lett. b TUIR; art. 19 c. 1 lett. b D.Lgs. 117/2026 from 2027) at
    :attr:`separate_tax_rate`; arrears of the tax year
    of the run are ordinary income of the run and the rate is not used.

    Attributes:
        event_date: Date the arrears are attributed to.
        amount: Gross arrears amount in EUR.  Must be >= 0.
        separate_tax_rate: Rate of the separate taxation: the rate on half
            the income of the two years before the year of receipt (art. 21
            c. 1 TUIR; art. 23 c. 1 D.Lgs. 117/2026 from 2027), in [0, 1].
            ``None``: the engine computes it from
            ``PriorYearTaxFacts.net_income_biennio``.
        reference_period: The competence period the arrears refer to.  An
            earlier tax year selects the separate taxation, the tax year of
            the run the ordinary one, a later year is rejected.  ``None``
            leaves the taxation undetermined: the run taxes the arrears
            separately as a simulation, with a ``missing_fact`` blocker.
        unused_deductions: The deductions of art. 12 and art. 13 cc. 1-2
            TUIR not used in the years the arrears refer to, which reduce
            the separate tax (art. 21 c. 4 TUIR), from the worker's
            declaration of those used.  ``None`` reduces nothing.
    """

    event_date: date
    amount: Decimal
    separate_tax_rate: Decimal | None = None
    reference_period: PeriodId | None = None
    unused_deductions: Decimal | None = None

    def __post_init__(self) -> None:  # noqa: D105
        check_amount(self.event_date, self.amount, "ArrearsEvent", "arrears")
        require_decimal(
            self.separate_tax_rate,
            "ArrearsEvent.separate_tax_rate",
            feature="arrears",
            minimum=_ZERO,
            maximum=_ONE,
            optional=True,
        )
        require_decimal(
            self.unused_deductions,
            "ArrearsEvent.unused_deductions",
            feature="arrears",
            minimum=_ZERO,
            optional=True,
        )
        require_instance(
            self.reference_period,
            PeriodId,
            "ArrearsEvent.reference_period",
            feature="arrears",
            optional=True,
        )
