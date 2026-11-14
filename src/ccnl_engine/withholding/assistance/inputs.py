"""The 730-4 statement the employer receives and settles on the payslips.

The results of a 730 tax return reach the employer as the 730-4 statement
(art. 51-bis D.L. 69/2013; DM 164/1999 art. 19): the balance and the first
acconto of each tax, the second acconto, and the installments the worker
asked for.  They are facts the employer receives, not a computation of the
employer: the engine settles them, it does not compute the return.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.collection.validators import items_of_type, tuple_of
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import (
    parse_enum,
    require_date,
    require_decimal,
    require_int,
)

__all__ = ["Form730Installment", "Form730Kind", "Form730Line", "Form730Settlement"]

_FEATURE = "fiscal_adjustment"
_MAX_INSTALLMENTS = 6


class Form730Kind(StrEnum):
    """A line of the 730-4 statement.

    Attributes:
        IRPEF_BALANCE: IRPEF balance of the year of the return.
        IRPEF_FIRST_ADVANCE: First IRPEF acconto of the current year.
        IRPEF_SECOND_ADVANCE: Second or single IRPEF acconto, withheld in
            November and never in installments.
        REGIONAL_SURTAX: Regional surtax balance.
        MUNICIPAL_SURTAX: Municipal surtax balance.
        MUNICIPAL_SURTAX_ADVANCE: Municipal surtax acconto of the current
            year.
    """

    IRPEF_BALANCE = "irpef_balance"
    IRPEF_FIRST_ADVANCE = "irpef_first_advance"
    IRPEF_SECOND_ADVANCE = "irpef_second_advance"
    REGIONAL_SURTAX = "regional_surtax"
    MUNICIPAL_SURTAX = "municipal_surtax"
    MUNICIPAL_SURTAX_ADVANCE = "municipal_surtax_advance"


@dataclass(frozen=True, slots=True)
class Form730Line:
    """One amount of the 730-4 statement.

    Attributes:
        kind: The tax and part.
        amount: Positive to withhold, negative to refund.

    Raises:
        InvalidInputError: When ``kind`` is not a :class:`Form730Kind` or
            ``amount`` is not a ``Decimal``.
    """

    kind: Form730Kind
    amount: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        kind = parse_enum(self.kind, Form730Kind, "Form730Line.kind", feature=_FEATURE)
        object.__setattr__(self, "kind", kind)
        require_decimal(self.amount, "Form730Line.amount", feature=_FEATURE)


@dataclass(frozen=True, slots=True)
class Form730Settlement:
    """The 730-4 statement of the worker, as the employer received it.

    Attributes:
        received_on: Day the employer received it: the payslip of the month
            after settles it.
        lines: Its amounts, one per kind.
        installments: Monthly installments the worker asked for the
            balances and first acconti, 1 for none, at most 6.

    Raises:
        InvalidInputError: When a field is not of its type, a kind repeats,
            or ``installments`` is not between 1 and 6.
    """

    received_on: date
    lines: tuple[Form730Line, ...]
    installments: int = 1

    def __post_init__(self) -> None:  # noqa: D105
        owner = "Form730Settlement"
        require_date(self.received_on, f"{owner}.received_on", feature=_FEATURE)
        lines = tuple_of(
            self.lines,
            f"{owner}.lines",
            items_of_type(Form730Line, feature=_FEATURE),
            feature=_FEATURE,
        )
        object.__setattr__(self, "lines", lines)
        kinds = [line.kind for line in lines]
        if len(set(kinds)) != len(kinds):
            msg = f"{owner}.lines must hold each kind once"
            raise InvalidInputError(msg, field=f"{owner}.lines", feature=_FEATURE)
        require_int(
            self.installments,
            f"{owner}.installments",
            feature=_FEATURE,
            minimum=1,
            maximum=_MAX_INSTALLMENTS,
        )


@dataclass(frozen=True, slots=True)
class Form730Installment:
    """What one payslip settles of a line of the statement.

    Attributes:
        kind: The line.
        year: Year of the payslip that settles it.
        month: Month of that payslip.
        amount: Principal: positive withheld, negative refunded.
        interest: Interest of the deferral, withheld with the principal.
    """

    kind: Form730Kind
    year: int
    month: int
    amount: Decimal
    interest: Decimal = Decimal(0)
