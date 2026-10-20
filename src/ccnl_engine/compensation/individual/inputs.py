"""Pay elements agreed with the worker above the CCNL minimum.

A superminimo or an assegno ad personam is a monthly amount the employer
pays on top of the CCNL tables by individual agreement.  The engine pays it
as a fixed allowance of the level: part time, a partial month and the ratei
of an extra month scale it like the minimo, and it enters the TFR base
unless the agreement says otherwise.  An absorbable element shrinks by the
increases of the minimo after the day its amount is stated (see
:mod:`~ccnl_engine.compensation.individual.rules`).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import (
    reject,
    require_bool,
    require_code,
    require_date,
    require_decimal,
    require_instance,
)

__all__ = ["FEATURE", "IndividualElement", "check_individual_elements"]

#: Feature the individual elements are validated and decided under.
FEATURE = "base_salary"


@dataclass(frozen=True, slots=True)
class IndividualElement:
    """A monthly pay element agreed with the worker, above the CCNL minimum.

    Attributes:
        code: Lower snake case code of the element, unique within the
            employment, e.g. ``"superminimo"``; it names the earning
            (``allowance_code``) on the payslip.
        monthly: Full-time monthly amount in EUR on :attr:`as_of`, above
            zero.
        absorbable: Whether the increases of the CCNL minimo absorb it
            (superminimo assorbibile).  ``False`` keeps it whole on a
            renewal (assegno ad personam non assorbibile).
        as_of: Day on which :attr:`monthly` is the amount, required for an
            absorbable element: the increases of the minimo of the level
            from this day to the competence date of the run reduce it, down
            to zero.
        extra_months: Whether the element is paid on the extra months of
            the CCNL (tredicesima, quattordicesima) too.
        tfr_relevant: Whether the element enters the TFR base (art. 2120
            c. 2 c.c.: every amount paid in connection with the employment,
            unless the agreement excludes it).

    Raises:
        InvalidInputError: When a field is not of its type, ``monthly`` is
            not above zero, or an absorbable element has no ``as_of``.
    """

    code: str
    monthly: Decimal
    absorbable: bool = False
    as_of: date | None = None
    extra_months: bool = True
    tfr_relevant: bool = True

    def __post_init__(self) -> None:  # noqa: D105
        require_code(self.code, "IndividualElement.code", feature=FEATURE)
        require_decimal(
            self.monthly, "IndividualElement.monthly", feature=FEATURE, positive=True
        )
        for name in ("absorbable", "extra_months", "tfr_relevant"):
            require_bool(
                getattr(self, name), f"IndividualElement.{name}", feature=FEATURE
            )
        require_date(
            self.as_of, "IndividualElement.as_of", feature=FEATURE, optional=True
        )
        if self.absorbable and self.as_of is None:
            reject(
                "IndividualElement.as_of",
                "the day of the stated amount, required for an absorbable element",
                self.as_of,
                feature=FEATURE,
            )


def check_individual_elements(
    value: object, path: str
) -> tuple[IndividualElement, ...]:
    """Validate the individual elements of an employment.

    Returns:
        The elements as a tuple.

    Raises:
        InvalidInputError: When ``value`` is not a tuple or a list of
            :class:`IndividualElement`, or two elements share a code.
    """
    if not isinstance(value, tuple | list):
        reject(path, "a tuple or a list of IndividualElement", value, feature=FEATURE)
    for i, element in enumerate(value):
        require_instance(element, IndividualElement, f"{path}[{i}]", feature=FEATURE)
    codes = [e.code for e in value]
    if len(set(codes)) != len(codes):
        msg = f"two individual elements share a code: {sorted(codes)}"
        raise InvalidInputError(msg, field=path, feature=FEATURE)
    return tuple(value)
