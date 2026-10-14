"""Independent oracle of the credits paid on top of IRPEF, tax year 2026.

Written from the statutory text, deliberately without importing anything from
``ccnl_engine``.  It covers an employee whose only income is the employment:

- trattamento integrativo, D.L. 3/2020 art. 1 cc. 1-2 (Normattiva, text in
  force on 14 October 2026): due when the reddito complessivo is not above
  15,000 EUR and the imposta lorda on the employment income exceeds "la
  detrazione spettante ai sensi dell'articolo 13, comma 1 [...] diminuita
  dell'importo di 75 euro rapportato al periodo di lavoro nell'anno"; its
  1,200 EUR "è rapportato al periodo di lavoro" (c. 2).  The band above
  15,000 EUR of c. 1, second period, is outside this scope;
- somma esente, L. 207/2024 art. 1 cc. 4-5 (Normattiva, same day): due when
  the reddito complessivo is not above 20,000 EUR, at 7.1% of the
  employment income up to 8,500 EUR, 5.3% up to 15,000 EUR and 4.8% above;
  the income is "rapportato all'intero anno" only to pick the percentage.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from tests.knowledge.ccnl_engine.irpef.oracles import (
    employment_deduction,
    gross_irpef,
)

__all__ = ["somma_esente", "trattamento_integrativo"]

_CENT = Decimal("0.01")
_DAYS_IN_YEAR = 365
_ZERO = Decimal("0.00")


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def trattamento_integrativo(income: Decimal, days: int) -> Decimal:
    """Return the trattamento integrativo of ``days`` of employment.

    Returns:
        ``1,200 * days / 365`` when the income and the capienza allow it,
        else zero; rounded to cents.

    Raises:
        ValueError: When ``income`` is above 15,000, outside the scope.
    """
    if income > Decimal(15_000):
        msg = f"income {income} is above the 15,000 EUR this oracle covers"
        raise ValueError(msg)
    threshold = employment_deduction(income, days) - _cents(
        Decimal(75) * days / _DAYS_IN_YEAR
    )
    if gross_irpef(income) <= threshold:
        return _ZERO
    return _cents(Decimal(1_200) * days / _DAYS_IN_YEAR)


def somma_esente(income: Decimal, days: int) -> Decimal:
    """Return the somma esente of an employment income earned in ``days``.

    Returns:
        The percentage of the annualised income times ``income``, zero
        above 20,000 EUR; rounded to cents.
    """
    if income > Decimal(20_000):
        return _ZERO
    annualised = income * _DAYS_IN_YEAR / days
    if annualised <= Decimal(8_500):
        rate = Decimal("0.071")
    elif annualised <= Decimal(15_000):
        rate = Decimal("0.053")
    else:
        rate = Decimal("0.048")
    return _cents(income * rate)
