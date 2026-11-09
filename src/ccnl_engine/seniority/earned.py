"""Increments already earned at their original monthly amount."""

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.employment.fact.inputs import FEATURE
from ccnl_engine.validators import require_decimal, require_int


@dataclass(frozen=True, slots=True)
class EarnedIncrements:
    """Seniority increments whose amount stays as matured, not repriced.

    The CCNL table prices the increments of a run (Federmeccanica art. 6:
    after a promotion the increments "ragguagliati agli importi previsti per
    la categoria di arrivo").  Some keep the amount they matured at: the
    increments the norme transitorie of the same article fix, or those
    matured under another CCNL and kept on a transfer.  State them here, as
    the payslip prints them.

    Attributes:
        count: Increments matured, ``>= 0``.
        monthly: Their full-time monthly amount in EUR, ``>= 0``.

    Raises:
        InvalidInputError: When ``count`` is not a non-negative int or
            ``monthly`` not a non-negative Decimal.
    """

    count: int
    monthly: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        require_int(self.count, "EarnedIncrements.count", feature=FEATURE, minimum=0)
        require_decimal(
            self.monthly,
            "EarnedIncrements.monthly",
            feature=FEATURE,
            minimum=Decimal(0),
        )
