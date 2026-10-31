"""What the runs withheld to date under each personal withholding.

The closing state carries it from run to run and across tax years
(:class:`~ccnl_engine.balance.obligation.models.EmploymentObligations`):
the residual due on a run is the ``total_due`` the caller states less what
was withheld to date.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import final

from ccnl_engine.personal_withholding.inputs import FEATURE
from ccnl_engine.validators import require_decimal, require_str

__all__ = ["WithheldToDate"]


@final
@dataclass(frozen=True, slots=True)
class WithheldToDate:
    """Amount withheld to date under one personal withholding.

    Attributes:
        withholding_id: Id of the
            :class:`~ccnl_engine.personal_withholding.inputs.PersonalWithholding`.
        withheld: Amount withheld by the runs closed so far, at least zero.

    Raises:
        InvalidInputError: When ``withholding_id`` is blank or ``withheld``
            is not a finite amount at least zero.
    """

    withholding_id: str
    withheld: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        owner = "WithheldToDate"
        require_str(
            self.withholding_id,
            f"{owner}.withholding_id",
            feature=FEATURE,
            non_blank=True,
        )
        require_decimal(
            self.withheld, f"{owner}.withheld", feature=FEATURE, minimum=Decimal(0)
        )
