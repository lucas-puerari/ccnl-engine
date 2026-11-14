"""The art. 15 TUIR deduction of the charges the conguaglio takes in.

Art. 15 c. 1 TUIR deducts 19% of the charges from the imposta lorda: the
rate of the AdE 730/2026 instructions (rigo E1).  The Normattiva page shows
22% at every date back to 2004 and records no act that changed the rate, so
it is not read as one.  Letter c): the medical expenses "per la parte che
eccede lire 250 mila" (129.11 EUR).  Letter f): premiums up to 530 EUR
against death or a permanent disability of at least 5%, raised to 750 EUR
with the premiums that protect a person with a severe disability, and up
to 1291.14 EUR against the risk of not being self-sufficient, net of the
former.  C. 3-bis: the letter f) deduction is whole up to 120,000 EUR of
reddito complessivo, then (240,000 - reddito) / 120,000, nil from 240,000;
letter c) is never reduced.  Art. 16-ter TUIR caps the charges above 75,000
EUR of income, but it leaves out the medical expenses and its smallest cap
(4,000 EUR) is above the letter f) maximum (1,291.14 EUR): it never binds
here.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.tax_credit.art15.inputs import Art15Kind

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.tax_credit.art15.inputs import Art15Expense

__all__ = ["art15_deduction"]

_RATE = Decimal("0.19")
_HEALTH_FRANCHISE = Decimal("129.11")
_LIFE_CAP = Decimal(530)
_PROTECTION_CAP = Decimal(750)
_CARE_CAP = Decimal("1291.14")
_FULL_UP_TO = Decimal(120000)
_NIL_FROM = Decimal(240000)
_ZERO = Decimal(0)


def _total(expenses: Iterable[Art15Expense], kind: Art15Kind) -> Decimal:
    return sum((e.amount for e in expenses if e.kind is kind), _ZERO)


def _income_share(income: Decimal) -> Decimal:
    if income <= _FULL_UP_TO:
        return Decimal(1)
    return max(_ZERO, (_NIL_FROM - income) / _FULL_UP_TO)


def art15_deduction(expenses: tuple[Art15Expense, ...], income: Decimal) -> Decimal:
    """Return the art. 15 deduction of ``expenses`` at reddito ``income``.

    Returns:
        19% of the medical expenses above the franchise plus 19% of the
        premiums within their caps, the latter reduced by the income share
        of c. 3-bis, rounded to the cent.
    """
    health = max(_ZERO, _total(expenses, Art15Kind.HEALTH) - _HEALTH_FRANCHISE)
    life = min(_total(expenses, Art15Kind.LIFE_INSURANCE), _LIFE_CAP)
    protection = min(
        _total(expenses, Art15Kind.DISABILITY_PROTECTION_INSURANCE),
        _PROTECTION_CAP - life,
    )
    care = min(
        _total(expenses, Art15Kind.LONG_TERM_CARE_INSURANCE),
        _CARE_CAP - life - protection,
    )
    premiums = (life + protection + care) * _income_share(income)
    return money((health + premiums) * _RATE)
