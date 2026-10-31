"""Deductions from the net pay the employer pays to a third party.

The caller states the facts of each order or contract: its kind, the day it
was notified to the employer, the first payment it applies to, the amount
due to the creditor and, for the kinds whose amount is set outside the law,
the monthly amount.  The engine computes what each run withholds from the
net pay and the legal limits
(:mod:`~ccnl_engine.personal_withholding.rules`), and carries what was
withheld to date in the closing state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, final

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import (
    parse_enum,
    reject,
    require_date,
    require_decimal,
    require_instance,
    require_str,
)

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

__all__ = [
    "FEATURE",
    "PersonalWithholding",
    "PersonalWithholdingKind",
    "check_personal_withholdings",
]

#: Capability the deductions are validated and decided under.
FEATURE = "personal_withholdings"


class PersonalWithholdingKind(StrEnum):
    """What the employer withholds for, which sets the legal limit.

    Attributes:
        SALARY_ASSIGNMENT: Cessione del quinto: a loan repaid by assigning
            up to a fifth of the net pay (art. 5 and 52 DPR 180/1950).
        PAYMENT_DELEGATION: Delegazione di pagamento: a further installment
            the employer accepted to pay to a lender (art. 69 and 70 DPR
            180/1950).
        MAINTENANCE: Garnishment for maintenance (crediti alimentari), in
            the measure the judge authorized (art. 545 c. 3 c.p.c.).
        TAX: Garnishment for taxes due to the State, the provinces or the
            municipalities (art. 545 c. 4 c.p.c.).
        TAX_COLLECTION: Garnishment by the agente della riscossione (art.
            72-ter DPR 602/1973; art. 171 D.Lgs. 33/2025 from 2027).
        ORDINARY: Garnishment for any other credit (art. 545 c. 4 c.p.c.).
    """

    SALARY_ASSIGNMENT = "salary_assignment"
    PAYMENT_DELEGATION = "payment_delegation"
    MAINTENANCE = "maintenance"
    TAX = "tax"
    TAX_COLLECTION = "tax_collection"
    ORDINARY = "ordinary"


#: Kinds whose monthly amount is stated: the installment of the contract or
#: the measure the judge set.  The law sets the amount of the others.
INSTALLMENT_KINDS = frozenset({
    PersonalWithholdingKind.SALARY_ASSIGNMENT,
    PersonalWithholdingKind.PAYMENT_DELEGATION,
    PersonalWithholdingKind.MAINTENANCE,
})


@final
@dataclass(frozen=True, slots=True)
class PersonalWithholding:
    """One garnishment order or salary assignment notified to the employer.

    Attributes:
        withholding_id: Non-blank reference of the order or contract,
            unique within the employment; the closing state carries what
            was withheld to date under it.
        kind: What it is withheld for; its string value is accepted.
        notified_on: Day the order or the contract was notified to the
            employer.  It ranks the deductions: an earlier one keeps its
            amount and a later one takes what the combined limits leave
            (art. 68-70 DPR 180/1950).
        starts_on: First payment date it applies to, not before
            ``notified_on``: a cessione takes effect from its notification
            (art. 1 DPR 180/1950).
        total_due: Amount due to the creditor when the deduction starts on
            this payroll, above zero: the loan to repay, or the credit and
            costs of the order.  For a deduction started on another payroll,
            what is left of it.
        installment: Monthly installment of a salary assignment or a
            payment delegation, or monthly measure of a maintenance order,
            above zero; ``None`` for the other kinds, whose amount is the
            legal fraction of the net pay.

    Raises:
        InvalidInputError: When a field is not of its type, ``starts_on``
            precedes ``notified_on``, ``total_due`` is not above zero, or
            ``installment`` is missing for a kind that states it or given
            for one that does not.
    """

    withholding_id: str
    kind: PersonalWithholdingKind
    notified_on: date
    starts_on: date
    total_due: Decimal
    installment: Decimal | None = None

    def __post_init__(self) -> None:  # noqa: D105
        owner = "PersonalWithholding"
        require_str(
            self.withholding_id,
            f"{owner}.withholding_id",
            feature=FEATURE,
            non_blank=True,
        )
        kind = parse_enum(
            self.kind, PersonalWithholdingKind, f"{owner}.kind", feature=FEATURE
        )
        object.__setattr__(self, "kind", kind)
        require_date(self.notified_on, f"{owner}.notified_on", feature=FEATURE)
        require_date(self.starts_on, f"{owner}.starts_on", feature=FEATURE)
        if self.starts_on < self.notified_on:
            reject(
                f"{owner}.starts_on",
                f"a date not before notified_on ({self.notified_on.isoformat()})",
                self.starts_on,
                feature=FEATURE,
            )
        require_decimal(
            self.total_due, f"{owner}.total_due", feature=FEATURE, positive=True
        )
        stated = kind in INSTALLMENT_KINDS
        require_decimal(
            self.installment,
            f"{owner}.installment",
            feature=FEATURE,
            positive=True,
            optional=not stated,
        )
        if not stated and self.installment is not None:
            reject(
                f"{owner}.installment",
                f"None for a {kind} garnishment, whose amount the law sets",
                self.installment,
                feature=FEATURE,
            )


def check_personal_withholdings(
    value: object, path: str
) -> tuple[PersonalWithholding, ...]:
    """Validate the deductions of an employment.

    Returns:
        The deductions as a tuple.

    Raises:
        InvalidInputError: When ``value`` is not a tuple or a list of
            :class:`PersonalWithholding`, or two share an id.
    """
    if not isinstance(value, tuple | list):
        reject(path, "a tuple or a list of PersonalWithholding", value, feature=FEATURE)
    for i, item in enumerate(value):
        require_instance(item, PersonalWithholding, f"{path}[{i}]", feature=FEATURE)
    ids = [w.withholding_id for w in value]
    if len(set(ids)) != len(ids):
        msg = f"two personal withholdings share an id: {sorted(ids)}"
        raise InvalidInputError(msg, field=path, feature=FEATURE)
    return tuple(value)
