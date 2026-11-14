"""An art. 15 TUIR charge the employer withheld or paid under an agreement.

Art. 23 c. 3 DPR 600/1973: the conguaglio takes into account the art. 15
deductions "per oneri a fronte dei quali il datore di lavoro ha effettuato
trattenute", and, for letters c) and f), the payments under collective or
company agreements.  The charge and its amount are facts of the employer.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.validators import parse_enum, require_decimal

__all__ = ["Art15Expense", "Art15Kind"]

_OWNER = "Art15Expense"
_FEATURE = "art15_deductions"


class Art15Kind(StrEnum):
    """The art. 15 c. 1 TUIR charge.

    Attributes:
        HEALTH: Medical expenses, letter c).
        LIFE_INSURANCE: Premiums against death or a permanent disability of
            at least 5%, letter f).
        DISABILITY_PROTECTION_INSURANCE: Premiums against death to protect
            a person with a severe disability, letter f).
        LONG_TERM_CARE_INSURANCE: Premiums against the risk of not being
            self-sufficient, letter f).
    """

    HEALTH = "health"
    LIFE_INSURANCE = "life_insurance"
    DISABILITY_PROTECTION_INSURANCE = "disability_protection_insurance"
    LONG_TERM_CARE_INSURANCE = "long_term_care_insurance"


@dataclass(frozen=True, slots=True)
class Art15Expense:
    """An art. 15 charge of the year the conguaglio takes into account.

    Attributes:
        kind: The charge.
        amount: What the employer withheld for it, or paid under the
            agreement, in the tax year, ``>= 0``.

    Raises:
        InvalidInputError: When ``kind`` is not an :class:`Art15Kind` or
            ``amount`` is negative.
    """

    kind: Art15Kind
    amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        kind = parse_enum(self.kind, Art15Kind, f"{_OWNER}.kind", feature=_FEATURE)
        object.__setattr__(self, "kind", kind)
        require_decimal(
            self.amount, f"{_OWNER}.amount", feature=_FEATURE, minimum=Decimal(0)
        )
